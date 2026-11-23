"""Lägger in ett nytt foto som mästerfil: bilder/live-original/live-<namn>-original.jpg.
Roterar enligt EXIF, räknar om till sRGB, tar bort EXIF (ingen GPS eller kamerainfo) och sparar i högsta kvalitet.
Med --morkare N mörkas starkt mättade bakgrunder (t.ex. en orange gardin) med N steg.
Körs från projektroten. argv: kamerafil namn [--morkare N]"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from bildfix import ladda, morka_bakgrund, SRGB_ICC
fil, namn = sys.argv[1], sys.argv[2]
im, prof = ladda(fil)
if '--morkare' in sys.argv: im = morka_bakgrund(im, float(sys.argv[sys.argv.index('--morkare') + 1]))
ut = f'bilder/live-original/live-{namn}-original.jpg'
im.save(ut, quality=95, subsampling=0, optimize=True, icc_profile=SRGB_ICC)
print(ut, im.size, prof or 'sRGB')
