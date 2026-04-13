# Vibe Skills 结构化路由

## 新增文件
- `config/vibe-routing.json`：结构化路由规则
- `scripts/select_vibe_skill.py`：基于任务文本推荐 Vibe skill 的本地选择器

## 作用
这一步把此前写在 Markdown 里的路由规则，沉淀成可机器读取的配置与脚本，便于未来接入自动发现、自动推荐或更智能的路由系统。

## 使用方式
### 1. 手动测试推荐
```bash
python3 scripts/select_vibe_skill.py "先帮我理清需求，然后给一个实施方案"
```

### 2. 查看 JSON 规则
```bash
cat config/vibe-routing.json
```

## 当前能力
- 分层匹配：runtime / commands / core / themes
- 关键词命中评分
- 基于去重规则过滤冲突推荐
- 输出 top-N 推荐 skill

## 后续可扩展
- 增加别名词典
- 引入负向规则
- 为不同任务类型设置权重模板
- 接入 CoPaw 的自动发现或路由机制
