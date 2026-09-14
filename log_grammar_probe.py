#!/usr/bin/env python3
"""CMO message-log grammar probe — GENERATED from 092_aar.js by gen_probe.py. Do not hand-edit.

Usage:  python3 log_grammar_probe.py <log.txt> [more.txt ...]
Prints per-class record counts, coverage, and the parse invariant for each file.
"""
import re, sys, collections
from datetime import datetime, timezone

MONTHS = {m:i for i,m in enumerate(['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec'])}
TS_FORMATS = [
    [
        "MDY12",
        "M/D/YYYY h:mm:ss AM",
        "^(\\d{1,2})/(\\d{1,2})/(\\d{4}) (\\d{1,2}):(\\d{2}):(\\d{2}) ([AP])M - ([\\s\\S]*)$"
    ],
    [
        "DMY12",
        "D/M/YYYY h:mm:ss AM",
        "^(\\d{1,2})/(\\d{1,2})/(\\d{4}) (\\d{1,2}):(\\d{2}):(\\d{2}) ([AP])M - ([\\s\\S]*)$"
    ],
    [
        "MDY24",
        "M/D/YYYY HH:mm:ss",
        "^(\\d{1,2})/(\\d{1,2})/(\\d{4}) (\\d{1,2}):(\\d{2}):(\\d{2}) - ([\\s\\S]*)$"
    ],
    [
        "DMY24",
        "D/M/YYYY HH:mm:ss",
        "^(\\d{1,2})/(\\d{1,2})/(\\d{4}) (\\d{1,2}):(\\d{2}):(\\d{2}) - ([\\s\\S]*)$"
    ],
    [
        "DMMMY",
        "DD-MMM-YY HH:mm:ss",
        "^(\\d{1,2})-([A-Za-z]{3})-(\\d{2}) (\\d{1,2}):(\\d{2}):(\\d{2}) - ([\\s\\S]*)$"
    ],
    [
        "DMMMY4",
        "DD-MMM-YYYY HH:mm:ss",
        "^(\\d{1,2})-([A-Za-z]{3})-(\\d{4}) (\\d{1,2}):(\\d{2}):(\\d{2}) - ([\\s\\S]*)$"
    ],
    [
        "ISO",
        "YYYY-MM-DD HH:mm:ss",
        "^(\\d{4})-(\\d{2})-(\\d{2}) (\\d{1,2}):(\\d{2}):(\\d{2}) - ([\\s\\S]*)$"
    ]
]
SIDE = re.compile(r'^\[([^\]]+)\] ?(.*)$', re.S)
ANYTS = re.compile(r'^(?:\d{1,2}[/-][A-Za-z0-9]{1,4}[/-]\d{2,4}|\d{4}-\d{2}-\d{2}) \d{1,2}:\d{2}:\d{2}(?: [AP]M)? - ')

