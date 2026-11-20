$ErrorActionPreference = 'Stop'
Set-Location (Resolve-Path (Join-Path $PSScriptRoot '..'))
Write-Host 'WFS iOS Virtual Lab v3 - Docker launcher' -ForegroundColor Cyan
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { throw 'Docker tidak tersedia. Instal Docker Desktop dan aktifkan WSL2.' }
docker info *> $null
if ($LASTEXITCODE -ne 0) { throw 'Docker Engine belum berjalan. Jalankan Docker Desktop.' }
docker compose up -d --build
if ($LASTEXITCODE -ne 0) { throw 'Docker Compose gagal.' }
Write-Host 'Menunggu API health check...' -ForegroundColor Cyan
$healthy = $false
for ($i=0; $i -lt 30; $i++) {
  try {
    $response = Invoke-RestMethod -Uri 'http://127.0.0.1:6080/api/health' -TimeoutSec 2
    if ($response.status -eq 'ok') { $healthy = $true; break }
  } catch { }
  Start-Sleep -Seconds 2
}
if (-not $healthy) {
  docker compose ps
  docker compose logs --tail 80
  throw 'API belum siap. Lihat log di atas.'
}
Write-Host 'API berhasil merespons. Dashboard: http://localhost:6080' -ForegroundColor Green
Start-Process 'http://localhost:6080'
