#!/usr/bin/env python3
"""Download the 76 sticker files listed in sticker_manifest.csv into ./emoji/."""
import csv
import pathlib
import time
import urllib.request
import urllib.error

ROOT = pathlib.Path(__file__).resolve().parent
MANIFEST = ROOT / "sticker_manifest.csv"
OUT = ROOT / "emoji"
REPORT = ROOT / "download-report.csv"
USER_AGENT = "Mozilla/5.0 (compatible; StickerAssetImporter/1.0)"

def looks_like_image(data: bytes, filename: str) -> bool:
    ext = pathlib.Path(filename).suffix.lower()
    if ext in (".jpg", ".jpeg"):
        return data.startswith(b"\xff\xd8\xff")
    if ext == ".png":
        return data.startswith(b"\x89PNG\r\n\x1a\n")
    if ext == ".gif":
        return data.startswith((b"GIF87a", b"GIF89a"))
    if ext == ".webp":
        return len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP"
    return False

def get_image(url: str, filename: str):
    last_error = "unknown error"
    for attempt in range(1, 4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "image/avif,image/webp,image/apng,image/*,*/*;q=0.8"})
            with urllib.request.urlopen(req, timeout=35) as response:
                data = response.read(20 * 1024 * 1024 + 1)
                if len(data) > 20 * 1024 * 1024:
                    raise ValueError("file exceeds 20 MB safety limit")
                if not looks_like_image(data, filename):
                    ctype = response.headers.get("Content-Type", "unknown")
                    raise ValueError(f"response is not a valid {pathlib.Path(filename).suffix} image (Content-Type: {ctype})")
                return data
        except Exception as exc:
            last_error = str(exc)
            if attempt < 3:
                time.sleep(attempt * 2)
    raise RuntimeError(last_error)

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with MANIFEST.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    report=[]
    success=0
    for row in rows:
        filename = row["filename"]
        dest = OUT / filename
        try:
            data = get_image(row["source_url"], filename)
            dest.write_bytes(data)
            success += 1
            status, detail = "OK", f"{len(data)} bytes"
            print(f"OK {row['number']:02d}/76 {filename} ({len(data)} bytes)")
        except Exception as exc:
            status, detail = "FAILED", str(exc)
            print(f"FAILED {row['number']:02d}/76 {filename}: {detail}")
        report.append({"number": row["number"], "category": row["category"], "name": row["name"], "filename": filename, "source_url": row["source_url"], "status": status, "detail": detail})
    with REPORT.open("w", newline="", encoding="utf-8-sig") as f:
        w=csv.DictWriter(f, fieldnames=list(report[0].keys()))
        w.writeheader(); w.writerows(report)
    # Generate an index with CDN links, while clearly marking failed downloads.
    with (OUT/"index.csv").open("w", newline="", encoding="utf-8-sig") as f:
        fields=["number","category","name","filename","cdn_url","download_status"]
        w=csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for item,row in zip(rows, report):
            w.writerow({"number":item["number"],"category":item["category"],"name":item["name"],"filename":item["filename"],"cdn_url":item["cdn_url"],"download_status":row["status"]})
    print(f"\nResult: {success}/{len(rows)} images downloaded. See download-report.csv for failures.")
    if success == 0:
        raise SystemExit("No images were downloaded. The source host may be unavailable or blocking requests.")

if __name__ == "__main__":
    main()
