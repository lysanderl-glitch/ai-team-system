[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot '..')
$ObsMemoryDir = if ($env:OBS_MEMORY_DIR) { $env:OBS_MEMORY_DIR } else { Join-Path $RepoRoot 'obs\00-system\claude-code-memory' }
$ClaudeMemoryDir = if ($env:CLAUDE_MEMORY_DIR) { $env:CLAUDE_MEMORY_DIR } else { Join-Path $RepoRoot '.claude\memory' }
$BackupDir = if ($env:BACKUP_DIR) { $env:BACKUP_DIR } else { Join-Path $RepoRoot '.claude\memory-backup' }

Write-Host '=== Claude Memory 同步 ==='
Write-Host ("来源: {0}" -f $ObsMemoryDir)
Write-Host ("目标: {0}" -f $ClaudeMemoryDir)

if (-not (Test-Path $ObsMemoryDir)) {
  Write-Host ("跳过：OBS memory 目录不存在：{0}" -f $ObsMemoryDir)
  exit 0
}

New-Item -ItemType Directory -Force -Path $ClaudeMemoryDir | Out-Null

if (Test-Path $ClaudeMemoryDir) {
  Write-Host '创建备份...'
  Remove-Item -Recurse -Force -ErrorAction SilentlyContinue $BackupDir
  Copy-Item -Recurse -Force $ClaudeMemoryDir $BackupDir
}

Write-Host '同步文件...'

$files = Get-ChildItem -Path $ObsMemoryDir -Filter '*.md' -File
foreach ($f in $files) {
  Copy-Item -Force $f.FullName (Join-Path $ClaudeMemoryDir $f.Name)
  Write-Host ("  ✓ {0}" -f $f.Name)
}

Write-Host ''
Write-Host '同步完成!'
