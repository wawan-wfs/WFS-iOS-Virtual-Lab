import hashlib
import os
import platform
import plistlib
import shutil
import tempfile
import zipfile
from pathlib import Path
from flask import Flask, jsonify, request, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder="static")
FIRMWARE_DIR = Path(os.getenv("FIRMWARE_DIR", "/data/firmware"))
MAX_UPLOAD = int(os.getenv("MAX_UPLOAD_MB", "12000")) * 1024 * 1024
app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD


def inspect_ipsw(path):
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) > 100000:
            raise ValueError("Terlalu banyak entri ZIP")
        manifest_names = [n for n in names if n == "BuildManifest.plist"]
        if not manifest_names:
            return {"valid_zip": True, "manifest_found": False, "entries": len(names)}
        info = archive.getinfo(manifest_names[0])
        if info.file_size > 10 * 1024 * 1024:
            raise ValueError("BuildManifest terlalu besar")
        manifest = plistlib.loads(archive.read(info))
        identities = manifest.get("BuildIdentities", [])
        devices = sorted({str(i.get("Info", {}).get("DeviceClass")) for i in identities if i.get("Info", {}).get("DeviceClass")})
        return {
            "valid_zip": True, "manifest_found": True, "entries": len(names),
            "product_version": str(manifest.get("ProductVersion", "unknown")),
            "product_build": str(manifest.get("ProductBuildVersion", "unknown")),
            "supported_product_types": manifest.get("SupportedProductTypes", []),
            "device_classes": devices,
            "identity_count": len(identities),
            "note": "Inspeksi metadata saja; tidak menyalakan iOS."
        }


@app.get("/")
def home():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/health")
def health():
    return jsonify(status="ok", service="WFS iOS Virtual Lab v3", mode="IPSW inspection / UI simulation")


@app.get("/api/status")
def status():
    return jsonify(
        mode="inspector",
        platform=platform.platform(),
        firmware_files=[{"name": p.name, "bytes": p.stat().st_size} for p in sorted(FIRMWARE_DIR.glob("*.ipsw")) if p.is_file()][:50],
        qemu_installed=bool(shutil.which("qemu-system-aarch64")),
        ios_boot_available=False,
        detail="iPhone18,2 boot requires compatible Darwin-VM firmware preparation; no-Mac boot is not provided."
    )


@app.post("/api/inspect")
def inspect():
    uploaded = request.files.get("firmware")
    if uploaded is None or not uploaded.filename or not uploaded.filename.lower().endswith(".ipsw"):
        return jsonify(error="Pilih file .ipsw"), 400
    FIRMWARE_DIR.mkdir(parents=True, exist_ok=True)
    # Avoid filename/path traversal; never overwrite previously uploaded file.
    filename = secure_filename(uploaded.filename)
    if not filename.lower().endswith(".ipsw"):
        return jsonify(error="Nama file tidak valid"), 400
    fd, temporary = tempfile.mkstemp(prefix=".upload-", dir=FIRMWARE_DIR)
    os.close(fd)
    temp_path = Path(temporary)
    try:
        length = 0
        with temp_path.open("wb") as target:
            while True:
                chunk = uploaded.stream.read(1024 * 1024)
                if not chunk:
                    break
                length += len(chunk)
                if length > MAX_UPLOAD:
                    raise ValueError("Ukuran firmware melampaui batas")
                target.write(chunk)
        if not zipfile.is_zipfile(temp_path):
            raise ValueError("File bukan arsip IPSW/ZIP yang valid")
        details = inspect_ipsw(temp_path)
        sha = hashlib.sha256()
        with temp_path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(4 * 1024 * 1024), b""):
                sha.update(chunk)
        digest = sha.hexdigest()
        target = FIRMWARE_DIR / f"{Path(filename).stem[:60]}-{digest[:12]}.ipsw"
        os.replace(temp_path, target)
        return jsonify(filename=target.name, bytes=length, sha256=digest, **details)
    except (ValueError, zipfile.BadZipFile, plistlib.InvalidFileException) as e:
        return jsonify(error=str(e)), 400
    finally:
        temp_path.unlink(missing_ok=True)


@app.errorhandler(413)
def too_large(_):
    return jsonify(error="File terlalu besar untuk batas upload saat ini"), 413
