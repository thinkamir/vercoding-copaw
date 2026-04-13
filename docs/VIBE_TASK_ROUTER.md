# Vibe Task Router

## Purpose
`route_task.py` is the pre-routing layer on top of `select_vibe_skill.py`.

It is meant for upstream automation or future CoPaw integration points that need a more actionable answer than just “which Vibe skill scores highest”.

## Output
The router returns:
- `route_mode`
- `primary`
- `invocation`
- `fallbacks`
- `router_evidence`

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

## Intended next step
This file is the bridge toward plugging structured routing into a real CoPaw invocation chain.
