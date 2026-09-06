# CMO Database Dashboard — Feature & Guidance Glossary

This is the complete reference behind the dashboard's **Feature glossary** page — every sensor capability, feature code, weapon-guidance method, target class and sensor/weapon type explained (251 entries). It is also browsable inside the dashboard itself (**Reference → Feature glossary**), where you can hover any chip for the short version or click it for the full entry.

Explanations are paraphrased from the *Command: Modern Operations* manual where it covers a term (page-cited); they are **not** verbatim — this is our own commentary, not game data. Each entry is epistemically tagged: **OBSERVED** = stated in the manual or directly observed; **INFERRED** = standard real-world/behavioural meaning, not spelled out in the manual; **SPECULATIVE** = uncertain how the engine models it.

## Weapon guidance methods

| Term | Requires | In game | Tag | Source |
|---|---|---|---|---|
| **No guidance — the weapon follows a ballistic path after release or launch.** | Nothing; accuracy comes from the delivery platform’s aim and ballistics. | No guidance — the weapon follows a ballistic path after release or launch. Dumb bombs, rockets and gun rounds. Hit chance depends on range, delivery profile and the platform’s fire-control quality. | OBSERVED | Manual p.287 |
| **Inertial guidance** | Target coordinates at launch. | the weapon flies to a pre-set coordinate using only its own internal navigation, with no outside input after launch. Fire-and-forget against fixed points. Accuracy ranges from crude (early ballistic missiles) to very precise; it cannot chase a moving target unless paired with a terminal seeker. | OBSERVED | Manual p.288 |
| **Inertial navigation corrected by satellite positioning (GPS/GLONASS/BeiDou) for tight accuracy against fixed coordinates; often a backup or aid to another mode.** | Target coordinates at launch (and, realistically, satellite availability). | Inertial navigation corrected by satellite positioning (GPS/GLONASS/BeiDou) for tight accuracy against fixed coordinates; often a backup or aid to another mode. Precise strike on fixed or surveyed locations. Example: the AGM-88E AARGM falls back to GPS + active radar if the target radar it was homing on shuts down. | OBSERVED | Manual p.291; INFERRED that CMO does not model GPS jamming degradation unless a scenario sets it |
| **Electro-optical guidance** | Enough daylight/clarity for the seeker to see the target, and a lock (some are lock-on-before-launch). | the weapon homes on a visual image of the target. Ranges from crude early trackers (GBU-8 HOBOS) to imaging seekers that can even act as makeshift sensors in their own right. | OBSERVED | Manual p.288 |
| **Infrared guidance** | Sufficient IR contrast; older seekers are aspect-limited. | the weapon homes on the target’s heat signature. Three classes — stern-chase (must sit directly behind, e.g. AIM-9B), rear-aspect (behind but more flexible, e.g. AIM-9H), and all-aspect (any angle, off-boresight with a helmet sight, e.g. AIM-9L+). | OBSERVED | Manual p.288, 294 |
| **Active radar homing** | Nothing from the shooter after the seeker is active; it can be datalinked or CEC-cued mid-course. | the missile’s own radar finds and tracks the target, going autonomous once the seeker locks. Launch-and-leave — the shooter can turn cold or engage other targets. Modern datalinked active-radar missiles can be launched from long range. | OBSERVED | Manual p.294 |
| **Semi-active radar homing** | The shooter (or a supporting platform) to keep its fire-control radar locked on the target for the whole flight. | the missile rides radar energy reflected off a target that a radar is actively “painting.” It carries no radar of its own. Break the lock — the shooter turns away, or the target masks behind terrain — and the missile loses control. Early SARH also ties up the shooter’s radar so it can’t search or engage anything else while guiding. | OBSERVED | Manual p.288, 294 |
| **Track-via-missile** | The guidance radar to keep tracking both the target and the missile. | the missile relays its seeker returns to a ground/ship radar that computes the intercept and commands the missile — a SARH variant used by systems such as Patriot. Ties the engagement to the controlling radar much like SARH; losing that track breaks guidance. | INFERRED | Standard TVM behavior; not detailed by name in the manual |
| **Anti-radiation (passive) homing** | The target radar to be emitting. | the weapon homes passively on a radar’s own emissions. A SEAD weapon — an emitter that shuts down denies a basic ARM its source. Advanced ARMs (e.g. AARGM) fall back to GPS/INS and active radar to keep going. | OBSERVED | Manual p.291 |
| **Semi-active laser (laser-guided)** | Something to paint the target — the launching aircraft, a buddy platform, or a ground designator — with line of sight to the target through weapon impact. | the weapon homes on laser energy reflected from a target being lased by a designator. The classic laser-guided bomb; lose the designation and it misses. Loadouts needing an external lasing platform are flagged in the database (RequiresBuddyIllumination). | OBSERVED | Manual p.288 |
| **Torpedo terminal homing** | For wire-guided runs, the guidance wire must stay intact — hard turns or speed over ~10 kt snaps it, after which the torpedo goes autonomous on its terminal seeker. | traditional active/passive sonar guidance, or wake-homing that follows a ship’s wake. Sonar homing is considerably easier to decoy than wake-homing. | OBSERVED | Manual p.291 |
| **Terrain contour matching** | Pre-loaded terrain/route data; works over land with usable relief. | a cruise missile compares the ground profile it overflies against stored maps to fix its position en route. Flagged as the TERCOM weapon code; supports precise low-level cruise navigation to a fixed target. | INFERRED | Standard TERCOM; not detailed by name in the manual |

