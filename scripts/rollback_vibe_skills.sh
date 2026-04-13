#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: bash scripts/rollback_vibe_skills.sh <backup_timestamp>" >&2
  exit 1
fi

bash scripts/sync_vibe_skills.sh --rollback "$1"
