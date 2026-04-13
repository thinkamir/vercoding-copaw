# Vibe Skills 本地索引

## 1. Runtime 入口
### Vibe Skills
- 作用：canonical `vibe` governed runtime 入口
- 适合：复杂任务、需要澄清需求/计划/执行/验证/清理的一体化流程
- 何时优先：任务不是小修小补，而是多阶段推进

## 2. Command Wrappers
### Vibe Command - vibe
- 作用：兼容命令式进入 `vibe`
- 适合：用户直接说 `/vibe` 或 `vibe`

### Vibe Command - vibe-do-it
- 作用：偏执行推进，默认到 `phase_cleanup`
- 适合：方案已批准，用户要直接做

### Vibe Command - vibe-how-do-we-do
- 作用：先出实施方案，停在 `xl_plan`
- 适合：用户要先看方案，不立即执行

### Vibe Command - vibe-implement
- 作用：按已批准方案进入实现
- 适合：计划已定，开始编码/实现

### Vibe Command - vibe-review
- 作用：review-first 的受治理入口
- 适合：用户要先审查问题和风险

### Vibe Command - vibe-what-do-i-want
- 作用：需求澄清与范围冻结
- 适合：需求还模糊，需要先明确边界

## 3. Core Methods
### Vibe Core - Writing Plans
- 作用：把批准需求转成实施计划
- 适合：需要明确文件路径、步骤、验证项
- 常协同：Context Hunter / Create Plan / AIOS Architect

### Vibe Core - Code Reviewer
- 作用：以 findings 为先的证据型 review
- 适合：代码审查、回归风险排查
- 常协同：Systematic Debugging / Build Error Resolver / TDD Guide

### Vibe Core - Systematic Debugging
- 作用：系统化排障
- 适合：bug、测试失败、集成问题、非预期行为
- 常协同：Build Error Resolver / Context Hunter / TDD Guide

### Vibe Core - TDD Guide
- 作用：以 RED -> GREEN -> REFACTOR 约束开发
- 适合：功能开发、行为变更、重构、修 bug
- 常协同：Writing Plans / Code Reviewer / Systematic Debugging

### Vibe Core - Subagent Development
- 作用：对子任务做分治/子代理式推进
- 适合：已有批准计划，任务彼此独立
- 常协同：Vibe Skills / Writing Plans / Autonomous Builder

### Vibe Core - Brainstorming
- 作用：实现前的创意和方案探索
- 适合：设计未定、新功能构思、trade-off 讨论
- 常协同：AIOS Architect / Create Plan / Writing Plans

## 4. Theme Packs
### Vibe Theme - AIOS Architect
- 作用：架构、选型、API、安全、性能方案
- 适合：需要从系统层面设计方案
- 常协同：Brainstorming / Writing Plans / Create Plan

### Vibe Theme - Create Plan
- 作用：只读分析后快速产出简洁计划
- 适合：用户明确要计划，不要立刻改代码
- 常协同：Context Hunter / Writing Plans / AIOS Architect

### Vibe Theme - Context Hunter
- 作用：实施前发现仓库已有模式和隐性规范
- 适合：开发、修 bug、重构前的仓库侦察
- 常协同：Create Plan / Systematic Debugging / Code Reviewer

### Vibe Theme - Build Error Resolver
- 作用：构建/编译/依赖/环境/测试错误排障
- 适合：工程命令失败、构建失败
- 常协同：Systematic Debugging / Code Reviewer / TDD Guide

### Vibe Theme - Comprehensive Research
- 作用：多来源调研与交叉验证
- 适合：需要多轮搜索、读取、验证的信息任务
- 常协同：Brainstorming / AIOS Architect / Create Plan

### Vibe Theme - Autonomous Builder
- 作用：端到端自动开发推进
- 适合：新项目、连续实现、长链路开发
- 常协同：Vibe Skills / Writing Plans / TDD Guide / Subagent Development

## 5. 推荐选型规则
- **需求不清楚**：先 `Vibe Command - vibe-what-do-i-want` 或 `Vibe Core - Brainstorming`
- **先看方案**：`Vibe Theme - Create Plan` 或 `Vibe Command - vibe-how-do-we-do`
- **要做架构设计**：`Vibe Theme - AIOS Architect`
- **要进代码前摸仓库**：`Vibe Theme - Context Hunter`
- **要系统化排 bug**：`Vibe Core - Systematic Debugging`
- **要 review**：`Vibe Core - Code Reviewer`
- **要按 TDD 推进**：`Vibe Core - TDD Guide`
- **要连续自动开发**：`Vibe Theme - Autonomous Builder`
- **任务复杂且需要总控**：`Vibe Skills`

## 6. 路由增强文档
- 更完整的中文触发词、协同/去重规则、简化决策树：见 `VIBE_SKILLS_ROUTING.md`