## Sensor capabilities — what a sensor searches for or measures

| Term | Requires | In game | Tag | Source |
|---|---|---|---|---|
| **Air search** | — | the sensor detects airborne targets — aircraft, helicopters and missiles. Contributes to the air picture; most fire-control and air-search radars carry it. | OBSERVED | Manual §9.1.1 (p.281) |
| **Surface search** | — | detects ships and boats on the sea surface. | OBSERVED | Manual §9.1.1 |
| **Submarine search** | — | detects submerged submarines (sonar, MAD). | OBSERVED | Manual §9.1.1 |
| **Land search – fixed facility** | — | detects fixed ground installations (buildings, SAM sites, radars). | OBSERVED | Manual §9.1.1 |
| **Land search – mobile unit** | — | detects moving or relocatable ground units (vehicles, mobile launchers). Usually needs a moving-target capability to pull these out of ground clutter. | OBSERVED | Manual §9.1.1 |
| **Periscope search** | — | picks out submarine periscopes and masts — very small returns against sea clutter. | OBSERVED | Manual §9.1.1 |
| **C-RAM** | — | detects incoming rockets, artillery and mortar rounds. Cues very-short-range defences against ballistic sub-munitions. | OBSERVED | Manual §9.1.1 |
| **Space search (ABM)** | — | detects targets at ballistic-missile / space altitudes. Needed to see and cue against ballistic-missile threats. | OBSERVED | Manual §9.1.1 |
| **Mine & obstacle search** | — | detects sea mines and underwater obstacles. | OBSERVED | Manual §9.1.1 |
| **Torpedo warning** | — | detects incoming torpedoes. Triggers evasion and countermeasures. | OBSERVED | Manual §9.1.1 |
| **Missile approach warning** | — | detects incoming missiles (MAWS). Cues last-ditch defensive maneuver and countermeasures. | OBSERVED | Manual §9.1.1 |
| **Range information** | — | the sensor can measure a contact’s range, not just its bearing. Sensors that measure more of range/altitude/speed/heading build a fuller, more actionable track; a bearing-only sensor can’t form a firing solution by itself. | OBSERVED | Manual §9.1.1 |
| **Altitude information** | — | the sensor can measure a contact’s altitude (a 3D sensor). Needed for a complete air track and for altitude-dependent engagements. | OBSERVED | Manual §9.1.1 |
| **Speed information** | — | the sensor can measure a contact’s speed. | OBSERVED | Manual §9.1.1 |
| **Heading information** | — | the sensor can measure a contact’s course/heading. | OBSERVED | Manual §9.1.1 |
| **Navigation only** | — | a radar limited to navigation — it does not detect or track combat targets. Purely a flying aid; contributes nothing to the tactical picture. | OBSERVED | Manual §9.1.1 |
| **Ground mapping only** | — | produces a ground map for navigation/bombing but does not track combat targets. | OBSERVED | Manual §9.1.1 |
| **Terrain avoidance / following only** | — | supports low-level flight, not target detection. | OBSERVED | Manual §9.1.1 |
| **Weather only** | — | a weather radar; no combat detection role. | OBSERVED | Manual §9.1.1 |
| **Weather and navigation only** | — | combined weather/nav radar; no combat detection role. | OBSERVED | Manual §9.1.1 |
| **Over-the-horizon backscatter (OTH-B)** | — | bounces HF energy off the ionosphere to see far beyond the horizon. Enormous detection range but imprecise — an early-warning cue, not a fire-control track. | OBSERVED | Manual §9.1.1 / OTH discussion |
| **Over-the-horizon surface wave (OTH-SW)** | — | follows the sea surface to detect low targets beyond the horizon. Long-range early warning with limited precision. | INFERRED | Standard OTH-SW; not detailed by name in the manual |
| **Time-Difference-of-Arrival (TDOA)** | — | passively fixes an emitter’s position from timing differences across receivers. How networked ESM turns bearings into a position fix. | INFERRED | Standard TDOA; manual notes ESM triangulation p.284 |
| **Direction finding (DF)** | — | passively measures the bearing to an emitter. A single DF sensor gives a bearing line; multiple/ networked ESM triangulate to a fix. | OBSERVED | Manual p.284 |

## Sensor features & modes

