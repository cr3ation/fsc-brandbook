"""Skriver brandbook.pdf med tryckbilderna. Webbversionens index.html används som den är; bara
bildmappen byts mot tryckversionerna (300 ppi). argv: paketmapp tryckbilder arbetsmapp"""
import sys, os, re, shutil
from playwright.sync_api import sync_playwright
PAKET, TRYCK, ARB = sys.argv[1:4]
WEBB = os.path.join(PAKET, 'webbversion')
if os.path.exists(ARB): shutil.rmtree(ARB)
os.makedirs(os.path.join(ARB, 'img'))
shutil.copytree(os.path.join(WEBB, 'fonts'), os.path.join(ARB, 'fonts'))
html = open(os.path.join(WEBB, 'index.html'), encoding='utf-8').read()
for namn in sorted(set(re.findall(r'src="img/([^"]+)"', html))):
    k = os.path.join(TRYCK, namn)
    shutil.copy(k if os.path.exists(k) else os.path.join(WEBB, 'img', namn), os.path.join(ARB, 'img', namn))
open(os.path.join(ARB, 'index.html'), 'w', encoding='utf-8').write(html)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page()
    pg.goto('file://' + os.path.abspath(os.path.join(ARB, 'index.html'))); pg.emulate_media(media='print')
    pg.wait_for_load_state('networkidle'); pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(1000)
    trasiga = pg.evaluate("[...document.images].filter(i=>!i.complete||i.naturalWidth===0).map(i=>i.getAttribute('src'))")
    assert not trasiga, f'Bilder som inte laddar: {trasiga}'
    pg.pdf(path=os.path.join(PAKET, 'brandbook.pdf'), prefer_css_page_size=True, print_background=True)
    b.close()
print('brandbook.pdf klar')