PATTERNS = [
    ('ENG_MISSILE', re.compile('^(?P<w>.+?) #(?P<sn>\\d+) (?P<res>HIT|MISS): Weapon: .+? is attacking (?P<tgt>.+?) with a base PH of (?P<bph>[\\d.]+)%\\.(?P<mods>[\\s\\S]*?)Final PH: (?P<fph>[\\d.]+)% *Result: (?P<roll>\\d+) - (?P<r2>HIT|MISS)(?P<tail>[^\\n]*)', re.S), True),
    ('ENG_GUN', re.compile('^(?P<gun>.+?) (?P<res>HIT|MISS): Gun \\(.+?\\) is attacking (?P<tgt>.+?) with a base-Ph of (?P<bph>[\\d.]+)%\\.(?P<mods>[\\s\\S]*?)Final Ph: (?P<fph>[\\d.]+)% *Result: (?P<roll>\\d+) - (?P<r2>HIT|MISS)(?P<tail>[^\\n]*)', re.S), True),
    ('FIRE_POH', re.compile('^(?P<plat>.+?) attacks with weapon: (?P<w>.+?)\\. Nominal PoH: (?P<nom>[\\d.]+)%\\.(?P<mods>[\\s\\S]*?)Final PoH at fire/launch point: (?P<fin>[\\d.]+)%', re.S), True),
    ('FIRE_CEP', re.compile('^(?P<plat>.+?) attacks with weapon: (?P<w>.+?)\\. Nominal CEP: (?P<nom>[\\d.]+)(?P<u>m|ft|nm)\\.(?P<mods>[\\s\\S]*?)Final CEP at fire/launch point: (?P<fin>[\\d.]+)(?P<u2>m|ft|nm)', re.S), True),
    ('SOFTKILL', re.compile('^(?P<kind>Decoy|Defensive jammer|Offensive jammer) \\((?P<sys>.+?); Tech: (?P<tech>.+?)\\) (?:from|on) (?P<plat>.+?) is attempting to (?P<verb>seduce|spoof|jam) sensor: (?P<sensor>.+?) \\(Tech: (?P<stech>.+?)\\)\\((?:Guiding weapon|Of): (?P<wpn>.+?)\\)\\. Final probability: (?P<p>[\\d.]+)%\\. Result: (?P<roll>\\d+) - (?P<r>SUCCESS|FAILURE)', re.S), True),
    ('FUEL_LOSS', re.compile('^(?P<unit>.+?) has run out of fuel and crashed!', re.S), True),
    ('ABANDONED', re.compile('^(?P<unit>.+?) has no functioning engines and is being abandoned', re.S), True),
    ('CREW_INCAP', re.compile('^Cockpit & crew incapacitated - aircraft is out of control!', re.S), True),
    ('COMPONENT_HIT', re.compile('^(?P<comp>[A-Z][\\w &]*?) hit - penetration (?P<pct>[\\d.]+)%', re.S), True),
    ('DMG_COMP_DEGRADE', re.compile('^(?P<unit>.+?) damage report: (?P<comp>.+?) has (?:been (?:lightly|moderately|heavily) damaged|suffered additional (?:light |moderate |heavy )?damage)', re.S), True),
    ('TERM_NOSENSOR', re.compile('^(?P<w>.+?) #(?P<sn>\\d+) (?P<res>MISS): Weapon: .+? has no functioning sensors', re.S), True),
    ('GROUP_DISSOLVE', re.compile('^(?P<g>.+?) has no units left; dissolving', re.S), True),
    ('FLIGHT_ASSEMBLED', re.compile('^Flight (?P<f>.+?) has finished assembling', re.S), True),
    ('HOSTED', re.compile('^(?P<unit>.+?) was hosted in (?P<where>[\\s\\S]+)$', re.S), True),
    ('PATHEVAL', re.compile('^(?:The unit )?(?P<u>.+?) (?:will wait until path evaluation|path evaluation terminated)', re.S), True),
    ('TERM', re.compile('^(?P<w>.+?) (?:#(?P<sn>\\d+) )?(?P<res>HIT|MISS): (?P<detail>(?!Weapon:|Gun \\()[\\s\\S]*)$', re.S), True),
    ('DMG_DP', re.compile('^(?P<unit>.+?) has suffered (?P<type>weapon|blast|underground shock|fragmentation|fire|flooding) damage: (?P<dp>[\\d.]+) DPs', re.S), True),
    ('DMG_COMPONENT', re.compile('^(?P<unit>.+?) damage report: (?P<comp>.+?) has been destroyed[!.]', re.S), True),
    ('SINKING', re.compile('^(?P<unit>.+?) is sinking!!!', re.S), True),
    ('BDA_REPORT', re.compile('^(?P<by>.+?) reports BDA status change on contact: (?P<c>[\\s\\S]+)$', re.S), True),
    ('DMG_STATE', re.compile('^(?P<unit>.+?) has (?:a )?(?:severe |major |moderate |light |minor )?(?P<state>flooding|fire|structural damage)', re.S), True),
    ('FIRE_OUT', re.compile('^(?P<unit>.+?) has extinguished all fires', re.S), True),
    ('CONTROLS_LOST', re.compile('^(?P<unit>.+?) has its flight controls knocked out', re.S), True),
    ('CABIN_HIT', re.compile('^(?P<unit>.+?) suffered penetration on pressurized cabin', re.S), True),
    ('REPAIR_DONE', re.compile('^(?P<unit>.+?)(?:: structural integrity fully restored!| damage report: *(?P<c2>.*?) has been fully repaired\\.)', re.S), True),
    ('REPAIRING', re.compile('^(?P<unit>.+?) damage report: *(?P<comp>.*?) is being repaired \\((?P<lvl>[^)]+)\\)', re.S), True),
    ('FIRE_WARN', re.compile('^WARNING: (?P<unit>.+?) is risking uncontrollable fires!', re.S), True),
    ('REPAIR', re.compile('^(?P<unit>.+?): structural damage being repaired, now at (?P<pct>[\\d.]+)%', re.S), True),
    ('DESTROYED', re.compile('^(?P<unit>.+?) has been destroyed!', re.S), True),
    ('PENETRATION', re.compile('^(?P<pct>\\d+)% penetration achieved', re.S), True),
    ('NEARMISS', re.compile('^Weapon: (?P<w>.+?) #(?P<sn>\\d+) missed (?P<tgt>.+?) by (?P<d>[\\d.]+)(?P<u>ft|m|nm)', re.S), True),
    ('CEP_UPDATE', re.compile('^Weapon: (?P<w>.+?) #(?P<sn>\\d+) has a (?P<rate>\\d+)% rate on recent GNSS updates - CEP adjusted to: (?P<cep>[\\d.]+)', re.S), True),
    ('SEEKER_DETECT', re.compile('^(?:.+?Seeker|Multiple sensors) on (?P<w>.+?) detected new potential target (?P<tgt>[\\s\\S]+)$', re.S), True),
    ('LOCKON', re.compile('^(?P<w>.+?) has locked on to (?P<tgt>[\\s\\S]+)$', re.S), True),
    ('IMPACT', re.compile('^Weapon: (?P<w>.+?) has impacted (?P<tgt>[\\s\\S]+)$', re.S), True),
    ('WPN_NOUPDATE', re.compile('^Weapon: (?P<w>.+?) is not receiving firm target updates from parent unit', re.S), True),
    ('WPN_NOREFLECT', re.compile('^Weapon: (?P<w>.+?) can no longer see reflected energy from target', re.S), True),
    ('WPN_LOGIC', re.compile('^Weapon: (?P<w>.+?) (?:is running blind|overshot|has no eligible|has only one|has been redirected)', re.S), True),
    ('GODSEYE', re.compile("^GOD'S EYE (?P<state>ENABLED|DISABLED)\\.", re.S), True),
    ('AIRFIELD_SPOT_NEW', re.compile('^New aircraft spotted on (?P<loc>.+?) \\((?P<cap>[^)]+)\\) by (?P<by>.+?) \\(Sensor: (?P<sensor>.+?)\\)\\.', re.S), True),
    ('AIRFIELD_SPOT_ID', re.compile('^Aircraft previously spotted on (?P<loc>.+?) \\((?P<cap>[^)]+)\\) has been (?:identified|type-classified) as: (?P<cls>.+?) \\(recon by: (?P<by>.+?) - Sensor: (?P<sensor>.+?)\\)\\.', re.S), True),
    ('DOCTRINE', re.compile('^The Unit (?P<u>.+?) cannot fire against (?P<tgt>.+?) with weapon (?P<w>.+?)(?:\\. REASON: (?P<reason>[\\s\\S]*))?$', re.S), True),
    ('CONTACT_NEW', re.compile('^(?:NEW DELAYED CONTACT|New contact!)', re.S), True),
    ('CONTACT_PROBABLE', re.compile('^New probable (?P<what>\\w+) contact!', re.S), True),
    ('CONTACT_ID', re.compile('^Contact:? *(?P<c>[\\s\\S]*?) has been (?:type-classified|classified|positively identified) as: (?P<cls>[\\s\\S]+)$', re.S), True),
    ('CONTACT_RENAME', re.compile('^Contact:? (?P<c>.+?) is now known as: (?P<n>[\\s\\S]+)$', re.S), True),
    ('CONTACT_HOSTILE', re.compile('^Contact:? (?P<c>.+?) was observed attacking a friendly unit', re.S), True),
    ('CONTACT_MANUAL', re.compile('^Contact:? (?P<c>.+?) has been manually marked as hostile!', re.S), True),
    ('CONTACT_ATTRIB', re.compile('^Contact:? (?P<c>.+?) is the most likely firing unit of(?P<of>[\\s\\S]*?) and is now considered as hostile!', re.S), True),
    ('CONTACT_UPDATE', re.compile('^Updating data for contact: (?P<c>.+?), based on new information by: (?P<by>[\\s\\S]+)$', re.S), True),
    ('CONTACT_LOST_PRIV', re.compile('^(?P<holder>.+?): Private contact ?(?P<c>[\\s\\S]*?) has been lost\\.', re.S), True),
    ('CONTACT_LOST', re.compile('^(?:(?P<holder>\\S+) ?:)?Contact:? ?(?P<c>[\\s\\S]*?) has been lost\\.', re.S), True),
    ('COMMS', re.compile('(?:rejoined the communications network|has lost communications)', re.S), False),
    ('SIDE_SWITCH', re.compile('^Switched side to: (?P<side>[\\s\\S]+)$', re.S), True),
    ('POSTURE', re.compile("^Side '(?P<a>.+?)' is now considered (?P<p>\\w+) to (?P<b>[\\s\\S]+)$", re.S), True),
    ('EVENT', re.compile("^Event: '(?P<ev>.+?)' has been fired\\.", re.S), True),
    ('SPECIAL_MSG', re.compile('^\\s*(?:<|@import\\b|\\{|\\}|(?:font|background|color|margin|padding|border|display|text|line|width|height|max|min|flex|grid|position|top|left|right|bottom|letter|box|opacity|z-index)[\\w-]*\\s*:\\s*\\S)', re.S), True),
]

