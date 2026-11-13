#!/bin/bash
set -euo pipefail
repo="$(cd "$(dirname "$0")" && pwd)"
git -C "$repo" pull --ff-only
skill_root="${CODEX_HOME:-$HOME/.codex}/skills"
backup_root="$repo/.local-backups/$(date +%Y%m%d-%H%M%S)-$$"
mkdir -p "$skill_root"
for name in replace-pet-air-freshener-suite batch-pet-listing-images create-pet-breed-choices; do
  source_dir="$repo/skills/$name"
  target="$skill_root/$name"
  if [ -e "$target" ]; then
    mkdir -p "$backup_root"
    cp -R "$target" "$backup_root/$name"
  fi
  mkdir -p "$target"
  cp -R "$source_dir/." "$target/"
done
printf '%s\n' '全套图已同步，请在 Codex 新聊天中使用。'