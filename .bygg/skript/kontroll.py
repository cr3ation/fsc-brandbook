"""Kontrollerar PDF:en: antal sidor, sidformat och att varje foto ligger på minst 300 ppi.
Renderar dessutom alla sidor till PNG för granskning. argv: brandbook.pdf sidantal png-mapp"""
import sys, os, fitz
pdf, sidor, ut = sys.argv[1], int(sys.argv[2]), sys.argv[3]
d = fitz.open(pdf); r = d[0].rect
print(f'{len(d)} sidor, {r.width/72*25.4:.0f}×{r.height/72*25.4:.0f} mm')
assert len(d) == sidor, f'Boken ska ha {sidor} sidor (tryckeriets krav), men har {len(d)}'
lag = []
for nr, s in enumerate(d, 1):
    for img in s.get_images(full=True):
        for rect in s.get_image_rects(img[0]):
            if rect.width < 20: continue
            ppi = img[2] / (rect.width / 72)
            print(f'  s.{nr:<3}{img[2]}×{img[3]} px på {rect.width/72*25.4:.1f}×{rect.height/72*25.4:.1f} mm = {ppi:.0f} ppi')
            if ppi < 295: lag.append((nr, round(ppi)))
assert not lag, f'Bilder under 300 ppi: {lag}'
os.makedirs(ut, exist_ok=True)
for nr, s in enumerate(d, 1): s.get_pixmap(dpi=110).save(os.path.join(ut, f's{nr:02d}.png'))
print('PDF:en är godkänd')
