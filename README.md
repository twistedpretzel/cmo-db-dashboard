# CMO Database Dashboard

A single-file, offline HTML dashboard for browsing and analysing the **Command: Modern Operations** unit database — every aircraft, ship, submarine, facility, ground unit, sensor and weapon, with type-specific visualisations and comparison tools.

You point the included script at the database from **your own CMO install** and it generates a self-contained `.html` file you can open in any modern browser. No internet, no server, no install step.

> **This release contains only the generator (a Python script) and an HTML template — no game data.** Each user builds the dashboard from the database in their own copy of the game. See [Sharing & licensing](#sharing--licensing).

---

## What's in this release

| File | What it is |
|------|------------|
| `build_dashboard.py` | The extractor. Reads a CMO `.db3` database and writes the dashboard HTML. Python standard library only. |
| `cmo_db_dashboard.template.html` | The dashboard UI (HTML/CSS/JS). The script injects your data into this. |
| `README.md` | This file. |

---

## Requirements

- **Python 3.8+** — standard library only, nothing to `pip install`.
- **A Command: Modern Operations installation** (you must own the game — this tool does not include its data).
- **A current browser** to view the output: Chrome/Edge 80+, Firefox 113+, or Safari 16.4+. (The page decompresses its embedded data on load using the browser's built-in `DecompressionStream`.)

---

## Quick start

1. Put `build_dashboard.py` and `cmo_db_dashboard.template.html` **in your CMO `DB` folder** — the one containing `DB3K_517.db3` (and usually a `CWDB_*.db3`, an `Images/` folder, etc.). On a typical Steam install that's something like:

   ```
   .../steamapps/common/Command Modern Operations/DB/
   ```

2. From that folder, run the script against the database you want:

   ```bash
   python build_dashboard.py DB3K_517.db3
   ```

   It takes about ten seconds and writes `DB3K_517_dashboard.html` next to it.

3. Double-click the generated HTML to open it in your browser. Done.

Keeping the HTML **inside the `DB` folder** lets it find the unit photos (`Images/DB3000/*.webp`) by relative path. Moved elsewhere it still works fully — the pictures just won't show.

### Other databases / options

```bash
python build_dashboard.py DB3K_518.db3          # any newer DB3K version, same command
python build_dashboard.py CWDB_517.db3          # the Cold War database (images from Images/CWDB)
python build_dashboard.py DB3K_517.db3 -o out.html
python build_dashboard.py DB3K_517.db3 --json dump.json   # also dump the raw extracted JSON
```

When a new game/database version ships, just re-run the script on the new `.db3`.

---

## What the dashboard does

- **Browse** all five platform types plus sensors and weapons, with fast search, sortable columns, and rich filters (guidance, features/codes, damage points, target class, sensor capability/band, "carries weapon family", operator, era, and more). One-click **CSV export** of any filtered list.
- **Detail pages** with type-aware visualisations — radar frequency strips and detection envelopes, optics/IR zoom, sonar depth envelopes, ESM direction-finding, weapon engagement envelopes and warhead breakdowns, per-aspect signatures, propulsion speed-by-altitude curves, and the mounts/magazines/loadouts each platform carries.
- **Compare** up to four platforms, sensors or weapons side by side with overlaid envelopes.
- **Systems tools:** an *Electronic Warfare* explainer (OECM/DECM), a *Detection matchup* calculator (at what range does X detect Y, by radar/IR/EO, per aspect), and *Threat rings* (a platform's search / engagement-radar / SAM envelope, scaled to a chosen target's radar cross-section).
- **Analysis tools:** a *Trend explorer* (plot any metric against any other), and *Leaderboards* (top-N by speed, range, stealth, quietness, etc., with a service-era timeline).
- **Light and dark themes**, keyboard-free navigation, and shareable/bookmarkable URLs for any filtered view.

Every number is extracted from the database. Where a value is a modelled estimate rather than a stored field — notably the RCS-scaled radar detection ranges — the page says so and shows the method, so you can sanity-check it. Treat radar/IR ranges and threat rings as **clean-air planning envelopes**: they don't account for terrain masking, jamming, or the game engine's full dynamic detection model.

---

## How it works

The script opens the database **read-only**, pulls the tables the dashboard needs into a compact JSON structure, compresses it (raw `deflate`), base64-encodes it, and substitutes it into the template at a marker. The result is one self-contained HTML file (~5 MB) that carries a compressed copy of *your* database inside it and needs nothing else at runtime.

The dashboard stores three small preferences (theme, "show deprecated", the compare tray) in your browser's `localStorage`. That data lives only in your browser and is never transmitted anywhere.

---

## Sharing & licensing

- **The script and template in this release contain no game data** and are safe to share.
- **The generated HTML is different:** it embeds a complete copy of the CMO database, which is proprietary content owned by Slitherine / WarfareSims and covered by the game's End User Licence Agreement. **Do not redistribute the generated HTML (or the game's `Images/`) publicly.** If you want to share the tool, share this script + template and let other owners generate their own — which is the whole point of a script-only release.
- This project is an unofficial, fan-made utility. It is **not affiliated with, endorsed by, or supported by Slitherine or WarfareSims.** "Command: Modern Operations" and all database content and trademarks belong to their respective owners.
- The generator script and template themselves are provided **as-is, without warranty**, for personal use with a game you own. Do what you like with the code; the game's data and trademarks are not yours or mine to license.

---

## Troubleshooting

- **Blank page or a "decompression" error** → your browser is too old for `DecompressionStream`. Update to a current Chrome/Edge/Firefox/Safari.
- **`template not found`** → run the script from the folder that has `cmo_db_dashboard.template.html`, or pass `--template /path/to/it`.
- **Unit photos don't appear** → keep the generated HTML inside the `DB` folder so `Images/…` resolves; otherwise this is expected and harmless.
- **Wrong or missing entries** → make sure you ran it against the intended `.db3`. The overview page shows which database and the extraction time.