def build(key, m):
    g = m.groups()
    if key in ('MDY12','DMY12'):
        h = int(g[3]) % 12 + (12 if g[6] == 'P' else 0)
        y, mo, d = int(g[2]), (int(g[0]) if key=='MDY12' else int(g[1])), (int(g[1]) if key=='MDY12' else int(g[0]))
        return datetime(y, mo, d, h, int(g[4]), int(g[5]), tzinfo=timezone.utc), g[7]
    if key in ('MDY24','DMY24'):
        y, mo, d = int(g[2]), (int(g[0]) if key=='MDY24' else int(g[1])), (int(g[1]) if key=='MDY24' else int(g[0]))
        return datetime(y, mo, d, int(g[3]), int(g[4]), int(g[5]), tzinfo=timezone.utc), g[6]
    if key in ('DMMMY','DMMMY4'):
        mo = MONTHS.get(g[1].lower())
        if mo is None: return None, None
        yy = int(g[2]); y = yy if key=='DMMMY4' else (2000+yy if yy < 50 else 1900+yy)
        return datetime(y, mo+1, int(g[0]), int(g[3]), int(g[4]), int(g[5]), tzinfo=timezone.utc), g[6]
    if key == 'ISO':
        return datetime(int(g[0]), int(g[1]), int(g[2]), int(g[3]), int(g[4]), int(g[5]), tzinfo=timezone.utc), g[6]
    return None, None

