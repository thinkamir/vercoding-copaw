#!/usr/bin/env bash
set -euo pipefail

UPSTREAM_URL="https://github.com/foryourhealth111-pixel/Vibe-Skills"
TMP_DIR="/tmp/Vibe-Skills-sync"
WS_ROOT="/app/working/workspaces/default"
ACTIVE_ROOT="/app/working/active_skills"
CUSTOM_ROOT="$WS_ROOT/customized_skills"
BACKUP_ROOT="$WS_ROOT/backups/vibe-skills"
REPORT_DIR="$WS_ROOT/reports"
MODE="full"
DIFF_ONLY="0"
DO_BACKUP="1"
ROLLBACK_ID=""

usage() {
  cat <<EOF
Usage:
  bash scripts/sync_vibe_skills.sh [options] [upstream_url]

Options:
  --mode <full|core|commands|themes|index>   Selective sync mode (default: full)
  --diff                                     Show planned changes only, do not write
  --no-backup                                Disable backup before sync
  --rollback <timestamp>                     Roll back from backup snapshot
  --help                                     Show help

Examples:
  bash scripts/sync_vibe_skills.sh
  bash scripts/sync_vibe_skills.sh --mode commands
  bash scripts/sync_vibe_skills.sh --diff
  bash scripts/sync_vibe_skills.sh --rollback 2026-04-13T08-00-00Z
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --mode)
      MODE="$2"; shift 2 ;;
    --diff)
      DIFF_ONLY="1"; shift ;;
    --no-backup)
      DO_BACKUP="0"; shift ;;
    --rollback)
      ROLLBACK_ID="$2"; shift 2 ;;
    --help|-h)
      usage; exit 0 ;;
    http://*|https://*)
      UPSTREAM_URL="$1"; shift ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1 ;;
  esac
done

mkdir -p "$REPORT_DIR" "$BACKUP_ROOT"
TS="$(date -u '+%Y-%m-%dT%H-%M-%SZ')"
REPORT_FILE="$REPORT_DIR/vibe-sync-$TS.md"

backup_current() {
  local dst="$BACKUP_ROOT/$TS"
  mkdir -p "$dst/customized_skills" "$dst/active_skills"
  find "$CUSTOM_ROOT" -maxdepth 1 -type d -name 'Vibe*' -exec cp -r {} "$dst/customized_skills/" \; 2>/dev/null || true
  find "$ACTIVE_ROOT" -maxdepth 1 -type d -name 'Vibe*' -exec cp -r {} "$dst/active_skills/" \; 2>/dev/null || true
  for f in VIBE_SKILLS_INTEGRATION.md VIBE_SKILLS_INDEX.md; do
    [[ -f "$WS_ROOT/$f" ]] && cp "$WS_ROOT/$f" "$dst/"
  done
  echo "$dst"
}

rollback_to() {
  local src="$BACKUP_ROOT/$ROLLBACK_ID"
  [[ -d "$src" ]] || { echo "Backup not found: $src" >&2; exit 1; }
  find "$CUSTOM_ROOT" -maxdepth 1 -type d -name 'Vibe*' -exec rm -rf {} + 2>/dev/null || true
  find "$ACTIVE_ROOT" -maxdepth 1 -type d -name 'Vibe*' -exec rm -rf {} + 2>/dev/null || true
  cp -r "$src/customized_skills/." "$CUSTOM_ROOT/" 2>/dev/null || true
  cp -r "$src/active_skills/." "$ACTIVE_ROOT/" 2>/dev/null || true
  [[ -f "$src/VIBE_SKILLS_INTEGRATION.md" ]] && cp "$src/VIBE_SKILLS_INTEGRATION.md" "$WS_ROOT/"
  [[ -f "$src/VIBE_SKILLS_INDEX.md" ]] && cp "$src/VIBE_SKILLS_INDEX.md" "$WS_ROOT/"
  echo "Rollback completed from $ROLLBACK_ID"
  exit 0
}

[[ -n "$ROLLBACK_ID" ]] && rollback_to

rm -rf "$TMP_DIR"
git clone --depth=1 "$UPSTREAM_URL" "$TMP_DIR" >/dev/null 2>&1

