#!/usr/bin/env python3
import hashlib
import json
import re
import sys
import time
from pathlib import Path


STATE_TTL_SECONDS = 12 * 60 * 60
ACTIVATE_NAMES = {"omo"}
SESSION_END_CLEANUP_REASONS = {"clear", "logout"}
ROUTING_NOTE = (
    "The user explicitly entered OmO mode for this conversation. "
    "Prioritize OmO routing in subsequent turns, use the smallest suitable agent set, "
    "delegate implementation instead of writing code directly, and keep carrying forward prior context."
)
RECOVERY_NOTE = (
    "The user previously entered OmO mode for this conversation. "
    "Keep prioritizing OmO routing after resume or compaction."
)


def load_payload() -> dict:
    raw = sys.stdin.read().strip()
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def digest_for_payload(payload: dict) -> str:
    transcript_path = payload.get("transcript_path") or ""
    session_id = str(payload.get("session_id") or "")
    cwd = payload.get("cwd") or ""
    seed = transcript_path or f"{cwd}|{session_id}"
    return hashlib.sha1(seed.encode("utf-8")).hexdigest()


def state_dir(payload: dict, create: bool = False) -> Path:
    cwd = payload.get("cwd") or "."
    path = Path(cwd) / ".claude" / "omo"
    if create:
        path.mkdir(parents=True, exist_ok=True)
    return path


def conversation_key(payload: dict) -> str:
    transcript_path = payload.get("transcript_path")
    if transcript_path:
        return digest_for_payload({"transcript_path": transcript_path})

    session_id = str(payload.get("session_id") or "").strip()
    if session_id:
        return re.sub(r"[^A-Za-z0-9._-]", "_", session_id)
    return digest_for_payload(payload)


def session_state_path(payload: dict, create_dir: bool = False) -> Path:
    return state_dir(payload, create=create_dir) / f"{conversation_key(payload)}.json"


def load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def iso_timestamp(ts: float) -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(ts))


def state_updated_at(data: dict) -> float:
    if "updated_at" in data:
        return float(data.get("updated_at") or 0)
    return float(data.get("timestamps", {}).get("updated_at") or 0)


def state_transcript_path(data: dict) -> str | None:
    if "transcript_path" in data:
        return data.get("transcript_path")
    return data.get("conversation", {}).get("transcript_path")


def is_expired(data: dict) -> bool:
    return time.time() - state_updated_at(data) > STATE_TTL_SECONDS


def build_state(payload: dict, command_name: str, prompt: str, existing: dict | None = None) -> dict:
    now = time.time()
    activation = existing.get("activation", {}) if existing else {}
    activated_at = float(activation.get("activated_at") or now)
    activated_at_iso = activation.get("activated_at_iso") or iso_timestamp(activated_at)
    lifecycle = existing.get("lifecycle", {}) if existing else {}
    return {
        "mode": "omo",
        "status": "active",
        "storage": {
            "key": conversation_key(payload),
            "strategy": "transcript_path",
        },
        "workspace": {
            "cwd": payload.get("cwd"),
        },
        "conversation": {
            "session_id": payload.get("session_id"),
            "transcript_path": payload.get("transcript_path"),
        },
        "activation": {
            "command": command_name,
            "prompt": prompt,
            "activated_at": activated_at,
            "activated_at_iso": activated_at_iso,
        },
        "lifecycle": lifecycle,
        "routing_note": ROUTING_NOTE,
        "updated_at": now,
        "updated_at_iso": iso_timestamp(now),
    }


def save_state(path: Path, payload: dict, command_name: str, prompt: str, existing: dict | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = build_state(payload, command_name, prompt, existing=existing)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def safe_unlink(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def extract_command_name(prompt: str) -> str | None:
    text = prompt.strip()
    if not text.startswith("/"):
        return None
    first = text.split(None, 1)[0][1:]
    return first or None


def command_base(name: str | None) -> str | None:
    if not name:
        return None
    return name.split(":")[-1]


def is_activation_command(name: str | None) -> bool:
    base = command_base(name)
    return base in ACTIVATE_NAMES


def load_state(payload: dict) -> tuple[Path | None, dict | None]:
    direct_path = session_state_path(payload)
    direct_data = load_json(direct_path)
    if direct_data:
        if is_expired(direct_data):
            safe_unlink(direct_path)
        else:
            return direct_path, direct_data

    transcript_path = payload.get("transcript_path")
    if not transcript_path:
        return None, None

    state_root = state_dir(payload)
    if not state_root.exists():
        return None, None

    for path in state_root.glob("*.json"):
        data = load_json(path)
        if not data:
            continue
        if is_expired(data):
            safe_unlink(path)
            continue
        if state_transcript_path(data) == transcript_path:
            return path, data

    return None, None


def touch_state(path: Path, payload: dict, state: dict) -> Path:
    target = session_state_path(payload, create_dir=True)
    command_name = state.get("activation", {}).get("command") or "omo"
    prompt = state.get("activation", {}).get("prompt") or f"/{command_name}"
    save_state(target, payload, command_name, prompt, existing=state)
    if path != target:
        safe_unlink(path)
    return target


def emit_additional_context(event_name: str, message: str) -> None:
    output = {
        "hookSpecificOutput": {
            "hookEventName": event_name,
            "additionalContext": message,
        }
    }
    sys.stdout.write(json.dumps(output, ensure_ascii=True))


def handle_user_prompt_submit(payload: dict) -> int:
    prompt = payload.get("prompt", "")
    path, state = load_state(payload)
    command_name = extract_command_name(prompt)

    if is_activation_command(command_name):
        save_state(session_state_path(payload, create_dir=True), payload, command_name or "omo", prompt)
        return 0

    if not state:
        return 0

    touch_state(path or session_state_path(payload), payload, state)

    if command_name:
        return 0

    emit_additional_context(
        "UserPromptSubmit",
        ROUTING_NOTE,
    )
    return 0


def handle_session_start(payload: dict) -> int:
    path, state = load_state(payload)
    if not state:
        return 0
    touch_state(path or session_state_path(payload), payload, state)
    emit_additional_context(
        "SessionStart",
        RECOVERY_NOTE,
    )
    return 0


def handle_session_end(payload: dict) -> int:
    reason = payload.get("reason")
    path, state = load_state(payload)

    if reason in SESSION_END_CLEANUP_REASONS:
        if path:
            safe_unlink(path)
        return 0

    if not state:
        return 0

    now = time.time()
    lifecycle = state.get("lifecycle", {})
    lifecycle["last_end_reason"] = reason or "other"
    lifecycle["last_ended_at"] = now
    lifecycle["last_ended_at_iso"] = iso_timestamp(now)
    state["lifecycle"] = lifecycle
    touch_state(path or session_state_path(payload, create_dir=True), payload, state)
    return 0


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "user-prompt-submit"
    payload = load_payload()

    if mode == "user-prompt-submit":
        return handle_user_prompt_submit(payload)
    if mode == "session-start":
        return handle_session_start(payload)
    if mode == "session-end":
        return handle_session_end(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