| Term | Requires | In game | Tag | Source |
|---|---|---|---|---|
| **Identification Friend or Foe (IFF)** | — | interrogates transponders to sort friendly contacts from unknown/hostile. Helps resolve a contact’s side quickly so you can decide to engage. | OBSERVED | Manual p.283–284 |
| **Classification / Brilliant Weapon** | — | the sensor can classify a contact’s type or class; on a weapon seeker it enables autonomous target acquisition. Turns a raw contact into a typed track; “brilliant” weapons can pick their own target. | OBSERVED | Manual p.283 |
| **NCTR – Jet Engine Modulation** | — | identifies an aircraft type from the radar return off its spinning engine blades. IDs enemy aircraft flying head-on without cooperative IFF (e.g. F-15C/APG-70). | OBSERVED | Manual p.283 |
| **NCTR – Narrow-Beam Interleaved Search & Track (NBILST)** | — | an advanced NCTR that positively identifies aerial targets from any angle. Any-aspect positive ID (e.g. F-22/APG-77) — no need to be head-on. | OBSERVED | Manual p.283 |
| **Continuous tracking capability** | — | the sensor can hold a dedicated, continuous track on a target rather than only intermittent search hits. Required to keep a firm track that can support an engagement. | OBSERVED | Manual p.282 |
| **Continuous tracking (target-tracking radar)** | — | a dedicated tracking radar variant of the above. | OBSERVED | Manual p.282 |
| **Continuous tracking (visual)** | — | an optical sensor able to hold a continuous track on a target. | INFERRED | Optical tracking; manual optical section p.284 |
| **Periscope search – basic** | — | early ability to detect periscopes/masts against sea clutter. | OBSERVED | Manual §9.1.1 |
| **Periscope/surface search – fine range resolution + rapid scan (1980+)** | — | better clutter rejection and revisit for spotting small masts. | INFERRED | Era-gated capability flag; manual sensor section |
| **Periscope/surface search – advanced processing (2000+)** | — | modern processing further improves small-contact detection. | INFERRED | Era-gated capability flag |
| **Track-while-scan (TWS)** | — | the radar tracks multiple targets while still scanning, instead of committing to a single painted target. Without TWS a radar “can either guide missiles to its painted target or search for contacts, but not both.” TWS lets it do both and cue active-radar missiles on several targets. | OBSERVED | Manual p.282 |
| **Moving Target Indicator (MTI)** | — | filters out stationary ground clutter to reveal moving targets. Lets a radar pull moving vehicles/aircraft out of the ground return. | OBSERVED | Manual p.282–283 |
| **Low Probability of Intercept (LPI)** | — | the radar shapes its waveform/emissions to be hard for an enemy ESM/RWR to detect. Harder for passive receivers to notice the emitter and get a bearing — you can search while staying quieter. | INFERRED | LPI standard; manual emission-management discussion pp.282–284 |
| **Night-capable optics (LLTV / NVG / CCD / searchlight)** | — | the electro-optical sensor can see in low light or darkness. Extends passive visual ID/tracking into night conditions. | OBSERVED | Manual optical section p.284 |
| **Pulse-only radar** | — | a basic radar with no doppler processing. Cannot reliably look down against ground clutter, but is immune to doppler-notching evasion (there is no velocity gate to hide in). | OBSERVED | Manual p.283, 417 |
| **Pulse-Doppler, full look-down/shoot-down (LDSD)** | — | uses doppler to separate moving targets from ground clutter. Can detect and engage low-flying or terrain-following targets from above. | OBSERVED | Manual p.282–283 |
| **Pulse-Doppler, limited LDSD** | — | partial look-down/shoot-down capability against clutter. | INFERRED | Graded LDSD flag; manual p.283 |
| **Passive Electronically Scanned Array (PESA)** | — | a phased array that steers its beam electronically from a single feed. Fast beam steering and (per the model) assumed frequency-agile, so jam- and notch-resistant. | OBSERVED | Manual p.417 |
| **Active Electronically Scanned Array (AESA)** | — | a phased array of many transmit/receive modules steering the beam electronically. Frequency-agile (jam-resistant), makes doppler-notching “pointless,” and holds very precise tracks that are hard to break — but its strongest detection is in the center lobe, so edges are weaker. | OBSERVED | Manual p.283, 417 |
| **Can classify ground targets (SAR)** | — | synthetic-aperture radar images the ground finely enough to classify what it sees. Turns a ground return into an identifiable target. | OBSERVED | Manual sensor section |
| **Continuous-wave illumination** | A continuous line of sight on the target — while illuminating, the radar cannot engage others. | the radar paints a target with a continuous beam to guide a semi-active (SARH) missile. Ties up the illuminating radar for the whole SARH engagement. | OBSERVED | Manual p.282 |
| **Interrupted continuous-wave illumination** | — | time-shares the illuminating beam so one radar can support more than one SARH engagement. Eases the “one target at a time” limit of pure CW illumination. | INFERRED | ICWI standard; manual illumination discussion p.282 |
| **Weapon fire-control radar (no CW illumination)** | — | provides the fire-control track without needing continuous-wave illumination — e.g. for active-radar or track-via-missile weapons. Supports engagements without tying the radar to a single painted target. | INFERRED | Derived from CW/illumination model p.282 |
| **Frequency agile** | — | the radar hops operating frequency. More resistant to noise jamming and significantly less affected by doppler-notching. All PESA/AESA radars are assumed frequency-agile. | OBSERVED | Manual p.282, 417 |
| **Cognitive EW** | — | adaptive, software-defined EW that senses the threat environment and changes technique on the fly. Represents modern reactive jamming/ECCM; strongest against fixed, known techniques. | SPECULATIVE | Modern capability; not detailed in the manual |
| **Generates AAW fire-control data** | — | the sensor produces a track good enough to direct anti-air weapons. Marks a radar that can actually cue a SAM/AAW engagement, not just search. | INFERRED | Fire-control role; manual p.282 |
| **Shallow-water capable (partial)** | — | the sonar still functions, with reduced performance, in littoral/shallow water. Less degraded than a blue-water-only sonar in the shallows. | INFERRED | Littoral sonar limits discussed p.300 |
| **Shallow-water capable (full)** | — | the sonar is designed for effective shallow-water/littoral operation. Retains classification/detection where deep-water sonars struggle. | INFERRED | Littoral sonar limits discussed p.300 |

