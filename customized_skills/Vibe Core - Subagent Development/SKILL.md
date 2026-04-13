---
name: vibe-subagent-development
description: 子代理驱动开发。适用于已经有明确实施计划且任务间大多独立、可在会话内分治执行的场景。
---

# Vibe Core: Subagent Development

来源：Vibe-Skills `core/skills/subagent-driven-development`

## 适用场景
- 已有批准方案
- 多个子任务相对独立
- 需要分工并行/隔离上下文执行

## 核心规则
- 每个任务使用**新鲜子上下文**
- 先做**规范符合性审查**，再做质量审查
- 只要 review 问题还没关完，就**不能标记完成**
