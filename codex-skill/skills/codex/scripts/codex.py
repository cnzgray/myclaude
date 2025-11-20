#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///
"""
Codex CLI wrapper with cross-platform support and session management.

Usage:
    New session:  uv run codex.py "task" [model] [workdir]
    Resume:       uv run codex.py resume <session_id> "task" [model] [workdir]
    Alternative:  python3 codex.py "task"
    Direct exec:  ./codex.py "task"
"""
import subprocess
import json
import sys
import os
from typing import Optional

DEFAULT_MODEL = 'gpt-5-codex'
DEFAULT_WORKDIR = '.'
DEFAULT_TIMEOUT = 7200  # 2 hours in seconds
FORCE_KILL_DELAY = 5


def log_error(message: str):
    """输出错误信息到 stderr"""
    sys.stderr.write(f"ERROR: {message}\n")


def log_warn(message: str):
    """输出警告信息到 stderr"""
    sys.stderr.write(f"WARN: {message}\n")


def resolve_timeout() -> int:
    """解析超时配置（秒）"""
    raw = os.environ.get('CODEX_TIMEOUT', '')
    if not raw:
        return DEFAULT_TIMEOUT

    try:
        parsed = int(raw)
        if parsed <= 0:
            log_warn(f"Invalid CODEX_TIMEOUT '{raw}', falling back to {DEFAULT_TIMEOUT}s")
            return DEFAULT_TIMEOUT
        # 环境变量是毫秒，转换为秒
        return parsed // 1000 if parsed > 10000 else parsed
    except ValueError:
        log_warn(f"Invalid CODEX_TIMEOUT '{raw}', falling back to {DEFAULT_TIMEOUT}s")
        return DEFAULT_TIMEOUT


def normalize_text(text) -> Optional[str]:
    """规范化文本：字符串或字符串数组"""
    if isinstance(text, str):
        return text
    if isinstance(text, list):
        return ''.join(text)
    return None


def parse_args():
    """解析命令行参数"""
    if len(sys.argv) < 2:
        log_error('Task required')
        sys.exit(1)

    # 解析可选标志（-c/--model_reasoning_effort），支持 -c=val 或 -c val
    reasoning = None
    i = 1
    cleaned_argv = [sys.argv[0]]
    while i < len(sys.argv):
        a = sys.argv[i]
        if a.startswith('-c=') or a.startswith('--model_reasoning_effort='):
            reasoning = a.split('=', 1)[1]
            i += 1
            continue
        if a in ('-c', '--model_reasoning_effort'):
            if i + 1 < len(sys.argv):
                reasoning = sys.argv[i + 1]
                i += 2
                continue
            else:
                log_error('-c/--model_reasoning_effort requires a value')
                sys.exit(1)
        cleaned_argv.append(a)
        i += 1

    # 检测是否为 resume 模式
    if cleaned_argv[1] == 'resume':
        if len(sys.argv) < 4:
            log_error('Resume mode requires: resume <session_id> <task>')
            sys.exit(1)
        return {
            'mode': 'resume',
            'session_id': sys.argv[2],
            'task': sys.argv[3],
            'model': sys.argv[4] if len(sys.argv) > 4 else DEFAULT_MODEL,
            'workdir': sys.argv[5] if len(sys.argv) > 5 else DEFAULT_WORKDIR,
            'reasoning': reasoning
        }
    else:
        return {
            'mode': 'new',
            'task': sys.argv[1],
            'model': sys.argv[2] if len(sys.argv) > 2 else DEFAULT_MODEL,
            'workdir': sys.argv[3] if len(sys.argv) > 3 else DEFAULT_WORKDIR,
            'reasoning': reasoning
        }


