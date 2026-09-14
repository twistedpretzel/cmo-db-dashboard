# CMO Database Dashboard

A single-file, offline HTML dashboard for browsing and analysing the **Command: Modern Operations** unit database — every aircraft, ship, submarine, facility, ground unit, satellite, sensor and weapon, with type-specific visualisations and comparison tools.

You run one small tool against the database from **your own CMO install** and it generates a self-contained `.html` file you can open in any modern browser. No internet, no server, no accounts.

> **This project contains only the generator, an HTML template and documentation — no game data beyond the database's own term and code identifiers, which the glossary explains in its own words.** No ranges, kill probabilities, signatures or loadouts appear anywhere in this repository. Each user builds the dashboard from the database in their own copy of the game. See [Sharing & licensing](#sharing--licensing).

---

## Easiest way — no Python needed (Windows)

1. Go to the **[Releases](../../releases)** page and download **`build_dashboard.exe`** from the latest release.
2. Copy it into your game's **`DB` folder** — the one that contains `DB3K_517.db3`. On a typical Steam install that's:

   ```
   ...\steamapps\common\Command Modern Operations\DB\
   ```

3. **Double-click `build_dashboard.exe`.** It finds the newest database automatically, builds the dashboard (about ten seconds), and opens it in your browser. Done.

That's the whole process — no Python, no command line, nothing to type.