PREVIEW_FILE="$REPORT_DIR/vibe-sync-preview-$TS.txt"
{
  echo "Mode: $MODE"
  echo "Upstream: $UPSTREAM_URL"
  echo "Root skill: $TMP_DIR/SKILL.md"
  echo "Commands:"; find "$TMP_DIR/commands" -maxdepth 1 -type f 2>/dev/null | sort
  echo "Core skills:"; find "$TMP_DIR/core/skills" -maxdepth 1 -mindepth 1 -type d 2>/dev/null | sort
  echo "Bundled skills:"; find "$TMP_DIR/bundled/skills" -maxdepth 1 -mindepth 1 -type d 2>/dev/null | sort | sed -n '1,50p'
} > "$PREVIEW_FILE"

if [[ "$DIFF_ONLY" == "1" ]]; then
  cat <<EOF > "$REPORT_FILE"
# Vibe Sync Diff Report

- Time: $TS
- Mode: $MODE
- Upstream: $UPSTREAM_URL
- Action: diff only
- Preview file: $PREVIEW_FILE

## Notes
This run did not modify local files. Review the preview file for candidate upstream content.
EOF
  echo "Diff report generated: $REPORT_FILE"
  exit 0
fi

BACKUP_PATH=""
if [[ "$DO_BACKUP" == "1" ]]; then
  BACKUP_PATH="$(backup_current)"
fi

copy_dir_if_exists() {
  local src="$1"
  local dst="$2"
  [[ -d "$src" ]] || return 0
  mkdir -p "$dst"
  cp -r "$src/." "$dst/"
}

sync_root() {
  mkdir -p "$CUSTOM_ROOT/Vibe Skills" "$ACTIVE_ROOT/Vibe Skills"
  cp "$TMP_DIR/SKILL.md" "$CUSTOM_ROOT/Vibe Skills/SKILL.md"
  cp "$TMP_DIR/SKILL.md" "$ACTIVE_ROOT/Vibe Skills/SKILL.md"
  cat > "$CUSTOM_ROOT/Vibe Skills/UPSTREAM.md" <<EOF
# Vibe Skills (Upstream Integration)

- Upstream: $UPSTREAM_URL
- Synced at: $TS
- Scope: CoPaw local integration
EOF
  cp "$CUSTOM_ROOT/Vibe Skills/UPSTREAM.md" "$ACTIVE_ROOT/Vibe Skills/UPSTREAM.md"
}

sync_commands() {
  local names=(
    "vibe"
    "vibe-do-it"
    "vibe-how-do-we-do"
    "vibe-implement"
    "vibe-review"
    "vibe-what-do-i-want"
  )
  for n in "${names[@]}"; do
    mkdir -p "$CUSTOM_ROOT/Vibe Command - $n" "$ACTIVE_ROOT/Vibe Command - $n"
    cat > "$CUSTOM_ROOT/Vibe Command - $n/SKILL.md" <<EOF
---
name: $n-command
description: Auto-generated CoPaw wrapper for upstream command: $n
---

# Vibe Command: $n

Auto-generated from Phase 6 sync script.
Use canonical \`Vibe Skills\` runtime semantics for this command wrapper.
EOF
    cp "$CUSTOM_ROOT/Vibe Command - $n/SKILL.md" "$ACTIVE_ROOT/Vibe Command - $n/SKILL.md"
  done
}

sync_index() {
  [[ -f "$WS_ROOT/VIBE_SKILLS_INDEX.md" ]] || cat > "$WS_ROOT/VIBE_SKILLS_INDEX.md" <<EOF
# Vibe Skills 本地索引

请参考 `VIBE_SKILLS_INTEGRATION.md` 查看当前集成结构。
EOF
}

case "$MODE" in
  full)
    sync_root
    sync_commands
    sync_index
    ;;
  core)
    sync_root
    ;;
  commands)
    sync_commands
    ;;
  themes)
    sync_index
    ;;
  index)
    sync_index
    ;;
  *)
    echo "Invalid mode: $MODE" >&2
    exit 1 ;;
esac

cat <<EOF > "$REPORT_FILE"
# Vibe Sync Report

- Time: $TS
- Upstream: $UPSTREAM_URL
- Mode: $MODE
- Backup: ${BACKUP_PATH:-disabled}
- Preview file: $PREVIEW_FILE

## Result
Sync completed successfully.

## Notes
Phase 6 script currently manages:
- root runtime sync
- command wrapper regeneration
- index bootstrap/check
- backup / diff / rollback support
EOF

echo "Sync completed: $REPORT_FILE"
