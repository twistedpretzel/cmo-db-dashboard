# CMO Message Log — Grammar Specification
**Phase 0 deliverable · v0.8 · 2026-09-14**
Target feature: AAR / log-reader module for the CMO DB Dashboard (proposed v1.4.0)

This document defines every record pattern the log parser will recognise, what fields each
yields, and how confident we are in it. **Nothing is built from this until you sign off.**
Every claim is tagged `OBSERVED` (seen in a sample log, count cited), `INFERRED` (deduced from
structure or from CMO behaviour, not directly demonstrated), or `SPECULATIVE` (a guess to be
tested).

---

## 1. Sample corpus

| Ref | File | Records | Era / setting | Character |
|---|---|---|---|---|
| `BALTIC` | AALog.txt | 871 | 2027 Barents/Baltic | Your hybrid-war scenario. AShM saturation vs. NATO AAW. Unit AI **on**. |
| `EG` | AALog_EG.txt | 501 | 1985 Soviet | Cold War ASW/tracking. **Zero weapon employment.** |
| `SCS` | AALog_SCS.txt | 620 | 2025 ASEAN/PRC | Surface action + SAM. Scenario Events **off**. |
| `TB5` | AALog_TB5.txt | 2,012 | 2027 (same as BALTIC) | Largest sample. Unit AI **off**. Full AAW/ASuW engagement. |
| `LIBDAWN` | AALog_Liberty_Dawn.txt | 727 | 2031 W. Pacific | Hypersonic glide-body strike + defense. Airfield ISR. |
| `LCS` | AALog_LCS_Test.txt | 652 | 2025 | Naval gunfire vs. a surface target. **No endgame PH records at all.** |
| `LUZON` | 2026-09-09_11.08.55.txt | 66,875 | 2028 W. Pacific | Nikel's. 142k lines. Different date format, multi-side. |
| `WARSAW` | 2026-09-13_12.00.10.txt | 49,212 | 1986 Central Europe | Nikel's. 98k lines. Heavy ground/SEAD, fuel losses. |
| | **Total** | **121,470** | | |

`OBSERVED` — The five logs together contain **300 fully-scored engagements**, **585 terminal
outcome records**, **171 soft-kill attempts**, **116 damage records** and **108 airfield ISR
records**. That is enough to specify the grammar. It is *not* enough to draw conclusions about
any individual weapon (see §6, F4).

**v0.8 changes:** Phase 4 built — see §9e and F26. UI pass on width and column layout.

**v0.7 changes:** Phase 3 built, and deliberately not as specified — see §9d and F24.

**v0.6 changes:** Phase 5 built — see §9c and F23.

**v0.5 changes:** two logs from forum user Nikel added — 23× the previous corpus. Two shipped
defects found and fixed (F18, F19), fifteen record classes added, the §7 BMD gap closed for real
(F20), and **an earlier finding corrected** (F21). Coverage re-established at 99.97% over
121,470 records.

**v0.4 changes:** Phase 2 built — see F15–F17 and §9. No new record classes.

**v0.3 changes:** `LCS` added — see F11–F13. Two new record classes (`FIRE_CEP`, `GODSEYE`),
`FIRE_UNGUIDED` renamed to `FIRE_POH` to pair with it, and **four real classes recovered from a
catch-all that had been silently absorbing them** (F12). Coverage re-established at 100.00% over
5,383 records.

**v0.2 changes:** `LIBDAWN` added. Two new record classes (§3, airfield ISR), one class enriched
(`DOCTRINE` now carries a quantified REASON), coverage raised to **100.00%**, and the
§7 "ballistic-missile intercept" gap closed — see F8–F10.

---

## 2. Record model

`OBSERVED` — Every log is a flat sequence of records with this shape:

```
M/D/YYYY H:MM:SS AM - [<Side>] <body>
```

Three structural facts the parser must handle:

1. **Blank-line separation.** Records are separated by a blank line. Non-trivial, because —
2. **Continuation lines exist.** A record body may span many lines with no timestamp.
   `OBSERVED` in BALTIC: your Havis North-1 `FLASH TRAFFIC` special message runs ~97 lines of
   raw HTML/CSS with no timestamp. Rule: **a line that does not match the timestamp anchor
   belongs to the preceding record.** Splitting on newline alone corrupts the record count.
3. **The side prefix is optional and is a *visibility* marker, not an attribution.**
   `[NATO] ...` means "NATO could see this". Engagement-resolution lines carry **no** side
   prefix at all. `INFERRED` — the shooter's side must therefore be resolved by DB join on
   the weapon name, not read off the line. This is a design constraint, not a nuisance (§6, F2).

---

## 3. Record classes

Tier 1 = the analytic payload. Tier 2 = context that makes Tier 1 interpretable. Tier 3 = noise
to be counted and discarded.

### Tier 1 — Scored events (the payload)

| Class | Count | Tag | Fields extracted |
|---|---|---|---|
| `ENG_MISSILE` | 251 | `OBSERVED` | weapon, serial, target, base PH, full modifier chain, final PH, die roll, result |
| `ENG_GUN` | 49 | `OBSERVED` | gun, target, base-Ph, distance adjustment, modifier chain, final Ph, roll, result |
| `FIRE_UNGUIDED` | 15 | `OBSERVED` | platform, weapon, nominal PoH, director penalty, sea-state penalty, final PoH *at launch* |
| `SOFTKILL` | 171 | `OBSERVED` | decoy/jammer, system, tech-gen, host platform, victim sensor + tech-gen, guided weapon, probability, roll, result |
| `TERM` | 585 | `OBSERVED` | weapon, serial, HIT/MISS, terminal detail (impact / near-miss distance / miss mode) |
| `TERM_NOSENSOR` | 17 | `OBSERVED` | weapon lost terminal homing — distinct miss mode, separate line shape |
| `PENETRATION` | 146 | `OBSERVED` | penetration % — **no weapon named** |
| `NEARMISS` | 14 | `OBSERVED` | weapon, target, miss distance + unit (ft/m/nm) |

**`ENG_MISSILE` is the richest record in the file.** Canonical instance (`OBSERVED`, TB5):

