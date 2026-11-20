# WFS iOS Virtual Lab v3 — Windows + Docker Desktop + WSL2

This is a **functional local firmware inspection service** and illustrative phone UI, **not** an iOS emulator. It deliberately does not claim native SpringBoard/IPA functionality. Firmware is NOT bundled.

## Quick start (PowerShell on Windows 10/11)
1. Install/update WSL2: `wsl --install` and `wsl --update`, reboot if requested.
2. Install Docker Desktop; enable Linux containers and WSL2 engine.
3. Extract ZIP to a project directory (prefer a local SSD, sufficient free disk space).
4. Run `powershell -ExecutionPolicy Bypass -File .\scripts\check-env.ps1`.
5. Run `powershell -ExecutionPolicy Bypass -File .\scripts\start.ps1`.
6. Browse to `http://localhost:6080`. Upload a legally obtained `.ipsw` file and inspect the manifest.
7. Stop: `powershell -ExecutionPolicy Bypass -File .\scripts\stop.ps1`.

## Ubuntu WSL2
`bash scripts/start.sh`; open `http://localhost:6080`.

## Files
- `compose.yaml`: single isolated non-root Python service, localhost-only port binding, persistent Docker named volume.
- `Dockerfile`, `requirements.txt`: runtime.
- `app/server.py`: Flask API with safe ZIP/plist metadata inspection and SHA256.
- `app/static/index.html`: responsive dashboard and a clearly labeled UI mockup.
- `scripts/start.ps1`, `stop.ps1`, `check-env.ps1`, `start.sh`: launch/diagnose.
- `scripts/prepare-darwin-source.sh`: optional upstream source checkout, not firmware preparation.
- `firmware_data` Docker named volume: persists uploaded IPSW across container recreation. `data/firmware/` is a placeholder directory and is not mounted. Do not commit/share Apple firmware.

## API
- `GET /api/health` — liveness.
- `GET /api/status` — runtime, uploaded firmware list, iOS boot unavailable.
- `POST /api/inspect` — multipart `firmware` `.ipsw`, returns plist metadata and SHA256.

## Important limitations
- `jprx/darwin-vm` currently documents Mac-only `get_files.sh` and `fix_perms.sh`. Its tested iPhone 17 is `iPhone18,3`; do not assume `iPhone18,2` works.
- The optional source checkout does not compile/boot iOS. The project intentionally does not attempt to bypass firmware protections.
- Only access the dashboard from the local machine. Port 6080 binds to `127.0.0.1`.
- File uploads are stored in the Docker named volume and limited to 12,000 MiB by default; adjust in Compose if necessary. Docker/Windows disk space and proxies may impose other limits.
- For performance, if working primarily in WSL2, keep source files in the Linux filesystem rather than `/mnt/c`.

## References
- https://docs.docker.com/desktop/features/wsl/
- https://github.com/jprx/darwin-vm

## Pengujian offline

```bash
python -m unittest discover -s tests -v
python -m compileall -q app
```

Paket v3.1 memperbaiki masalah sebelumnya: upload IPSW besar tidak lagi memakai `/tmp` tmpfs 128 MB, melainkan Docker named volume `upload_temp`. Selama upload, kapasitas disk dapat terpakai sekitar dua kali ukuran IPSW (temporary + final), jadi pastikan storage Docker cukup. `scripts/start.ps1` kini memeriksa respons HTTP API sebelum membuka browser.

**Validasi:** offline unit test inspector, sintaks Python/JavaScript berhasil pada lingkungan pembuat. Docker build/runtime **belum bisa diuji** di lingkungan tersebut karena Docker Engine tidak tersedia dan paket pip tidak dapat diambil. Uji akhir pada Docker Desktop lokal tetap diperlukan. Tidak ada emulator iOS native, QEMU runner, atau boot iOS nyata dalam rilis ini.
