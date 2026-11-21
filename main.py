#!/usr/bin/env python3
"""Republic of Zalvara — invented passport spread.

Renders one open-passport spread (1024x1024 PNG) to /output/entry.png.
Pure PIL, system fonts only, no network. All people, places, dates and
stamps are invented; every stamp date falls after the passport's issue
date (14 MAR 2024) and the stamps run in chronological order.
"""
import math
import os
from PIL import Image, ImageDraw, ImageFont

OUT = "/output/entry.png"
W, H = 1024, 1024

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


def font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except OSError:
        return ImageFont.load_default()


def text(d, xy, s, f, fill, anchor="la"):
    d.text(xy, s, font=f, fill=fill, anchor=anchor)


def centred(d, cx, y, s, f, fill):
    d.text((cx, y), s, font=f, fill=fill, anchor="ma")


def guilloche(d, box, colour, step=7):
    """Fine wavy guilloche-ish lines across a page, very faint."""
    x0, y0, x1, y1 = box
    for yy in range(y0, y1, step):
        pts = []
        for xx in range(x0, x1 + 1, 12):
            pts.append((xx, yy + 2.5 * math.sin(xx / 38.0 + yy / 23.0)))
        d.line(pts, fill=colour, width=1)


def emblem(d, cx, cy, r, ink):
    """Coat-of-arms-ish emblem: ring, eight-point star, shield."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=ink, width=3)
    d.ellipse([cx - r + 6, cy - r + 6, cx + r - 6, cy + r - 6],
              outline=ink, width=1)
    for k in range(8):
        a = math.pi * k / 4
        x1 = cx + (r - 8) * math.cos(a)
        y1 = cy + (r - 8) * math.sin(a)
        x2 = cx + (r - 22) * math.cos(a + math.pi / 8)
        y2 = cy + (r - 22) * math.sin(a + math.pi / 8)
        d.line([cx, cy, x1, y1], fill=ink, width=2)
        d.line([cx, cy, x2, y2], fill=ink, width=1)
    d.polygon([(cx - 13, cy - 4), (cx + 13, cy - 4), (cx + 9, cy + 12),
               (cx, cy + 19), (cx - 9, cy + 12)], outline=ink, width=2)


def portrait(d, box):
    """Stylised drawn portrait: dignified bust, suit, subtle shading.

    Rendered on its own layer so the backdrop arcs stay inside the frame.
    """
    x0, y0, x1, y1 = box
    bw, bh = x1 - x0, y1 - y0
    pimg = Image.new("RGB", (bw, bh), (58, 96, 104))
    pd = ImageDraw.Draw(pimg)
    # backdrop arcs (clipped to the frame by construction)
    for r in (150, 120, 92):
        pd.ellipse([75 - r, 60 - r, 75 + r, 60 + r],
                   outline=(86, 128, 136), width=1)
    # shoulders / suit
    pd.polygon([(8, bh), (30, 128), (62, 112), (88, 112), (120, 128),
                (bw - 8, bh)], fill=(38, 48, 74))
    pd.polygon([(62, 112), (75, 128), (88, 112), (75, 106)],
               fill=(244, 238, 222))
    pd.polygon([(70, 128), (75, 120), (80, 128), (78, 148), (72, 148)],
               fill=(122, 32, 40))
    # neck and head
    pd.rectangle([66, 92, 84, 116], fill=(214, 176, 142))
    pd.ellipse([48, 30, 102, 100], fill=(226, 190, 158))
    # hair: dark swept cap
    pd.pieslice([46, 24, 104, 78], 180, 360, fill=(52, 40, 34))
    pd.polygon([(48, 52), (102, 52), (100, 40), (50, 40)],
               fill=(52, 40, 34))
    # ears, brows, eyes, nose, mouth
    pd.ellipse([44, 58, 52, 74], fill=(226, 190, 158))
    pd.ellipse([98, 58, 106, 74], fill=(226, 190, 158))
    pd.line([58, 62, 70, 60], fill=(52, 40, 34), width=2)
    pd.line([80, 60, 92, 62], fill=(52, 40, 34), width=2)
    pd.ellipse([60, 66, 68, 71], fill=(40, 32, 26))
    pd.ellipse([82, 66, 90, 71], fill=(40, 32, 26))
    pd.line([75, 70, 73, 84], fill=(190, 150, 120), width=2)
    pd.line([66, 90, 84, 90], fill=(150, 90, 80), width=2)
    # soft cheek shading
    pd.ellipse([54, 76, 66, 86], fill=(214, 172, 140))
    pd.ellipse([84, 76, 96, 86], fill=(214, 172, 140))
    d._image.paste(pimg, (x0, y0))
    d.rectangle(box, outline=(70, 60, 40), width=2)


def stamp_circle(d, cx, cy, r, ink, lines, angle=0):
    """Circular arrival stamp, drawn on a transparent overlay then rotated."""
    size = int(2 * r + 24)
    ov = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    c = size // 2
    od.ellipse([c - r, c - r, c + r, c + r], outline=ink + (200,), width=3)
    od.ellipse([c - r + 9, c - r + 9, c + r - 9, c + r - 9],
               outline=ink + (200,), width=1)
    f1 = font(SANS_B, 13)
    f2 = font(SANS_B, 12)
    f3 = font(SANS, 11)
    od.text((c, c - r + 30), lines[0], font=f1, fill=ink + (215,),
            anchor="ma")
    od.text((c, c - 12), lines[1], font=f2, fill=ink + (215,), anchor="ma")
    od.text((c, c + 8), lines[2], font=f3, fill=ink + (215,), anchor="ma")
    od.text((c, c + r - 42), lines[3], font=f2, fill=ink + (215,),
            anchor="ma")
    ov = ov.rotate(angle, resample=Image.BICUBIC, expand=False)
    return ov, (cx - size // 2, cy - size // 2)


def stamp_rect(d, cx, cy, w, h, ink, lines, angle=0):
    size_w, size_h = w + 24, h + 24
    ov = Image.new("RGBA", (size_w, size_h), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.rectangle([10, 10, 10 + w, 10 + h], outline=ink + (205,), width=3)
    od.rectangle([14, 14, 10 + w - 4, 10 + h - 4], outline=ink + (160,),
                 width=1)
    f1 = font(SANS_B, 13)
    f2 = font(SANS, 11)
    y = 22
    for i, ln in enumerate(lines):
        od.text((size_w // 2, y), ln, font=f1 if i == 0 else f2,
                fill=ink + (215,), anchor="ma")
        y += 18
    ov = ov.rotate(angle, resample=Image.BICUBIC, expand=False)
    return ov, (cx - size_w // 2, cy - size_h // 2)


def main():
    img = Image.new("RGB", (W, H), (43, 37, 30))
    d = ImageDraw.Draw(img)
    # desk vignette + soft shadow under the spread
    for i in range(60):
        d.rectangle([0, H - 1 - i, W, H - i], fill=(43 - i // 6, 37 - i // 7,
                                                     30 - i // 8))
    d.rectangle([46, 108, 988, 948], fill=(0, 0, 0))
    # caption above the spread
    centred(d, 512, 34, "REPUBLIC OF ZALVARA  ·  PASSPORT  ·  OPEN SPREAD",
            font(SANS_B, 20), (232, 222, 200))
    centred(d, 512, 62, "An invented document — no real country, no real person",
            font(SANS, 15), (178, 168, 148))

    ink = (42, 38, 30)
    label = (110, 96, 74)
    page_l = (44, 92, 502, 936)
    page_r = (522, 92, 980, 936)
    for pg, fill in ((page_l, (246, 238, 216)), (page_r, (248, 241, 221))):
        d.rounded_rectangle(pg, radius=4, fill=fill, outline=(120, 104, 78),
                            width=2)
    guilloche(d, (page_l[0] + 8, page_l[1] + 8, page_l[2] - 8,
                  page_l[3] - 8), (214, 198, 168))
    guilloche(d, (page_r[0] + 8, page_r[1] + 8, page_r[2] - 8,
                  page_r[3] - 8), (216, 200, 170))

    # ---------------- LEFT PAGE: data page ----------------
    cx = (page_l[0] + page_l[2]) // 2
    emblem(d, cx, 152, 30, (96, 74, 40))
    centred(d, cx, 196, "REPUBLIC OF ZALVARA", font(SERIF_B, 25), ink)
    centred(d, cx, 226, "P A S S P O R T", font(SERIF_B, 19),
            (96, 74, 40))
    d.line([page_l[0] + 30, 258, page_l[2] - 30, 258], fill=(96, 74, 40),
           width=2)
    centred(d, cx, 266, "THE HIGHLAND REPUBLIC OF THE NORTHERN ISLES",
            font(SANS, 11), label)

    # portrait + fields
    portrait(d, (page_l[0] + 28, 296, page_l[0] + 178, 296 + 190))
    centred(d, page_l[0] + 103, 492, "HOLDER'S PORTRAIT", font(SANS, 10),
            label)
    fx = page_l[0] + 196
    fields = [
        ("SURNAME", "VOSS"),
        ("GIVEN NAMES", "ELENA MARIS"),
        ("NATIONALITY", "ZALVARAN"),
        ("DATE OF BIRTH", "12 JUN 1991"),
        ("PLACE OF BIRTH", "VELMARA, ZALVARA"),
        ("SEX", "F"),
    ]
    y = 300
    for lab, val in fields:
        text(d, (fx, y), lab, font(SANS, 11), label)
        text(d, (fx, y + 15), val, font(SERIF_B, 16), ink)
        y += 38
    d.line([page_l[0] + 28, 536, page_l[2] - 28, 536], fill=(150, 132, 100),
           width=1)
    # lower data block
    rows = [
        ("DATE OF ISSUE", "14 MAR 2024", "DATE OF EXPIRY", "14 MAR 2034"),
        ("DOCUMENT No.", "ZV 4829137", "TYPE", "P  ·  ORDINARY"),
    ]
    y = 552
    for l1, v1, l2, v2 in rows:
        text(d, (page_l[0] + 28, y), l1, font(SANS, 11), label)
        text(d, (page_l[0] + 28, y + 15), v1, font(SERIF_B, 16), ink)
        text(d, (page_l[0] + 252, y), l2, font(SANS, 11), label)
        text(d, (page_l[0] + 252, y + 15), v2, font(SERIF_B, 16), ink)
        y += 46
    text(d, (page_l[0] + 28, y), "AUTHORITY", font(SANS, 11), label)
    text(d, (page_l[0] + 28, y + 15),
         "MINISTRY OF THE INTERIOR", font(SERIF_B, 15), ink)
    text(d, (page_l[0] + 28, y + 34),
         "PASSPORT OFFICE — VELMARA", font(SERIF_B, 15), ink)
    text(d, (page_l[0] + 28, y + 56),
         "ISSUED IN ZALVARAN AND ENGLISH", font(SANS, 11), label)
    # MRZ
    mrz_y = 800
    d.rectangle([page_l[0] + 20, mrz_y - 8, page_l[2] - 20, mrz_y + 46],
                fill=(238, 230, 206), outline=(150, 132, 100), width=1)
    text(d, (page_l[0] + 28, mrz_y),
         "P<ZLVVOSS<<ELENA<MARIS<<<<<<<<<<<<<<<<<<<<", font(MONO, 13), ink)
    text(d, (page_l[0] + 28, mrz_y + 18),
         "ZV4829137<6ZLV9106128F3403145<<<<<<<<<<<<<<08", font(MONO, 13),
         ink)
    text(d, (page_l[0] + 28, 906), "PAGE 1 — DATA PAGE", font(SANS, 10),
         label)

    # ---------------- RIGHT PAGE: visas & stamps ----------------
    cxr = (page_r[0] + page_r[2]) // 2
    centred(d, cxr, 116, "VISAS — ARRIVALS & DEPARTURES", font(SERIF_B, 19),
            ink)
    centred(d, cxr, 142, "PAGES 4 – 5  ·  STAMPS IN CHRONOLOGICAL ORDER",
            font(SANS, 11), label)
    d.line([page_r[0] + 30, 168, page_r[2] - 30, 168], fill=(96, 74, 40),
           width=2)

    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    stamps = [
        ("circle", (page_r[0] + 118, 268), 62, (28, 84, 160),
         ["DRAVENHOLD", "KESTREL PORT", "ARRIVAL", "02 APR 2024"], -8),
        ("rect", (page_r[0] + 340, 268), (196, 108), (34, 122, 74),
         ["TALVORIA", "PORT MERIDIAN", "ARRIVAL", "27 SEP 2024"], 6),
        ("circle", (page_r[0] + 118, 452), 62, (104, 52, 140),
         ["OSTARA", "NORTH GATE", "DEPARTURE", "11 FEB 2025"], 10),
        ("rect", (page_r[0] + 340, 452), (196, 108), (28, 84, 160),
         ["ZALVARA — VELMARA", "ARRIVAL", "18 MAR 2025"], -6),
    ]
    for kind, (sx, sy), size, inkc, lines, ang in stamps:
        if kind == "circle":
            ov, pos = stamp_circle(d, sx, sy, size, inkc, lines, ang)
        else:
            ov, pos = stamp_rect(d, sx, sy, size[0], size[1], inkc, lines,
                                 ang)
        overlay.alpha_composite(ov, pos)
    img.paste(Image.alpha_composite(img.convert("RGBA"), overlay)
              .convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img)

    # visa-condition box — the telling paperwork detail
    vy = 560
    d.rectangle([page_r[0] + 28, vy, page_r[2] - 28, vy + 118],
                outline=(96, 74, 40), width=2)
    d.rectangle([page_r[0] + 32, vy + 4, page_r[2] - 32, vy + 114],
                outline=(150, 132, 100), width=1)
    centred(d, cxr, vy + 12, "VISA CONDITION — NORTHERN ISLES",
            font(SERIF_B, 14), (96, 74, 40))
    centred(d, cxr, vy + 36,
            "HOLDER MAY ENTER THE NORTHERN ISLES", font(SERIF_B, 14), ink)
    centred(d, cxr, vy + 56, "WITHOUT VISA — STAY MAX 90 DAYS",
            font(SERIF_B, 14), ink)
    centred(d, cxr, vy + 76, "IN ANY 180 DAYS  ·  NO PAID WORK",
            font(SERIF_B, 14), ink)
    centred(d, cxr, vy + 96, "CONDITION 7B — HIGHLAND TREATY 2019",
            font(SANS, 10), label)

    # fee stamp
    fov, fpos = stamp_rect(d, cxr - 90, 748, 210, 84, (150, 40, 40),
                          ["FEE PAID — 45 ZLV", "14 MAR 2024", "VELMARA"],
                          -7)
    tmp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    tmp.alpha_composite(fov, fpos)
    img.paste(Image.alpha_composite(img.convert("RGBA"), tmp).convert("RGB"),
              (0, 0))
    d = ImageDraw.Draw(img)
    text(d, (page_r[0] + 252, 716), "FEE STAMP", font(SANS, 11), label)
    text(d, (page_r[0] + 252, 734), "PAID AT ISSUE", font(SERIF_B, 14), ink)
    text(d, (page_r[0] + 252, 756), "RECEIPT No. 7714", font(SERIF_B, 14),
         ink)

    text(d, (page_r[0] + 28, 830),
         "HOLDER'S SIGNATURE ______________________", font(SERIF, 14), ink)
    text(d, (page_r[0] + 28, 856), "Elena Maris Voss", font(SERIF, 15), ink)
    centred(d, cxr, 884, "ALL STAMPS DATED AFTER ISSUE — 14 MAR 2024",
            font(SANS_B, 11), (96, 74, 40))
    text(d, (page_r[0] + 28, 906), "PAGES 4–5 — VISAS", font(SANS, 10),
         label)
    text(d, (page_r[2] - 28, 906), "ZLV · 4829137", font(SANS, 10), label,
         anchor="ra")

    os.makedirs("/output", exist_ok=True)
    img.save(OUT, "PNG", optimize=True)
    print("wrote", OUT, img.size, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
