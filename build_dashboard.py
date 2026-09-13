#!/usr/bin/env python3
"""
build_dashboard.py — extract a Command: Modern Operations database (DB3K_*.db3 or CWDB_*.db3)
into a single self-contained HTML dashboard.

Easiest use: put this (or the prebuilt build_dashboard.exe) in your game's DB folder and
run it with no arguments — it finds the newest DB3K_*.db3 automatically, builds the
dashboard next to it, and opens it in your browser.

    python build_dashboard.py                              # auto-detect newest DB3K_*.db3 here
    python build_dashboard.py DB3K_517.db3                 # -> DB3K_517_dashboard.html
    python build_dashboard.py CWDB_517.db3                 # Cold War database (images from Images/CWDB)
    python build_dashboard.py DB3K_517.db3 -o my.html
    python build_dashboard.py DB3K_517.db3 --json out.json # also dump the raw JSON for inspection
    python build_dashboard.py --no-open                    # don't launch a browser afterwards

Keep the generated HTML inside the DB folder so its relative Images/DB3000/*.webp links resolve.
Takes ~10 s; output is ~5 MB and opens directly in Chrome/Edge/Firefox (no server needed).
The prebuilt .exe carries this template inside it, so end users need only that one file.

The script reads the database read-only, packs the tables the dashboard needs into a compact
column/row JSON structure, deflates it, base64-encodes it and injects it into
cmo_db_dashboard.template.html at the marker  /*__DB_BLOB__*/ .

Only the Python standard library is required.
"""
import argparse, base64, glob, json, os, re, sqlite3, sys, time, webbrowser, zlib

ARC_COLS = ['SB1','SB2','SMF1','SMF2','SMA1','SMA2','SS1','SS2',
            'PB1','PB2','PMF1','PMF2','PMA1','PMA2','PS1','PS2']

def arcmask(row, suffix=''):
    m = 0
    for i, c in enumerate(ARC_COLS):
        v = row[c + suffix] if (c + suffix) in row.keys() else 0
        if v in (1, '1', True, 'True'):
            m |= (1 << i)
    return m

def rc(r, name):
    """Safe column read from a sqlite3.Row: returns None if the column is absent.
    Lets the extractor tolerate schema differences across DB versions (older DB3K and CWDB
    lack some columns the current DB3K has, e.g. DataWeaponWRA.AutoFireRange)."""
    return r[name] if name in r.keys() else None

def norm(v):
    """Normalise SQLite values for JSON: booleans stored as text -> 0/1, floats trimmed."""
    if v is None:
        return None
    if isinstance(v, str):
        if v in ('True', 'Yes'):
            return 1
        if v in ('False', 'No'):
            return 0
        return v
    if isinstance(v, float):
        if v == int(v) and abs(v) < 1e15:
            return int(v)
        return round(v, 4)
    return v

