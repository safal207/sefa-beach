"""Verify deployed bytes against the exact staged manifest, with a bounded deadline."""
import argparse
import hashlib
import json
import pathlib
import re
import sys
import time
import urllib.parse
import urllib.request

FILES = {"index.html", "revenue-dashboard-local.html", "menu-baseline.json",
         "sales-lines-template.csv", "sales-context-template.csv"}

def digest(data):
    return hashlib.sha256(data).hexdigest()

def validate(manifest):
    if manifest.get("schema") != "sefa-release-v1" or not re.fullmatch(r"[0-9a-f]{40}", manifest.get("commit", "")):
        raise ValueError("Invalid manifest schema or commit")
    files = manifest.get("files")
    if not isinstance(files, dict) or set(files) != FILES or not all(isinstance(v,str) and re.fullmatch(r"[0-9a-f]{64}", v) for v in files.values()):
        raise ValueError("Manifest file allowlist or hashes invalid")

def verify_once(site, expected, fetch):
    validate(expected)
    live = json.loads(fetch(site + "release-manifest.json"))
    if live != expected:
        raise ValueError("Published manifest does not match staged release")
    results = {}
    for name, wanted in expected["files"].items():
        url = site if name == "index.html" else site + name
        actual = digest(fetch(url))
        results[name] = {"expected": wanted, "actual": actual, "match": actual == wanted}
    return results

def verify(site, expected, report, max_seconds=180):
    validate(expected)
    parsed = urllib.parse.urlsplit(site)
    if parsed.scheme != "https" or not parsed.hostname or parsed.query or parsed.fragment:
        raise ValueError("A plain HTTPS Pages URL is required")
    site = site.rstrip("/") + "/"
    deadline = time.monotonic() + max_seconds
    last = {"status":"FAIL", "commit":expected["commit"], "files":{}}
    attempt = 0
    def fetch(url):
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("Publication verification exceeded deadline")
        request = urllib.request.Request(url + "?release=" + expected["commit"], headers={"Cache-Control":"no-cache", "Accept-Encoding":"identity"})
        with urllib.request.urlopen(request, timeout=min(10, remaining)) as response:
            if urllib.parse.urlsplit(response.geturl()).hostname != parsed.hostname:
                raise ValueError("Unexpected redirect host")
            return response.read(2_000_000)
    while time.monotonic() < deadline:
        attempt += 1
        try:
            results = verify_once(site, expected, fetch)
            last = {"status":"PASS" if all(x["match"] for x in results.values()) else "FAIL",
                    "commit":expected["commit"], "files":results, "attempt":attempt}
            if last["status"] == "PASS":
                break
        except Exception as exc:
            last = {"status":"FAIL", "commit":expected["commit"], "files":{}, "attempt":attempt, "error":str(exc)}
        time.sleep(max(0, min(5, deadline-time.monotonic())))
    pathlib.Path(report).write_text(json.dumps(last, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(last, indent=2))
    return last["status"] == "PASS"

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--site",required=True)
    p.add_argument("--manifest",required=True)
    p.add_argument("--report",required=True)
    args=p.parse_args()
    expected=json.loads(pathlib.Path(args.manifest).read_text(encoding="utf-8"))
    sys.exit(0 if verify(args.site,expected,args.report) else 1)
