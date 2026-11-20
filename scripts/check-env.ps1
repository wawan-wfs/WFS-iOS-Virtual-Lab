Write-Host '=== WFS iOS Virtual Lab: diagnostik ==='
foreach ($cmd in @('wsl','docker')) {
  if (Get-Command $cmd -ErrorAction SilentlyContinue) { Write-Host "$cmd : tersedia" } else { Write-Warning "$cmd : tidak ditemukan" }
}
wsl --status
wsl --list --verbose
docker version
docker compose version