def detect(lines):
    counts = collections.Counter(); a = b = 0
    slash = re.compile(r'^(\d{1,2})/(\d{1,2})/\d{4} ')
    for line in lines[:20000]:
        if not ANYTS.match(line): continue
        for key, label, rx in TS_FORMATS:
            if key in ('DMY12','DMY24'): continue
            if re.match(rx, line): counts[key] += 1; break
        sm = slash.match(line)
        if sm:
            if int(sm.group(1)) > 12: b += 1
            if int(sm.group(2)) > 12: a += 1
    if not counts: return None, False
    best = counts.most_common(1)[0][0]; ambiguous = False
    if best in ('MDY12','MDY24'):
        if b > a: best = 'DMY12' if best == 'MDY12' else 'DMY24'
        elif a == 0 and b == 0: ambiguous = True
    return best, ambiguous

def split_records(text):
    lines = text.split('\n')
    key, ambiguous = detect(lines)
    if not key: return [], None, False
    rx = dict((k, r) for k, l, r in TS_FORMATS)[key]
    cre = re.compile(rx); recs = []; cur = None
    for line in lines:
        m = cre.match(line)
        if m:
            t, rest = build(key, m)
            if t is not None:
                if cur: recs.append(cur)
                cur = [t, rest]; continue
        if cur: cur[1] += '\n' + line
    if cur: recs.append(cur)
    return recs, key, ambiguous