class Extractor:
    def __init__(self, path):
        self.con = sqlite3.connect('file:%s?mode=ro' % path.replace('\\', '/'), uri=True)
        self.con.row_factory = sqlite3.Row
        self.tables = {r[0] for r in self.con.execute("select name from sqlite_master where type='table'")}

    def has(self, t):
        return t in self.tables

    def cols(self, t):
        return [r[1] for r in self.con.execute('pragma table_info(%s)' % t)]

    def table(self, t, drop=()):
        """Whole table as {c:[cols], r:[[...]]}."""
        cols = [c for c in self.cols(t) if c not in drop]
        rows = []
        for r in self.con.execute('select %s from %s' % (','.join('"%s"' % c for c in cols), t)):
            rows.append([norm(v) for v in r])
        return {'c': cols, 'r': rows}

    def grouped(self, t, keycol='ID', fn=None):
        """Join table grouped by key -> {id: [fn(row) ...]}."""
        if not self.has(t):
            return {}
        out = {}
        order = ''
        if 'ComponentNumber' in self.cols(t):
            order = ' order by ID, ComponentNumber'
        for r in self.con.execute('select * from %s%s' % (t, order)):
            out.setdefault(r[keycol], []).append(fn(r) if fn else r['ComponentID'])
        return out

    def enums(self):
        out = {}
        for t in sorted(self.tables):
            if not t.startswith('Enum'):
                continue
            cols = self.cols(t)
            if len(cols) < 2:
                continue
            d = {}
            for r in self.con.execute('select "%s","%s" from %s' % (cols[0], cols[1], t)):
                d[r[0]] = r[1]
            out[t[4:]] = d
        # Sensor role comments carry the range bands; keep them.
        if self.has('EnumSensorRole') and 'Comment' in self.cols('EnumSensorRole'):
            out['SensorRoleComment'] = {r[0]: r[1] for r in self.con.execute('select ID, Comment from EnumSensorRole where Comment is not null')}
        return out

    def signatures(self, t):
        out = {}
        cols = self.cols(t)
        has_top = 'Top' in cols
        for r in self.con.execute('select * from %s' % t):
            vals = [norm(r['Front']), norm(r['Side']), norm(r['Rear'])] + ([norm(r['Top'])] if has_top else [])
            out.setdefault(r['ID'], {})[r['Type']] = vals
        return out

    def platform(self, kind):
        """kind in Aircraft, Ship, Submarine, Facility, GroundUnit"""
        base = 'Data' + kind
        d = {'main': self.table(base)}
        sens_fn = lambda r: [r['ComponentID'], arcmask(r), arcmask(r, 'Max'),
                             norm(r['DegOverride']) if 'DegOverride' in r.keys() else 0,
                             norm(r['DegOverrideMax']) if 'DegOverrideMax' in r.keys() else 0,
                             norm(r['VerticalDegMax']) if 'VerticalDegMax' in r.keys() else 0,
                             norm(r['MastHeight']) if 'MastHeight' in r.keys() else 0]
        d['sensors'] = self.grouped(base + 'Sensors', fn=sens_fn)
        d['mounts'] = self.grouped(base + 'Mounts', fn=lambda r: [r['ComponentID'], arcmask(r)])
        d['magazines'] = self.grouped(base + 'Magazines')
        d['loadouts'] = self.grouped(base + 'Loadouts')
        d['prop'] = self.grouped(base + 'Propulsion')
        d['fuel'] = self.grouped(base + 'Fuel')
        d['codes'] = self.grouped(base + 'Codes', fn=lambda r: r['CodeID'])
        d['comms'] = self.grouped(base + 'Comms')
        d['acfac'] = self.grouped(base + 'AircraftFacilities')
        d['dock'] = self.grouped(base + 'DockingFacilities')
        d['sig'] = self.signatures(base + 'Signatures') if self.has(base + 'Signatures') else {}
        return d

    def run(self):
        t0 = time.time()
        E = self.enums()
        out = {'meta': {}, 'enums': E}
        out['meta']['db'] = [dict(r) for r in self.con.execute('select * from ManagementDatabase')] if self.has('ManagementDatabase') else []
        out['sensor'] = self.table('DataSensor')
        out['sensorCaps'] = self.grouped('DataSensorCapabilities', fn=lambda r: r['CodeID'])
        out['sensorCodes'] = self.grouped('DataSensorCodes', fn=lambda r: r['CodeID'])
        out['sensorFreqST'] = self.grouped('DataSensorFrequencySearchAndTrack', fn=lambda r: r['Frequency'])
        out['sensorFreqIL'] = self.grouped('DataSensorFrequencyIlluminate', fn=lambda r: r['Frequency'])
        out['sensorGroups'] = self.grouped('DataSensorSensorGroups')

        out['weapon'] = self.table('DataWeapon')
        out['weaponTargets'] = self.grouped('DataWeaponTargets', fn=lambda r: r['CodeID'])
        out['weaponCodes'] = self.grouped('DataWeaponCodes', fn=lambda r: r['CodeID'])
        out['weaponWarheads'] = self.grouped('DataWeaponWarheads')
        out['weaponSensors'] = self.grouped('DataWeaponSensors', fn=lambda r: [r['ComponentID'], arcmask(r), arcmask(r, 'Max')])
        out['weaponProp'] = self.grouped('DataWeaponPropulsion')
        out['weaponFuel'] = self.grouped('DataWeaponFuel')
        out['weaponSig'] = self.signatures('DataWeaponSignatures')
        out['weaponWRA'] = self.grouped('DataWeaponWRA', fn=lambda r: [rc(r,'CodeID'), rc(r,'WeaponQty'), rc(r,'ShooterQty'), rc(r,'AutoFireRange'), rc(r,'SelfDefenceRange')])
        out['weaponComms'] = self.grouped('DataWeaponComms') if self.has('DataWeaponComms') else {}
        out['warhead'] = self.table('DataWarhead')
        out['weaponRecord'] = {r['ID']: [rc(r,'ComponentID'), rc(r,'DefaultLoad'), rc(r,'MaxLoad'), rc(r,'ROF'), rc(r,'Multiple')]
                               for r in self.con.execute('select * from DataWeaponRecord')}
        out['mount'] = self.table('DataMount')
        out['mountWeapons'] = self.grouped('DataMountWeapons')
        out['mountMagWeapons'] = self.grouped('DataMountMagazineWeapons')
        out['mountSensors'] = self.grouped('DataMountSensors')
        out['mountDirectors'] = self.grouped('DataMountDirectors')
        out['magazine'] = self.table('DataMagazine')
        out['magazineWeapons'] = self.grouped('DataMagazineWeapons')
        out['loadout'] = self.table('DataLoadout')
        out['loadoutWeapons'] = self.grouped('DataLoadoutWeapons', fn=lambda r: [rc(r,'ComponentID'), norm(rc(r,'Optional')), norm(rc(r,'Internal'))])
        out['propulsion'] = self.table('DataPropulsion', drop=('Comments',))
        out['propPerf'] = self.grouped('DataPropulsionPerformance', fn=lambda r: [rc(r,'AltitudeBand'), rc(r,'Throttle'), rc(r,'Speed'), norm(rc(r,'AltitudeMin')), norm(rc(r,'AltitudeMax')), norm(rc(r,'Consumption'))])
        out['fuel'] = {r['ID']: [rc(r,'Type'), rc(r,'Capacity')] for r in self.con.execute('select * from DataFuel')}
        out['comm'] = self.table('DataComm', drop=('Comments',))
        out['acfacility'] = {r['ID']: [rc(r,'Type'), rc(r,'PhysicalSize'), rc(r,'Capacity'), rc(r,'RunwayLength')] for r in self.con.execute('select * from DataAircraftFacility')}
        out['dockfacility'] = self.table('DataDockingFacility') if self.has('DataDockingFacility') else None
        for kind in ['Aircraft', 'Ship', 'Submarine', 'Facility', 'GroundUnit', 'Satellite']:
            out[kind] = self.platform(kind)
        # satellites carry orbital elements (their propulsion/loadouts tables don't exist, so platform() leaves those empty)
        if self.has('DataSatelliteOrbits'):
            out['Satellite']['orbits'] = self.grouped('DataSatelliteOrbits', fn=lambda r: [
                rc(r, 'Plane'), norm(rc(r, 'Inclination')), norm(rc(r, 'Apogee')), norm(rc(r, 'Perigee')),
                norm(rc(r, 'OrbitalPeriod')), rc(r, 'MissonName'), rc(r, 'Operational')])
        out['meta']['extracted'] = time.strftime('%Y-%m-%d %H:%M:%S')
        out['meta']['seconds'] = round(time.time() - t0, 1)
        return out

