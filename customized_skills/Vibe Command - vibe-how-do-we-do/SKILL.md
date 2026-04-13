---
name: vibe-how-command
description: 兼容包装入口。以方案设计/执行路径为主，停在 `xl_plan`。
---

# Vibe Command: vibe-how-do-we-do

这是对上游 `commands/vibe-how-do-we-do.md` 的 CoPaw 本地适配。

## 用途
适用于用户表达：
- /vibe-how-do-we-do
- 先出方案
- 先规划，不立刻执行

## 执行语义
- 使用 canonical `vibe` skill
- 目标是 approach selection / plan design / execution sequencing
- 停在 `xl_plan`
- 不继续进入 `plan_execute` 或 `phase_cleanup`，除非用户再次明确要求
