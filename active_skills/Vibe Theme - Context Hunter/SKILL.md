---
name: vibe-context-hunter
description: 实施前的代码库模式发现能力。适用于功能开发、修 bug、重构前的模式、约定和已有实现调查。
---

# Vibe Theme: Context Hunter

来源：Vibe-Skills `bundled/skills/context-hunter`

## 触发场景
- 准备开发新功能，但不确定仓库既有模式
- 准备修 bug / 重构，希望先看类似实现
- 需要找现有工具函数、命名规范、测试风格、schema 习惯

## 推荐工作流
1. 找类似功能和相关模块
2. 追踪数据流、验证、缓存、错误处理模式
3. 检查命名风格、测试风格、schema 约定
4. 搜索现有工具函数与公共组件
5. 基于已有模式再决定实现方案

## 协同建议
- 出只读计划前：配合 `Vibe Theme - Create Plan`
- 排障时：配合 `Vibe Core - Systematic Debugging`
- 改完后审查：配合 `Vibe Core - Code Reviewer`

## 不适合
- 用户只需要一个很小、很明确的单点修改
- 已经有充分上下文，无需再做仓库侦察
