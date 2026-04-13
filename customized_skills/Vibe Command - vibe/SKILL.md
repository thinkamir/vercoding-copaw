---
name: vibe-command
description: 兼容包装入口。调用 canonical `vibe` skill 进入受治理运行时；适用于希望通过命令式入口触发 Vibe-Skills 的场景。
---

# Vibe Command: vibe

这是对上游 `commands/vibe.md` 的 CoPaw 本地适配。

## 用途
当用户以命令式方式表达：
- /vibe
- vibe
- 用 vibe 进入受治理执行

则应优先转到 canonical **`Vibe Skills`** skill，并遵循其 governed runtime contract。

## 执行语义
- 这是 compatibility shim，不是第二套运行时
- 优先使用 canonical `vibe` skill
- 保持 requirements -> plan -> execute -> verify 的受治理流程

## 上游等价内容
Use the canonical `vibe` skill and follow its governed runtime contract for this request.
