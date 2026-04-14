# Vercoding-CoPaw 功能总览

## 项目定位
这是一个面向 CoPaw 的 Vibe-Skills 集成层仓库，不是上游 Vibe-Skills 全量镜像。

目标是把上游高价值能力以“可路由、可执行、可评测、可回滚、可解释”的方式接入 CoPaw。

---

## 当前已完成阶段

### Phase 1：核心 Vibe Skill 接入
已接入基础 `Vibe Skills` 能力，并建立本地定制与运行态镜像目录：
- `customized_skills/`
- `active_skills/`

### Phase 2：命令型 wrapper skills 接入
已接入：
- `Vibe Command - vibe`
- `Vibe Command - vibe-do-it`
- `Vibe Command - vibe-how-do-we-do`
- `Vibe Command - vibe-implement`
- `Vibe Command - vibe-review`
- `Vibe Command - vibe-what-do-i-want`

并新增同步脚本：
- `scripts/sync_vibe_skills.sh`

### Phase 3：高价值 core skills 接入
已接入：
- `Vibe Core - Writing Plans`
- `Vibe Core - Code Reviewer`
- `Vibe Core - Systematic Debugging`
- `Vibe Core - TDD Guide`
- `Vibe Core - Subagent Development`
- `Vibe Core - Brainstorming`

### Phase 4：主题扩展 skills 接入
已接入：
- `Vibe Theme - AIOS Architect`
- `Vibe Theme - Create Plan`
- `Vibe Theme - Context Hunter`
- `Vibe Theme - Build Error Resolver`
- `Vibe Theme - Comprehensive Research`
- `Vibe Theme - Autonomous Builder`

### Phase 5：统一索引与深层适配
新增：
- `VIBE_SKILLS_INDEX.md`

并对高频技能做深层适配，提升 CoPaw 场景可用性。

### Phase 6：同步 / 回滚 / 报告增强
脚本能力已增强为：
- 模式同步：`--mode <full|core|commands|themes|index>`
- 预览 diff：`--diff`
- 关闭备份：`--no-backup`
- 按时间戳回滚：`--rollback <timestamp>`

新增：
- `scripts/rollback_vibe_skills.sh`
- `reports/vibe-sync-*.md`
- `reports/vibe-sync-preview-*.txt`

### Phase 7：路由增强文档
新增：
- `VIBE_SKILLS_ROUTING.md`

### Phase 8：结构化路由层
新增：
- `config/vibe-routing.json`
- `scripts/select_vibe_skill.py`
- `docs/VIBE_SKILLS_ROUTING_STRUCTURED.md`

支持把 Markdown 路由规则变成可执行的本地路由选择器。

### Phase 9：可解释路由
结构化路由升级为可解释路由，支持：
- `aliases`
- `negative_keywords`
- `intent_boosts`
- 推荐理由
- 排除理由

### Phase 10：CLI 化
`select_vibe_skill.py` 已支持：
- `--format json|text`
- `--top N`
- stdin 输入
- `recommendation_mode`
- `mode_reason`
- `recommended`
- `native_hints`
- `excluded`

### Phase 11：任务前置路由层
新增：
- `scripts/route_task.py`
- `docs/VIBE_TASK_ROUTER.md`

支持输出更适合上层自动化调用的结构化结果。

### Phase 12：协议化接口层
`route_task.py` 已补齐：
- `schema_version`
- `confidence`
- `decision_trace`
- `can_auto_execute`
- `requires_human_confirmation`
- `human_confirmation_reasons`

并支持：
- `--batch`

内置风险门：
- `should_require_human_confirmation(...)`

### Phase 13：回归评测体系
新增：
- `tests/route_cases.json`
- `scripts/eval_router.py`
- `docs/VIBE_ROUTER_EVAL.md`

支持：
- expected vs actual 校验
- `--fail-on-error`
- text / JSON 输出

### Phase 14：GitHub Actions 自动评测
新增：
- `.github/workflows/router-eval.yml`

在 push / PR / 手动触发时自动执行回归。

### Phase 15：生产近似场景回归覆盖
测试用例扩展到 `24` 条，覆盖：
- 中文表达
- 中英混合表达
- build / review / debug / clarify 冲突
- native browser / github / search / cron / code
- 风险确认门
- 边界输入
- 低置信输入

### Phase 16：按标签 / 案例过滤
`eval_router.py` 支持：
- `--tag`
- `--case-id`

### Phase 17：预设测试套件
`eval_router.py` 支持：
- `--preset full|smoke|native|vibe|risky|edge`