# ============================================================
# Changelog (--vs): diff the new database against a previous one.
# Keys on stable entity IDs (confirmed stable across DB versions: entities are never
# renumbered, and removals are done by flipping the Deprecated flag, not by deleting rows).
# Emits ONLY the deltas (added / removed / (un)deprecated / changed fields / changed
# components) as a compact structure. Component names are resolved in-browser from the
# main embedded DB, so this carries IDs, not names.
# ============================================================

# Enum-backed scalar fields, so the changelog page can resolve raw IDs to labels via E().
CL_ENUM_FIELD = {
    'aircraft':  {'Category': 'AircraftCategory', 'Type': 'AircraftType'},
    'ship':      {'Category': 'ShipCategory', 'Type': 'ShipType'},
    'sub':       {'Category': 'SubmarineCategory', 'Type': 'SubmarineType'},
    'facility':  {'Category': 'FacilityCategory', 'Type': 'FacilityType'},
    'ground':    {'Category': 'GroundUnitCategory'},
    'sensor':    {'Type': 'SensorType', 'Role': 'SensorRole', 'Generation': 'SensorGeneration'},
    'weapon':    {'Type': 'WeaponType', 'Generation': 'WeaponGeneration'},
}

# Which entity types to diff, and their SQL table + dashboard route.
CL_ENTITIES = [
    ('aircraft', 'DataAircraft', 'Aircraft'),
    ('ship', 'DataShip', 'Ship'),
    ('sub', 'DataSubmarine', 'Submarine'),
    ('facility', 'DataFacility', 'Facility'),
    ('ground', 'DataGroundUnit', 'GroundUnit'),
    ('sensor', 'DataSensor', 'Sensor'),
    ('weapon', 'DataWeapon', 'Weapon'),
]