## Sensor types

| Term | Requires | In game | Tag | Source |
|---|---|---|---|---|
| **Radar** | — | active radio-frequency sensor — emits and listens for the echo, so it can be detected by ESM. | OBSERVED | Manual p.281 |
| **Semi-active** | — | a seeker that homes on radar energy reflected off a target another radar is illuminating (SARH). | OBSERVED | Manual p.288 |
| **Visual** | — | a passive electro-optical/visual sensor — sees but does not emit, and can confirm identity. | OBSERVED | Manual p.284 |
| **Infrared** | — | a passive sensor that detects heat; strong against hot targets, no emission of its own. | OBSERVED | Manual p.284 |
| **Track-via-missile (TVM)** | — | a guidance sensor where the missile relays returns to a ground/ship radar that commands it. | INFERRED | Sensor type |
| **Terminal semi-active** | — | a semi-active seeker that goes active only in the terminal phase of flight. | INFERRED | Sensor type |
| **ESM** | — | Electronic Support Measures — passively detects and classifies emitters (radars, jammers) without emitting. | OBSERVED | Manual p.284 |
| **ECM** | — | Electronic Countermeasures — an active jammer that degrades enemy radars. | OBSERVED | Manual (EW) |
| **EMP projector** | — | a directed electromagnetic-pulse effector. | SPECULATIVE | Sensor type; not detailed in the manual |
| **Passive Coherent Location** | — | detects targets passively using reflections of ambient RF (e.g. broadcast/GSM), with no emission of its own. | INFERRED | Sensor type |
| **Laser designator** | — | paints a target with a laser for semi-active laser-guided weapons. | OBSERVED | Manual p.288–289 |
| **Laser spot tracker (LST)** | — | detects and tracks a laser spot placed on a target by a designator. | INFERRED | Sensor type |
| **Laser rangefinder** | — | measures precise range to a target with a laser pulse. | OBSERVED | Sensor type |
| **LIDAR** | — | laser-based detection/imaging. | INFERRED | Sensor type |
| **Hull sonar, passive-only** | — | hull-mounted sonar that only listens — quiet, gives bearing but not range on its own. | OBSERVED | Manual sonar section |
| **Hull sonar, active/passive** | — | hull sonar that can ping for range or listen passively. | OBSERVED | Manual sonar section |
| **Hull sonar, active-only** | — | hull sonar that only pings. | INFERRED | Sensor type |
| **Bow sonar, active/passive** | — | bow-mounted active/passive sonar. | INFERRED | Sensor type |
| **Towed array (TASS), passive-only** | — | a long towed hydrophone array — very sensitive at low frequency and very quiet, but degraded when the ship maneuvers or speeds up. | OBSERVED | Manual sonar section |
| **Towed array (TASS), active/passive** | — | a towed array that can also ping. | INFERRED | Sensor type |
| **Towed array (TASS), active** | — | an active towed array. | INFERRED | Sensor type |
| **Variable-depth sonar (VDS), passive-only** | — | a sonar body lowered on a cable to listen below the thermocline. | OBSERVED | Manual p.300 (thermal layers) |
| **Variable-depth sonar (VDS), active/passive** | — | a lowered sonar that can ping or listen below the layer. | INFERRED | Sensor type |
| **Variable-depth sonar (VDS), active-only** | — | a lowered active sonar. | INFERRED | Sensor type |
| **Dipping sonar, passive-only** | — | a sonar a helicopter lowers into the water while hovering, then listens. | OBSERVED | Sensor type |
| **Dipping sonar, active/passive** | — | a helicopter dipping sonar that can ping or listen. | OBSERVED | Sensor type |
| **Dipping sonar, active-only** | — | a helicopter dipping sonar that pings. | INFERRED | Sensor type |
| **Bottom-fixed sonar, passive-only** | — | a seabed hydrophone array (SOSUS-style) that listens over long ranges. | INFERRED | Sensor type |
| **MAD** | — | Magnetic Anomaly Detector — senses the magnetic disturbance of a submerged submarine at very short range; used to confirm and pinpoint a contact, not to search widely. | OBSERVED | ASW sensor type |
| **Wake detector** | — | senses a ship’s wake (supports wake-homing torpedoes). | INFERRED | Sensor type |
| **Acoustic intercept** | — | warns the platform when it is being pinged by an active sonar (a sonar RWR). | OBSERVED | Sensor type |
| **Mine sweep – mechanical cable cutter** | — | tows cutters to sever moored-mine cables so they float up. | OBSERVED | MCM type |
| **Mine sweep – magnetic influence** | — | drags a magnetic field to trigger magnetic-fuzed mines at a safe distance. | OBSERVED | MCM type |
| **Mine sweep – acoustic influence** | — | radiates noise to trigger acoustic-fuzed mines. | OBSERVED | MCM type |
| **Mine sweep – magnetic & acoustic multi-influence** | — | combined magnetic and acoustic sweep. | INFERRED | MCM type |
| **Mine sweep – two-ship magnetic influence** | — | two ships tow a shared magnetic sweep. | INFERRED | MCM type |
| **Mine neutralization – moored-mine cable cutter** | — | cuts individual moored mines. | INFERRED | MCM type |
| **Mine neutralization – explosive charge disposal** | — | destroys a located mine with a charge (often via ROV). | INFERRED | MCM type |
| **Mine neutralization – diver-deployed charge** | — | a clearance diver places a charge on the mine. | INFERRED | MCM type |
| **Microwave emitter** | — | a directed high-power microwave effector. | INFERRED | Sensor type |
| **Non-detecting emitter** | — | an emitter with no detection function (a beacon/illuminator placeholder). | INFERRED | Sensor type |
| **Sensor group** | — | a container that bundles several sensors so a platform fits them as one item. | OBSERVED | Database structure |