```
RIM-174A ERAM SM-6 Blk IA Dual II #4122 HIT: Weapon: ... is attacking
SS-N-33 [3M22 Zircon] #3995 with a base PH of 90%.  Target speed modifier: -5%.
Intercept angle 96 deg, tgt 4584 kts, intc 2488 kts. LOS rate 12.12 deg/s.
AgilityScore 5, CrossingMod 0.91, KinMod 0.74. PH reduced by 32%.
Final PH: 54% Result: 46 - HIT.
```

`OBSERVED` — the modifier chain is a closed vocabulary. Across all 256 scored engagements only
these clause types appear:

| Clause | n | Applies to |
|---|---|---|
| `Target speed modifier: N%` | 241 | both |
| `Intercept angle / tgt kts / intc kts` | 207 | missile |
| `LOS rate N deg/s` | 207 | missile |
| `AgilityScore N, CrossingMod N, KinMod N` | 207 | missile |
| `PH reduced by N%` | 207 | missile |
| `PH adjusted for weapon speed: N% (pure-aerodynamic attitude control)` | 61 | missile |
| `Base-Ph adjusted for distance: N%` | 49 | gun |
| `Target signature modifier: N% (Director [X] has tech-gen: Y)` | 87 | both |
| `Target is at Mach N; effective flak hit probability reduced by same factor` | 22 | gun |
| `Proximity fuze (Gun (NN-NNmm)) - Ph increased by Nx` | 20 | gun |
| `Sea-skimmer modifier: N%` | 11 | both |
| `Target is missile with random/zig-zag terminal manouver — reduced by N%` | 8 | gun |
| `Aircraft weight fraction / agility adjusted for proficiency / altitude / aspect` | 14 | missile vs. aircraft |

`INFERRED` — this vocabulary is stable enough to parse into a **typed modifier list**
(`{name, value, kind}`) rather than a free-text blob. That is what makes the waterfall
visualisation possible. `SPECULATIVE` — clauses for torpedo, mine, DEW and ASW engagements
almost certainly exist and are **not in this corpus** (see §7).

### Tier 2 — Effects and context

| Class | Count | Tag | Notes |
|---|---|---|---|
| `DMG_DP` | 37 | `OBSERVED` | `<unit> has suffered {weapon\|blast\|underground shock\|fragmentation} damage: N DPs` |
| `DMG_COMP_DEGRADE` | 46 | `OBSERVED` | `<unit> damage report: <component> has been {lightly\|moderately\|heavily} damaged` |
| `DMG_COMPONENT` | 15 | `OBSERVED` | `<unit> damage report: <component> has been destroyed!` |
| `DMG_STATE` / `SINKING` | 18 | `OBSERVED` | severe fire / flooding / `is sinking!!!` |
| `DESTROYED` | 9 | `OBSERVED` | unit killed |
| `CEP_UPDATE` | 17 | `OBSERVED` | GNSS update rate → CEP adjustment, per weapon serial |
| `SEEKER_DETECT` / `LOCKON` | 96 | `OBSERVED` | weapon seeker acquisition — gives time-to-lock |
| `CONTACT_*` (6 classes) | 1,312 | `OBSERVED` | new / classified / renamed / hostile / updated / lost, incl. private (per-holder) contacts |
| `COMMS` | 212 | `OBSERVED` | comms net join/loss. All 212 are in `EG`. |
| `DOCTRINE` | 31 | `OBSERVED` | `The Unit X cannot fire against Y with weapon Z` — **plus an optional quantified `REASON:` clause** (see F10) |
| `AIRFIELD_SPOT_NEW` | 44 | `OBSERVED` | `New aircraft spotted on <location> (<capacity>) by <observer> (Sensor: <sensor>)` |
| `AIRFIELD_SPOT_ID` | 64 | `OBSERVED` | `Aircraft previously spotted on <location> has been {identified\|type-classified} as: <type> (recon by: <observer> - Sensor: <sensor>)` |
| `GROUP_DISSOLVE`, `POSTURE`, `SIDE_SWITCH`, `BDA_REPORT`, `PATHEVAL` | 27 | `OBSERVED` | low volume, cheap to keep |

`OBSERVED` — the damage records form a **complete chain**: DP accumulation → component degraded
→ component destroyed → fire/flooding → sinking → destroyed. Real BDA is therefore derivable,
not just a kill count.

### Tier 3 — Noise

| Class | Count | Tag | Disposition |
|---|---|---|---|
| `EVENT` | 959 | `OBSERVED` | 24% of all records. Pure scenario-trigger spam. Count and drop. |
| `WPN_LOGIC` | 326 | `OBSERVED` | Retarget / running-blind / overshot. 310 of 326 are in `BALTIC` alone. |
| `SPECIAL_MSG` | 19 | `OBSERVED` | HTML briefing blocks. Render as narrative timeline markers, don't parse. |

---

## 4. Coverage

`OBSERVED` — the pattern set in §3 classifies **121,432 of 121,470 records (99.97%)** across all
eight logs, without a catch-all absorbing the remainder (F12). The residue is 38 records in a
long tail of repair-state and component-damage phrasings.

The reference implementation `log_grammar_probe.py` is now **generated** from the dashboard's
pattern list by `gen_probe.py`, so the two cannot drift. It is no longer an independently
*authored* parser; what it still provides is an independent regex engine and control flow, and a
way to run the grammar over a folder of logs offline. That cross-check earned its keep
immediately: it caught that the dashboard matches unanchored patterns by search while the probe
was anchoring them, which had mis-scored one whole log. Adding `LIBDAWN` initially dropped coverage to 84.04% — an entire unseen record
family (airfield ISR) plus two field-shape assumptions that were too narrow (a parking-spot
capacity can be a length, `(2000m)`, not only `(2x Very Large Aircraft)`; fire severity includes
`minor`). Both are now patterned.

`INFERRED` — that 84% dip is the strongest argument in this document for the unmatched counter
below. A single new scenario type introduced 116 records the parser had never seen, and it
would have dropped every one of them silently.

**Design requirement:** the AAR page must display its own unmatched-record count. Silent drops
are how a parser rots without anyone noticing when Slitherine changes a message string.

---

## 5. Parse validation

I did not want to trust my own regexes, so the extraction was checked against an invariant the
parser does not use.

`OBSERVED` — CMO logs both the final probability *and* the die roll. If the parse is correct,
`roll` vs `Final PH` must predict `HIT`/`MISS` every time. Result across all 256 scored
engagements:

