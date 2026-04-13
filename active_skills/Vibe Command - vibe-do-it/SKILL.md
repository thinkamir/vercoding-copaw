---
name: vibe-do-it-command
description: 兼容包装入口。以执行优先偏置进入 canonical `vibe`，默认推进到 `phase_cleanup`。
---

# Vibe Command: vibe-do-it

这是对上游 `commands/vibe-do-it.md` 的 CoPaw 本地适配。

## 用途
适用于用户表达：
- /vibe-do-it
- 直接执行
- 按已批准方案推进

## 执行语义
- 使用 canonical `vibe` skill
- 偏向已批准方案的执行
- 不重新开启第二份 requirement/plan surface
- 默认推进到 `phase_cleanup`