## Weapon features & guidance / employment codes

| Term | Requires | In game | Tag | Source |
|---|---|---|---|---|
| **Illuminate at launch** | Fire-control illumination at release (SARH). | the launching platform must illuminate (paint) the target at the moment of launch. | OBSERVED | Manual p.288 |
| **Terminal illumination** | The guiding radar to keep painting the target into impact (SARH). | the target must be illuminated during the missile’s terminal/homing phase. | OBSERVED | Manual p.282, 288 |
| **Supports buddy illumination** | — | a platform other than the launcher can lase/illuminate the target. “Buddy lasing” — one unit designates while another launches or drops from farther away. | OBSERVED | Manual p.289 |
| **Home On Jam (HOJ)** | — | if a target jams the seeker, the missile homes on the jamming source itself. Turns enemy self-protection jamming into a beacon to home on. | INFERRED | Standard HOJ; not named in the manual |
| **Anti-air stern chase** | — | can only engage an air target from directly behind (earliest IR). | OBSERVED | Manual p.288 |
| **Anti-air rear-aspect** | — | engages from behind, more flexibly than a stern-chase weapon. | OBSERVED | Manual p.288 |
| **Anti-air all-aspect** | — | can engage an air target from any angle, not just from behind. | OBSERVED | Manual p.288, 294 |
| **Anti-air dogfight (high off-boresight)** | — | can be launched at large angles off the nose, cued by a helmet-mounted sight. | OBSERVED | Manual p.294 |
| **No diving-target modifier** | — | the usual accuracy penalty against steeply diving targets does not apply to this weapon. | INFERRED | Modeling flag; not detailed in the manual |
| **Capable vs sea-skimmer** | — | can engage very low, sea-skimming targets such as anti-ship missiles. Needed to intercept pop-up, wave-top threats that other weapons miss. | OBSERVED | Manual p.316 |
| **ARH AAW – no HQ track required** | — | an active-radar air-to-air missile that can be launched without a high-quality track from the shooter. The seeker finds the target itself — supports snap/BOL shots. | INFERRED | Active-radar model p.289, 294 |
| **C-RAM capable** | — | can intercept rockets, artillery and mortar rounds. | OBSERVED | Manual §9.1.1 |
| **Lock-on-after-launch (LOAL), CEC-capable** | — | fired without a precise lock, and guidable via Cooperative Engagement by a platform other than the launcher. A third party can hand off/guide the shot; the shooter can stay silent or turn away. | OBSERVED | Manual p.58, 294, 383 |
| **Flight profile – terrain following** | — | flies low, hugging the terrain, to penetrate under radar coverage. | OBSERVED | Manual p.42, 190 |
| **Lock-on-after-launch (LOAL)** | A target point/area; tight cross-range but relaxed downrange tolerance. | fired without a precise lock; the seeker acquires the target after launch. | OBSERVED | Manual p.58 |
| **Launcher occupied during guidance** | — | the launcher/illuminator is tied up guiding this weapon and cannot act elsewhere until it completes. Like classic SARH — one such engagement at a time. | OBSERVED | Manual p.282 |
| **ARM target memory** | — | the anti-radiation missile remembers a radar’s last known position and continues to it if the emitter shuts down. Switching the radar off no longer fully defeats the shot. | OBSERVED | Manual p.291 |
| **Loiter capability** | — | can orbit/wait over an area for a target before attacking. | INFERRED | Loitering-munition behavior |
| **Loiter capability (parachute)** | — | loiters under a parachute, e.g. a sensor-fuzed submunition. | INFERRED | Submunition behavior |
| **Search pattern** | — | runs a programmed search pattern to find its target (e.g. a torpedo or loitering weapon). | INFERRED | Weapon behavior flag |
| **Drive-through logic** | — | presses on through the target area under a defined logic if it does not immediately acquire. | INFERRED | Weapon behavior flag |
| **Bearing-only launch (BOL)** | — | fire a guided weapon without designating a target — designate a point/bearing where the seeker activates to hunt. Lets you shoot at a suspected location and let the seeker sort it out. | OBSERVED | Manual p.75 |
| **Depressed ballistic trajectory** | — | a flattened, lower ballistic arc (Iskander, ATACMS) — faster to target and harder to intercept than a lofted arc. | INFERRED | Trajectory flag; ballistic modeling p.287 |
| **Ballistic trajectory** | — | flies a ballistic arc (ballistic missiles, GMLRS). | OBSERVED | Manual p.287 |
| **Multi-stage missile** | — | has multiple propulsion stages (e.g. a booster plus a sustainer/second stage). | INFERRED | Propulsion flag |
| **Pod – terrain avoidance (land 300 ft / sea 200 ft)** | — | a targeting/navigation pod that enables terrain-avoidance flight down to the listed floor. | OBSERVED | Manual (label) |
| **Pod – terrain following (land 200 ft / sea 100 ft)** | — | a pod that enables lower terrain-following flight. | OBSERVED | Manual (label) |
| **Pod – day-only navigation** | — | a navigation pod usable only in daylight. | OBSERVED | Manual (label) |
| **Pod – day-only navigation/attack** | — | a nav-and-attack pod, daylight only. | OBSERVED | Manual (label) |
| **Pod – night navigation** | — | a night-capable navigation pod. | OBSERVED | Manual (label) |
| **Pod – night navigation/attack** | — | a night nav-and-attack pod (incl. bomb/rocket delivery). | OBSERVED | Manual (label) |
| **Pod – reconnaissance, day only.** | — | Pod – reconnaissance, day only. | OBSERVED | Manual (label) |
| **Pod – reconnaissance, night capable.** | — | Pod – reconnaissance, night capable. | OBSERVED | Manual (label) |
| **Weapon – INS navigation** | — | navigates by inertial guidance alone (see the INS guidance method). | OBSERVED | Manual p.288 |
| **Weapon – INS with GNSS navigation** | — | inertial navigation aided by satellite positioning (see INS + GNSS). | OBSERVED | Manual p.291 |
| **Weapon – TERCOM navigation** | — | terrain-contour-matching cruise navigation to a fixed target. | INFERRED | Standard TERCOM; not named in the manual |
| **Weapon – pre-briefed target only** | — | can strike only a target/coordinates set before launch; no in-flight retargeting. | INFERRED | Employment flag |
| **Weapon – can target specific subsystems** | — | can aim at a chosen subsystem/aimpoint of a target rather than the whole unit. | INFERRED | Employment flag |
| **Terminal maneuver – pop-up** | — | climbs then dives onto the target in the terminal phase (top-down attack; helps defeat point defences). | INFERRED | Terminal-maneuver flag |
| **Terminal maneuver – zig-zag** | — | weaves in the terminal phase to complicate interception. | INFERRED | Terminal-maneuver flag |
| **Terminal maneuver – random (advanced)** | — | unpredictable terminal jinking to defeat defences. | INFERRED | Terminal-maneuver flag |
| **Re-attack capability** | — | if it misses or fails to acquire, it can come around for another pass. | INFERRED | Employment flag |
| **Weapon altitude control possible** | — | its cruise altitude can be set by the player. | INFERRED | Employment flag |
| **Attitude control – aerodynamic only** | — | steers with aerodynamic surfaces alone (limited where the air is too thin). | INFERRED | Control flag |
| **Attitude control – non-aerodynamic only** | — | steers with thrust-vectoring/reaction control only (for exo-atmospheric flight). | INFERRED | Control flag |
| **Attitude control – combined** | — | uses both aerodynamic surfaces and reaction/thrust-vector control. | INFERRED | Control flag |
| **Uses GPS** | — | can take navigation fixes from the US GPS constellation. | INFERRED | Navigation flag |
| **Uses GLONASS** | — | can take navigation fixes from the Russian GLONASS constellation. | INFERRED | Navigation flag |
| **Uses BeiDou/COMPASS** | — | can take navigation fixes from the Chinese BeiDou constellation. | INFERRED | Navigation flag |
| **Uses NavIC/IRNSS** | — | can take navigation fixes from the Indian NavIC constellation. | INFERRED | Navigation flag |
| **Weapon – has imaging seeker** | — | carries an imaging (EO/IIR) seeker that can also help confirm the target’s identity. | INFERRED | Seeker flag |
| **Mine – contact fuze** | — | detonates on direct physical contact. | OBSERVED | Manual (label) |
| **Mine – magnetic fuze, simple magnetic** | — | triggers on a ship’s magnetic signature (basic). | INFERRED | Mine fuze flag |
| **Mine – magnetic fuze, total-field magnetometer** | — | an advanced magnetic trigger, harder to sweep. | INFERRED | Mine fuze flag |
| **Mine – passive acoustic fuze, broad-band (simple)** | — | triggers on a passing ship’s radiated noise. | INFERRED | Mine fuze flag |
| **Mine – passive acoustic fuze, narrow-band (advanced)** | — | a selective acoustic trigger, harder to spoof. | INFERRED | Mine fuze flag |
| **Mine – pressure fuze** | — | triggers on the pressure signature of a passing ship (very hard to sweep). | INFERRED | Mine fuze flag |
| **Mine – seismic fuze** | — | triggers on ground/seismic vibration. | INFERRED | Mine fuze flag |
| **Mine – delay counter** | — | lets a set number of ships pass before it will fire. | INFERRED | Mine logic flag |
| **Mine – arming delay** | — | waits a set time after being laid before it arms. | INFERRED | Mine logic flag |
| **Mine – target discrimination / identification** | — | distinguishes target types to fire selectively. | INFERRED | Mine logic flag |
| **Mine – remote controlled** | — | can be armed, disarmed or fired by remote command. | INFERRED | Mine logic flag |
| **Warhead – single re-entry vehicle (RV)** | — | one re-entry body. | INFERRED | Warhead-bus flag |
| **Warhead – multiple re-entry vehicles (MRV)** | — | several RVs that strike the same general area. | INFERRED | Warhead-bus flag |
| **Warhead – multiple independent RVs (MIRV)** | — | several RVs each aimed at a separate target. | INFERRED | Warhead-bus flag |
| **Fuze – impact** | — | detonates on hitting the target. | OBSERVED | Manual (label) |
| **Fuze – barometric/altimeter** | — | detonates at a set altitude (airburst). | INFERRED | Fuze flag |
| **Fuze – proximity** | — | detonates when close to the target. | OBSERVED | Manual (label) |
| **Fuze – top-down proximity** | — | fires downward onto a target from above (e.g. NLAW, TOW Aero) to hit thin top armour. | OBSERVED | Manual (label) |
| **Fuze – combination** | — | more than one fuzing mode (e.g. impact plus proximity). | INFERRED | Fuze flag |
| **Fuze – shock-factor (under-keel) optimized** | — | detonates below a ship’s keel to maximise the whipping/shock effect. | INFERRED | Fuze flag |
| **Capable vs mobile land unit** | — | can engage moving ground targets. | INFERRED | Employment flag |
| **Is a retarded munition** | — | a high-drag bomb that slows sharply after release so the aircraft can escape a low-level toss. | OBSERVED | Retarded-bomb behavior |
| **Boosted penetrator** | — | rocket-boosted to increase impact velocity and penetration. | INFERRED | Warhead flag |
| **Torpedo – straight-running** | — | runs on a straight course with no homing. | OBSERVED | Manual p.291 |
| **Torpedo – wake homing** | — | follows the target ship’s wake to the hull; considerably harder to decoy than sonar homing. | OBSERVED | Manual p.291 |
| **Torpedo – straight-running with time detonation** | — | straight run with a timed detonation. | INFERRED | Torpedo flag |
| **Torpedo – pattern-running** | — | runs a programmed search pattern to find a target. | INFERRED | Torpedo flag |
| **Flight profile – hi-hi-lo** | — | cruises high for range, then drops to low altitude for the terminal run (range vs detection trade-off). | INFERRED | Flight-profile flag |
| **Flight profile – level cruise flight** | — | flies a constant-altitude cruise to the target. | INFERRED | Flight-profile flag |

