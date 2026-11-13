#!/bin/bash
set -euo pipefail
repo="$(cd "$(dirname "$0")" && pwd)"
git -C "$repo" pull --ff-only
skill_root="${CODEX_HOME:-$HOME/.codex}/skills"
source_dir="$repo/skills/replace-pet-air-freshener-suite"
target="$skill_root/replace-pet-air-freshener-suite"
mkdir -p "$skill_root"
if [ -e "$target" ]; then
  mkdir -p "$repo/.local-backups"
  cp -R "$target" "$repo/.local-backups/suite-$(date +%Y%m%d-%H%M%S)-$$"
fi
mkdir -p "$target"
cp -R "$source_dir/." "$target/"
printf '%s\n' '全套图已同步，请在 Codex 新聊天中使用。'