If the folder also contains an *older* database version (e.g. both `DB3K_517.db3` and `DB3K_518.db3` are present), the tool automatically adds a **"What's new"** page listing everything that changed between them — new and retired units, weapons and sensors, and the specific stats and loadouts that were adjusted. It compares whichever database it builds against the next-older one of the same kind in the folder, so this works both when you double-click (newest vs. the one before it) and when you drop a specific database on the tool (that database vs. the one before *it*). Keep your last database around and each update comes with its own changelog. (Don't want it? See "just build one database" below.)

**First run: a blue "Windows protected your PC" box may appear.** That's SmartScreen being cautious about a new file from an unknown indie author — it is expected here and does not mean anything is wrong. Click **More info → Run anyway**. If you'd like to confirm the download first, each release includes a `build_dashboard.exe.sha256` checksum you can verify.

The generated `DB3K_517_dashboard.html` is **saved right next to the game's database** — it's a permanent file, not just a browser view. Keep it in the `DB` folder (so it can find the unit photos) and **double-click that `.html`, or bookmark it, to reopen any time** — you don't need to rebuild. Only re-run the tool when your game database updates.

**Want an older database?** Double-clicking always builds the newest. To build a specific one instead, **drag its `.db3` file onto `build_dashboard.exe`** (or, from a terminal, `build_dashboard.exe DB3K_515.db3`). The dashboard is written next to whichever database you pick — and it gets its own "What's new" page comparing it against the next-older database in the folder, just like the double-click path.

**Just build one database, no changelog?** Run it from a terminal with `--no-changelog` (e.g. `build_dashboard.exe DB3K_518.db3 --no-changelog`). The tool then builds only that dashboard and skips the comparison.

---

## With Python instead

If you already have (or don't mind installing) Python, you can run the script directly — this works on Windows, macOS and Linux.

- **Python 3.8+** — standard library only, nothing to `pip install`.
- Get the files with the green **Code → Download ZIP**, then unzip (or clone). **Don't** open a file on GitHub and use *Save as* — that saves the web page, not the file, and is the usual cause of a "template not found" error. If you grab files individually, use each file's **Raw** button.
- Copy **`build_dashboard.py`**, **`cmo_db_dashboard.template.html`**, and (on Windows) **`run_dashboard.bat`** into your game's `DB` folder.

Then either:

- **Windows:** double-click **`run_dashboard.bat`** (you can also drag a specific `.db3` onto it), or
- **Any OS, from a terminal in that folder:**

  ```bash
  python build_dashboard.py                 # newest DB3K_*.db3 here, + changelog vs the one before it
  python build_dashboard.py CWDB_517.db3     # a specific database, + changelog vs the one before it
  python build_dashboard.py --no-open        # build without launching a browser
  python build_dashboard.py --no-changelog   # build just this database, skip the "What's new" page
  python build_dashboard.py DB3K_518.db3 --vs DB3K_505.db3    # compare against a *specific* older DB
  ```

  Type that at a **Command Prompt / PowerShell / terminal** — *not* at the Python `>>>` prompt. If you see `>>>`, you're inside Python; type `exit()` first. (Getting `SyntaxError: invalid syntax` on the command almost always means it was typed at the `>>>` prompt.)

When a new game/database version ships, just run it again — it always picks the newest `DB3K_*.db3`.

---

## What the dashboard does

- **Browse** all six platform types (aircraft, ships, submarines, facilities, ground units and satellites) plus sensors and weapons, with fast search **by name or DBID**, sortable columns, and rich filters (guidance, features, damage points, target class, sensor capability/band, "carries weapon family", operator, era, and more). One-click **CSV export** of any filtered list.
- **Detail pages** with type-aware visualisations — radar frequency strips and detection envelopes, optics/IR zoom, sonar depth envelopes, ESM direction-finding, weapon engagement envelopes and warhead breakdowns, per-aspect signatures, propulsion speed-by-altitude curves, and the mounts, magazines and loadouts each platform carries (including radars mounted on launcher vehicles).
- **Compare** up to four platforms, sensors or weapons side by side with overlaid envelopes.
- **Systems tools:** an *Electronic Warfare* explainer (OECM/DECM), a *Detection matchup* calculator (at what range does X detect Y, by radar/IR/EO, per aspect), and *Threat rings* (a platform's search / engagement-radar / SAM envelope, scaled to a chosen target's radar cross-section).
- **Analysis tools:** a *Trend explorer* (plot any metric against any other) and *Leaderboards* (top-N by speed, range, stealth, quietness, etc., with a service-era timeline).
- **Scenario ORBAT:** ingest a snapshot of a scenario (exported with the one-click Lua script shown on the page) to see its full order of battle inside the dashboard — grouped by side → task group → platform type, with per-type totals, a rolled-up "Airborne" picture, a per-side force summary, live status/loadout/readiness, loadout links to the exact fit, and **aggregated ordnance** (each group totals its magazines by weapon type, e.g. "142× UGM-109E Tomahawk Blk IV TACTOM", and expands to the count each hull carries). Sides are collapsed on open so it's spoiler-safe.
- **Satellites & anti-satellite engagement:** satellites are a full platform type with orbital elements; each satellite card shows which of the database's ASAT weapons can reach that orbit (filtered by altitude ceiling and range) and a ground-footprint diagram of the area from which each weapon could engage.
- **What's new:** when you build with a previous database to compare against (see below), a *Reference* page shows the full database-to-database changelog — units, weapons and sensors added, retired (deprecated) or removed, and the exact fields (ranges, kill probabilities, service dates, and more) and components (mounts, sensors, loadouts) that changed on each existing entry, every one deep-linked to its detail page.
- **Feature glossary:** a searchable *Reference* page explaining every sensor capability, feature code, weapon-guidance method, target class and sensor/weapon type, plus platform attributes (armor, ergonomics, autonomy, cockpit visibility), the communications model, and all 130 aircraft/ship/submarine/ground-unit feature codes (557 entries). Hover any chip on a detail page for a plain-language tooltip, or click it for the full write-up — sourced from the game manual where possible and tagged OBSERVED / INFERRED / SPECULATIVE. The complete reference is in [GLOSSARY.md](GLOSSARY.md).
- **AAR — message log reader:** load a CMO message log (`AALog.txt`) and the dashboard reads it back as an after-action review, across six tabs. **Overview** — what the log contains, an activity timeline, and how each weapon that reached an endgame actually ended (impact, spoofed, malfunction, or simply out of energy). **Weapons** — every weapon resolved against the loaded database, with hit rates carrying 95% confidence intervals, the logged base probability checked against the database's own `PoK`, expandable per target class and speed band, and a list of engagements fought beyond the weapon's rated `TargetSpeedMax`. **Mechanics** — probability against crossing rate, modifier incidence, worked engagement chains as the engine wrote them, and soft-kill systems compared declared-against-realised. **Losses** — losses by cause (including units lost to fuel rather than enemy fire), and which impacts actually did damage as against which struck a target that was already finished. **ORBAT** — with a scenario snapshot also loaded, damage taken read against the class's database damage points, expenditure against magazine contents, and losses against the roster. Everything exports to CSV; the log is read entirely in your browser and never leaves it.
- **Light and dark themes** and shareable, bookmarkable URLs for any filtered view.

Every number is extracted from the database. Where a value is a modelled estimate rather than a stored field — notably the RCS-scaled radar detection ranges — the page says so and shows the method. Treat radar/IR ranges and threat rings as **clean-air planning envelopes**: they don't account for terrain masking, jamming, or the engine's full dynamic detection model.

---

## Reading a message log (AAR)

CMO writes a running message log while a scenario plays. The dashboard's **AAR log** page reads
one, parses it into typed records, and reports on it. Nothing is uploaded — parsing happens in
your browser, and the log never leaves your machine.

1. Save a copy of the log aside. CMO overwrites it each session.
2. Open **AAR log** in the dashboard and choose the file, or paste its contents.
3. One log at a time — loading another replaces it. Export first if you want to keep one; the
   exported JSON loads straight back in.

**Message Log settings matter.** In CMO, under *Options ▸ Message Log*, the analysis needs
**Weapon Endgame Calculations**, **Unguided Weapon Accuracy Modifiers**, **Weapon Damage**,
**Unit Damage**, **Unit Lost** and **Point Defence**. Turning **Scenario Events**, **Unit AI**,
**Debug** and **User Interface** off cuts the file size substantially without losing anything the
page uses. The Load page lists this too, and the page tells you when a measure is unavailable
because the records it needs aren't in the file, rather than quietly reporting zero.

Date formats differ by Windows regional settings; the reader detects the format from the file and
shows which one it used. Records that several sides could see are written once per side, and those
duplicates are merged so counts aren't doubled.

[LOG_GRAMMAR.md](LOG_GRAMMAR.md) documents every record pattern the reader recognises, how it was
derived, and what is deliberately *not* claimed from the data. `log_grammar_probe.py` runs the same
grammar over a folder of logs from the command line if you want to check coverage on your own files.

---

## How it works

The tool opens the database **read-only**, pulls the tables the dashboard needs into a compact JSON structure, compresses it (raw `deflate`), base64-encodes it, and substitutes it into the template at a marker. The result is one self-contained HTML file (~5 MB) that carries a compressed copy of *your* database inside it and needs nothing else at runtime — the page decompresses its data in the browser using the built-in `DecompressionStream` (Chrome/Edge 80+, Firefox 113+, Safari 16.4+).

The dashboard stores a few small items (theme, "show deprecated", the compare tray, and any scenario snapshot you ingest into the Scenario ORBAT page) in your browser's `localStorage`. That data lives only in your browser and is never transmitted anywhere.

---

## For maintainers — building & releasing the .exe

The Windows executable is built automatically by GitHub Actions (`.github/workflows/build-exe.yml`) using PyInstaller — a Windows `.exe` can only be built on Windows, which is why it runs in CI.

- **Publish a release:** push a version tag and the workflow builds `build_dashboard.exe`, generates its checksum, and attaches both to a new GitHub Release:

  ```bash
  git tag v1.0.0
  git push origin v1.0.0
  ```

- **Just build without releasing:** the **Actions** tab → *Build Windows executable* → *Run workflow* produces the `.exe` as a downloadable build artifact.
- **Build locally** (on Windows, with `pip install pyinstaller`): `pyinstaller build_dashboard.spec` → `dist/build_dashboard.exe`. The template is bundled inside the executable via the spec's `datas`, so the resulting `.exe` is fully standalone.

---

## Sharing & licensing

- **The generator, template, documentation and build files in this repository contain no game data** — beyond the database's own enum identifiers used as keys for the glossary's original write-ups — and are provided under the MIT [LICENSE](LICENSE).
- **The generated `*_dashboard.html` is different:** it embeds a complete copy of the CMO database, which is proprietary content owned by Slitherine / WarfareSims and covered by the game's End User Licence Agreement (which defines the databases and artwork as protected "Property" and forbids distributing, publishing, copying or publicly displaying them without written permission). **Do not redistribute the generated HTML, or the game's `Images/`, publicly.** Share this tool instead and let other owners generate their own — which is the whole point of a data-free release.
- This project is an unofficial, fan-made utility. It is **not affiliated with, endorsed by, or supported by Slitherine or WarfareSims.** "Command: Modern Operations" and all database content and trademarks belong to their respective owners.
- The tool is provided **as-is, without warranty**, for personal use with a game you own.

---

## Troubleshooting

- **"Windows protected your PC" on the .exe** → expected for an unsigned indie tool; click *More info → Run anyway*. To verify the download, check it against the release's `.sha256`.
- **Antivirus flags the .exe** → PyInstaller executables occasionally trigger false positives. If you'd rather not run the `.exe`, use the Python script path above; it's plain, readable source.
- **The window flashes and closes / shows an error** → run it inside the `DB` folder that has your `.db3`. The tool prints the reason and waits for you to press Enter before closing.
- **"No CMO database found"** → the `.exe` or script isn't in a folder containing a `DB3K_*.db3` (or `CWDB_*.db3`). Move it into your game's `DB` folder.
- **`SyntaxError: invalid syntax`** → the command was typed at Python's `>>>` interactive prompt. Type `exit()` to leave Python, then run it from a normal Command Prompt / terminal (or just use the `.exe` / `run_dashboard.bat`).
- **"template not found"** → `cmo_db_dashboard.template.html` isn't beside the script, or it was saved as a web page. Re-download via **Code → Download ZIP** (or the file's **Raw** button). The prebuilt `.exe` avoids this entirely — the template is inside it.
- **Blank page or a "decompression" error in the browser** → your browser is too old for `DecompressionStream`; update to a current Chrome/Edge/Firefox/Safari.
- **Unit photos don't appear** → keep the generated HTML inside the `DB` folder so `Images/…` resolves; otherwise this is expected and harmless.
- **Nothing opened in the browser** → the file was still written to the `DB` folder; open `*_dashboard.html` yourself, or run with a browser set as your default.