## Weapon target classes

| Term | Requires | In game | Tag | Source |
|---|---|---|---|---|
| **Aircraft** | — | fixed-wing aircraft. | OBSERVED | Target class |
| **Helicopter** | — | rotary-wing aircraft (often a separate clearance because of their low speed/altitude). | OBSERVED | Target class |
| **Missile** | — | airborne missiles — for interceptors and point-defence weapons. | OBSERVED | Target class |
| **Satellite** | — | on-orbit targets (ASAT weapons). | OBSERVED | Target class |
| **C-RAM** | — | rockets, artillery and mortar rounds in flight. | OBSERVED | Target class |
| **Surface vessel** | — | ships and boats on the surface. | OBSERVED | Target class |
| **Submarine** | — | submerged submarines. | OBSERVED | Target class |
| **Mine** | — | sea mines (for mine-clearance weapons). | OBSERVED | Target class |
| **Torpedo** | — | incoming torpedoes (for anti-torpedo weapons). | OBSERVED | Target class |
| **Land structure – soft** | — | unhardened fixed structures. | OBSERVED | Target class |
| **Land structure – hardened** | — | bunkers and hardened fixed sites (need penetrators). | OBSERVED | Target class |
| **Runway** | — | airfield runways/taxiways (cratering weapons). | OBSERVED | Target class |
| **Radar** | — | emitting radars (typically anti-radiation weapons). | OBSERVED | Target class |
| **Mobile target – soft** | — | unarmoured moving ground targets (trucks, mobile launchers). | OBSERVED | Target class |
| **Mobile target – hardened** | — | armoured moving ground targets (tanks). | OBSERVED | Target class |
| **Mobile target – personnel** | — | troops/infantry in the open. | OBSERVED | Target class |
| **Underwater structure** | — | fixed underwater targets. | OBSERVED | Target class |
| **Air base** | — | airfield as an area target. | OBSERVED | Target class |

