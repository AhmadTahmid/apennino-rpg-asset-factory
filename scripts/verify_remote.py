import json
import urllib.request

manifest_url = "https://raw.githubusercontent.com/AhmadTahmid/apennino-rpg-asset-factory/main/review_manifest.json"
print(f"Checking manifest at: {manifest_url}")

req = urllib.request.Request(manifest_url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req) as resp:
    data = json.loads(resp.read().decode("utf-8"))
    print(f"Manifest loaded successfully! Found {len(data)} indexed assets.\n")

for item in data:
    url = item["raw_url"]
    asset_id = item["id"]
    try:
        r = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(r) as uresp:
            status = uresp.status
            ctype = uresp.headers.get("Content-Type", "")
            clen = uresp.headers.get("Content-Length", "")
            print(f"[OK] HTTP {status} | {ctype:<12} | {clen:>8} bytes | {asset_id}")
    except Exception as e:
        print(f"[FAIL] {asset_id}: {e}")
