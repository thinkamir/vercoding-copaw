---
name: vibe-systematic-debugging
description: 系统化排障能力。适用于故障、bug、测试失败、集成异常和一切非预期行为分析。
---

# Vibe Core: Systematic Debugging

来源：Vibe-Skills `core/skills/systematic-debugging`

## 触发场景
- 运行报错、接口异常、测试失败
- 构建通过但行为不对
- 多组件联动下出现不稳定问题
- 用户要求定位根因，而不是直接猜修复

## 推荐工作流
1. 复现问题，记录命令、输入、环境、错误输出
2. 划分边界：前端 / 后端 / DB / 第三方 / 配置
3. 收集证据，缩小问题面
4. 形成 root cause 假设并验证
5. 再提出最小修复，并重跑验证

## 协同建议
- 构建命令失败：配合 `Vibe Theme - Build Error Resolver`
- 需要先摸仓库模式：配合 `Vibe Theme - Context Hunter`
- 修复后补验证：配合 `Vibe Core - TDD Guide`

## 不适合
- 用户只想直接要一个理论解释，不做排障
- 问题完全无法复现且也拿不到任何证据
