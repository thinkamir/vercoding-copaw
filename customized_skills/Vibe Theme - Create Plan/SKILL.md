---
name: vibe-create-plan
description: 面向编码任务的简洁计划生成能力。适用于用户明确要求“先给计划”的场景。
---

# Vibe Theme: Create Plan

来源：Vibe-Skills `bundled/skills/create-plan`

## 触发场景
- 用户明确说：先给方案、先出计划、别急着改代码
- 任务属于编码/重构/修复，但当前更需要结构化行动清单
- 希望先明确范围、步骤、验证方式

## 推荐工作流
1. 快速只读扫描 README / docs / 关键模块
2. 如非阻塞，少问或不问，直接带合理假设继续
3. 输出简短 intent + scope + ordered checklist
4. 包含至少一个验证项与一个风险/边界项
5. 如有未知，单列 Open questions

## 协同建议
- 先摸仓库：配合 `Vibe Theme - Context Hunter`
- 计划更工程化：配合 `Vibe Core - Writing Plans`
- 涉及系统设计：配合 `Vibe Theme - AIOS Architect`

## 不适合
- 用户已经明确要求直接改代码并验证
- 需求仍然很模糊，尚未完成范围澄清
