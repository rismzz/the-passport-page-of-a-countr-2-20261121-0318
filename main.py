#!/usr/bin/env python3
"""Republic of Zalvara - invented passport spread.

Renders one open-passport spread (1024x1024 PNG) to entry.png.
Pure Python 3.13 standard library only (os, math, struct, zlib):
a small raster canvas, a built-in 5x7 bitmap font, and a hand-written
PNG encoder. No third-party imports of any kind.

All people, places, dates and stamps are invented; every stamp date
falls after the passport's issue date (14 MAR 2024) and the stamps run
in chronological order.
"""
import math
import os
import struct
import zlib

OUT = os.path.join(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"),
                   "entry.png")
W, H = 1024, 1024

# ---------------------------------------------------------------- font
# 5x7 bitmap glyphs. '#' is an inked pixel, '.' is blank.
_G = {
"A": ("###..", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
"B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
"C": (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
"D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
"E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
"F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
"G": (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."),
"H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
"I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
"J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
"K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
"L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
"M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
"N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
"O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
"P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
"Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
"R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
"S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
"T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
"U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
"V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
"W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
"X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
"Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
"Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
"a": (".....", ".....", ".####", "....#", ".####", "#...#", ".####"),
"b": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
"c": (".....", ".....", ".###.", "#...#", "#....", "#...#", ".###."),
"d": ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
"e": (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
"f": ("..##.", ".#..#", ".#...", "####.", ".#...", ".#...", ".#..."),
"g": (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
"h": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
"i": (".....", "..#..", ".....", ".##..", "..#..", "..#..", ".###."),
"j": (".....", "...#.", ".....", "..##.", "...#.", "...#.", "...#.", ),
"k": ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
"l": (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
"m": (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
"n": (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
"o": (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
"p": (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
"q": (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
"r": (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
"s": (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
"t": (".#...", ".#...", "####.", ".#...", ".#...", ".#...", "..##."),
"u": (".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"),
"v": (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
"w": (".....", ".....", "#...#", "#...#", "#.#.#", "#.#.#", ".#.#."),
"x": (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
"y": (".....", ".....", "#...#", "#...#", "#...#", ".####", "....#"),
"z": (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
"0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
"1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
"2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
"3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
"4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
"5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
"6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
"7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
"8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
"9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
" ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
"-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
"\u2014": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
"\u2013": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
"\u00b7": (".....", ".....", ".##..", ".##..", ".....", ".....", "....."),
"<": ("...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."),
">": ("#....", ".#...", "..#..", "...#.", "..#..", ".#...", "#...."),
"/": ("....#", "...#.", "...#.", "..#..", "..#..", ".#...", "#...."),
":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
"(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
"&": (".##..", "#..#.", "#.#..", ".#...", "#.##.", "#..#.", ".##.#"),
"'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
"!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
"?": (".###.", "#...#", "#...#", "....#", "..#..", ".....", "..#.."),
"+": (".....", ".....", "..#..", ".###.", "..#..", ".....", "....."),
"=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
'"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
"_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
"%": ("##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"),
"#": (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
"*": (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
}
# fix the truncated 'j' glyph (7 rows required)
_G["j"] = (".....", "...#.", ".....", "..##.", "...#.", "...#.", ".##..")
_G["g"] = (".....", ".....", ".####", "#...#", "#...#", ".####", "....#")
_G["y"] = (".....", ".....", "#...#", "#...#", "#...#", ".####", ".###.")


def text_width(s, sx):
    return len(s) * int(round(6 * sx)) - int(round(sx))


def draw_text(cv, x, y, s, sx, sy, colour, align="left"):
    """Draw string s with its top-left at (x, y); sx/sy may be fractional."""
    w = text_width(s, sx)
    if align == "center":
        x -= w // 2
    elif align == "right":
        x -= w
    cx = x
    adv = 6 * sx
    for ch in s:
        glyph = _G.get(ch, _G["?"])
        for gy in range(7):
            row = glyph[gy]
            y0 = int(round(y + gy * sy))
            y1 = int(round(y + (gy + 1) * sy))
            for gx in range(5):
                if row[gx] != "#":
                    continue
                x0 = int(round(cx + gx * sx))
                x1 = int(round(cx + (gx + 1) * sx))
                cv.fill_rect(x0, y0, x1, y1, colour)
        cx += adv


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(w * h * 3)
        r, g, b = bg
        for i in range(w * h):
            self.px[3 * i] = r
            self.px[3 * i + 1] = g
            self.px[3 * i + 2] = b

    def set(self, x, y, colour):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = 3 * (y * self.w + x)
            self.px[i], self.px[i + 1], self.px[i + 2] = colour

    def fill_rect(self, x0, y0, x1, y1, colour):
        x0 = max(0, int(x0)); y0 = max(0, int(y0))
        x1 = min(self.w, int(x1)); y1 = min(self.h, int(y1))
        for y in range(y0, y1):
            base = 3 * (y * self.w + x0)
            for x in range(x0, x1):
                i = base + 3 * (x - x0)
                self.px[i], self.px[i + 1], self.px[i + 2] = colour

    def rect(self, x0, y0, x1, y1, colour, width=1):
        for k in range(width):
            self.fill_rect(x0 + k, y0 + k, x1 - k, y0 + k + 1, colour)
            self.fill_rect(x0 + k, y1 - k - 1, x1 - k, y1 - k, colour)
            self.fill_rect(x0 + k, y0 + k, x0 + k + 1, y1 - k, colour)
            self.fill_rect(x1 - k - 1, y0 + k, x1 - k, y1 - k, colour)

    def line(self, x0, y0, x1, y1, colour, width=1):
        dx = x1 - x0
        dy = y1 - y0
        steps = max(abs(dx), abs(dy), 1)
        r = width // 2
        for i in range(steps + 1):
            t = i / steps
            x = int(round(x0 + dx * t))
            y = int(round(y0 + dy * t))
            self.fill_rect(x - r, y - r, x + r + 1, y + r + 1, colour)

    def circle(self, cx, cy, r, colour, width=1):
        for k in range(width):
            rr = r - k
            if rr <= 0:
                break
            n = max(24, int(2 * math.pi * rr))
            for i in range(n):
                a = 2 * math.pi * i / n
                self.set(int(round(cx + rr * math.cos(a))),
                         int(round(cy + rr * math.sin(a))), colour)

    def fill_circle(self, cx, cy, r, colour):
        for y in range(cy - r, cy + r + 1):
            dy = y - cy
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self.fill_rect(cx - dx, y, cx + dx + 1, y + 1, colour)

    def ellipse(self, cx, cy, rx, ry, colour, width=1):
        for k in range(width):
            n = max(32, int(2 * math.pi * max(rx, ry)))
            for i in range(n):
                a = 2 * math.pi * i / n
                self.set(int(round(cx + (rx - k) * math.cos(a))),
                         int(round(cy + (ry - k) * math.sin(a))), colour)

    def fill_ellipse(self, cx, cy, rx, ry, colour):
        for y in range(cy - ry, cy + ry + 1):
            dy = (y - cy) / ry
            dx = int(rx * math.sqrt(max(0.0, 1.0 - dy * dy)))
            self.fill_rect(cx - dx, y, cx + dx + 1, y + 1, colour)

    def polygon(self, pts, colour):
        """Scanline-filled polygon."""
        if len(pts) < 3:
            return
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    t = (y - y0) / (y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.fill_rect(int(round(xs[i])), y,
                               int(round(xs[i + 1])) + 1, y + 1, colour)

    def polyline(self, pts, colour, width=1):
        for i in range(len(pts) - 1):
            self.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
                      colour, width)


class StampCanvas:
    """Small RGBA canvas for a stamp, rotated and blended onto the page."""
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.rgb = bytearray(w * h * 3)
        self.a = bytearray(w * h)

    def set(self, x, y, colour, alpha):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = y * self.w + x
            self.rgb[3 * i:3 * i + 3] = bytes(colour)
            self.a[i] = alpha

    def fill_rect(self, x0, y0, x1, y1, colour, alpha=255):
        for y in range(max(0, y0), min(self.h, y1)):
            for x in range(max(0, x0), min(self.w, x1)):
                self.set(x, y, colour, alpha)

    def rect(self, x0, y0, x1, y1, colour, alpha=255, width=1):
        for k in range(width):
            self.fill_rect(x0 + k, y0 + k, x1 - k, y0 + k + 1, colour, alpha)
            self.fill_rect(x0 + k, y1 - k - 1, x1 - k, y1 - k, colour, alpha)
            self.fill_rect(x0 + k, y0 + k, x0 + k + 1, y1 - k, colour, alpha)
            self.fill_rect(x1 - k - 1, y0 + k, x1 - k, y1 - k, colour, alpha)

    def circle(self, cx, cy, r, colour, alpha=255, width=1):
        for k in range(width):
            rr = r - k
            if rr <= 0:
                break
            n = max(24, int(2 * math.pi * rr))
            for i in range(n):
                a = 2 * math.pi * i / n
                self.set(int(round(cx + rr * math.cos(a))),
                         int(round(cy + rr * math.sin(a))), colour, alpha)

    def text(self, x, y, s, sx, sy, colour, alpha=255, align="left"):
        w = text_width(s, sx)
        if align == "center":
            x -= w // 2
        elif align == "right":
            x -= w
        cx = x
        for ch in s:
            glyph = _G.get(ch, _G["?"])
            for gy in range(7):
                row = glyph[gy]
                y0 = int(round(y + gy * sy))
                y1 = int(round(y + (gy + 1) * sy))
                for gx in range(5):
                    if row[gx] != "#":
                        continue
                    x0 = int(round(cx + gx * sx))
                    x1 = int(round(cx + (gx + 1) * sx))
                    self.fill_rect(x0, y0, x1, y1, colour, alpha)
            cx += 6 * sx


def blit_rotated(page, stamp, cx, cy, angle_deg):
    """Paste stamp centred at (cx, cy), rotated angle_deg, alpha-blended."""
    ang = math.radians(angle_deg)
    ca, sa = math.cos(ang), math.sin(ang)
    hw, hh = stamp.w / 2.0, stamp.h / 2.0
    corners = [(x, y) for x in (-hw, hw) for y in (-hh, hh)]
    rot = [(x * ca - y * sa, x * sa + y * ca) for x, y in corners]
    x0 = int(cx + min(p[0] for p in rot)) - 1
    x1 = int(cx + max(p[0] for p in rot)) + 1
    y0 = int(cy + min(p[1] for p in rot)) - 1
    y1 = int(cy + max(p[1] for p in rot)) + 1
    for dy in range(max(0, y0), min(page.h, y1 + 1)):
        for dx in range(max(0, x0), min(page.w, x1 + 1)):
            rx, ry = dx - cx, dy - cy
            sx = rx * ca + ry * sa + hw
            sy = -rx * sa + ry * ca + hh
            ix, iy = int(sx), int(sy)
            if 0 <= ix < stamp.w and 0 <= iy < stamp.h:
                al = stamp.a[iy * stamp.w + ix]
                if al == 0:
                    continue
                i = 3 * (dy * page.w + dx)
                j = 3 * (iy * stamp.w + ix)
                for k in range(3):
                    page.px[i + k] = (stamp.rgb[j + k] * al +
                                      page.px[i + k] * (255 - al)) // 255


# ---------------------------------------------------------------- PNG
def write_png(cv, path):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 6)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


# ---------------------------------------------------------------- pieces
def guilloche(cv, box, colour, step=7):
    x0, y0, x1, y1 = box
    for yy in range(y0, y1, step):
        pts = []
        for xx in range(x0, x1 + 1, 12):
            pts.append((xx, int(round(yy + 2.5 * math.sin(xx / 38.0 +
                                                         yy / 23.0)))))
        cv.polyline(pts, colour, 1)


def emblem(cv, cx, cy, r, ink):
    cv.circle(cx, cy, r, ink, 3)
    cv.circle(cx, cy, r - 6, ink, 1)
    for k in range(8):
        a = math.pi * k / 4
        x1 = cx + (r - 8) * math.cos(a)
        y1 = cy + (r - 8) * math.sin(a)
        x2 = cx + (r - 22) * math.cos(a + math.pi / 8)
        y2 = cy + (r - 22) * math.sin(a + math.pi / 8)
        cv.line(cx, cy, int(round(x1)), int(round(y1)), ink, 2)
        cv.line(cx, cy, int(round(x2)), int(round(y2)), ink, 1)
    cv.polygon([(cx - 13, cy - 4), (cx + 13, cy - 4), (cx + 9, cy + 12),
                (cx, cy + 19), (cx - 9, cy + 12)], ink)


def portrait(cv, box):
    x0, y0, x1, y1 = box
    bw, bh = x1 - x0, y1 - y0
    p = Canvas(bw, bh, (58, 96, 104))
    # backdrop arcs (clipped to the frame by construction)
    for r in (150, 120, 92):
        p.ellipse(75, 60, r, r, (86, 128, 136), 1)
    # shoulders / suit
    p.polygon([(8, bh), (30, 128), (62, 112), (88, 112), (120, 128),
               (bw - 8, bh)], (38, 48, 74))
    p.polygon([(62, 112), (75, 128), (88, 112), (75, 106)],
              (244, 238, 222))
    p.polygon([(70, 128), (75, 120), (80, 128), (78, 148), (72, 148)],
              (122, 32, 40))
    # neck and head
    p.fill_rect(66, 92, 84, 116, (214, 176, 142))
    p.fill_ellipse(75, 65, 27, 35, (226, 190, 158))
    # hair: dark swept cap - top half of an ellipse; the face is redrawn
    # below it so the cap sits on the forehead instead of covering it
    p.fill_ellipse(75, 48, 29, 26, (52, 40, 34))
    p.fill_ellipse(75, 70, 26, 30, (226, 190, 158))
    # ears, brows, eyes, nose, mouth
    p.fill_ellipse(48, 66, 4, 8, (226, 190, 158))
    p.fill_ellipse(102, 66, 4, 8, (226, 190, 158))
    p.line(58, 62, 70, 60, (52, 40, 34), 2)
    p.line(80, 60, 92, 62, (52, 40, 34), 2)
    p.fill_ellipse(64, 68, 4, 3, (40, 32, 26))
    p.fill_ellipse(86, 68, 4, 3, (40, 32, 26))
    p.line(75, 70, 73, 84, (190, 150, 120), 2)
    p.line(66, 90, 84, 90, (150, 90, 80), 2)
    # soft cheek shading
    p.fill_ellipse(60, 81, 6, 5, (214, 172, 140))
    p.fill_ellipse(90, 81, 6, 5, (214, 172, 140))
    # paste into the page
    for y in range(bh):
        src = y * bw * 3
        dst = 3 * ((y0 + y) * cv.w + x0)
        cv.px[dst:dst + bw * 3] = p.px[src:src + bw * 3]
    cv.rect(x0, y0, x1, y1, (70, 60, 40), 2)


def stamp_circle(cx, cy, r, ink, lines, angle=0):
    size = int(2 * r + 24)
    ov = StampCanvas(size, size)
    c = size // 2
    ov.circle(c, c, r, ink, 200, 3)
    ov.circle(c, c, r - 9, ink, 200, 1)
    ov.text(c, c - r + 30, lines[0], 1.3, 1.6, ink, 215, "center")
    ov.text(c, c - 12, lines[1], 1.2, 1.5, ink, 215, "center")
    ov.text(c, c + 8, lines[2], 1.1, 1.4, ink, 215, "center")
    ov.text(c, c + r - 42, lines[3], 1.2, 1.5, ink, 215, "center")
    return ov, cx, cy, angle


def stamp_rect(cx, cy, w, h, ink, lines, angle=0):
    sw, sh = w + 24, h + 24
    ov = StampCanvas(sw, sh)
    ov.rect(10, 10, 10 + w, 10 + h, ink, 205, 3)
    ov.rect(14, 14, 10 + w - 4, 10 + h - 4, ink, 160, 1)
    y = 22
    for i, ln in enumerate(lines):
        if i == 0:
            ov.text(sw // 2, y, ln, 1.3, 1.6, ink, 215, "center")
        else:
            ov.text(sw // 2, y, ln, 1.1, 1.4, ink, 215, "center")
        y += 18
    return ov, cx, cy, angle


# ---------------------------------------------------------------- main
def main():
    img = Canvas(W, H, (43, 37, 30))
    # desk vignette
    for i in range(60):
        img.fill_rect(0, H - 1 - i, W, H - i,
                      (43 - i // 6, 37 - i // 7, 30 - i // 8))
    img.fill_rect(46, 108, 988, 948, (0, 0, 0))
    # caption above the spread
    draw_text(img, 512, 34, "REPUBLIC OF ZALVARA  \u00b7  PASSPORT  \u00b7  "
              "OPEN SPREAD", 1.5, 2.0, (232, 222, 200), "center")
    draw_text(img, 512, 62, "An invented document \u2014 no real country, "
              "no real person", 1.0, 1.4, (178, 168, 148), "center")

    ink = (42, 38, 30)
    label = (110, 96, 74)
    page_l = (44, 92, 502, 936)
    page_r = (522, 92, 980, 936)
    for pg, fill in ((page_l, (246, 238, 216)), (page_r, (248, 241, 221))):
        img.fill_rect(pg[0], pg[1], pg[2], pg[3], fill)
        img.rect(pg[0], pg[1], pg[2], pg[3], (120, 104, 78), 2)
    guilloche(img, (page_l[0] + 8, page_l[1] + 8, page_l[2] - 8,
                    page_l[3] - 8), (214, 198, 168))
    guilloche(img, (page_r[0] + 8, page_r[1] + 8, page_r[2] - 8,
                    page_r[3] - 8), (216, 200, 170))

    # ---------------- LEFT PAGE: data page ----------------
    cx = (page_l[0] + page_l[2]) // 2
    emblem(img, cx, 152, 30, (96, 74, 40))
    draw_text(img, cx, 196, "REPUBLIC OF ZALVARA", 2.0, 2.8, ink, "center")
    draw_text(img, cx, 226, "P A S S P O R T", 1.8, 2.4, (96, 74, 40),
              "center")
    img.line(page_l[0] + 30, 258, page_l[2] - 30, 258, (96, 74, 40), 2)
    draw_text(img, cx, 266, "THE HIGHLAND REPUBLIC OF THE NORTHERN ISLES",
              1.0, 1.4, label, "center")

    # portrait + fields
    portrait(img, (page_l[0] + 28, 296, page_l[0] + 178, 296 + 190))
    draw_text(img, page_l[0] + 103, 492, "HOLDER'S PORTRAIT", 1.0, 1.4,
              label, "center")
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
        draw_text(img, fx, y, lab, 1.1, 1.5, label)
        draw_text(img, fx, y + 15, val, 1.6, 2.2, ink)
        y += 38
    img.line(page_l[0] + 28, 536, page_l[2] - 28, 536, (150, 132, 100), 1)
    # lower data block
    rows = [
        ("DATE OF ISSUE", "14 MAR 2024", "DATE OF EXPIRY", "14 MAR 2034"),
        ("DOCUMENT No.", "ZV 4829137", "TYPE", "P  \u00b7  ORDINARY"),
    ]
    y = 552
    for l1, v1, l2, v2 in rows:
        draw_text(img, page_l[0] + 28, y, l1, 1.1, 1.5, label)
        draw_text(img, page_l[0] + 28, y + 15, v1, 1.6, 2.2, ink)
        draw_text(img, page_l[0] + 252, y, l2, 1.1, 1.5, label)
        draw_text(img, page_l[0] + 252, y + 15, v2, 1.6, 2.2, ink)
        y += 46
    draw_text(img, page_l[0] + 28, y, "AUTHORITY", 1.1, 1.5, label)
    draw_text(img, page_l[0] + 28, y + 15, "MINISTRY OF THE INTERIOR",
              1.5, 2.0, ink)
    draw_text(img, page_l[0] + 28, y + 34, "PASSPORT OFFICE \u2014 VELMARA",
              1.5, 2.0, ink)
    draw_text(img, page_l[0] + 28, y + 56, "ISSUED IN ZALVARAN AND ENGLISH",
              1.1, 1.5, label)
    # MRZ
    mrz_y = 800
    img.fill_rect(page_l[0] + 20, mrz_y - 8, page_l[2] - 20, mrz_y + 46,
                  (238, 230, 206))
    img.rect(page_l[0] + 20, mrz_y - 8, page_l[2] - 20, mrz_y + 46,
             (150, 132, 100), 1)
    draw_text(img, page_l[0] + 28, mrz_y,
              "P<ZLVVOSS<<ELENA<MARIS<<<<<<<<<<<<<<<<<<<<", 1.0, 2.0, ink)
    draw_text(img, page_l[0] + 28, mrz_y + 18,
              "ZV4829137<6ZLV9106128F3403145<<<<<<<<<<<<<<08", 1.0, 2.0, ink)
    draw_text(img, page_l[0] + 28, 906, "PAGE 1 \u2014 DATA PAGE", 1.0, 1.4,
              label)

    # ---------------- RIGHT PAGE: visas & stamps ----------------
    cxr = (page_r[0] + page_r[2]) // 2
    draw_text(img, cxr, 116, "VISAS \u2014 ARRIVALS & DEPARTURES", 1.7, 2.3,
              ink, "center")
    draw_text(img, cxr, 142, "PAGES 4 \u2013 5  \u00b7  STAMPS IN "
              "CHRONOLOGICAL ORDER", 1.0, 1.4, label, "center")
    img.line(page_r[0] + 30, 168, page_r[2] - 30, 168, (96, 74, 40), 2)

    stamps = [
        ("circle", (page_r[0] + 118, 268), 62, (28, 84, 160),
         ["DRAVENHOLD", "KESTREL PORT", "ARRIVAL", "02 APR 2024"], -8),
        ("rect", (page_r[0] + 340, 268), (196, 108), (34, 122, 74),
         ["TALVORIA", "PORT MERIDIAN", "ARRIVAL", "27 SEP 2024"], 6),
        ("circle", (page_r[0] + 118, 452), 62, (104, 52, 140),
         ["OSTARA", "NORTH GATE", "DEPARTURE", "11 FEB 2025"], 10),
        ("rect", (page_r[0] + 340, 452), (196, 108), (28, 84, 160),
         ["ZALVARA \u2014 VELMARA", "ARRIVAL", "18 MAR 2025"], -6),
    ]
    for kind, (sx, sy), size, inkc, lines, ang in stamps:
        if kind == "circle":
            ov, ox, oy, oa = stamp_circle(sx, sy, size, inkc, lines, ang)
        else:
            ov, ox, oy, oa = stamp_rect(sx, sy, size[0], size[1], inkc,
                                        lines, ang)
        blit_rotated(img, ov, ox, oy, oa)

    # visa-condition box
    vy = 560
    img.rect(page_r[0] + 28, vy, page_r[2] - 28, vy + 118, (96, 74, 40), 2)
    img.rect(page_r[0] + 32, vy + 4, page_r[2] - 32, vy + 114,
             (150, 132, 100), 1)
    draw_text(img, cxr, vy + 12, "VISA CONDITION \u2014 NORTHERN ISLES",
              1.4, 1.9, (96, 74, 40), "center")
    draw_text(img, cxr, vy + 36, "HOLDER MAY ENTER THE NORTHERN ISLES",
              1.5, 2.0, ink, "center")
    draw_text(img, cxr, vy + 56, "WITHOUT VISA \u2014 STAY MAX 90 DAYS",
              1.5, 2.0, ink, "center")
    draw_text(img, cxr, vy + 76, "IN ANY 180 DAYS  \u00b7  NO PAID WORK",
              1.5, 2.0, ink, "center")
    draw_text(img, cxr, vy + 96, "CONDITION 7B \u2014 HIGHLAND TREATY 2019",
              1.0, 1.4, label, "center")

    # fee stamp
    ov, ox, oy, oa = stamp_rect(cxr - 90, 748, 210, 84, (150, 40, 40),
                                ["FEE PAID \u2014 45 ZLV", "14 MAR 2024",
                                 "VELMARA"], -7)
    blit_rotated(img, ov, ox, oy, oa)
    draw_text(img, page_r[0] + 252, 716, "FEE STAMP", 1.1, 1.5, label)
    draw_text(img, page_r[0] + 252, 734, "PAID AT ISSUE", 1.4, 1.9, ink)
    draw_text(img, page_r[0] + 252, 756, "RECEIPT No. 7714", 1.4, 1.9, ink)

    draw_text(img, page_r[0] + 28, 830,
              "HOLDER'S SIGNATURE ______________________", 1.2, 1.6, ink)
    draw_text(img, page_r[0] + 28, 856, "Elena Maris Voss", 1.5, 2.0, ink)
    draw_text(img, cxr, 884, "ALL STAMPS DATED AFTER ISSUE \u2014 "
              "14 MAR 2024", 1.2, 1.6, (96, 74, 40), "center")
    draw_text(img, page_r[0] + 28, 906, "PAGES 4\u20135 \u2014 VISAS", 1.0,
              1.4, label)
    draw_text(img, page_r[2] - 28, 906, "ZLV \u00b7 4829137", 1.0, 1.4,
              label, "right")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    write_png(img, OUT)
    print("wrote", OUT, (W, H), os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