## Weapon types

| Term | Requires | In game | Tag | Source |
|---|---|---|---|---|
| **Guided weapon** | — | a guided missile or smart bomb. | OBSERVED | Weapon type |
| **Rocket** | — | an unguided rocket. | OBSERVED | Weapon type |
| **Bomb** | — | a gravity bomb (guided or unguided depending on its codes). | OBSERVED | Weapon type |
| **Gun** | — | a gun or cannon firing shells. | OBSERVED | Weapon type |
| **Decoy (expendable)** | — | chaff, flares or similar one-shot decoys. | OBSERVED | Weapon type |
| **Decoy (towed)** | — | a decoy towed behind the platform. | OBSERVED | Weapon type |
| **Decoy (vehicle)** | — | a decoy that flies/moves on its own (e.g. MALD). | OBSERVED | Weapon type |
| **Training round** | — | an inert practice munition. | INFERRED | Weapon type |
| **Dispenser** | — | dispenses submunitions/bomblets. | OBSERVED | Weapon type |
| **Contact bomb – suicide** | — | a one-way contact charge (suicide attack). | INFERRED | Weapon type |
| **Contact bomb – sabotage** | — | a placed contact/sabotage charge. | INFERRED | Weapon type |
| **Guided projectile** | — | a guided gun round. | OBSERVED | Weapon type |
| **Small arms** | — | personal/crew-served small-arms fire. | OBSERVED | Weapon type |
| **UAV (expendable)** | — | a one-way attack UAV / loitering munition. | OBSERVED | Weapon type |
| **Sensor pod** | — | a carried targeting/nav/recon pod — a store, not a weapon. | OBSERVED | Weapon type |
| **Drop tank** | — | an external fuel tank. | OBSERVED | Weapon type |
| **Buddy store** | — | an aerial-refuelling pod for buddy tanking. | OBSERVED | Weapon type |
| **Ferry tank** | — | an extra fuel tank for ferrying, not combat. | INFERRED | Weapon type |
| **Torpedo** | — | an underwater guided/unguided weapon. | OBSERVED | Manual p.291 |
| **Depth charge** | — | an unguided anti-submarine charge fuzed to detonate at depth. | OBSERVED | Weapon type |
| **Sonobuoy** | — | an air-dropped sonar buoy (a sensor delivered as a “weapon” store). | OBSERVED | Weapon type |
| **Bottom mine** | — | a mine that rests on the seabed (shallow water). | OBSERVED | Weapon type |
| **Moored mine** | — | a mine held at depth by a cable to an anchor. | OBSERVED | Weapon type |
| **Floating mine** | — | a mine that floats at the surface. | OBSERVED | Weapon type |
| **Moving mine** | — | a mobile mine that transits to its position before settling. | INFERRED | Weapon type |
| **Rising mine** | — | sits deep, then launches a payload upward when a target passes (e.g. CAPTOR). | INFERRED | Weapon type |
| **Drifting mine** | — | an unmoored mine that drifts with the current. | INFERRED | Weapon type |
| **Attached mine** | — | a mine placed directly on a hull (limpet). | INFERRED | Weapon type |
| **Dummy mine** | — | an inert mine used to complicate clearance. | INFERRED | Weapon type |
| **Guided depth charge** | — | a depth charge with guidance/standoff. | INFERRED | Weapon type |
| **Helicopter-towed package** | — | a towed MCM/ASW package flown by a helicopter. | INFERRED | Weapon type |
| **Aircraft (as a store)** | — | a deployable aircraft/UAV carried and launched from a mount. | INFERRED | Weapon type |
| **Ship (as a store)** | — | a deployable boat/craft launched from a parent (e.g. a USV or landing craft). | INFERRED | Weapon type |
| **Submarine (as a store)** | — | a deployable submersible/UUV launched from a parent. | INFERRED | Weapon type |
| **Satellite (as a store)** | — | a satellite deployed by a launch vehicle. | INFERRED | Weapon type |
| **Ground unit (as a store)** | — | a deployable ground element launched/dropped from a parent. | INFERRED | Weapon type |
| **RV / MRV / MIRV** | — | a ballistic-missile re-entry-vehicle bus carrying one or more warheads. | OBSERVED | Weapon type |
| **Pallet munition** | — | palletised standoff munitions air-dropped from a cargo aircraft (e.g. Rapid Dragon). | INFERRED | Weapon type |
| **Laser** | — | a directed-energy laser weapon — hits at the speed of light, needs dwell time on larger targets. | OBSERVED | Manual p.292 |
| **Microwave** | — | a directed high-power-microwave weapon (anti-electronics). | INFERRED | Weapon type |
| **Laser dazzler** | — | a low-power laser that blinds/dazzles sensors or personnel rather than destroying. | INFERRED | Weapon type |
| **Hypersonic glide vehicle** | — | a boosted, unpowered glider that maneuvers at hypersonic speed. | OBSERVED | Manual (ballistic/HGV) p.287 |
| **Glide vehicle** | — | an unpowered glide body released to coast to its target. | INFERRED | Weapon type |
| **Hypersonic cruise missile** | — | a powered cruise missile sustaining hypersonic speed. | INFERRED | Weapon type |
| **Cargo** | — | carried cargo/supplies (not a weapon). | OBSERVED | Weapon type |
| **Troops** | — | embarked troops carried by the platform. | OBSERVED | Weapon type |
| **Paratroops** | — | troops delivered by parachute. | OBSERVED | Weapon type |


_251 terms._
