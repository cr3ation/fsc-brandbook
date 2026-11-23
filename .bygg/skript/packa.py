"""Zippar boken (projektroten utan dolda mappar och zipfiler) som Freeport-Soul-Collective-Brandbook/.
Namn med å/ä/ö sparas som UTF-8. Körs från projektroten. argv: zipfil"""
import sys, os, zipfile
ut = sys.argv[1]; TOPP = 'Freeport-Soul-Collective-Brandbook'
os.makedirs(os.path.dirname(os.path.abspath(ut)), exist_ok=True)
with zipfile.ZipFile(ut, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    z.write('.', TOPP + '/')
    for rot, mappar, filer in os.walk('.'):
        mappar[:] = sorted(d for d in mappar if not d.startswith('.') and d != '__pycache__')
        rel = os.path.normpath(os.path.join(TOPP, rot))
        if rot != '.': z.write(rot, rel + '/')
        for f in sorted(filer):
            if f.startswith('.') or (rot == '.' and f.endswith('.zip')): continue
            z.write(os.path.join(rot, f), os.path.join(rel, f))
print(ut, f'{os.path.getsize(ut)/1e6:.1f} MB')