# Component (join) tables to diff per existing entity, by entity route.
# ('key', table, valuecol, comptype) — comptype tells the page how to resolve the id.
CL_COMPONENTS = {
    'aircraft': [('mounts', 'DataAircraftMounts', 'ComponentID', 'mount'),
                 ('sensors', 'DataAircraftSensors', 'ComponentID', 'sensor'),
                 ('loadouts', 'DataAircraftLoadouts', 'ComponentID', 'loadout')],
    'ship': [('mounts', 'DataShipMounts', 'ComponentID', 'mount'),
             ('sensors', 'DataShipSensors', 'ComponentID', 'sensor'),
             ('magazines', 'DataShipMagazines', 'ComponentID', 'magazine')],
    'sub': [('mounts', 'DataSubmarineMounts', 'ComponentID', 'mount'),
            ('sensors', 'DataSubmarineSensors', 'ComponentID', 'sensor'),
            ('magazines', 'DataSubmarineMagazines', 'ComponentID', 'magazine')],
    'facility': [('mounts', 'DataFacilityMounts', 'ComponentID', 'mount'),
                 ('sensors', 'DataFacilitySensors', 'ComponentID', 'sensor'),
                 ('magazines', 'DataFacilityMagazines', 'ComponentID', 'magazine')],
    'ground': [('mounts', 'DataGroundUnitMounts', 'ComponentID', 'mount'),
               ('sensors', 'DataGroundUnitSensors', 'ComponentID', 'sensor'),
               ('magazines', 'DataGroundUnitMagazines', 'ComponentID', 'magazine')],
    'sensor': [('caps', 'DataSensorCapabilities', 'CodeID', 'cap'),
               ('codes', 'DataSensorCodes', 'CodeID', 'scode')],
    'weapon': [('codes', 'DataWeaponCodes', 'CodeID', 'wcode'),
               ('targets', 'DataWeaponTargets', 'CodeID', 'wtarget'),
               ('warheads', 'DataWeaponWarheads', 'ComponentID', 'warhead')],
}


def _cl_rows(con, table):
    """{id: {col: normalised value}} for an entity table."""
    out = {}
    for r in con.execute('select * from "%s"' % table):
        d = {k: norm(r[k]) for k in r.keys()}
        out[d['ID']] = d
    return out


def _cl_multiset(con, table, valcol):
    """{entityID: {compID: count}} for a join table (missing table -> {})."""
    from collections import Counter
    out = {}
    try:
        cur = con.execute('select ID, "%s" from "%s"' % (valcol, table))
    except sqlite3.Error:
        return out
    for eid, cid in cur:
        if cid is None:
            continue
        out.setdefault(eid, Counter())[cid] += 1
    return out


def _cl_diff_ms(a, b):
    """Diff two Counters -> (added, removed) as sorted [[id, count], ...] lists."""
    added, removed = [], []
    for cid in set(a) | set(b):
        d = a.get(cid, 0) - b.get(cid, 0)   # a=new, b=prev
        if d > 0:
            added.append([cid, d])
        elif d < 0:
            removed.append([cid, -d])
    added.sort(); removed.sort()
    return added, removed


