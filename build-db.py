#!/usr/bin/env python3
"""Build the cc-mods CrossCode mod database (npDatabase) that CCModManager reads.

Reads `input-locations.json` (a list of mod sources) and emits `npDatabase.json` (pretty) and
`npDatabase.min.json` (compact) on this branch. CCModManager fetches
`https://raw.githubusercontent.com/cc-mods/CCModDB/stable/npDatabase.min.json` when the repo
`@cc-mods/CCModDB/stable` is configured (it is pre-registered in cc-ios).

Each input entry is one of:
    { "repo": "cc-mods/cc-ultrawide" }    # resolve the repo's LATEST release .ccmod (recommended)
    { "url":  "https://.../foo-1.0.0.ccmod" }   # a direct .ccmod URL (version-pinned)

For each entry the script downloads the .ccmod, computes its SHA-256, reads the `ccmod.json` at the
archive root, and writes a database entry keyed by the mod id:

    "<id>": {
        "metadataCCMod": { ...the ccmod.json... },
        "installation": [ { "type": "zip", "url": "...", "source": "", "hash": { "sha256": "..." } } ],
        "stars": 0,
        "lastUpdateTimestamp": <release epoch ms>
    }

Usage:
    python build-db.py                 # build from input-locations.json
    GITHUB_TOKEN=ghp_... python build-db.py   # authenticated (higher API rate limit)

Only the Python standard library is used.
"""
import hashlib
import io
import json
import os
import sys
import urllib.request
import zipfile
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
API = "https://api.github.com"


def _req(url, accept="application/vnd.github+json"):
    headers = {"User-Agent": "cc-mods-ccmoddb-build", "Accept": accept}
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return urllib.request.Request(url, headers=headers)


def _get_json(url):
    with urllib.request.urlopen(_req(url)) as r:
        return json.load(r)


def _get_bytes(url):
    with urllib.request.urlopen(_req(url, accept="application/octet-stream")) as r:
        return r.read()


def resolve_repo_latest(repo):
    """Return (ccmod_url, release_epoch_ms) for a repo's latest release .ccmod asset."""
    rel = _get_json(f"{API}/repos/{repo}/releases/latest")
    asset = next((a for a in rel.get("assets", []) if a["name"].endswith(".ccmod")), None)
    if not asset:
        raise SystemExit(f"error: {repo} latest release has no .ccmod asset")
    ts = rel.get("published_at") or rel.get("created_at")
    epoch_ms = 0
    if ts:
        epoch_ms = int(datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")
                       .replace(tzinfo=timezone.utc).timestamp() * 1000)
    return asset["browser_download_url"], epoch_ms


def entry_for(url, epoch_ms):
    data = _get_bytes(url)
    sha = hashlib.sha256(data).hexdigest()
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        names = z.namelist()
        if "ccmod.json" not in names:
            raise SystemExit(f"error: {url} has no ccmod.json at the archive root")
        meta = json.loads(z.read("ccmod.json").decode("utf-8"))
    mod_id = meta.get("id")
    if not mod_id:
        raise SystemExit(f"error: {url} ccmod.json is missing an id")
    entry = {
        "metadataCCMod": meta,
        "installation": [
            {"type": "zip", "url": url, "source": "", "hash": {"sha256": sha}}
        ],
        "stars": 0,
    }
    if epoch_ms:
        entry["lastUpdateTimestamp"] = epoch_ms
    return mod_id, entry


def main():
    inputs = json.load(open(os.path.join(HERE, "input-locations.json"), encoding="utf-8"))
    db = {}
    for item in inputs:
        if "repo" in item:
            url, epoch_ms = resolve_repo_latest(item["repo"])
        elif "url" in item:
            url, epoch_ms = item["url"], 0
        else:
            raise SystemExit(f"error: input entry needs 'repo' or 'url': {item}")
        mod_id, entry = entry_for(url, epoch_ms)
        if mod_id in db:
            raise SystemExit(f"error: duplicate mod id '{mod_id}'")
        db[mod_id] = entry
        print(f"  {mod_id}: {url}")
        print(f"    sha256 {entry['installation'][0]['hash']['sha256']}")

    pretty = os.path.join(HERE, "npDatabase.json")
    minified = os.path.join(HERE, "npDatabase.min.json")
    with open(pretty, "w", encoding="utf-8") as f:
        json.dump(db, f, indent="\t", ensure_ascii=False)
        f.write("\n")
    with open(minified, "w", encoding="utf-8") as f:
        json.dump(db, f, separators=(",", ":"), ensure_ascii=False)
        f.write("\n")
    print(f"Wrote {pretty} and {minified} ({len(db)} mods).")


if __name__ == "__main__":
    main()
