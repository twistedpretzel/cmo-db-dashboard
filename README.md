# CMO Database Dashboard

A single-file, offline HTML dashboard for browsing and analysing the **Command: Modern Operations** unit database — every aircraft, ship, submarine, facility, ground unit, sensor and weapon, with type-specific visualisations and comparison tools.

You run one small tool against the database from **your own CMO install** and it generates a self-contained `.html` file you can open in any modern browser. No internet, no server, no accounts.

> **This project contains only the generator and an HTML template — no game data.** Each user builds the dashboard from the database in their own copy of the game. See [Sharing & licensing](#sharing--licensing).

---

## Easiest way — no Python needed (Windows)

1. Go to the **[Releases](../../releases)** page and download **`build_dashboard.exe`** from the latest release.
2. Copy it into your game's **`DB` folder** — the one that contains `DB3K_517.db3`. On a typical Steam install that's:

   ```
   ...\steamapps\common\Command Modern Operations\DB\
   ```

3. **Double-click `build_dashboard.exe`.** It finds the newest database automatically, builds the dashboard (about ten seconds), and opens it in your browser. Done.

That's the whole process — no Python, no command line, nothing to type.

**First run: a blue "Windows protected your PC" box may appear.** That's SmartScreen being cautious about a new file from an unknown indie author — it is expected here and does not mean anything is wrong. Click **More info → Run anyway**. If you'd like to confirm the download first, each release includes a `build_dashboard.exe.sha256` checksum you can verify.

The generated `DB3K_517_dashboard.html` is **saved right next to the game's database** — it's a permanent file, not just a browser view. Keep it in the `DB` folder (so it can find the unit photos) and **double-click that `.html`, or bookmark it, to reopen any time** — you don't need to rebuild. Only re-run the tool when your game database updates.

**Want an older database?** Double-clicking always builds the newest. To build a specific one instead, **drag its `.db3` file onto `build_dashboard.exe`** (or, from a terminal, `build_dashboard.exe DB3K_515.db3`). The dashboard is written next to whichever database you pick.

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
  python build_dashboard.py                 # auto-detects the newest DB3K_*.db3 here
  python build_dashboard.py CWDB_517.db3     # or name a specific database
  python build_dashboard.py --no-open        # build without launching a browser
  ```

  Type that at a **Command Prompt / PowerShell / terminal** — *not* at the Python `>>>` prompt. If you see `>>>`, you're inside Python; type `exit()` first. (Getting `SyntaxError: invalid syntax` on the command almost always means it was typed at the `>>>` prompt.)

When a new game/database version ships, just run it again — it always picks the newest `DB3K_*.db3`.

---

## What the dashboard does

- **Browse** all five platform types plus sensors and weapons, with fast search, sortable columns, and rich filters (guidance, features, damage points, target class, sensor capability/band, "carries weapon family", operator, era, and more). One-click **CSV export** of any filtered list.
- **Detail pages** with type-aware visualisations — radar frequency strips and detection envelopes, optics/IR zoom, sonar depth envelopes, ESM direction-finding, weapon engagement envelopes and warhead breakdowns, per-aspect signatures, propulsion speed-by-altitude curves, and the mounts, magazines and loadouts each platform carries (including radars mounted on launcher vehicles).
- **Compare** up to four platforms, sensors or weapons side by side with overlaid envelopes.
- **Systems tools:** an *Electronic Warfare* explainer (OECM/DECM), a *Detection matchup* calculator (at what range does X detect Y, by radar/IR/EO, per aspect), and *Threat rings* (a platform's search / engagement-radar / SAM envelope, scaled to a chosen target's radar cross-section).
- **Analysis tools:** a *Trend explorer* (plot any metric against any other) and *Leaderboards* (top-N by speed, range, stealth, quietness, etc., with a service-era timeline).
- **Feature glossary:** a searchable *Reference* page explaining every sensor capability, feature code, weapon-guidance method, target class and sensor/weapon type (251 entries). Hover any chip on a sensor or weapon page for a plain-language tooltip, or click it for the full write-up — sourced from the game manual where possible and tagged OBSERVED / INFERRED / SPECULATIVE. The complete reference is in [GLOSSARY.md](GLOSSARY.md).
- **Light and dark themes** and shareable, bookmarkable URLs for any filtered view.

Every number is extracted from the database. Where a value is a modelled estimate rather than a stored field — notably the RCS-scaled radar detection ranges — the page says so and shows the method. Treat radar/IR ranges and threat rings as **clean-air planning envelopes**: they don't account for terrain masking, jamming, or the engine's full dynamic detection model.

---

## How it works

The tool opens the database **read-only**, pulls the tables the dashboard needs into a compact JSON structure, compresses it (raw `deflate`), base64-encodes it, and substitutes it into the template at a marker. The result is one self-contained HTML file (~5 MB) that carries a compressed copy of *your* database inside it and needs nothing else at runtime — the page decompresses its data in the browser using the built-in `DecompressionStream` (Chrome/Edge 80+, Firefox 113+, Safari 16.4+).

The dashboard stores three small preferences (theme, "show deprecated", the compare tray) in your browser's `localStorage`. That data lives only in your browser and is never transmitted anywhere.

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

- **The generator, template, and build files in this repository contain no game data** and are provided under the MIT [LICENSE](LICENSE).
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
