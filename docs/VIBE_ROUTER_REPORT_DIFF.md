# Vibe Router Report Diff

## Purpose
Phase 19 adds report-to-report comparison so router changes are not only validated as pass/fail, but also inspected for drift.

This is useful when:
- a routing rule changes but the suite still passes
- confidence shifts need review
- risk-gating behavior changes
- primary recommendation changes across versions

## File
- `scripts/diff_router_reports.py`

## Input
This script compares two JSON reports produced by:
- `scripts/eval_router.py --output ... --output-format json`

## What gets compared
For each shared case id, the diff checks:
- `passed`
- `actual.route_mode`
- `actual.primary.name`
- `actual.primary.type`
- `actual.confidence`
- `actual.requires_human_confirmation`
- `actual.can_auto_execute`
- `actual.human_confirmation_reasons`

It also reports:
- added case ids
- removed case ids
- old/new summary totals

## Usage
### Compare two reports in text format
```bash
python3 scripts/diff_router_reports.py reports/baseline.json reports/current.json
```

### Compare two reports in JSON format
```bash
python3 scripts/diff_router_reports.py reports/baseline.json reports/current.json --format json
```

### Write diff report to file
```bash
python3 scripts/diff_router_reports.py \
  reports/baseline.json \
  reports/current.json \
  --output reports/router-diff.json \
  --output-format json
```

### Ignore tiny confidence drift
```bash
python3 scripts/diff_router_reports.py \
  reports/baseline.json \
  reports/current.json \
  --confidence-threshold 0.01
```

### Fail CI or local scripts when drift exists
```bash
python3 scripts/diff_router_reports.py \
  reports/baseline.json \
  reports/current.json \
  --fail-on-change
```

## Typical workflow
1. generate a baseline report
2. adjust routing rules or router logic
3. generate a new report
4. diff the two reports
5. review changed primary picks, confidence drift, and risk-gate changes

## Output summary
Text output includes:
- old summary
- new summary
- counts for added / removed / changed / unchanged
- field-level changes per changed case

JSON output includes structured arrays for:
- `added_case_ids`
- `removed_case_ids`
- `changed_cases`
- `unchanged_case_ids`

## Suggested next use
This can later feed:
- CI drift artifacts
- PR comments
- route drift dashboards
- regression baselines checked into the repository
