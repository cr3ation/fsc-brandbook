"""Öppnar webbversionen och kontrollerar att alla bilder laddar. argv: index.html"""
import sys, os
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1400, 'height': 900}); fel = []
    pg.on('requestfailed', lambda r: fel.append(r.url))
    pg.goto('file://' + os.path.abspath(sys.argv[1])); pg.wait_for_load_state('networkidle')
    pg.evaluate('window.scrollTo(0, document.body.scrollHeight)'); pg.wait_for_timeout(1000)
    bilder = pg.evaluate("[...document.images].map(i=>[i.getAttribute('src'), i.complete && i.naturalWidth>0])")
    trasiga = [s for s, ok in bilder if not ok]
    b.close()
assert not trasiga and not fel, f'Trasiga bilder: {trasiga} {fel}'
print(f'Webbversionen: {len(bilder)} bilder, alla laddar')
