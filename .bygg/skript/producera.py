"""Gör bokens bilder från källfotona enligt källa/bilder.json.
Tryckversion (300 ppi, exakt bildförhållande) och webbversion (högst 1600 px).
Körs från projektroten. argv: bilder.json ut-tryck ut-webb cube [id,id,...]"""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image, ImageOps
from bildfix import ladda, morka_bakgrund, guldtona, kanttona, load_cube

cfg = json.load(open(sys.argv[1], encoding='utf-8')); TRYCK, WEBB = sys.argv[2:4]; lut = load_cube(sys.argv[4])
bara = set(sys.argv[5].split(',')) if len(sys.argv) > 5 and sys.argv[5] else None
os.makedirs(TRYCK, exist_ok=True); os.makedirs(WEBB, exist_ok=True)
cache = {}
def kallbild(mid):
    if mid not in cache:
        m = cfg['motiv'][mid]; im, prof = ladda(m['fil'])
        if m.get('mörkare_bakgrund'): im = morka_bakgrund(im, m['mörkare_bakgrund'])
        cache.clear(); cache[mid] = (im, prof)
    return cache[mid]
rapport = []
for y in sorted(cfg['ytor'], key=lambda y: cfg['motiv'][y['motiv']]['fil']):
    if bara and y['id'] not in bara: continue
    m = cfg['motiv'][y['motiv']]; im, prof = kallbild(y['motiv']); W, H = im.size
    A = y['mm'][0] / y['mm'][1]
    cw, ch = (H * A, H) if W / H > A else (W, W / A)
    cw *= y.get('scale', 1); ch *= y.get('scale', 1)
    x0 = min(max(y['cx'] * W - cw / 2, 0), W - cw); y0 = min(max(y['cy'] * H - ch / 2, 0), H - ch)
    ut = im.crop((round(x0), round(y0), round(x0 + cw), round(y0 + ch)))
    if y.get('spegla'): ut = ImageOps.mirror(ut)
    ppi = ut.width / (y['mm'][0] / 25.4)
    tw, th = round(y['mm'][0] / 25.4 * 300), round(y['mm'][1] / 25.4 * 300)
    if ut.width >= tw: ut = ut.resize((tw, th), Image.LANCZOS)
    if not y.get('original') and not m.get('ingen_guldton'): ut = guldtona(ut, m, lut)
    if y.get('kanttoning'): ut = kanttona(ut, *y['kanttoning'])
    ut.save(os.path.join(TRYCK, y['id'] + '.jpg'), quality=92, optimize=True, subsampling=0)
    w = ut.copy(); w.thumbnail((1600, 1600), Image.LANCZOS)
    w.save(os.path.join(WEBB, y['id'] + '.jpg'), quality=82, optimize=True, progressive=True)
    rapport.append(dict(id=y['id'], fil=m['fil'], ppi=round(ppi), tryck=list(ut.size)))
    print(f"{y['id']:16} {m['fil']:28} {round(ppi):5d} ppi  {ut.size[0]}x{ut.size[1]}", flush=True)
    assert ppi >= 300, f"{y['id']} har bara {ppi:.0f} ppi"
json.dump(rapport, open(os.path.join(TRYCK, 'rapport.json'), 'w'), indent=1, ensure_ascii=False)
