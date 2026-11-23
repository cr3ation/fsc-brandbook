"""Guldtonade versioner av mästerfilerna: bilder/live-original/*-original.jpg -> bilder/live-guldton/*-guldton.jpg.
Körs från projektroten. argv: bilder.json cube"""
import sys, os, json
sys.path.insert(0, os.path.dirname(__file__))
from PIL import ImageCms
from bildfix import ladda, guldtona, load_cube, SRGB

cfg = json.load(open(sys.argv[1], encoding='utf-8')); lut = load_cube(sys.argv[2]); UT = 'bilder/live-guldton'
icc = ImageCms.ImageCmsProfile(SRGB).tobytes(); os.makedirs(UT, exist_ok=True)
for f in os.listdir(UT): os.remove(os.path.join(UT, f))
for m in cfg['motiv'].values():
    if 'paketnamn' not in m: continue
    im, _ = ladda(m['fil'])
    guldtona(im, m, lut).save(os.path.join(UT, f"live-{m['paketnamn']}-guldton.jpg"), quality=92, optimize=True, icc_profile=icc)
    print(f"live-{m['paketnamn']}-guldton.jpg  {im.size[0]}x{im.size[1]}", flush=True)
