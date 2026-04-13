# Vibe Skills 结构化路由

## 新增文件
- `config/vibe-routing.json`：结构化路由规则
- `scripts/select_vibe_skill.py`：基于任务文本推荐 Vibe skill 的本地选择器
- `docs/VIBE_ROUTING_EVAL_CASES.md`：路由评测样例集

## Phase 10 增强
相比上一版，本阶段新增：
- `--format json|text`
- `--top N`
- 支持 stdin 输入
- 增加“优先 Vibe 还是优先 CoPaw 原生 skill”的建议
- 增加评测样例集

## 使用方式
### 1. JSON 输出
```bash
python3 scripts/select_vibe_skill.py --format json --top 3 "先帮我理清需求，然后给一个实施方案"
```

### 2. 文本输出
```bash
python3 scripts/select_vibe_skill.py --format text "先别实现，先 review 一下这个 diff 的风险"
```

### 3. 从 stdin 读取
```bash
echo "打开网页并截图，顺便点一下按钮" | python3 scripts/select_vibe_skill.py --format text
```

## 当前能力
- 分层匹配：runtime / commands / core / themes
- 关键词命中评分
- 别名意图映射
- 负向命中惩罚
- 基于去重规则过滤冲突推荐
- 输出 top-N 推荐 skill
- 输出“为什么推荐 / 为什么排除”
- 输出是否更适合优先使用 CoPaw 原生 skill

## 后续可扩展
- 增加更多行业/场景别名词典
- 引入正则或语义匹配
- 为不同任务类型设置权重模板
- 接入 CoPaw 的自动发现或路由机制
