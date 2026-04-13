---
name: vibe-build-error-resolver
description: 构建错误与工程失败的兼容排障入口。适用于编译、依赖、环境、测试、运行时等构建相关问题。
---

# Vibe Theme: Build Error Resolver

来源：Vibe-Skills `bundled/skills/build-error-resolver`

## 适用场景
- 构建失败
- 编译/类型/lint 错误
- 依赖或环境配置不一致
- 测试或运行时异常

## 最小工作流
1. 捕获原始失败命令与完整输出
2. 分类问题类型（依赖/编译/环境/测试运行）
3. 用最小修改修复根因
4. 重跑原始命令验证
5. 输出证据：命令、结果、最终状态
