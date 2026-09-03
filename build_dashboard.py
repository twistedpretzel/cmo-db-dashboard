#!/usr/bin/env python3
"""
build_dashboard.py — extract a Command: Modern Operations database (DB3K_*.db3 or CWDB_*.db3)
into a single self-contained HTML dashboard.

Usage (from the DB folder, where cmo_db_dashboard.template.html lives):
    python build_dashboard.py DB3K_517.db3                 # -> DB3K_517_dashboard.html
    python build_dashboard.py DB3K_518.db3                 # any newer DB3K works the same way
    python build_dashboard.py CWDB_517.db3                 # Cold War database (images from Images/CWDB)
    python build_dashboard.py DB3K_517.db3 -o my.html
    python build_dashboard.py DB3K_517.db3 --json out.json # also dump the raw JSON for inspection

Keep the generated HTML inside the DB folder so its relative Images/DB3000/*.webp links resolve.
Takes ~10 s; output is ~5 MB and opens directly in Chrome/Edge/Firefox (no server needed).

The script reads the database read-only, packs the tables the dashboard needs into a compact
column/row JSON structure, deflates it, base64-encodes it and injects it into
cmo_db_dashboard.template.html at the marker  /*__DB_BLOB__*/ .

Only the Python standard library is required.
"""
import argparse, base64, json, os, sqlite3, sys, time, zlib

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

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('db', help='path to DB3K_*.db3 / CWDB_*.db3')
    ap.add_argument('-o', '--out', help='output HTML (default: <dbname>_dashboard.html next to the db)')
    ap.add_argument('-t', '--template', help='template HTML (default: cmo_db_dashboard.template.html next to this script)')
    ap.add_argument('--json', help='also write the raw JSON to this path')
    a = ap.parse_args()

    here = os.path.dirname(os.path.abspath(__file__))
    template = a.template or os.path.join(here, 'cmo_db_dashboard.template.html')
    if not os.path.exists(template):
        sys.exit('template not found: %s' % template)
    dbname = os.path.splitext(os.path.basename(a.db))[0]
    out = a.out or os.path.join(os.path.dirname(os.path.abspath(a.db)), dbname + '_dashboard.html')

    print('reading', a.db)
    ex = Extractor(a.db)
    data = ex.run()
    data['meta']['file'] = os.path.basename(a.db)
    data['meta']['name'] = dbname
    data['meta']['size'] = os.path.getsize(a.db)
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
    assert marker in html, 'marker not found in template'
    html = html.replace(marker, blob, 1)
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    print('wrote', out, '(%.1f MB)' % (os.path.getsize(out) / 1e6))

if __name__ == '__main__':
    main()
