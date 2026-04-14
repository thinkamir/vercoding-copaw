# Vibe Runtime Host

## Purpose
Phase 21 introduces a local runtime host that sits behind `execute_routed_task.py`.

This upgrades execution from:
- route -> dispatch payload -> stub

to:
- route -> dispatch payload -> runtime host -> normalized host dispatch result

## New files
- `config/runtime-host.json`
- `scripts/runtime_host.py`

## Runtime host role
The runtime host is the first unified execution host inside this repository.

It is responsible for:
- validating whether a dispatch payload is truly auto-dispatchable
- mapping `adapter_type` to a configured host handler
- normalizing invocation payloads
- optionally running a shell command template when explicitly allowed
- returning a single structured host result contract

## Flow
```text
raw task text
  -> route_task.py
  -> execute_routed_task.py
  -> dispatch payload
  -> runtime_host.py
  -> host handler
  -> structured host result
```

## Handler types
Current handler types:
- `command_alias_host`
- `skill_name_host`
- `native_family_host`

Mapped from adapter types:
- `vibe_wrapper`
- `vibe_skill`
- `native_copaw`

## Host result fields
Typical host result fields include:
- `accepted`
- `host_status`
- `handler`
- `invocation_payload`
- `execution`

## Host status values
Examples:
- `rejected_by_policy`
- `rejected_missing_adapter`
- `rejected_missing_handler`
- `host_dispatched_command_alias`
- `host_dispatched_skill_name`
- `host_dispatched_native_family`

## Why this matters
Before Phase 21, `execute_routed_task.py --execute` only returned a local stub marker.

Now it actually sends the route into a dedicated runtime host layer that:
- re-validates policy gates
- applies handler mapping
- returns a host-level execution contract

This is a real integration step because upper layers can now depend on a distinct runtime host boundary instead of direct script-local branching.

## Usage
### Route and execute through runtime host
```bash
python3 scripts/execute_routed_task.py --execute --format text "按方案推进，直接干"
```

### Feed a saved execution payload directly into the host
```bash
python3 scripts/execute_routed_task.py --format json --output reports/exec.json --output-format json "打开网页并截图"
python3 scripts/runtime_host.py --input reports/exec.json --format text
```

### Pipe JSON directly into the host
```bash
python3 scripts/execute_routed_task.py --format json "帮我搜索最新资料" | python3 scripts/runtime_host.py --format text
```

### Allow host shell execution when configured
```bash
python3 scripts/runtime_host.py --input reports/exec.json --allow-shell-execute
```

## Safety behavior
- Non auto-dispatchable payloads are rejected by the host.
- Missing adapters or missing handlers are rejected by the host.
- Shell execution is opt-in and still requires handler support plus a configured command template.

## Intended next step
The next step after this is to connect host handlers to real CoPaw runtime backends so command alias / skill family dispatch can call actual toolchains rather than local host normalization only.
