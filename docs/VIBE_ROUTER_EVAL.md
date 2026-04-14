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
Supports grouped execution through:
- `tags` in each case
- `--tag` filter in `eval_router.py`
- `--case-id` filter in `eval_router.py`

## Phase 17 additions
Supports named preset suites through `--preset`:
- `full`
- `smoke`
- `native`
- `vibe`
- `risky`
- `edge`

Rules:
- `full` means full suite
- `--preset` can be combined with `--case-id`
- `--preset` cannot be combined with `--tag`

## Phase 18 additions
Supports report file output through:
- `--output <path>`
- `--output-format json|text|match-console`

Typical use cases:
- persist local reports under `reports/`
- upload CI artifacts
- compare outputs across runs

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

### Run a preset suite
```bash
python3 scripts/eval_router.py --preset smoke
python3 scripts/eval_router.py --preset risky
python3 scripts/eval_router.py --preset full
```

### Write JSON report file
```bash
python3 scripts/eval_router.py --preset full --output reports/router-eval.json --output-format json
```

### Write text report file matching console format
```bash
python3 scripts/eval_router.py --preset smoke --format text --output reports/router-eval.txt --output-format match-console
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

Current CI behavior:
- runs regression eval
- writes `reports/router-eval.json`
- uploads the report as an artifact

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

## Phase 19 additions
Historical report diffing is now supported through:
- `scripts/diff_router_reports.py`
- `docs/VIBE_ROUTER_REPORT_DIFF.md`

This adds report-to-report drift inspection for:
- primary recommendation changes
- confidence drift
- risk gate changes
- added / removed cases

## Next step
A later phase can add fixed baselines, CI diff artifacts, snapshots, or PR annotations.