规则：
- preset 与 `--case-id` 可组合
- preset 与 `--tag` 禁止混用

### Phase 18：评测报告输出 + CI artifact
`eval_router.py` 支持：
- `--output`
- `--output-format json|text|match-console`

CI 现在会输出：
- `reports/router-eval.json`

并上传 artifact：
- `router-eval-report`

### Phase 19：历史报告对比 / drift 检测
新增：
- `scripts/diff_router_reports.py`
- `docs/VIBE_ROUTER_REPORT_DIFF.md`

支持比较两份 `router-eval.json`，识别：
- primary 推荐变化
- route_mode 变化
- confidence 漂移
- 风险确认门变化
- case 增删

### Phase 20：接入实际调用链的执行桥接层
新增：
- `config/execution-adapters.json`
- `scripts/execute_routed_task.py`
- `docs/VIBE_EXECUTION_CHAIN.md`

支持把 `route_task.py` 的路由结果真正转成：
- dispatch payload
- adapter target
- auto-dispatch / manual-handoff / blocked-confirmation 状态
- preview / stub dispatch / 可选 shell execution

这意味着仓库已经从“路由建议层”升级到“执行桥接层”。

### Phase 21：引入 runtime host 宿主分发层
新增：
- `config/runtime-host.json`
- `scripts/runtime_host.py`
- `docs/VIBE_RUNTIME_HOST.md`

支持把执行桥接结果继续送入统一宿主层，由 host 负责：
- auto-dispatch 校验
- adapter_type -> handler 映射
- invocation payload 规范化
- host-level dispatch result 输出
- 可选 handler shell execution

这意味着仓库已进一步从“执行桥接层”升级到“runtime host 宿主层”。

### Phase 22：接入真实 backend handler 分层
新增：
- `scripts/runtime_backends.py`

支持 runtime host 按 backend family 继续分发到更具体的处理器，当前已覆盖：
- `vibe_wrapper`
- `vibe_skill`
- `native_copaw/browser`
- `native_copaw/github`
- `native_copaw/web-search`
- `native_copaw/cron`
- `native_copaw/code`

支持输出 backend-specific payload、backend status 与对应的执行准备结果。

这意味着仓库已进一步从“runtime host 宿主层”升级到“backend handler 分层执行架构”。

---

## 当前核心脚本清单

### 1. 技能同步与回滚
- `scripts/sync_vibe_skills.sh`
- `scripts/rollback_vibe_skills.sh`

### 2. 路由选择与任务前置路由
- `scripts/select_vibe_skill.py`
- `scripts/route_task.py`

### 3. 评测与报告
- `scripts/eval_router.py`
- `scripts/diff_router_reports.py`

---

## 当前文档清单
- `docs/VIBE_SKILLS_INTEGRATION.md`
- `docs/VIBE_SKILLS_INDEX.md`
- `docs/VIBE_SKILLS_ROUTING.md`
- `docs/VIBE_SKILLS_ROUTING_STRUCTURED.md`
- `docs/VIBE_TASK_ROUTER.md`
- `docs/VIBE_ROUTING_EVAL_CASES.md`
- `docs/VIBE_ROUTER_EVAL.md`
- `docs/VIBE_ROUTER_REPORT_DIFF.md`
- `docs/VIBE_FEATURES_SUMMARY.md`

---

## 当前仓库已经具备的能力

### 集成能力
- 精选接入 Vibe-Skills
- 本地定制与运行态镜像分层
- 支持同步、预览、回滚、报告

### 路由能力
- 结构化路由
- 可解释推荐
- 原生 skill 与 Vibe skill 分流
- 风险任务确认门
- 批量任务路由

### 评测能力
- 路由 expected/actual 回归
- 分类回归
- 预设套件回归
- JSON / text 输出
- 报告落盘
- CI 自动评测
- 历史报告 diff / drift 检测

### 工程能力
- README 与专项文档齐全
- GitHub Actions 已接入
- 可作为后续更深自动调用链集成基础

---

## 推荐后续方向
如果继续迭代，建议优先做：

1. **CI 中增加 diff 基线对比**
   - 自动对比上一次 artifact 或固定 baseline

2. **输出 JUnit / machine-readable artifact**
   - 更方便接 CI 平台展示

3. **PR 注释 / 注解**
   - 自动把 drift 结果贴到 PR

4. **更细粒度中文别名和负向规则治理**
   - 进一步提高中文真实场景命中率

5. **将 `route_task.py` 真正接到 CoPaw 执行链**
   - 从“建议路由”升级成“执行前决策层”
