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
        out['weaponWRA'] = self.grouped('DataWeaponWRA', fn=lambda r: [r['CodeID'], r['WeaponQty'], r['ShooterQty'], r['AutoFireRange'], r['SelfDefenceRange']])
        out['warhead'] = self.table('DataWarhead')
        out['weaponRecord'] = {r['ID']: [r['ComponentID'], r['DefaultLoad'], r['MaxLoad'], r['ROF'], r['Multiple']]
                               for r in self.con.execute('select * from DataWeaponRecord')}
        out['mount'] = self.table('DataMount')
        out['mountWeapons'] = self.grouped('DataMountWeapons')
        out['mountMagWeapons'] = self.grouped('DataMountMagazineWeapons')
        out['mountSensors'] = self.grouped('DataMountSensors')
        out['mountDirectors'] = self.grouped('DataMountDirectors')
        out['magazine'] = self.table('DataMagazine')
        out['magazineWeapons'] = self.grouped('DataMagazineWeapons')
        out['loadout'] = self.table('DataLoadout')
        out['loadoutWeapons'] = self.grouped('DataLoadoutWeapons', fn=lambda r: [r['ComponentID'], norm(r['Optional']), norm(r['Internal'])])
        out['propulsion'] = self.table('DataPropulsion', drop=('Comments',))
        out['propPerf'] = self.grouped('DataPropulsionPerformance', fn=lambda r: [r['AltitudeBand'], r['Throttle'], r['Speed'], norm(r['AltitudeMin']), norm(r['AltitudeMax']), norm(r['Consumption'])])
        out['fuel'] = {r['ID']: [r['Type'], r['Capacity']] for r in self.con.execute('select * from DataFuel')}
        out['comm'] = self.table('DataComm', drop=('Comments',))
        out['acfacility'] = {r['ID']: [r['Type'], r['PhysicalSize'], r['Capacity'], r['RunwayLength']] for r in self.con.execute('select * from DataAircraftFacility')}
        out['dockfacility'] = self.table('DataDockingFacility') if self.has('DataDockingFacility') else None
        for kind in ['Aircraft', 'Ship', 'Submarine', 'Facility', 'GroundUnit']:
            out[kind] = self.platform(kind)
        out['meta']['extracted'] = time.strftime('%Y-%m-%d %H:%M:%S')
        out['meta']['seconds'] = round(time.time() - t0, 1)
        return out

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
        m = re.search(r'(\d+)', os.path.basename(p))
        return int(m.group(1)) if m else -1
    db3k = [p for p in dbs if os.path.basename(p).upper().startswith('DB3K')]
    cwdb = [p for p in dbs if os.path.basename(p).upper().startswith('CWDB')]
    for group in (db3k, cwdb):
        if group:
            return max(group, key=ver)
    return max(dbs, key=os.path.getmtime)

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

    print('reading', db)
    ex = Extractor(db)
    data = ex.run()
    data['meta']['file'] = os.path.basename(db)
    data['meta']['name'] = dbname
    data['meta']['size'] = os.path.getsize(db)
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
    print('wrote', out, '(%.1f MB)' % (os.path.getsize(out) / 1e6))

    if not a.no_open:
        try:
            webbrowser.open('file://' + os.path.abspath(out))
            print('opening in your browser...')
        except Exception:
            print('(open %s in your browser)' % out)
    return 0

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('db', nargs='?', help='DB3K_*.db3 / CWDB_*.db3 (optional; auto-detects the newest one in this folder)')
    ap.add_argument('-o', '--out', help='output HTML (default: <dbname>_dashboard.html next to the db)')
    ap.add_argument('-t', '--template', help='template HTML (default: bundled, or cmo_db_dashboard.template.html next to this script)')
    ap.add_argument('--json', help='also write the raw JSON to this path')
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
