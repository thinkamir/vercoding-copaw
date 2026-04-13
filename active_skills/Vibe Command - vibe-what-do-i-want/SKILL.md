---
name: vibe-want-command
description: 需求澄清型入口。使用 canonical `vibe` 做 intent clarification，并停在 requirement freeze。
---

# Vibe Command: vibe-what-do-i-want

这是对上游 `commands/vibe-what-do-i-want.md` 的 CoPaw 本地适配。

## 用途
适用于用户表达：
- /vibe-what-do-i-want
- 先澄清需求
- 先冻结范围

## 执行语义
- 使用 canonical `vibe` skill
- 做 intent clarification / scope freeze / requirement-first discovery
- 停在 `requirement_doc`
- 不继续进入 `xl_plan`、`plan_execute`、`phase_cleanup`，除非用户再次明确要求