def compute_changelog(new_con, prev_path):
    """new_con: open sqlite connection to the new DB. prev_path: path to previous .db3."""
    prev = sqlite3.connect('file:%s?mode=ro' % prev_path.replace('\\', '/'), uri=True)
    prev.row_factory = sqlite3.Row
    cl = {'entities': {}}
    for route, table, _kind in CL_ENTITIES:
        na = _cl_rows(new_con, table)
        pa = _cl_rows(prev, table)
        nk, pk = set(na), set(pa)
        added = sorted(nk - pk)
        removed = sorted(pk - nk)     # id absent entirely (anomaly; normally empty)
        common = nk & pk

        def nm(row):
            return row.get('Name') or row.get('ClassName') or ('#' + str(row.get('ID')))

        ent = {
            'added': [[i, nm(na[i])] for i in added],
            'removed': [[i, nm(pa[i])] for i in removed],
            'deprecated': [],     # became Deprecated
            'restored': [],       # un-deprecated
            'changed': [],        # field and/or component changes among common, non-status
        }
        # component multisets (only for common entities)
        comp_ms = {}
        for key, ctable, valcol, ctype in CL_COMPONENTS.get(route, []):
            comp_ms[key] = (_cl_multiset(new_con, ctable, valcol),
                            _cl_multiset(prev, ctable, valcol),
                            valcol, ctype)
        for i in sorted(common):
            no, po = na[i], pa[i]
            ndep, pdep = 1 if no.get('Deprecated') else 0, 1 if po.get('Deprecated') else 0
            if ndep and not pdep:
                ent['deprecated'].append([i, nm(no)])
                continue
            if pdep and not ndep:
                ent['restored'].append([i, nm(no)])
                # fall through: also report field changes on a restored entity
            # field changes (skip ID + Deprecated; Deprecated handled above)
            fields = []
            for col in no:
                if col in ('ID', 'Deprecated'):
                    continue
                if no.get(col) != po.get(col):
                    fields.append([col, po.get(col), no.get(col)])
            # component changes
            comps = []
            for key, (nms, pms, _vc, ctype) in comp_ms.items():
                from collections import Counter
                a = nms.get(i, Counter()); b = pms.get(i, Counter())
                if a == b:
                    continue
                addc, remc = _cl_diff_ms(a, b)
                if addc or remc:
                    comps.append({'k': key, 't': ctype, 'add': addc, 'rem': remc})
            if fields or comps:
                rec = {'id': i, 'n': nm(no)}
                if fields:
                    rec['f'] = fields
                if comps:
                    rec['c'] = comps
                if pdep and not ndep:
                    rec['restored'] = 1
                ent['changed'].append(rec)
        cl['entities'][route] = ent
    prev.close()
    return cl


def _db_display_name(path):
    return os.path.splitext(os.path.basename(path))[0]


def _frozen():
    """True when running as a PyInstaller-built .exe rather than a .py script."""
    return getattr(sys, 'frozen', False)

def _app_dir():
    """Folder to search for the database and write the dashboard into.
    For the .exe this is where the .exe sits (normally the game's DB folder); otherwise the cwd."""
    if _frozen():
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.getcwd()

def _find_template(explicit=None):
    """Locate cmo_db_dashboard.template.html: an explicit path, then the PyInstaller bundle,
    then next to the script, then the working/app folder."""
    cands = []
    if explicit:
        cands.append(explicit)
    if _frozen() and getattr(sys, '_MEIPASS', None):
        cands.append(os.path.join(sys._MEIPASS, 'cmo_db_dashboard.template.html'))
    else:
        cands.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cmo_db_dashboard.template.html'))
    cands.append(os.path.join(_app_dir(), 'cmo_db_dashboard.template.html'))
    cands.append(os.path.join(os.getcwd(), 'cmo_db_dashboard.template.html'))
    for c in cands:
        if c and os.path.exists(c):
            return c
    return None

