# cc-mods CCModDB

The CrossCode mod **database** for the [**cc-mods**](https://github.com/cc-mods) suite — the list
[CCModManager](https://github.com/CCDirectLink/CCModManager) reads to offer **one-click installs**.

It is a tiny, self-hosted database (same format as the official
[CCDirectLink/CCModDB](https://github.com/CCDirectLink/CCModDB)). CCModManager fetches
`npDatabase.min.json` from the **`stable`** branch.

## Use it

This database is **pre-registered in [cc-ios](https://github.com/cc-mods/cc-ios)** (its
`setup-ccloader.sh` adds it to CCModManager), so the cc-mods suite shows up one-click in the in-game
**Mods** tab on the phone automatically.

On **desktop**, add it once in CCModManager → **Settings → Repositories**:

```
@cc-mods/CCModDB/stable
```

(The `@owner/repo/branch` form expands to `https://raw.githubusercontent.com/owner/repo/branch`.)
Then the cc-mods mods appear in the **Online** tab for one-click install + auto-update.

## What's in it

| Mod | What it does |
|---|---|
| [cc-ultrawide](https://github.com/cc-mods/cc-ultrawide) | Ultrawide (21:9) field of view with integer scaling |
| [cc-aimassist](https://github.com/cc-mods/cc-aimassist) | Gentle controller aim assist |
| [cc-iostitlebuttons](https://github.com/cc-mods/cc-iostitlebuttons) | Restart/Close title buttons for cc-ios |

All three are standard CCLoader mods that also run inside the cc-ios WebKit wrapper.

## Files

```
input-locations.json    source list (one entry per mod: { "repo": "cc-mods/<name>" })
build-db.py             resolves each repo's latest release .ccmod, hashes it, reads ccmod.json
npDatabase.json         generated database (pretty)
npDatabase.min.json     generated database (compact) ← what CCModManager fetches
```

## Rebuild / update

When a mod cuts a new release, regenerate the database (no manual hashes — it downloads each
release `.ccmod` and computes the SHA-256 itself):

```bash
GH_TOKEN=$(gh auth token) python build-db.py   # token optional, just raises the API rate limit
git add npDatabase.json npDatabase.min.json
git commit -m "chore: rebuild database"
git push origin main:stable   # CCModManager reads the stable branch
```

`build-db.py` resolves each `{ "repo": ... }` entry to that repo's **latest** GitHub release, so you
usually don't edit URLs by hand — just re-run it after a release. To add a mod, add a line to
`input-locations.json` and rebuild.

## Notes

- Mod `id`s match `^[a-zA-Z0-9_-]+$`; every entry's dependencies are virtual packages (`ccloader`,
  `crosscode`) that always resolve, so the database is self-consistent.
- This is a personal/suite database. The mods can also be submitted to the official CCModDB for
  wider discoverability; that's independent of this repo.

## Legal

Unofficial fan project, **not affiliated with, authorized, or endorsed by Radical Fish Games**.
Contains no CrossCode code or assets — only mod metadata and download links. MIT licensed
(see [`LICENSE`](LICENSE)).
