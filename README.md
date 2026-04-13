# vercoding-copaw

CoPaw workspace integration for Vibe-Skills.

## Included
- `customized_skills/` Vibe local skills
- `active_skills/` mirrored Vibe runtime skills
- `scripts/sync_vibe_skills.sh` sync script with diff / backup / rollback support
- `scripts/rollback_vibe_skills.sh` rollback helper
- `scripts/select_vibe_skill.py` local structured skill selector
- `scripts/route_task.py` task pre-router for Vibe vs native CoPaw execution
- `config/vibe-routing.json` structured routing rules
- `docs/VIBE_SKILLS_INTEGRATION.md`
- `docs/VIBE_SKILLS_INDEX.md`
- `docs/VIBE_SKILLS_ROUTING.md`
- `docs/VIBE_SKILLS_ROUTING_STRUCTURED.md`
- `docs/VIBE_ROUTING_EVAL_CASES.md`
- `docs/VIBE_TASK_ROUTER.md`

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

### Read from stdin
```bash
echo "打开网页并截图，顺便点一下按钮" | python3 scripts/route_task.py --format text
```

### Sync upstream integration
```bash
bash scripts/sync_vibe_skills.sh --diff
bash scripts/sync_vibe_skills.sh
```

### Rollback
```bash
bash scripts/rollback_vibe_skills.sh <backup_timestamp>
```
