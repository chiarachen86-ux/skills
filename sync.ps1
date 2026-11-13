$ErrorActionPreference = 'Stop'
$repo = $PSScriptRoot
& git -C $repo -c http.sslBackend=openssl pull --ff-only
if ($LASTEXITCODE -ne 0) { throw 'GitHub sync failed. Local skills were not changed.' }
$skillRoot = if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME 'skills' } else { Join-Path $env:USERPROFILE '.codex/skills' }
New-Item -ItemType Directory -Force $skillRoot | Out-Null
$source = Join-Path $repo 'skills/replace-pet-air-freshener-suite'
$target = Join-Path $skillRoot 'replace-pet-air-freshener-suite'
if (Test-Path -LiteralPath $target) {
  $backupRoot = Join-Path $repo '.local-backups'
  New-Item -ItemType Directory -Force $backupRoot | Out-Null
  Copy-Item -LiteralPath $target -Destination (Join-Path $backupRoot ('suite-' + (Get-Date -Format 'yyyyMMdd-HHmmss-fff'))) -Recurse
}
Copy-Item -LiteralPath $source -Destination $skillRoot -Recurse -Force
Write-Host '全套图已同步。请在 Codex 新聊天中使用更新后的技能。'
