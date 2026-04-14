# Vibe Router Evaluation

## Purpose
This evaluation layer turns the router from a manually inspected helper into something regression-testable.

## Files
- `tests/route_cases.json`: expected routing cases with tags
- `scripts/eval_router.py`: evaluator for `route_task.py`
- `.github/workflows/router-eval.yml`: GitHub Actions workflow for regression checks

## Coverage focus
Phase 15 expanded coverage beyond smoke tests. The suite now targets:
- 中文表达与中英混合表达
- clarify / plan / build 冲突场景
- debug / build 冲突场景
- native browser / github / search / cron / code 路由
- 高风险确认门
- 边界与低置信输入

Current suite size:
- `24` route cases

## Phase 16 additions
Now supports grouped execution through:
- `tags` in each case
- `--tag` filter in `eval_router.py`
- `--case-id` filter in `eval_router.py`

Example tag groups used now:
- `smoke`
- `vibe`
- `native`
- `risky`
- `edge`
- `conflict`

## Usage
### Text summary
```bash
python3 scripts/eval_router.py
```

### JSON output
```bash
python3 scripts/eval_router.py --format json
```

### Fail CI on regression
```bash
python3 scripts/eval_router.py --fail-on-error
```

### Run only risky cases
```bash
python3 scripts/eval_router.py --tag risky
```

### Run only native cases
```bash
python3 scripts/eval_router.py --tag native
```

### Run one specific case
```bash
python3 scripts/eval_router.py --case-id github-native
```

## GitHub Actions
This repository now runs router regression checks automatically on:
- push to `main`
- pull requests
- manual workflow dispatch

Workflow file:
```text
.github/workflows/router-eval.yml
```

## What gets checked
Each test case can assert:
- `route_mode`
- `primary_name`
- `primary_type`
- `primary_name_contains`
- `requires_human_confirmation`
- `can_auto_execute`
- `min_confidence`
- `confirmation_reason_contains`

## Next step
A later phase can add fixture grouping presets, snapshots, route drift reports, or PR annotations.
