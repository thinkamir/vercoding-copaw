# Vibe Skills 路由增强规则

## 目标
让已接入的 Vibe skills 在 CoPaw 中更容易被正确选择，减少与现有 skills 的重叠、误触发和重复调用。

---

## 1. 一级路由：先判断是否需要 Vibe 总控

优先走 `Vibe Skills` 的情况：
- 任务是**多阶段**的：澄清需求 -> 方案 -> 实施 -> 验证 -> 清理
- 用户表达的是“帮我把这件事完整做完”而不是单点动作
- 任务需要较强治理，不能边做边漂移范围
- 任务涉及多技能串联、跨文件/跨模块/跨子任务推进

不要优先走 `Vibe Skills` 的情况：
- 单文件小修
- 单次查询
- 只要一个命令/一段说明
- 当前已有更明确、更专用的 CoPaw 原生 skill 足够解决

---

## 2. 二级路由：命令包装层触发词

### `Vibe Command - vibe`
触发词：
- /vibe
- vibe
- 用 vibe 跑一下
- 进入受治理执行

### `Vibe Command - vibe-do-it`
触发词：
- 直接做
- 开始执行
- 按方案推进
- 不用再讲，直接干

### `Vibe Command - vibe-how-do-we-do`
触发词：
- 先出方案
- 先看怎么做
- 给我实施路径
- 先规划一下

### `Vibe Command - vibe-implement`
触发词：
- 开始实现
- 进入开发
- 按这个计划写

### `Vibe Command - vibe-review`
触发词：
- 先 review
- 帮我审一下
- 看看有没有问题
- 做风险排查

### `Vibe Command - vibe-what-do-i-want`
触发词：
- 先帮我理清需求
- 我还没想清楚
- 帮我冻结范围
- 先做需求澄清

---

## 3. 三级路由：核心方法层选型

### `Vibe Core - Brainstorming`
优先于实现类 skill 的条件：
- 用户目标还模糊
- 存在多个方向或 trade-off
- 需要先讨论设计，而不是直接落代码

### `Vibe Core - Writing Plans`
优先条件：
- 需求已明确
- 需要工程化计划
- 需要 handoff-safe 的行动清单

### `Vibe Core - Systematic Debugging`
优先条件：
- 有报错 / bug / 测试失败 / 集成异常
- 用户要的是**根因定位**，不是拍脑袋修复

### `Vibe Core - Code Reviewer`
优先条件：
- 已有 diff / 改动 / 分支
- 任务重点是找问题、找风险、做评审

### `Vibe Core - TDD Guide`
优先条件：
- 功能开发 / bug 修复 / 重构
- 需要严格质量闭环
- 要求先测试再改实现

### `Vibe Core - Subagent Development`
优先条件：
- 已有批准计划
- 子任务相对独立
- 适合拆开推进

---

## 4. 四级路由：主题能力层选型

### `Vibe Theme - AIOS Architect`
适合：
- 架构设计
- 技术选型
- API / 安全 / 性能方案

### `Vibe Theme - Create Plan`
适合：
- 用户明确说“先给计划”
- 先只读，不急着改代码

### `Vibe Theme - Context Hunter`
适合：
- 开发/修复/重构前先摸清仓库模式
- 找类似实现、命名、测试、schema 约定

### `Vibe Theme - Build Error Resolver`
适合：
- 构建失败
- 编译 / lint / 类型 / 环境 / 测试命令异常

### `Vibe Theme - Comprehensive Research`
适合：
- 多来源调研
- 需要交叉验证
- 要明确局限和来源可靠性

### `Vibe Theme - Autonomous Builder`
适合：
- 长链路开发
- 需求到实现持续推进
- 小步迭代、多轮验证

---

## 5. 与现有 CoPaw skills 的协同/去重规则

### 优先保留 CoPaw 原生 skill 的场景
- 浏览器操作：优先 `browser_use` / Browser 类 skills
- GitHub 操作：优先 `Github` skill
- 网页搜索：优先 `web-search` / `duckduckgo-search` / `tavily`
- 编码执行：优先 `Code` / `Agentic Coding`
- cron / heartbeat：优先 `cron`、工作区规则和现有自动化体系

### 优先启用 Vibe skills 的场景
- 任务需要**治理式流程**而不是单点工具调用
- 任务需要“先澄清/先计划/先评审/先排障”的方法论约束
- 任务需要把多个 CoPaw 原生能力串成完整交付流程

### 去重原则
- 不要同时把 `Create Plan` 和 `Writing Plans` 当成同一层用途重复调用
  - 快速只读计划：`Create Plan`
  - 工程化实施计划：`Writing Plans`
- 不要同时把 `Systematic Debugging` 和 `Build Error Resolver` 当成同一个东西
  - 根因定位：`Systematic Debugging`
  - 构建类命令失败：`Build Error Resolver`
- 不要在需求还不清时直接走 `Autonomous Builder`
  - 先 `Brainstorming` / `vibe-what-do-i-want`

---

## 6. 推荐简化决策树

1. **任务复杂且多阶段？**
   - 是：先考虑 `Vibe Skills`
   - 否：继续看具体场景

2. **需求清楚吗？**
   - 不清楚：`Vibe Core - Brainstorming` / `Vibe Command - vibe-what-do-i-want`
   - 清楚：继续

3. **是计划问题还是执行问题？**
   - 计划：`Vibe Theme - Create Plan` 或 `Vibe Core - Writing Plans`
   - 执行：继续

4. **是 bug/报错/失败？**
   - 是：`Vibe Core - Systematic Debugging` 或 `Vibe Theme - Build Error Resolver`
   - 否：继续

5. **是评审/找风险？**
   - 是：`Vibe Core - Code Reviewer`
   - 否：继续

6. **是长链路开发推进？**
   - 是：`Vibe Theme - Autonomous Builder`

---

## 7. 实施建议
- 后续如果要进一步自动化路由，可把这里的触发词和规则沉淀到单独 JSON/YAML 索引中
- 如果未来要与 CoPaw 的自动发现机制结合，可优先把“触发词 + 优先级 + 冲突规则”结构化
