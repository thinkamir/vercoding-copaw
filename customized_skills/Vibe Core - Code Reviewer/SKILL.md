---
name: vibe-code-reviewer
description: 以问题优先、证据驱动的方式执行代码评审。适用于 review、风险排查、回归检查等任务。
---

# Vibe Core: Code Reviewer

来源：Vibe-Skills `core/skills/code-reviewer`

## 触发场景
- 用户要求 review 某段改动/某个分支
- 需要先找风险点，再决定是否合并/继续开发
- 需要回归风险、正确性、可维护性审查

## 推荐工作流
1. 看 diff / 相关文件 / 测试变化
2. 先列 findings，再写总结
3. 对每个 finding 给出证据与影响面
4. 标注严重度和修复建议
5. 总结 residual risk 与是否建议继续

## 协同建议
- 遇到异常行为：配合 `Vibe Core - Systematic Debugging`
- 构建或测试挂了：配合 `Vibe Theme - Build Error Resolver`
- 要把 review 反馈转成开发闭环：配合 `Vibe Core - TDD Guide`

## 不适合
- 用户只想要高层概述，不关心具体问题
- 当前没有实际代码/差异可评审
