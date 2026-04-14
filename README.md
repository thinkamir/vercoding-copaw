# vercoding-copaw

CoPaw workspace integration for Vibe-Skills.

## Included
- `customized_skills/` Vibe local skills
- `active_skills/` mirrored Vibe runtime skills
- `scripts/sync_vibe_skills.sh` sync script with diff / backup / rollback support
- `scripts/rollback_vibe_skills.sh` rollback helper
- `scripts/select_vibe_skill.py` local structured skill selector
- `scripts/route_task.py` task pre-router for Vibe vs native CoPaw execution
- `scripts/eval_router.py` regression evaluator for router behavior
- `config/vibe-routing.json` structured routing rules
- `tests/route_cases.json` route regression cases
- `docs/VIBE_SKILLS_INTEGRATION.md`
- `docs/VIBE_SKILLS_INDEX.md`
- `docs/VIBE_SKILLS_ROUTING.md`
- `docs/VIBE_SKILLS_ROUTING_STRUCTURED.md`
- `docs/VIBE_ROUTING_EVAL_CASES.md`
- `docs/VIBE_TASK_ROUTER.md`
- `docs/VIBE_ROUTER_EVAL.md`

## Scope
This repository contains the curated CoPaw-side integration layer for upstream Vibe-Skills, not the full upstream repository mirror.

## Quick Start
### Structured skill selector
```bash
python3 scripts/select_vibe_skill.py --format text "先帮我理清需求，然后给一个实施方案"
```

### Task pre-router
```bash
python3 scripts/route_task.py --format text "先帮我理清需求，然后给一个实施方案"
```

### Batch routing
```bash
printf '%s\n%s\n' "先帮我理清需求，然后给一个实施方案" "打开网页并截图" | python3 scripts/route_task.py --batch --format text
```

### Router regression eval
```bash
python3 scripts/eval_router.py
python3 scripts/eval_router.py --fail-on-error
```

## Router contract highlights
`route_task.py` now returns integration-oriented fields such as:
- `schema_version`
- `confidence`
- `can_auto_execute`
- `requires_human_confirmation`
- `decision_trace`

### Sync upstream integration
```bash
bash scripts/sync_vibe_skills.sh --diff
bash scripts/sync_vibe_skills.sh
```

### Rollback
```bash
bash scripts/rollback_vibe_skills.sh <backup_timestamp>
```
