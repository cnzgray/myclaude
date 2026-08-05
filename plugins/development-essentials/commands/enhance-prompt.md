---
description: 重写并增强用户指令,使其更清晰、具体、无歧义,并保留代码块等特殊格式。
disable-model-invocation: true
argument-hint: "<task info>"
---

`/enhance-prompt <task info>`

Here is an instruction that I'd like to give you, but it needs to be improved. Rewrite and enhance this instruction to make it clearer, more specific, less ambiguous, and correct any mistakes. Do not use any tools: reply immediately with your answer, even if you're not sure. Consider the context of our conversation history when enhancing the prompt. If there is code in triple backticks (```) consider whether it is a code sample and should remain unchanged.Reply with the following format:

### BEGIN RESPONSE

<enhanced-prompt>enhanced prompt goes here</enhanced-prompt>

### END RESPONSE
