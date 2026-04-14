# Vibe Router Evaluation

## Purpose
This evaluation layer turns the router from a manually inspected helper into something regression-testable.

## Files
- `tests/route_cases.json`: expected routing cases
- `scripts/eval_router.py`: evaluator for `route_task.py`
- `.github/workflows/router-eval.yml`: GitHub Actions workflow for regression checks

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
A later phase can expand this into matrix testing, richer fixtures, snapshots, or PR annotations.
