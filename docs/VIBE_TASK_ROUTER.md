# Vibe Task Router

## Purpose
`route_task.py` is the pre-routing layer on top of `select_vibe_skill.py`.

It is meant for upstream automation or future CoPaw integration points that need a more actionable answer than just “which Vibe skill scores highest”.

## Phase 12 protocol fields
The router now returns a more integration-friendly contract:
- `schema_version`
- `route_mode`
- `confidence`
- `can_auto_execute`
- `requires_human_confirmation`
- `human_confirmation_reasons`
- `primary`
- `invocation`
- `fallbacks`
- `decision_trace`
- `router_evidence`

## Batch mode
Supports batch routing from stdin:
- JSON array input
- newline-delimited input

Example:
```bash
printf '%s\n%s\n' "先帮我理清需求，然后给一个实施方案" "打开网页并截图" | python3 scripts/route_task.py --batch --format text
```

Or:
```bash
echo '["先帮我理清需求","帮我看一下 GitHub PR 并评论这个 issue"]' | python3 scripts/route_task.py --batch --format json
```

## Examples

### 1. Vibe-first task
```bash
python3 scripts/route_task.py --format text "先帮我理清需求，然后给一个实施方案"
```

### 2. Native-first task
```bash
python3 scripts/route_task.py --format text "打开网页并截图，顺便点一下按钮"
```

### 3. JSON for upper-layer scripts
```bash
python3 scripts/route_task.py --format json --top 3 "帮我看一下 GitHub PR 并评论这个 issue"
```

## Routing policy
- If the task is clearly better handled by a native CoPaw skill family, return `native_copaw_first`.
- Otherwise, return `vibe` and surface the top-ranked Vibe skill as `primary`.
- Always include fallback options so upper layers can degrade gracefully.
- If the task text indicates risky write/destructive operations, set `requires_human_confirmation=true`.

## Intended next step
This file is the bridge toward plugging structured routing into a real CoPaw invocation chain.
