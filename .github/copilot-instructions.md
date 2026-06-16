# Copilot instructions — CCModDB

Part of the **[cc-mods](https://github.com/cc-mods)** CrossCode suite (the mod database CCModManager
reads for one-click installs).

📓 **Read the knowledge base first:**
**[`cc-mods/knowledge`](https://github.com/cc-mods/knowledge)** (private; org members only) is the
source of truth for hard-won findings. Most relevant here:
- [`ccmoddb-and-distribution.md`](https://github.com/cc-mods/knowledge/blob/main/ccmoddb-and-distribution.md)
  — the npDatabase format, how CCModManager fetches `stable`, custom-repo registration, the build.

**When you learn something durable, add it to `cc-mods/knowledge`** and keep this pointer intact.

## What this is

A self-hosted npDatabase (official CCModDB format). `input-locations.json` lists `{ "repo":
"cc-mods/<name>" }`; `build-db.py` resolves each repo's **latest release** `.ccmod`, computes
sha256, reads its `ccmod.json`, and writes `npDatabase.json` + `npDatabase.min.json`. CCModManager
fetches `https://raw.githubusercontent.com/cc-mods/CCModDB/stable/npDatabase.min.json`.

## How to update (after any mod releases a new version)

```powershell
$env:GH_TOKEN = (gh auth token)     # optional; raises the API rate limit
python build-db.py
git commit -am "chore: rebuild database (<mod> <ver>)"
git push origin main
git push origin main:stable         # CCModManager reads the stable branch
```

To add a mod: add a line to `input-locations.json`, then rebuild.

## Must-not-break

- **CCModManager reads the `stable` branch** — always push `main:stable` too, or installs go stale.
- Entries are keyed by **mod id**; `installation[].hash.sha256` must match the asset (build-db
  recomputes it — don't hand-edit hashes). `source: ""` for `.ccmod` (manifest at zip root).
- Every declared dependency must exist in the DB — our mods use only virtual `ccloader`/`crosscode`.
- `build-db.py` is **stdlib-only**. No secrets in commits.

## Verify

`python build-db.py` succeeds; `python -c "import json; json.load(open('npDatabase.min.json'))"`;
confirm the live raw `stable` URL returns the expected mod ids after pushing.