def dedupe_sides(recs):
    """One event visible to N sides is written N times. But a side can legitimately repeat the
    same body in the same second, so the real count is the largest any SINGLE side reports."""
    groups = collections.defaultdict(collections.Counter); parsed = []
    for t, body in recs:
        sm = SIDE.match(body)
        side = sm.group(1).strip() if sm else None
        core = (sm.group(2) if sm else body).strip()
        parsed.append((t, side, core)); groups[(t, core)][side] += 1
    keep = {k: max(c.items(), key=lambda kv: kv[1]) for k, c in groups.items()}
    used = collections.Counter(); out = []; dropped = 0
    for t, side, core in parsed:
        k = (t, core); s, n = keep[k]
        if side == s and used[k] < n: used[k] += 1; out.append((t, side, core))
        else: dropped += 1
    return out, dropped

def classify(text):
    recs, key, ambiguous = split_records(text)
    if not recs: return None
    recs, mirrored = dedupe_sides(recs)
    counts = collections.Counter(); unmatched = []
    for t, side, body in recs:
        if not body: counts['BLANK'] += 1; continue
        for name, pat, anchored in PATTERNS:
            if (pat.match(body) if anchored else pat.search(body)): counts[name] += 1; break
        else:
            counts['UNMATCHED'] += 1
            if len(unmatched) < 200: unmatched.append(body.split('\n')[0][:160])
    return dict(records=len(recs), mirrored=mirrored, fmt=key, ambiguous=ambiguous,
                counts=counts, unmatched=unmatched)

if __name__ == '__main__':
    files = sys.argv[1:]
    if not files: print(__doc__); raise SystemExit(2)
    grand = tot = 0
    for f in files:
        r = classify(open(f, encoding='utf-8', errors='replace').read())
        if not r: print(f'{f}: no recognised timestamp format'); continue
        un = r['counts'].get('UNMATCHED', 0); grand += un; tot += r['records']
        print(f"\n=== {f} ===")
        print(f"  {r['records']:,} records  ({r['mirrored']:,} side-mirrored merged)  "
              f"format {r['fmt']}{' (assumed)' if r['ambiguous'] else ''}  "
              f"coverage {100*(r['records']-un)/max(1,r['records']):.2f}%")
        for k, v in r['counts'].most_common():
            if k != 'UNMATCHED': print(f"    {v:>7,}  {k}")
        if un:
            print(f"    {un:>7,}  UNMATCHED")
            for u in r['unmatched'][:10]: print(f"             {u}")
    if len(files) > 1:
        print(f"\nTOTAL {tot:,} records, {grand:,} unmatched, coverage {100*(tot-grand)/max(1,tot):.2f}%")
