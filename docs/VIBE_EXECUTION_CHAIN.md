# Vibe Execution Chain

## Purpose
This file documents the first real execution bridge on top of `route_task.py`.

Before this phase, the repository could:
- recommend a route
- explain why that route was chosen
- gate risky tasks
- evaluate routing quality

Now it can also:
- convert route output into a dispatchable execution payload
- map selected routes to adapter targets
- block risky auto-dispatch
- preview or attempt execution through a single CLI entrypoint

## New files
- `config/execution-adapters.json`
- `scripts/execute_routed_task.py`

## Execution chain flow
```text
raw task text
  -> route_task.py
  -> selected primary route
  -> execution adapter lookup
  -> dispatch payload
  -> preview / stub dispatch / optional shell execution
```

## Adapter config
`config/execution-adapters.json` defines how routed outputs are bridged into execution targets.

Two adapter groups exist:

### 1. `vibe_wrappers`
Maps routed Vibe skills to:
- wrapper command aliases like `/vibe` or `vibe-do-it`
- direct skill-name dispatch targets for non-wrapper skills

### 2. `native_families`
Maps native CoPaw route families to:
- browser/browser_use
- github
- web-search/tavily/duckduckgo-search
- cron
- Code/Agentic Coding

## Dispatch status values
`execute_routed_task.py` returns a structured `dispatch` block with statuses such as:
- `manual_review_required`
- `blocked_confirmation`
- `manual_handoff`
- `adapter_missing`
- `ready_for_dispatch`
- `ready_for_auto_dispatch`

## Execution status values
The `execution` block returns statuses such as:
- `preview_only`
- `not_executed`
- `dispatched_stub`
- `shell_command_missing`
- `shell_executed`
- `shell_failed`
- `shell_timeout`

## Why stub dispatch exists
This repository still does not include the real CoPaw runtime host that can directly invoke every native skill family or wrapper command.

So Phase 20 starts by wiring the execution bridge in a safe way:
- route is resolved for real
- adapter is selected for real
- policy gates are enforced for real
- dispatch payload is emitted for real
- optional external shell execution is supported only if explicitly configured

This gives a machine-consumable bridge now, without pretending the runtime host already exists inside this repository.

## Usage
### Preview the execution chain
```bash
python3 scripts/execute_routed_task.py --format text "打开网页并截图，顺便点一下按钮"
```

### Emit JSON payload for an upper-layer runtime
```bash
python3 scripts/execute_routed_task.py --format json "按方案推进，直接干"
```

### Attempt auto-dispatch stub
```bash
python3 scripts/execute_routed_task.py --execute --format text "按方案推进，直接干"
```

### Write payload to a report file
```bash
python3 scripts/execute_routed_task.py \
  --format json \
  --output reports/execute-routed-task.json \
  --output-format json \
  "帮我搜索一下这个技术方案的最新资料"
```

### Enable actual shell execution for configured adapters only
```bash
python3 scripts/execute_routed_task.py \
  --execute \
  --shell-execute \
  --timeout 20 \
  "按方案推进，直接干"
```

## Safety behavior
- If `route_task.py` marks a task as risky, dispatch is blocked.
- If confidence/policy disallows auto execution, output becomes manual handoff.
- Shell execution only happens when:
  - `--execute` is provided
  - `--shell-execute` is provided
  - the selected adapter has a non-null `shell_command`

## Intended next step
The next integration step is to connect this dispatch payload to a real CoPaw runtime host or orchestration layer, so `ready_for_auto_dispatch` can become a true live invocation rather than a stub.
