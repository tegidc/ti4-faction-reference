# usage: python3 -I process.py factions.json rawdir outdir manifest.json
import json, sys, os, re
from PIL import Image
fj, raw, out, man = sys.argv[1:5]
SHORT = {
 'arborec':"Arborec",'argent':"Argent Flight",'letnev':"Barony of Letnev",'saar':"Clan of Saar",
 'keleres':"Council Keleres",'muaat':"Embers of Muaat",'hacan':"Emirates of Hacan",'empyrean':"Empyrean",
 'sol':"Federation of Sol",'creuss':"Ghosts of Creuss",'l1z1x':"L1Z1X Mindnet",'mahact':"Mahact Gene-Sorcerers",
 'mentak':"Mentak Coalition",'naalu':"Naalu Collective",'naaz-rokha':"Naaz-Rokha Alliance",'nekro':"Nekro Virus",
 'nomad':"Nomad",'norr':"Sardakk N'orr",'ul':"Titans of Ul",'jol-nar':"Universities of Jol-Nar",
 'vuilraith':"Vuil'raith Cabal",'winnu':"Winnu",'xxcha':"Xxcha Kingdom",'yin':"Yin Brotherhood",'yssaril':"Yssaril Tribes",
 'crimson':"Crimson Rebellion",'deepwrought':"Deepwrought Scholarate",'firmament':"Firmament / Obsidian",
 'bastion':"Last Bastion",'ral-nel':"Ral Nel Consortium"}
SORT = {  # name players call them, used for A-Z
 'arborec':'Arborec','argent':'Argent','letnev':'Letnev','saar':'Saar','keleres':'Keleres','muaat':'Muaat','hacan':'Hacan',
 'empyrean':'Empyrean','sol':'Sol','creuss':'Creuss','l1z1x':'L1Z1X','mahact':'Mahact','mentak':'Mentak','naalu':'Naalu',
 'naaz-rokha':'Naaz-Rokha','nekro':'Nekro','nomad':'Nomad','norr':"Sardakk N'orr",'ul':'Titans of Ul','jol-nar':'Jol-Nar',
 'vuilraith':"Vuil'raith",'winnu':'Winnu','xxcha':'Xxcha','yin':'Yin','yssaril':'Yssaril','crimson':'Crimson',
 'deepwrought':'Deepwrought','firmament':'Firmament / Obsidian','bastion':'Last Bastion','ral-nel':'Ral Nel'}
EDRANK = {'base':0,'pok':1,'codex1':2,'codex2':3,'codex3':4,'te':5}
def rank(c): return (int(c.get('version') or 0), EDRANK.get(c.get('edition'),0))
LABEL = {'tech':'Faction tech','promissory-note':'Promissory note','leader':'Leader','mech':'Mech','breakthrough':'Breakthrough',
         'planet':'Planet','legendary-planet-ability':'Legendary planet','sheet':'Faction sheet'}
ORDER = ['tech','promissory-note','leader','breakthrough','planet','legendary-planet-ability']
def conv(src, dst, maxd):
    im = Image.open(src); im.load()
    if im.mode not in ('RGB','RGBA'): im = im.convert('RGBA')
    im.thumbnail((maxd, maxd), Image.LANCZOS)
    im.save(dst, 'WEBP', quality=82, method=6)
    return im.size
res = []
for f in json.load(open(fj)):
    k = f['key']; d = os.path.join(out, k); os.makedirs(d, exist_ok=True)
    best = {}
    for c in f['components']:
        if c['type'] == 'tokens': continue
        t = 'reference-card' if c['type'].startswith('reference-card') else c['type']
        if t == 'leader' and 'commander-back' in c['key'] or c['key'].endswith('-back') : continue
        kk = (t, c['key'])
        if kk not in best or rank(c) > rank(best[kk]): best[kk] = c
    def item(c, maxd):
        src = os.path.join(raw, c['image_path'])
        name = re.sub(r'\.(jpg|png|jpeg)$', '.webp', os.path.basename(c['image_path']))
        name = re.sub(r'[^a-z0-9.-]', '', (c['type'] + '-' + name.replace('.face', '')).lower())
        w, h = conv(src, os.path.join(d, name), maxd)
        t = 'reference-card' if c['type'].startswith('reference-card') else c['type']
        return dict(src=f'cards/{k}/{name}', w=w, h=h, kind=LABEL.get(t, t), key=c['key'])
    comps = list(best.values())
    ref = [c for c in comps if c['type'].startswith('reference-card')]
    sheets = [c for c in comps if c['type']=='sheet']
    mechs = [c for c in comps if c['type']=='mech']
    special = sorted([c for c in comps if c['type'] in ORDER], key=lambda c: ORDER.index(c['type']))
    entry = dict(key=k, name=SHORT[k], full=f['name'], sort=SORT[k], edition=f['edition'],
        overview=[item(c,1400) for c in ref],
        units=[item(c,1800) for c in sheets]+[item(c,900) for c in mechs],
        special=[item(c,900) for c in special])
    # thumbnail: portrait crop from TE reference card's top-left corner
    rc = os.path.join(raw, ref[-1]['image_path']); im = Image.open(rc).convert('RGB')
    W, H = im.size; crop = im.crop((int(W*.005), 0, int(W*.235), int(H*.30)))
    crop.thumbnail((160,160), Image.LANCZOS); crop.save(os.path.join(d,'thumb.webp'),'WEBP',quality=80)
    entry['thumb'] = f'cards/{k}/thumb.webp'
    res.append(entry)
    print(k, len(entry['overview']), len(entry['units']), len(entry['special']))
res.sort(key=lambda e: e['sort'].lower())
json.dump(res, open(man,'w'), indent=1)
