"""Renderar sidor ur webbversionen till PNG, för att granska en ändring innan bygget.
argv: index.html utmapp [sidor, t.ex. 1,3,17; utan = alla]"""
import sys, os
from playwright.sync_api import sync_playwright
html, ut = sys.argv[1], sys.argv[2]; os.makedirs(ut, exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1123, 'height': 794}, device_scale_factor=1.6)
    pg.goto('file://' + os.path.abspath(html)); pg.emulate_media(media='print'); pg.wait_for_load_state('networkidle'); pg.wait_for_timeout(800)
    sek = pg.query_selector_all('section.page')
    nr = [int(x) for x in sys.argv[3].split(',')] if len(sys.argv) > 3 else range(1, len(sek) + 1)
    for n in nr: sek[n - 1].screenshot(path=os.path.join(ut, f's{n:02d}.png')); print('sida', n)
    b.close()