def _auto_db(folder):
    """Newest CMO database in folder: prefer the highest-numbered DB3K_*, then CWDB_*, else newest file."""
    dbs = [p for p in glob.glob(os.path.join(folder, '*.db3'))]
    if not dbs:
        return None
    def ver(p):
        # version is the number AFTER the prefix (DB3K_517 -> 517), not the "3" inside "DB3K".
        # Use the last digit-run of the name stem, so ".db3" and the "3" in "DB3K" don't win.
        stem = os.path.splitext(os.path.basename(p))[0]
        nums = re.findall(r'\d+', stem)
        return int(nums[-1]) if nums else -1
    db3k = [p for p in dbs if os.path.basename(p).upper().startswith('DB3K')]
    cwdb = [p for p in dbs if os.path.basename(p).upper().startswith('CWDB')]
    for group in (db3k, cwdb):
        if group:
            return max(group, key=ver)
    return max(dbs, key=os.path.getmtime)


def _auto_prev(folder, current):
    """The next-older database of the SAME family as `current` (for --vs auto).
    e.g. current DB3K_518 -> DB3K_517 if present. Returns a path or None."""
    cur = os.path.basename(current).upper()
    fam = 'DB3K' if cur.startswith('DB3K') else ('CWDB' if cur.startswith('CWDB') else None)
    if not fam:
        return None
    def ver(p):
        nums = re.findall(r'\d+', os.path.splitext(os.path.basename(p))[0])
        return int(nums[-1]) if nums else -1
    cv = ver(current)
    same = [p for p in glob.glob(os.path.join(folder, '*.db3'))
            if os.path.basename(p).upper().startswith(fam) and ver(p) < cv
            and os.path.abspath(p) != os.path.abspath(current)]
    return max(same, key=ver) if same else None

def _double_clicked():
    """Best-effort: True when launched by double-click on Windows — we own a brand-new console
    that closes on exit — so the window should pause. False when run from an existing terminal."""
    if os.name != 'nt':
        return False
    try:
        import ctypes
        return ctypes.windll.kernel32.GetConsoleProcessList((ctypes.c_uint * 2)(), 2) <= 1
    except Exception:
        return False

def _pause_before_exit():
    """Keep a double-clicked window (script or .exe) open so the user can read the result or error."""
    if _frozen() or _double_clicked():
        try:
            input('\nPress Enter to close...')
        except EOFError:
            pass