> **299 / 300 agree (99.7%)** — including all 44 engagements in `LIBDAWN`, which the v0.1
> pattern set had never been tested against.

The single disagreement is instructive rather than a defect: `RIM-162A ESSM, Final PH 68,
roll 68 → MISS`. `INFERRED` — **the engine's comparison is strict (`roll < PH`), not `≤`.**
An exact tie is a miss. The parser will encode that rule.

`OBSERVED` — secondary check: mean die roll across the first 256 engagements is **51.5** (a uniform 1–100
draw expects 50.5), and modelled mean final PH **51.8%** vs. realized hit rate **52.0%**. The
RNG is behaving and the model is self-consistent at aggregate scale.

`INFERRED` — taken together these two checks mean the field extraction is sound and the numbers
downstream of it can be trusted.

---

## 6. Findings that change the design

**F1 — The endgame record is a fire-control error budget, not a result line.** `OBSERVED`
Every term between base PH and final PH is exposed and named. This is the feature. Across the
corpus, modelled PH erosion from base to final, for weapons with n ≥ 5:

| Weapon | n | base PH | final PH | erosion | realized Pk |
|---|---|---|---|---|---|
| RIM-162A ESSM | 45 | 90.0% | 74.2% | −15.8 | 73% |
| RIM-162B ESSM | 33 | 90.0% | 65.6% | −24.4 | 64% |
| RIM-66M-2 SM-2MR Blk IIIA | 23 | 85.0% | 29.6% | **−55.4** | 26% |
| AIM-120D AMRAAM P3I.4 | 23 | 95.0% | 62.0% | −33.0 | 52% |
| RIM-174A ERAM SM-6 Blk I Dual I | 20 | 90.0% | 66.5% | −23.5 | 80% |
| AA-13 Arrow [R-37M] | 12 | 85.0% | 50.9% | −34.1 | 67% |
| Meteor | 10 | 95.0% | 64.5% | −30.5 | 50% |
| AK-630M 30mm Gatling | 8 | 64.2% | 14.0% | −50.2 | 25% |
| Mk15 Phalanx Blk 1B | 5 | 53.3% | 5.0% | **−48.3** | 0% |

The SM-2MR row is the whole argument for the feature. A 55-point erosion against Mach-5+
sea-skimmers is not visible anywhere in the catalog — only the log shows it, and only the
modifier chain explains *why*.

**F2 — The log is a visibility record, not ground truth.** `OBSERVED` (six `Switched side to:`
records in BALTIC; `[Side]` prefixes throughout). Every rate is "as observed by the side(s) you
had selected". `INFERRED` — this must be a persistent banner on the AAR page, and the ingest
must capture which sides were viewed. A per-weapon Pk quietly computed over a one-sided log is
exactly the kind of number that gets briefed and then falls apart.

**F3 — A log with zero engagements is a valid log.** `OBSERVED` — `EG` contains 501 records and
**not one HIT/MISS**; it is 217 contact classifications, 212 comms events and 37 lost private
contacts. `INFERRED` — the AAR page must detect this and degrade to a *detection & tracking*
view (sensor performance, classification latency, contact churn) rather than rendering empty
accuracy charts. This was the single most useful thing the extra logs told me.

