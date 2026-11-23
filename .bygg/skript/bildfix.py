"""Gemensamma bildfunktioner för bygget: läsa in foton, mörka ner bakgrund, guldtona och tona kanter."""
import io
import numpy as np
from PIL import Image, ImageOps, ImageCms, ImageFilter
from lut import load_cube, apply_lut, pre_adjust

Image.MAX_IMAGE_PIXELS = None
SRGB = ImageCms.createProfile('sRGB')
MIDNATT = np.array([9, 9, 11], np.float32)


def ladda(sokvag):
    """Läser ett foto, roterar enligt EXIF och räknar om till sRGB. Returnerar (bild, profilnamn)."""
    im = Image.open(sokvag); icc = im.info.get('icc_profile')
    im = ImageOps.exif_transpose(im).convert('RGB'); namn = ''
    if icc:
        prof = ImageCms.ImageCmsProfile(io.BytesIO(icc)); namn = ImageCms.getProfileDescription(prof).strip()
        if 'sRGB' not in namn:
            im = ImageCms.profileToProfile(im, prof, SRGB, outputMode='RGB')
    return im, namn


def morka_bakgrund(im, steg):
    """Mörkar ner starkt mättade ytor (t.ex. en orange scengardin) med `steg` bländarsteg.
    Ljusa, omättade motiv som hud och vita skjortor lämnas orörda. Masken är mjukad så att inga kanter syns."""
    hsv = np.asarray(im.convert('HSV')).astype(np.float32) / 255
    t = np.clip((hsv[..., 1] - .62) / (.80 - .62), 0, 1); m = t * t * (3 - 2 * t)
    mi = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.GaussianBlur(im.width / 300))
    m = np.asarray(mi).astype(np.float32)[..., None] / 255
    a = np.asarray(im).astype(np.float32) * (1 - m * (1 - 2 ** -steg))
    return Image.fromarray(a.clip(0, 255).astype(np.uint8))


def guldtona(im, motiv, lut, rad=512):
    """Exponering och kontrast enligt motivet, sedan fsc-guldton.cube. Görs i band för att spara minne."""
    a = np.asarray(im); ut = np.empty_like(a)
    for y in range(0, a.shape[0], rad):
        t = a[y:y + rad].astype(np.float32) / 255
        t = apply_lut(pre_adjust(t, exposure=motiv.get('exp', 0), contrast=motiv.get('con', 0)), lut, motiv.get('str', 1.0))
        ut[y:y + rad] = (t * 255 + .5).clip(0, 255).astype(np.uint8)
    return Image.fromarray(ut)


def kanttona(im, sida, andel):
    """Tonar en kant mot Midnatt. Används där en CSS-toning täcker kanten helt, så att PDF-visare
    inte visar en ljus glipa mellan foto och toning. Syns inte i boken."""
    a = np.asarray(im).astype(np.float32)
    if sida in ('top', 'bottom'): a = a.transpose(1, 0, 2)
    n = max(2, round(a.shape[1] * andel)); t = np.arange(n) / n
    alfa = (1 - t * t * (3 - 2 * t))[None, :, None]
    forst = sida in ('left', 'top')
    sl = slice(0, n) if forst else slice(a.shape[1] - n, a.shape[1])
    if not forst: alfa = alfa[:, ::-1]
    a[:, sl] = a[:, sl] * (1 - alfa) + MIDNATT * alfa
    if sida in ('top', 'bottom'): a = a.transpose(1, 0, 2)
    return Image.fromarray(np.ascontiguousarray(a).clip(0, 255).round().astype(np.uint8))
