# Vibe Routing Eval Cases

## Purpose
Quick sanity-check inputs for the local Vibe routing helper.

## Skill selector cases

### 1. Clarify + plan
```bash
python3 scripts/select_vibe_skill.py --format text "先帮我理清需求，然后给一个实施方案"
```
Expected:
- strong `Vibe Command - vibe-what-do-i-want`
- possibly `Vibe Command - vibe-how-do-we-do`

### 2. Debug root cause
```bash
python3 scripts/select_vibe_skill.py --format text "这个项目构建失败了，先定位根因，不要直接拍脑袋修"
```
Expected:
- `Vibe Core - Systematic Debugging`
- `Vibe Theme - Build Error Resolver` may appear but should not dominate if root-cause wording is stronger

### 3. Review first
```bash
python3 scripts/select_vibe_skill.py --format text "先别实现，先 review 一下这个 diff 的风险"
```
Expected:
- `Vibe Core - Code Reviewer`
- `Vibe Command - vibe-review`
- implementation-oriented skills should be suppressed

### 4. Native browser should win
```bash
echo "打开网页并截图，顺便点一下按钮" | python3 scripts/select_vibe_skill.py --format text
```
Expected:
- recommendation mode should lean `native_copaw_first`
- native browser hint should appear

### 5. Native GitHub should win
```bash
python3 scripts/select_vibe_skill.py --format text "帮我看一下 GitHub PR 并评论这个 issue"
```
Expected:
- recommendation mode should lean `native_copaw_first`
- native Github hint should appear

## Task router cases

### 6. Route to Vibe wrapper
```bash
python3 scripts/route_task.py --format text "先帮我理清需求，然后给一个实施方案"
```
Expected:
- `route_mode: vibe`
- primary should be a Vibe skill or wrapper
- invocation should contain wrapper suggestion when applicable

### 7. Route to native browser family
```bash
echo "打开网页并截图，顺便点一下按钮" | python3 scripts/route_task.py --format text
```
Expected:
- `route_mode: native_copaw_first`
- primary type should be `native_copaw`
- invocation should mention browser family

### 8. Route to native GitHub family
```bash
python3 scripts/route_task.py --format json "帮我看一下 GitHub PR 并评论这个 issue"
```
Expected:
- `route_mode: native_copaw_first`
- primary name should be `github`
