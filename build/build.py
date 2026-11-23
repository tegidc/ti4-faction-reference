# usage: python3 -E build/build.py  (run from the project folder) -> writes index.html from template.html
import json, re, os
here = os.path.dirname(os.path.abspath(__file__))
t = open('template.html').read()
d = json.load(open(os.path.join(here, 'manifest.json')))
full = json.load(open(os.path.join(here, 'unlocks.json')))
short = json.load(open(os.path.join(here, 'unlock_short.json')))
for f in d:
    # faction techs that upgrade a unit (Strike Wing Alpha II, Exotrireme II …) belong with the units
    up = [x for x in f['special'] if x['kind'] == 'Faction tech' and re.search(r'-ii$', x['key'])]
    for x in up: x['kind'] = 'Unit upgrade'
    f['special'] = [x for x in f['special'] if x not in up]
    f['units'] = f['units'] + up
    # leaders: role + what unlocks them
    for x in f['special']:
        if x['kind'] != 'Leader': continue
        k = x['key']; sub = 'obsidian' if 'obsidian' in k else ('firmament' if 'firmament' in k else '')
        role = 'agent' if k.startswith('agent') else 'commander' if k.startswith('commander') else 'hero'
        x['role'] = role
        if role == 'commander':
            x['unlock'] = short['firmament-obsidian' if sub == 'obsidian' else f['key']]
            x['unlockFull'] = full[f['key']]['commander' + ('-' + sub if sub else '')]
        elif role == 'hero':
            x['unlock'] = '3 scored objectives'
            x['unlockFull'] = 'Have 3 scored objectives'
open('index.html', 'w').write(t.replace('/*DATA*/', json.dumps(d, separators=(',', ':'))))
print('built index.html')