def run(a):
    autoselected = not a.db
    db = a.db or _auto_db(_app_dir())
    if not db:
        print("No CMO database (*.db3) found in this folder.")
        print("Put this file in your game's DB folder — the one that contains DB3K_517.db3")
        print("(usually ...\\Command Modern Operations\\DB) — and run it again.")
        return 1
    if not os.path.exists(db):
        print('Database not found:', db)
        return 1
    template = _find_template(a.template)
    if not template:
        print("Couldn't find cmo_db_dashboard.template.html.")
        print("Keep it next to build_dashboard.py, or pass --template <path>.")
        print("(The prebuilt build_dashboard.exe has the template built in.)")
        return 1

    dbname = os.path.splitext(os.path.basename(db))[0]
    out = a.out or os.path.join(os.path.dirname(os.path.abspath(db)), dbname + '_dashboard.html')

    if autoselected:
        n = len(glob.glob(os.path.join(_app_dir(), '*.db3')))
        print('Auto-selected %s (newest of %d database%s in this folder).'
              % (os.path.basename(db), n, '' if n == 1 else 's'))
        print('To build a different one, drag its .db3 file onto this program instead.\n')

    print('reading', db)
    try:
        ex = Extractor(db)
        data = ex.run()
    except (KeyError, IndexError, TypeError, sqlite3.Error) as e:
        print("\nCouldn't read %s — it may be an older or incompatible database version." % os.path.basename(db))
        print("Try the newest DB3K_*.db3 in your game's DB folder (this tool targets current CMO databases).")
        print("(details: %s)" % e)
        return 1
    data['meta']['file'] = os.path.basename(db)
    data['meta']['name'] = dbname
    data['meta']['size'] = os.path.getsize(db)

    # Zero-effort path: whenever we build a database and the user hasn't asked for a specific
    # comparison (--vs) or opted out (--no-changelog), automatically build a changelog against the
    # next-older database of the same family in the same folder if one is there. This covers both
    # double-clicking the .exe (newest is auto-picked) AND dragging a specific .db3 onto it.
    # Purely additive (adds a "What's new" page); silent if there's nothing older to compare against.
    if not a.vs and not a.no_changelog:
        pa = _auto_prev(_app_dir(), db)
        if pa:
            a.vs = pa
            print('Also building a "What\'s new" changelog vs the previous database (%s).'
                  % os.path.basename(pa))

    if a.vs:
        prev = a.vs
        if prev == 'auto':
            prev = _auto_prev(_app_dir(), db)
            if not prev:
                print('--vs auto: no older database found in this folder to compare against; skipping changelog.')
        if prev and prev != 'auto':
            if not os.path.exists(prev):
                print('--vs database not found:', prev)
                return 1
            print('building changelog:', os.path.basename(prev), '->', os.path.basename(db))
            try:
                cl = compute_changelog(ex.con, prev)
                cl['meta'] = {'from': _db_display_name(prev), 'to': dbname}
                data['changelog'] = cl
                ta = sum(len(v['added']) for v in cl['entities'].values())
                td = sum(len(v['deprecated']) for v in cl['entities'].values())
                tr = sum(len(v['removed']) for v in cl['entities'].values())
                tc = sum(len(v['changed']) for v in cl['entities'].values())
                print('  %d added, %d deprecated, %d removed, %d changed' % (ta, td, tr, tc))
            except sqlite3.Error as e:
                print('  could not build changelog (%s) — continuing without it.' % e)
    js = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
    if a.json:
        with open(a.json, 'w', encoding='utf-8') as f:
            f.write(js)
        print('json ->', a.json, len(js) // 1024, 'KB')
    raw = js.encode('utf-8')
    comp = zlib.compress(raw, 9)
    blob = base64.b64encode(comp).decode('ascii')
    print('json %.1f MB -> deflate %.1f MB -> base64 %.1f MB' % (len(raw) / 1e6, len(comp) / 1e6, len(blob) / 1e6))

    with open(template, 'r', encoding='utf-8') as f:
        html = f.read()
    marker = '/*__DB_BLOB__*/'
    if marker not in html:
        print('The template is missing its data marker — is cmo_db_dashboard.template.html intact?')
        return 1
    html = html.replace(marker, blob, 1)
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)

    print('\nSaved: %s  (%.1f MB)' % (os.path.abspath(out), os.path.getsize(out) / 1e6))
    print('This file is permanent — bookmark it or double-click it to reopen later, no rebuild needed.')
    print('Re-run this only when your game database updates.')
    if not a.no_open:
        try:
            webbrowser.open('file://' + os.path.abspath(out))
            print('Opening it now...')
        except Exception:
            print('Open the file above in your browser to view it.')
    return 0

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('db', nargs='?', help='DB3K_*.db3 / CWDB_*.db3 (optional; auto-detects the newest one in this folder)')
    ap.add_argument('-o', '--out', help='output HTML (default: <dbname>_dashboard.html next to the db)')
    ap.add_argument('-t', '--template', help='template HTML (default: bundled, or cmo_db_dashboard.template.html next to this script)')
    ap.add_argument('--json', help='also write the raw JSON to this path')
    ap.add_argument('--vs', metavar='PREV.db3',
                    help='build a Changelog page comparing this database against a previous one '
                         '(e.g. --vs DB3K_517.db3). Use --vs auto to pick the next-older database '
                         'of the same family found in this folder. By default the tool already '
                         'compares against the next-older database automatically; use this only to '
                         'name a specific one.')
    ap.add_argument('--no-changelog', action='store_true',
                    help='do not build the "What\'s new" changelog page, even if an older database '
                         'is present in the folder (builds just this one database).')
    ap.add_argument('--no-open', action='store_true', help='do not open the dashboard in a browser when finished')
    a = ap.parse_args()
    try:
        rc = run(a)
    except Exception as e:
        print('\nERROR:', e)
        rc = 1
    _pause_before_exit()
    sys.exit(rc)

if __name__ == '__main__':
    main()
