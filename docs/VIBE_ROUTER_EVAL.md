# Vibe Router Evaluation

## Purpose
This evaluation layer turns the router from a manually inspected helper into something regression-testable.

## Files
- `tests/route_cases.json`: expected routing cases
- `scripts/eval_router.py`: evaluator for `route_task.py`

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
This can later be wired into GitHub Actions or any local pre-commit/pre-push workflow.
