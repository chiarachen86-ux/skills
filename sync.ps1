$ErrorActionPreference = 'Stop'
$repo = $PSScriptRoot
& git -C $repo -c http.sslBackend=openssl pull --ff-only
if ($LASTEXITCODE -ne 0) { throw 'GitHub sync failed. Local skills were not changed.' }
$skillRoot = if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME 'skills' } else { Join-Path $env:USERPROFILE '.codex/skills' }
New-Item -ItemType Directory -Force $skillRoot | Out-Null
$skillNames = @('replace-pet-air-freshener-suite', 'batch-pet-listing-images', 'create-pet-breed-choices')
$backupRoot = Join-Path $repo ('.local-backups/' + (Get-Date -Format 'yyyyMMdd-HHmmss-fff') + '-' + $PID)
foreach ($name in $skillNames) {
  $source = Join-Path $repo "skills/$name"
  $target = Join-Path $skillRoot $name
  if (Test-Path -LiteralPath $target) {
    New-Item -ItemType Directory -Force $backupRoot | Out-Null
    Copy-Item -LiteralPath $target -Destination (Join-Path $backupRoot $name) -Recurse
  }
  Copy-Item -LiteralPath $source -Destination $skillRoot -Recurse -Force
}
Write-Host '全套图已同步。请在 Codex 新聊天中使用更新后的技能。'