**F4 — Sample sizes are small and unevenly distributed.** `OBSERVED` — 256 scored engagements
across four logs, but 213 of them come from `TB5` alone and `EG` contributes zero. Per-weapon n
runs 1–45. `INFERRED` — every accuracy figure needs a visible n and a confidence interval, and
the UI should grey out anything below a threshold (I'd set n ≥ 5). Without that the page
manufactures false precision.

**F5 — The dominant miss mode is kinematic, not probabilistic.** `OBSERVED` — of 304 terminal
MISS records:

| Miss mode | n |
|---|---|
| Ran out of energy, self-destructing | 204 |
| Impacted surface | 57 |
| Malfunctioned | 17 |
| All seekers spoofed | 19 |
| No functioning terminal-homing sensor | 17 |

**Two-thirds of misses never reached a PH roll at all.** `INFERRED` — "accuracy per weapon" as
normally understood (hits ÷ scored engagements) silently excludes the largest failure mode in
the data. The AAR needs *two* denominators, side by side: rounds expended vs. engagements
scored. A weapon with a 73% Pk that runs out of energy half the time is not a 73% weapon.

**F6 — Unguided fire is logged pre-launch, with its own modifier chain.** `OBSERVED`:

```
FNS Pohjanmaa attacks with weapon: 57mm/70 Bofors Mk3 GP Burst [4 rnds].
Nominal PoH: 25%. Director (EOS 500 [CCD]) is visual/EO/IR; accuracy decreased by 50%.
Sea state 4 & small ship - accuracy decreased by 10%. Final PoH at fire/launch point: 16.67%.
```

This is a *different record* from the endgame line — fired at launch, with director-type and
sea-state terms that never appear in the missile chain. It needs its own table and its own
chart. (It is also, as it happens, a 57mm Bofors Mk3 with an EO director degrading in sea
state 4, which is a familiar picture.)

**F7 — Your toggle change is confirmed in the data.** `OBSERVED` — `WPN_LOGIC` noise is 310
records in `BALTIC` (Unit AI on) vs. 15 in `TB5` (Unit AI off), on a log 2.3× larger. You were
right. See §8 for the rest of the recommended profile.

**F8 — Final PH has a hard floor of 5%.** `OBSERVED` — across all 300 scored engagements in the
corpus, the final PH distribution bottoms out at exactly **5%, 64 times, and never goes below
it**. `INFERRED` — this is an engine floor, not a coincidence of inputs. It matters for the
analytics in two ways: (a) a 5.0% final PH means "the model gave up", not "the model computed
5%", and the UI should mark those engagements distinctly; (b) any chart of modelled-vs-realized
PH will show a spike at 5% that is an artifact of the clamp, not a finding.

**F9 — Hypersonic defense is the clearest signal in the corpus.** `OBSERVED` — `LIBDAWN` is 32
engagements against a C-HGB (Common Hypersonic Glide Body) plus 12 against conventional targets
in the same log. Split:

| | n | Pk | base PH | final PH | target speed | LOS rate |
|---|---|---|---|---|---|---|
| vs C-HGB | 32 | **19%** | 75.3% | 26.1% | 3,905 kts (~Mach 6.8) | 11.15 °/s |
| vs everything else | 12 | 58% | 94.6% | 40.8% | 524 kts (~Mach 0.9) | **0.05 °/s** |

The LOS-rate column is the finding: a **220× difference in crossing rate** between the two
populations, in the same log, against the same shooters. That single number is the mechanism
behind the PH collapse, and it is exactly what the modifier waterfall (Phase 3) is for.

By interceptor, against the C-HGB:

| Interceptor | n | hits | Pk | base PH | final PH |
|---|---|---|---|---|---|
| SA-21b Growler [40N6] | 12 | 5 | 42% | 90% | 56.6% |
| FN-16 | 9 | 1 | 11% | 65% | **5.0%** |
| FN-6 | 5 | 0 | 0% | 65% | **5.0%** |
| SA-16 Gimlet [9M313] | 3 | 0 | 0% | 50% | **5.0%** |
| AA-12 Adder B [R-77-1] | 2 | 0 | 0% | 90% | **5.0%** |
| HQ-9B | 1 | 0 | 0% | 90% | 61.0% |

`OBSERVED` — 19 of 32 intercept attempts were MANPADS and short-range SAMs floored at the F8
minimum. `INFERRED` — an AAR that reports a single blended "Pk vs C-HGB = 19%" is actively
misleading; the real picture is one long-range system holding ~57% and everything else
contributing nothing but expenditure. **The weapon performance table must segment by target
class, not just by weapon.**

**F10 — Doctrine refusals can carry quantified targeting-quality data.** `OBSERVED` — the v0.1
corpus showed `DOCTRINE` as a bare refusal. `LIBDAWN` shows the richer form:

```
The Unit SSN 805 Tang [Virginia Class, Flight V] cannot fire against Radar (China YLC-8E) #N
with weapon IR-CPS. REASON: The target's downrange ambiguity (0.4nm) is larger than 1x the
weapon's acceptable limit (0.1nm)
```

`INFERRED` — this is the *shot that was never taken*, with the numeric reason it wasn't:
17 records of a hypersonic strike weapon held back because the track quality missed its
acceptance threshold. That is kill-chain data no other record class provides, and it argues for
promoting `DOCTRINE` out of Tier 2 into the Phase 2 analytics as a "denied engagements" view
alongside the scored ones.


**F11 — Direct gunfire is logged as CEP, not PoH, and the two must never be pooled.** `OBSERVED`
— `LCS` contains 72 fire records of a shape absent from every earlier log:

```
LCS 27 Nantucket [Freedom Class] attacks with weapon: 57mm/70 Bofors Mk3 GP Burst [4 rnds].
Nominal CEP: 20m. Director (DORNA [IR]) is visual/EO/IR; accuracy decreased by 50%.
Lots of rounds already fired in salvo; accuracy improving tremendously.
Sea state 0-3 & small ship - accuracy unaffected. Final CEP at fire/launch point: 6m.
```

`PoH` is a probability in percent where **higher is better**; `CEP` is a dispersion radius in
metres where **lower is better**. Averaging them together, or charting them on one axis, would
be meaningless. They are now separate classes (`FIRE_POH`, `FIRE_CEP`) with separate tables.

The CEP chain carries a term no PH chain has: **salvo warming**, a four-step ladder
(`A few … slightly` → `Some … measurably` → `Quite a few … substantially` → `Lots … tremendously`)
as the gun walks onto the target. `OBSERVED` across the 72 records:

| Weapon | bursts | nominal CEP | final CEP | tighter / worse |
|---|---|---|---|---|
| 57mm/70 Bofors Mk3 GP [4 rnds] | 42 | 19.6 m | **11.9 m** | 27 / 12 |
| 30mm Mk46 Mod 1 [Bushmaster II] [20 rnds] | 20 | 16.1 m | 16.1 m | 0 / 0 |
| 12.7mm/50 MG [10 rnds] | 10 | 24.0 m | 24.0 m | 0 / 0 |

`OBSERVED` — the extreme case is 20 m → 6 m on a warmed salvo, against −50% from an EO director.
`INFERRED` — only the 57mm ever shows the salvo term in this log, so spotting correction is
modelled for the main gun and not for the secondaries here.

**F12 — A catch-all pattern was silently absorbing real records.** `OBSERVED` — the v0.2
`SPECIAL_MSG` pattern ended in `[\w-]+\s*:\s*[^\s]`, intended for CSS declarations inside an
HTML briefing block. It matched **any** line beginning `word:`. Across the corpus it had quietly
swallowed 82 records that belong to four real classes:

| Recovered class | n | What it is |
|---|---|---|
| `IMPACT` — `Weapon: X has impacted Y` | 63 | A round's terminal outcome with no `HIT:`/`MISS:` framing |
| `CONTACT_MANUAL` — `has been manually marked as hostile!` | 16 | Operator ROE action |
| `CONTACT_ATTRIB` — `is the most likely firing unit of …` | 1 | Engine threat attribution |
| `WPN_NOUPDATE` — `is not receiving firm target updates …` | 1 | Midcourse datalink loss |

Only **one** record in the whole corpus was a genuine stylesheet fragment. `SPECIAL_MSG` is now
restricted to real markup and a known CSS-property list, and is no longer last-resort.

`INFERRED` — **the v0.2 claim of "100% coverage" was partly false comfort.** The unmatched
counter was doing its job; a permissive pattern upstream of it was not. The lesson generalises:
a catch-all in an ordered first-match-wins grammar is indistinguishable from a silent drop. Any
future pattern that could match broadly must be narrow by construction, not by position.

**F13 — A log can contain weapon employment and still have zero scored engagements.** `OBSERVED`
— `LCS` holds 413 terminal outcomes and 72 fire records but **not one endgame PH record**.
`INFERRED` — gun fire against a surface ship resolves through the CEP path and never produces a
PH roll; the `ENG_GUN` records in `TB5` are all point-defence engagements against missiles. So
three distinct log shapes now exist, and the page must handle each:

1. **Scored** (`TB5`, `BALTIC`, `LIBDAWN`, `SCS`) — endgame PH records present.
2. **Unguided-only** (`LCS`) — weapons employed, resolved by CEP; accuracy must come from
   terminal outcomes, not PH math.
3. **Detection-only** (`EG`) — no weapon employment at all.

The v0.2 page keyed its degradation on `engagements.length`, so `LCS` incorrectly rendered the
detection panel over a log containing 413 terminal outcomes. Now keyed on weapon employment.

**F14 — God's Eye defeats the visibility premise.** `OBSERVED` — `LCS` carries four
`GOD'S EYE ENABLED/DISABLED` records. `INFERRED` — while it is on, the log is not restricted to
one side's picture, so contact and detection counts in that window are not a measure of what the
side actually knew. The page now says so in the F2 banner whenever the log contains an enable.


**F15 — The database's PoK field *is* the logged base PH, and guns log at exactly two-thirds of
it.** `OBSERVED` — resolving every engagement's weapon by name against `DB3K_518` and comparing
the logged base PH to the weapon's `AirPoK`:

> **265 of 298 match exactly (89%).**

And the 33 that don't are not noise. Every one is a gun, and every one is at precisely ⅔ of the
database value:

| Weapon | logged base-Ph | DB `AirPoK` | ratio |
|---|---|---|---|
| 76mm/62 Super Rapido HE Burst | 3.3% | 5% | 0.667 |
| 57mm/70 Bofors Mk3 GP Burst | 16.7% | 25% | 0.667 |
| 20mm Mk15 Phalanx Blk 1B | 53.3% | 80% | 0.667 |
| AK-630M 30mm/65 Gatling | 46.7% | 70% | 0.667 |
| 27mm MLG-27 Burst | 2.7% | 4% | 0.675 |

`INFERRED` — **guns enter the engagement at two-thirds of their catalog `AirPoK`; guided weapons
enter at 100%.** Exactly one engagement in the corpus mismatches for any other reason (PL-21,
logged 90% vs. DB 95%), which is the DB-version effect of F17. This is a strong validation of the
name join: it is not fuzzy matching, it is reproducing the engine's own input.

**F16 — `TargetSpeedMax` explains the 5% floor.** `OBSERVED` — 27 engagements in the corpus have
a target moving faster than the shooting weapon's declared `TargetSpeedMax`:

| Weapon | `TargetSpeedMax` | fastest engaged | n | Pk | mean final PH |
|---|---|---|---|---|---|
| FN-16 | 950 kt | **3,879 kt** | 9 | 11% | 5.0% |
| FN-6 | 950 kt | 3,872 kt | 5 | 0% | 5.0% |
| SA-16 Gimlet [9M313] | 700 kt | 3,857 kt | 3 | 0% | 5.0% |
| RIM-66M-2 SM-2MR Blk IIIA | 2,901 kt | 3,001 kt | 6 | 0% | 13.3% |
| AA-12 Adder B [R-77-1] | 1,950 kt | 3,796 kt | 2 | 0% | 5.0% |
| AIM-120D AMRAAM P3I.4 | 1,950 kt | 2,898 kt | 2 | 0% | 42.0% |

`INFERRED` — the F8 floor and the F9 MANPADS collapse are the same phenomenon seen from two
sides: these are shots the catalog says the weapon cannot make, and the engine floors them rather
than refusing them. The page now flags every such engagement and lists them separately, because
"0% Pk" is a useless finding while "engaged a target four times its rated speed" is an actionable
one.

**F17 — The join is DB-version sensitive, and the log does not state its version.** `OBSERVED` —
a CMO message log contains no database identifier anywhere. Stress-tested by opening the modern
logs in a dashboard built on `CWDB_517` (the Cold War database): `BALTIC` resolved 2 of 39
weapons, `LIBDAWN` 0 of 44. `INFERRED` — resolution quality is therefore a property of the
*pairing*, not of the log. The page must never present an unresolved weapon as an absent one:
it shows the name as plain text, keeps it in the table, and states the count and the likely cause.
Verified: no errors, no empty tables, all panels render in the mismatched case.


**F18 — The parser was locale-bound, and returned zero records on a valid log.** `OBSERVED` —
CMO writes the timestamp in the machine's regional format. Every log in the v0.4 corpus was
`2/12/2027 10:00:00 AM`; Nikel's are `12-Mar-28 00:00:00`. The shipped regex matched **0 of
142,256 lines** — the feature simply did nothing, with no error a user could act on.

The fix detects the format **once from the whole file**, not per line. Per-line "try them all"
is unsafe here: `3/4/2028` is a valid date under both M/D and D/M and would be silently mis-dated.
Seven formats are recognised; M/D vs D/M is settled by evidence — any day above 12 anywhere in
the file proves the order. `INFERRED` — when nothing settles it (a single-day log, which four of
ours are) ordering is unaffected and only the displayed date could be wrong, so the page shows
the detected format and marks it "assumed".

**F19 — Records are mirrored once per observing side, and a naive dedupe destroys real data.**
`OBSERVED` — in `LUZON` the same event appears as `[RED] …` and `[Civilian] …` with an identical
timestamp and body: **4,253 mirrored records (6%)**. Every count and DP sum doubles.

But the obvious fix is wrong. Collapsing on (timestamp, body) would also destroy **316 records in
`TB5` and 252 in `BALTIC`** — a single side legitimately logs `100% penetration achieved` several
times in one second, and those are separate events. Measured across the corpus:

| Log | same-side repeats (real) | cross-side mirrors (duplicates) |
|---|---|---|
| BALTIC | 252 | 0 |
| TB5 | 316 | 0 |
| LCS | 32 | 0 |
| LUZON | 2,163 | 3,599 |
| WARSAW | 1,083 | 1 |

`INFERRED` — the number of real events is **the largest count any single side reports**, and the
surviving records are that side's. Note also that `WARSAW`'s apparent duplication was almost
entirely same-side repeats: one true mirror in 49,212 records. Mirroring is a property of how
many sides observed the action, not of the log format.

**F20 — Exo-atmospheric BMD, and the hit-to-kill clause that was eating engagements.** `OBSERVED`
— `LUZON` contains SM-3 NTW intercepts, closing §7's last open weapon class:

```
RIM-161E SM-3 NTW Blk IIA #15224 HIT: … base PH of 85%. Intercept angle 70 deg,
tgt 2947 kts, intc 8650 kts. … PH reduced by 1%.Final PH: 84%
Result: 77 - HIT, Hit-To-Kill warhead: Target destroyed outright. .
```

Two things the v0.4 grammar could not handle: the missing space before `Final PH`, and the
warhead clause appended after the result. The pattern required `Result: N - HIT.` with a literal
stop, so **12 scored intercepts were silently dropped**. Now captured, with the warhead note kept
as a field. `INFERRED` — no BMD-specific grammar exists even here; hit-to-kill is a warhead
annotation on the ordinary engagement record.

**F21 — CORRECTION to F5: the engine's comparison is not strict; the displayed PH is rounded.**
The v0.2 corpus had exactly one roll/PH tie, and §5 concluded the engine compares `roll < PH`.
With 4,262 engagements there are now **53 ties, and they split 43 HIT / 10 MISS**. `OBSERVED` —
every final PH in the corpus is an integer (0 of 4,262 are fractional), while intermediate
modifiers are clearly fractional. `INFERRED` — **the logged Final PH is a rounded display of an
unrounded internal value**, so a tie in the displayed numbers is genuinely indeterminate and
neither `<` nor `≤` is the rule.

This does not weaken the parse check, it sharpens it: excluding ties, the invariant holds
**4,209 / 4,209 — 100%**. It does mean the v0.2 claim of a strict comparison was an over-read of
n=1, and is withdrawn.

**F22 — Fifteen record classes added from the new corpus**, the analytically important ones being
loss-cause records: `FUEL_LOSS` (`has run out of fuel and crashed!`) and `ABANDONED`
(`has no functioning engines and is being abandoned`). `OBSERVED` — `WARSAW` has **280 losses to
causes other than enemy fire against 801 destroyed**. Also added: `COMPONENT_HIT`
(`Cockpit hit - penetration N%`), `CREW_INCAP`, `CONTROLS_LOST`, `CABIN_HIT`, `FIRE_OUT`,
`FIRE_WARN`, `REPAIR` / `REPAIRING` / `REPAIR_DONE` (units repair themselves over time),
`CONTACT_PROBABLE` (`New probable missile contact! (Guidance illumination detected)`),
`WPN_NOREFLECT`, `HOSTED`, `FLIGHT_ASSEMBLED`.


**F23 — Absence of a damage record means two different things, and conflating them fabricates
findings.** `OBSERVED` — the overkill measure rests on the engine ceasing to record damage once a
unit is dead or sinking, so an impact with no damage beside it is a round that changed nothing.
The first implementation applied that directly and produced **"100% overkill" for `LCS` and
`LIBDAWN`** — both of which simply contain no damage records at all, because the relevant Message
Log categories were off.

`INFERRED` — a unit with **no damage record anywhere in the log** tells you nothing about whether
its impacts worked. Those impacts are *effect unknown*, never *wasted*. The measure is therefore
computed only over units whose damage is actually logged, and a log with none of them gets a
plain statement that effect cannot be measured, plus the setting to change. Manufacturing an
overkill statistic out of a logging setting is the easiest way this page could lie, and it very
nearly did.

A second correction falls out of the same work. My earlier feasibility note to the author quoted
**93% overkill for `WARSAW`**. That was wrong: it counted only DP records and ignored component
damage, and `WARSAW` logs 890 component-degrade and 415 component-destroyed events. Counting a
destroyed component as proof of effect — which it plainly is — gives **274 measurable impacts,
265 effective, 9 wasted (3%)**. `LUZON` is the genuinely wasteful one and its figure stands.


**F24 — The modifier chain cannot be reconstructed, so the waterfall was not built.** `OBSERVED`
— Phase 3 was scoped around a per-engagement modifier waterfall: base PH, then each term, then
the final. Before drawing it I tested whether the logged terms actually compose into the logged
`Final PH`, across **1,599 unfloored, uncapped missile engagements**:

| Model | median error | within 1 point |
|---|---|---|
| Additive | 2.0 pts | 47% |
| Multiplicative | 2.6 pts | 21% |
| Mixed (multiplicative then additive penalty) | 3.4 pts | 17% |

Even the best model lands within half a point only **25%** of the time. Concrete case
(`RIM-162A ESSM`): base 90, target speed +20, PH reduced by 3 — additive gives 107, the log says
95. Another (`SM-6 Blk IA`): base 90, speed −5, reduced by 37 — additive gives 48, the log says 54.

`INFERRED` — **the engine applies terms it does not print.** A cascade chart showing
base → term → term → final would be a drawing of arithmetic that does not happen, and it would be
convincing precisely because it looks like a derivation. The waterfall is therefore not built, and
will not be unless the missing terms are identified.

What Phase 3 ships instead is the same information without the false precision: the chain
verbatim as the engine wrote it with the residual stated on every card, a modifier table framed
as **association** (final PH with the clause vs. without it) rather than contribution, and the
causal story carried by a scatter of final PH against LOS rate — pure observation, no model.

**F25 — Soft-kill probabilities are printed unrounded, unlike engagement PH.** `OBSERVED` — across
**909 decoy and jammer attempts**, `roll ≤ probability` predicts the outcome in **909 of 909**,
including all 8 exact ties. Contrast F21, where engagement ties split 43/10 because the PH is
rounded for display. `INFERRED` — soft-kill probabilities are whole numbers in the model itself
(they cluster on 5, 10, 15, 20, 25), so nothing is lost to rounding and the tie is decidable.

`OBSERVED` — aggregate calibration is good: mean declared 16.2% against 18.0% realised. Individual
systems diverge — `AN/ALE-70 FOTD` declared 25% and achieved 50.8% over 61 attempts — which is why
the table carries confidence intervals rather than bare rates.


**F26 — Unit names contain commas, and stopping at the first one split units in two.**
`OBSERVED` — the impact-target extractor took everything up to the first comma:
`Has impacted Bridge (Two-Lane, 60 Tons), No other units affected` yielded
`Bridge (Two-Lane`. Because damage records carry the full name, the same bridge appeared as
**two rows** — one with 114 impacts and a measured outcome, one with 27 impacts and
*effect unknown* — and 49 of `WARSAW`'s impacts were orphaned away from their own damage records.

`INFERRED` — a trailing clause is recognisable, an arbitrary comma is not. The extractor now
stops only at a comma that begins a known clause (`, No other units`, `, The explosion`,
`, Has detonated`, `, Has malfunctioned`, `, Will `) or at the end of the record. `WARSAW`'s
measurable impacts rose from 274 to 323 as the orphans rejoined.

Worth noting how this surfaced: it was invisible at the old page width and became obvious the
moment the tables were given the full window. Layout is not only cosmetic — truncation hides
defects.


---

## 7. Not observed — do not assume

**Closed in v0.2:** `LIBDAWN` was supplied as a ballistic/hypersonic engagement log.
`OBSERVED` — it produced **no BMD-specific grammar at all**: the engine scores a Mach-6.8 glide
body through the ordinary `ENG_MISSILE` record with the ordinary modifier vocabulary. `INFERRED`
— no parser work is needed for hypersonic or ballistic intercept; the *analytic* treatment
differs (F9), the grammar does not. Genuine exo-atmospheric BMD (SM-3 / THAAD / GBI class) is
still unobserved and may yet differ.

`SPECULATIVE` — the following are absent from all five logs and their grammars are **unknown**.
The parser will route them to the unmatched counter rather than guess:

- Torpedo engagement and endgame (`EG` is an ASW scenario but no weapon was ever fired)
- Mine detonation / minesweeping
- Submarine-specific engagement lines
- Directed-energy and EMP weapons
- Cyber / GPS-jamming effects
- Air-to-air gun employment
- Torpedo CEP/PoH fire records (the CEP path is confirmed only for guns)
- Aerial refuelling, and the `Air Operations` / `Docking Operations` categories generally

`INFERRED` — none of these block Phase 1. They are additive patterns, and the unmatched counter
is what will surface them when you play a scenario that produces them.

---

## 8. Recommended Message Log profile

`INFERRED` — mapping from the Options → Message Log categories to the record classes above. This
is inference from category names plus the observed deltas between your four logs; I have not
tested each toggle in isolation.

**Required — the feature does not work without these:**

| Category | Feeds |
|---|---|
| Weapon Endgame Calculations | `ENG_MISSILE`, `ENG_GUN` — the entire accuracy analysis |
| Unguided Weapon Accuracy Modifiers | `FIRE_UNGUIDED` — gun PoH chain |
| Weapon Damage | `DMG_DP`, `DMG_COMP_*` |
| Unit Damage | damage chain, sinking |
| Unit Lost | `DESTROYED` |
| Point Defence | soft-kill and CIWS engagement context |

**Recommended on:** Contact change + the New *Contact* family (detection & tracking view,
classification latency); Comms-related Message (cheap, and it is the whole story in an `EG`-type
log); Special Messages (narrative timeline markers).

**Recommended off:**

| Category | Why |
|---|---|
| Unit AI | Already off. 310 of 326 `WPN_LOGIC` records came from it. |
| Scenario Events | 959 records — **24% of the entire corpus** — with zero analytic content. |
| Debug | Currently **on**. No analytic value; adds volume. |
| User Interface | Currently **on**. Records your clicks, not the battle. |
| Doctrine & ROE, Air Ops, Docking Ops | Currently off; leave off for now. Revisit if you want sortie-generation analysis later. |

`INFERRED` — adopting this profile would have cut the 4,004-record corpus to roughly 2,700
records with **no loss** of any Tier 1 or Tier 2 content.

---

## 9. Phase 1 — BUILT (2026-09-13)

Delivered in `cmo_db_dashboard.template.html`:

1. **Parser** implementing §3 in JavaScript. `OBSERVED` — cross-checked against
   `log_grammar_probe.py` class-by-class across all five logs: **identical counts in every
   class in every log**, 4,731 records, 0 unmatched. The §5 strict-comparison rule and the
   F8 5% floor are both encoded (`floored` flag on every engagement).
2. **Ingest** reusing the Scenario ORBAT plumbing — paste box + file chooser, `localStorage`
   persistence. **One log at a time: a new ingest replaces the previous one.**
3. **Export** — JSON (complete parsed structure, **re-importable**, round-trip verified
   identical), plus engagements and terminal-outcome CSVs. Export is how a log is kept.
4. **Overview page** — visibility banner (F2), KPI row carrying both F5 denominators
   (weapons-to-endgame vs. scored engagements), activity timeline, terminal-outcome
   breakdown, record-class table by tier, and a live unmatched counter.
5. **Graceful degradation (F3)** — a log with no weapon employment renders a Detection &
   Tracking panel instead of empty accuracy charts, and the CSV exports disable themselves.

Two defects were found and fixed by the verification pass, both invisible to a casual look:
the activity timeline drew only typed-payload records (so a detection-only log charted
nothing), and the terminal-mode classifier's `Impacts? surface` never matched the actual
string `Impacted surface`, silently dumping 40 records into "other". All 602 terminal records
across the corpus now classify into a named mode, with zero "other".

## 9b. Phase 2 — BUILT (2026-09-13)

The AAR page gains a tab strip — **Overview · Weapons · Denied** — and a DB join.

1. **Name resolution.** Every log weapon and target name is resolved against the loaded catalog.
   `OBSERVED` — on `DB3K_518`: **62 of 63 weapon names (98%)** and **26 of 27 target names (96%)**.
   Targets arrive in two shapes (`SS-N-33 [3M22 Zircon]`, and instance form
   `STRIX #1 (Su-35K Flanker E)`); both are handled.
2. **Weapon performance table** — n, hits, Pk with a **Wilson 95% confidence interval**, logged
   base PH, DB `AirPoK` (with the ⅔ gun rule applied and shown), mean final PH, erosion, and
   flags. Rates below n=5 are dimmed and excluded from ranking. Every weapon links to its
   catalog card.
3. **Per-target-class expansion (F9)** — each row expands to target class × speed band.
4. **Performance by target speed** — pooled across weapons so it stays readable where per-weapon
   cells are too thin, with mean LOS rate per band: the F9 mechanism, visible.
5. **Beyond declared envelope (F16)** — every overspeed engagement, with the weapon's rated
   `TargetSpeedMax` against the fastest target it actually engaged.
6. **Denied engagements (F10)** — refusals grouped by weapon and shooter with the engine's stated
   reason and the observed range of the quantified values.
7. **Weapons CSV** — the fully joined per-engagement table, 20 columns.

Verified across all six logs on `DB3K_518` and again on `CWDB_517` as a deliberate
wrong-database stress test: no console errors, no empty tables, no 420px overflow, correct
empty-state on the two logs with no scored engagements. One real defect found and fixed in the
process — the new tables overflowed at phone width because a flex row in the speed-band panel
could not wrap.

## 9c. Phase 5 — BUILT (2026-09-14)

Answers the four requests from forum user Nikel. A fourth tab, **Losses**.

1. **Kill attribution, both directions.** `OBSERVED` — the impact record names weapon and target
   together, so no join is needed: 100% of `WARSAW`'s hits and 99% of `TB5`'s carry a named
   target (83% in `LUZON`, the rest being impacts on terrain). Each unit row expands to the
   weapons that struck it; the weapon table gives the reverse.
2. **Losses by cause.** `OBSERVED` — `WARSAW`: 136 units lost, of which **77 (57%) were not to
   enemy fire** (51 out of fuel, 26 abandoned with engines lost). `LUZON`: 119 lost, 8 not to
   enemy fire. This is the out-of-comms fuel bug Nikel describes, quantified.
3. **Overkill.** `OBSERVED` — `LUZON`: **184 measurable impacts, 38 did damage, 146 changed
   nothing — 79%**. Per hull, `AAW Escort 3 #PVJR` absorbed 26 JSM impacts, 6 of which did
   anything, and sank. Reproduced independently by `log_grammar_probe.py`: identical 184 / 38 /
   146. Gated per F23.
4. **Weapon effect** — the same measure from the firing end: impacts, effective, wasted, units
   hit, units lost.

Plus an **Effects CSV** carrying a `damage_logged` column so the unknown cases stay visibly
distinct in the export.

A second defect was found and fixed during verification: the Overview KPI read
**"112% reached a PH roll"** on `LUZON`. Scored engagements and terminal records are two
different record classes, not a subset relationship — a weapon can be scored without producing a
separate terminal record — so the ratio is now stated only when it is actually a ratio.

## 9d. Phase 3 — BUILT (2026-09-14)

A fifth tab, **Mechanics**. Scoped as a modifier waterfall; shipped as something else, for the
reason in F24.

1. **Probability against crossing rate** — every scored engagement plotted as final PH against
   the logged LOS rate, log x-axis, hits and misses distinguished by shape as well as colour.
   This is the F9 mechanism as observation rather than as a claim.
2. **Modifier incidence** — each clause with how often it appears, its mean value, and the mean
   final PH and Pk of engagements carrying it against those that do not. Labelled association,
   not contribution, on the card itself.
3. **Engagement chains** — two worked examples per log (largest probability loss, highest
   crossing rate), showing the engine's clauses verbatim with the additive residual stated. Floored
   engagements are excluded from the examples because they show the clamp rather than the
   mechanism.
4. **Soft kill** — attempts, mean declared probability, realised rate, and a per-system table with
   Wilson intervals (F25).

Verification caught one layout defect: a fifth tab pushed the tab strip past phone width, which
it could not wrap.

## 9e. Phase 4 — BUILT (2026-09-14)

A sixth tab, **ORBAT**. The requirement was that the scenario ORBAT and the log keep working
independently as well as together, so:

- **Independent by construction.** Separate ingest, separate storage keys, separate pages. Each
  renders fully with the other absent. Verified: all eight logs across all six tabs with no
  scenario loaded; the Scenario ORBAT page with no log loaded; and clearing either one leaves the
  other intact.
- **The ORBAT tab is inert without both.** With no snapshot it explains what the join would add
  and links to the ingest page, rather than erroring or showing empty tables. A dot on the tab
  marks when a snapshot is loaded and the cross-reference is live.

What the join produces:

1. **Damage against capacity** — the log has damage points taken, the ORBAT has each unit's DBID,
   the catalog has that class's `DamagePoints`. Only all three together turn "took 754 DP" into
   "took 140% of what it could absorb". This closes Nikel's remaining request.
2. **Expenditure against inventory** — rounds seen reaching an endgame against the quantity held
   across the snapshot, with the point-in-time caveat stated on the card.
3. **Losses against the roster** — per side, how much of the snapshot's force appears in the log
   as destroyed or sinking.
4. **ORBAT x-ref CSV.**

A match-rate line reports how many of the log's units were found in the snapshot, and a warning
fires below 50% — the usual cause being a snapshot from a different scenario or taken too late.

`SPECULATIVE` — **this was verified with a synthetic ORBAT generated from the log's own unit
names**, which exercises the join mechanics (151/151 matched, 109 resolving a catalog capacity)
but proves nothing about real exporter output. A run of `cmo_orbat_export.lua` on a real scenario
alongside its log is the outstanding test.

### UI pass (same release)

- The AAR pages were inheriting the 1,000px cap from the Scenario ORBAT layout and used about
  half a maximised window. They now run to 1,600px, with prose held at a readable measure.
- **Weapon effect** had the unknown count crammed into the wasted column as `9 +23?`, which
  broke the numeric alignment. Unknown is now its own column.

---

## 10. Original Phase 1 scope (as approved)

On your sign-off of this grammar:

1. **Parser** implementing §3, with the §5 strict-comparison rule and a visible unmatched counter.
2. **Ingest** reusing the Scenario ORBAT plumbing verbatim — paste box primary, file upload
   secondary, `localStorage` persistence. No new `.exe` mode, no change to distribution.
3. **Overview page** — timeline, record-class totals, sides observed, engagement/expenditure
   counts, and the graceful-degradation path from F3.

Explicitly **not** in Phase 1: the weapon performance table (Phase 2), the modifier waterfall
(Phase 3), and the ORBAT cross-join (Phase 4). Each gets its own gate.

**Resolved (v0.2):** one log at a time. Multi-log corpus is deferred and is no longer assumed by
any phase. `INFERRED` — this makes F4 (small-n) and F9 (segment by target class) more acute, not
less: within a single log, per-weapon-per-target-class cells will frequently be n < 5. The UI
must therefore lead with the modifier chain and the *reasons* for PH erosion, which are readable
at n = 1, and treat aggregate Pk as the secondary number. That is a change in emphasis from
v0.1 and it simplifies Phase 2.