def build_codex_args(params: dict) -> list:
    """构建 codex CLI 参数"""
    if params['mode'] == 'resume':
        args = [
            'codex', 'e',
            '--skip-git-repo-check',
        ]

        reasoning = params.get('reasoning')
        if reasoning:
            args += ['-c', reasoning]

        args += [
            '--json',
            'resume',
            params['session_id'],
            params['task']
        ]

        return args
    else:
        args = [
            'codex', 'e',
            '-m', params['model'],
            '--dangerously-bypass-approvals-and-sandbox',
            '--skip-git-repo-check',
            '-C', params['workdir'],
        ]

        # 传递模型推理强度（如果指定）
        reasoning = params.get('reasoning')
        if reasoning:
            args += ['-c', reasoning]

        args += [
            '--json',
            params['task']
        ]
        return args


def main():
    params = parse_args()
    # 根据模型选择默认推理等级（若未指定）并校验
    def resolve_reasoning_choice(model: str, choice: Optional[str]) -> Optional[str]:
        model_lower = model.lower() if model else ''
        if 'gpt-5.1-codex-max' in model_lower:
            allowed = ('low', 'medium', 'high', 'xhigh')
            default = 'xhigh'
        elif 'gpt-5.1' in model_lower:
            allowed = ('low', 'medium', 'high')
            default = 'high'
        else:
            # 对未知模型使用 medium 作为安全默认
            allowed = ('low', 'medium', 'high')
            default = 'medium'

        if choice is None:
            return default
        normalized = choice.lower()
        if normalized not in allowed:
            log_warn(f"Unsupported reasoning '{choice}' for model {model}. Falling back to {default}")
            return default
        return normalized

    # resolve reasoning and inject into params
    params['reasoning'] = resolve_reasoning_choice(params.get('model', DEFAULT_MODEL), params.get('reasoning'))
    codex_args = build_codex_args(params)
    timeout_sec = resolve_timeout()

    thread_id: Optional[str] = None
    last_agent_message: Optional[str] = None

    try:
        # 启动 codex 子进程
        process = subprocess.Popen(
            codex_args,
            stdout=subprocess.PIPE,
            stderr=sys.stderr,  # 错误直接透传到 stderr
            text=True,
            bufsize=1  # 行缓冲
        )

        # 逐行解析 JSON 输出
        for line in process.stdout:
            line = line.strip()
            if not line:
                continue

            try:
                event = json.loads(line)

                # 捕获 thread_id
                if event.get('type') == 'thread.started':
                    thread_id = event.get('thread_id')

                # 捕获 agent_message
                if (event.get('type') == 'item.completed' and
                    event.get('item', {}).get('type') == 'agent_message'):
                    text = normalize_text(event['item'].get('text'))
                    if text:
                        last_agent_message = text

            except json.JSONDecodeError:
                log_warn(f"Failed to parse line: {line}")

        # 等待进程结束
        returncode = process.wait(timeout=timeout_sec)

        # 优先检查是否有有效输出，而非退出码
        if last_agent_message:
            # 输出 agent_message
            sys.stdout.write(f"{last_agent_message}\n")

            # 输出 session_id（如果存在）
            if thread_id:
                sys.stdout.write(f"\n---\nSESSION_ID: {thread_id}\n")

            # 有输出但退出码非零，输出警告而非失败
            if returncode != 0:
                log_warn(f'Codex completed with non-zero status {returncode} but produced valid output')

            sys.exit(0)
        else:
            # 没有输出才算真正失败
            log_error(f'Codex exited with status {returncode} without agent_message output')
            sys.exit(returncode if returncode != 0 else 1)

    except subprocess.TimeoutExpired:
        log_error('Codex execution timeout')
        process.kill()
        try:
            process.wait(timeout=FORCE_KILL_DELAY)
        except subprocess.TimeoutExpired:
            pass
        sys.exit(124)

    except FileNotFoundError:
        log_error("codex command not found in PATH")
        sys.exit(127)

    except KeyboardInterrupt:
        process.terminate()
        try:
            process.wait(timeout=FORCE_KILL_DELAY)
        except subprocess.TimeoutExpired:
            process.kill()
        sys.exit(130)


if __name__ == '__main__':
    main()
