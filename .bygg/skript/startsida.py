"""Tar en skärmbild av startsidan på freeportsoul.se (1280×720, dubbel upplösning) med en valfri bild
i stället för reelen i bakgrunden. Så gjordes .bygg/startsida-2x.png (med AI-stämningsbilden
bilder/stamningsbilder/stamning-mikrofon-saxofon.jpg). Kräver nätverk. argv: bakgrundsbild utfil.png"""
import sys, base64
from playwright.sync_api import sync_playwright
bild, ut = sys.argv[1], sys.argv[2]
data = 'data:image/jpeg;base64,' + base64.b64encode(open(bild, 'rb').read()).decode()
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1280, 'height': 720}, device_scale_factor=2)
    pg.goto('https://freeportsoul.se', wait_until='load', timeout=60000); pg.wait_for_timeout(3000)
    pg.evaluate("""(d)=>new Promise(r=>{const v=document.querySelector('video');const i=document.createElement('img');
      i.className=v.className;const cs=getComputedStyle(v);
      for(const k of ['position','inset','width','height','objectFit','objectPosition','opacity','filter','zIndex']) i.style[k]=cs[k];
      i.onload=r;i.src=d;v.replaceWith(i);})""", data)
    pg.wait_for_timeout(500); pg.screenshot(path=ut); b.close()
print('klar', ut)
