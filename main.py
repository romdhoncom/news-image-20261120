# One Day on Earth — Friday 20 November 2026 (v2, dense front page).
# Pure Python 3 standard library only: own raster, own 5x7 bitmap font,
# own PNG encoder. No network, no clock, no randomness. Deterministic:
# two runs write byte-identical output.
import os
import struct
import sys
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- font ----
# 5x7 bitmap font. Each glyph is 7 rows of 5 characters ('#' = ink).
FONT = {
' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
'!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
'"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
'#': (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
'$': ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
'%': ("##..#", "##.#.", "....#", "...#.", "..#..", ".#...", "#..##"),
'&': (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", "#..#."),
"'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
'(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
'*': (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
'+': (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
',': (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
'-': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
'.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
'/': ("....#", "...#.", "...#.", "..#..", "..#..", ".#...", ".#..."),
'0': (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
'1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
'2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
'3': (".###.", "#...#", "....#", "..##.", "....#", "#...#", ".###."),
'4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
'5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
'6': ("..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."),
'7': ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
'8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
'9': (".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."),
':': (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
';': (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
'<': ("...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."),
'=': (".....", ".....", "#####", ".....", "#####", ".....", "....."),
'>': (".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."),
'?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
'@': (".###.", "#...#", "#.###", "#.#.#", "#.#..", "#....", ".###."),
'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
'C': (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
'D': ("###..", "#..#.", "#...#", "#...#", "#...#", "#..#.", "###.."),
'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
'G': (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".###."),
'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
'I': (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
'N': ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
'X': ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
'a': (".....", ".....", ".###.", "....#", ".####", "#...#", ".####"),
'b': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
'c': (".....", ".....", ".###.", "#...#", "#....", "#....", ".###."),
'd': ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
'e': (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
'f': ("..##.", ".#..#", ".#...", "####.", ".#...", ".#...", ".#..."),
'g': (".....", ".####", "#...#", "#...#", ".####", "....#", ".###."),
'h': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
'i': (".....", "..#..", ".....", ".##..", "..#..", "..#..", ".###."),
'j': (".....", "...#.", ".....", "..##.", "...#.", "...#.", ".##.."),
'k': ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
'l': (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
'm': (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
'n': (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
'o': (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
'p': (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
'q': (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
'r': (".....", ".....", "#.#..", "##.#.", "#....", "#....", "#...."),
's': (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
't': (".#...", ".#...", "####.", ".#...", ".#...", ".#...", "..##."),
'u': (".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"),
'v': (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
'w': (".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
'x': (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
'y': (".....", ".....", "#...#", "#...#", "#...#", ".####", "..##."),
'z': (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
'[': (".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."),
']': (".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."),
'_': (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
'\u00b7': (".....", ".....", ".....", ".##..", ".##..", ".....", "....."),
'\u2014': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
'\u00b0': (".##..", "#..#.", ".##..", ".....", ".....", ".....", "....."),
'\u2022': (".....", ".##..", "####.", "####.", ".##..", ".....", "....."),
}

def glyph_rows(ch):
    g = FONT.get(ch)
    if g is None:
        raise SystemExit("font has no glyph for %r" % ch)
    return g

def text_w(s, scale):
    return len(s) * 6 * scale - scale

def draw_text(img, x, y, s, scale, color):
    cx = x
    for ch in s:
        rows = glyph_rows(ch)
        for r in range(7):
            row = rows[r]
            for c in range(5):
                if row[c] == '#':
                    for dy in range(scale):
                        for dx in range(scale):
                            img.set(cx + c * scale + dx, y + r * scale + dy, color)
        cx += 6 * scale
    return cx

def draw_text_center(img, cx, y, s, scale, color):
    draw_text(img, cx - text_w(s, scale) // 2, y, s, scale, color)

def wrap_text(s, max_w, scale):
    """Greedy word wrap to a pixel width; returns list of lines."""
    words = s.split(' ')
    lines, cur = [], ''
    for w in words:
        trial = w if not cur else cur + ' ' + w
        if text_w(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

# --------------------------------------------------------------- image ----
PAPER = (247, 243, 232)
INK = (26, 26, 26)
RED = (179, 38, 30)
BLUE = (31, 78, 121)
GREY = (107, 107, 107)
PANEL = (237, 232, 216)
RULE = (180, 172, 150)
SEA = (214, 229, 238)
LAND = (239, 230, 200)
LANDB = (154, 139, 98)
DARK = (43, 43, 43)
CREAM = (247, 243, 232)
GOLD = (176, 141, 42)

class Img:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(w * h * 3)
        self.fill(bg)

    def fill(self, c):
        r, g, b = c
        for i in range(0, len(self.px), 3):
            self.px[i] = r
            self.px[i + 1] = g
            self.px[i + 2] = b

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = c

    def rect(self, x, y, w, h, c):
        for yy in range(max(0, y), min(self.h, y + h)):
            for xx in range(max(0, x), min(self.w, x + w)):
                self.set(xx, yy, c)

    def border(self, x, y, w, h, c, t=1):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def vline(self, x, y, h, c, t=1):
        self.rect(x, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        while True:
            self.rect(x, y, t, t, c)
            if x == x1 and y == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, c)

    def circle(self, cx, cy, r, c, t=1):
        for a in range(360):
            import math
            x = cx + int(r * math.cos(math.radians(a)))
            y = cy + int(r * math.sin(math.radians(a)))
            self.rect(x, y, t, t, c)

    def tri(self, pts, c):
        # Filled triangle via scanline on its bounding box.
        (x0, y0), (x1, y1), (x2, y2) = pts
        minx, maxx = min(x0, x1, x2), max(x0, x1, x2)
        miny, maxy = min(y0, y1, y2), max(y0, y1, y2)
        def sign(ax, ay, bx, by, cx, cy):
            return (ax - cx) * (by - cy) - (bx - cx) * (ay - cy)
        d = sign(x0, y0, x1, y1, x2, y2)
        if d == 0:
            return
        for yy in range(miny, maxy + 1):
            for xx in range(minx, maxx + 1):
                s1 = sign(xx, yy, x0, y0, x1, y1)
                s2 = sign(xx, yy, x1, y1, x2, y2)
                s3 = sign(xx, yy, x2, y2, x0, y0)
                if (d > 0 and s1 >= 0 and s2 >= 0 and s3 >= 0) or \
                   (d < 0 and s1 <= 0 and s2 <= 0 and s3 <= 0):
                    self.set(xx, yy, c)

    def poly(self, pts, c):
        # Filled polygon (scanline).
        if len(pts) < 3:
            return
        miny = min(p[1] for p in pts)
        maxy = max(p[1] for p in pts)
        n = len(pts)
        for yy in range(miny, maxy + 1):
            xs = []
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= yy < y1) or (y1 <= yy < y0):
                    if y1 != y0:
                        xs.append(x0 + (yy - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                for xx in range(int(xs[k]), int(xs[k + 1]) + 1):
                    self.set(xx, yy, c)

    def polyline(self, pts, c, t=1):
        for i in range(len(pts) - 1):
            self.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], c, t)

# ----------------------------------------------------------------- png ----
def png_bytes(img):
    raw = bytearray()
    stride = img.w * 3
    for y in range(img.h):
        raw.append(0)
        raw += img.px[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)
        return out
    ihdr = struct.pack(">IIBBBBB", img.w, img.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
            chunk(b"IDAT", comp) + chunk(b"IEND", b""))

# ------------------------------------------------------------- pictures ----
import math

SKY = (176, 205, 224)
NIGHT = (28, 42, 66)
SUN = (232, 164, 32)
GRN = (96, 140, 82)
SEA2 = (90, 140, 180)
SAND = (226, 205, 150)

def spiral(img, cx, cy, turns, rmax, color):
    steps = int(turns * 40)
    px, py = cx, cy
    for i in range(1, steps + 1):
        a = i / steps * turns * 2 * math.pi
        r = rmax * i / steps
        x = cx + int(r * math.cos(a))
        y = cy + int(r * math.sin(a))
        img.line(px, py, x, y, color, 2)
        px, py = x, y

def pic_cyclone(img, x, y, w, h):
    img.rect(x, y, w, h, SKY)
    img.rect(x, y + h - 12, w, 12, GRN)          # coast
    img.rect(x, y + h - 12, w, 2, SAND)
    spiral(img, x + w // 2, y + h // 2 - 4, 2.2, min(w, h) // 2 - 4, INK)
    img.disc(x + w // 2, y + h // 2 - 4, 3, RED)
    for dx in (-18, -6, 8, 18):
        img.line(x + w // 2 + dx, y + 6, x + w // 2 + dx - 3, y + 14, BLUE, 1)

def pic_missiles(img, x, y, w, h):
    img.rect(x, y, w, h, NIGHT)
    for bx, bw, bh in ((6, 12, 22), (22, 10, 30), (36, 14, 18), (54, 10, 26), (68, 12, 20)):
        img.rect(x + bx, y + h - 8 - bh, bw, bh, (110, 125, 160))
        img.rect(x + bx + 3, y + h - 8 - bh + 4, 2, 2, (255, 220, 120))
        img.rect(x + bx + 3, y + h - 8 - bh + 10, 2, 2, (255, 220, 120))
    # Missile trails falling onto the skyline, bright head at impact.
    for tx, bx in ((14, 24), (40, 50), (62, 70)):
        img.line(x + tx, y + 6, x + bx, y + h - 30, (255, 210, 90), 2)
        img.disc(x + bx, y + h - 30, 3, (255, 240, 160))
    cx, cy = x + w - 16, y + 14
    for a in range(0, 360, 30):
        img.line(cx, cy, cx + int(11 * math.cos(math.radians(a))),
                 cy + int(11 * math.sin(math.radians(a))), (255, 120, 40), 2)
    img.disc(cx, cy, 5, (255, 210, 90))

def pic_cop(img, x, y, w, h):
    img.rect(x, y, w, h, (220, 232, 220))
    cx, cy, r = x + w // 3, y + h // 2, min(w, h) // 2 - 6
    img.disc(cx, cy, r, SEA2)
    img.disc(cx - 6, cy - 6, 5, GRN)
    img.disc(cx + 7, cy + 5, 6, GRN)
    img.disc(cx + 2, cy - 10, 4, GRN)
    tx = x + 2 * w // 3 + 6
    img.rect(tx, y + 8, 10, h - 22, (220, 220, 220))
    img.border(tx, y + 8, 10, h - 22, INK, 1)
    img.rect(tx + 2, y + h - 16, 6, 8, RED)
    img.disc(tx + 5, y + h - 10, 7, RED)
    img.line(tx + 5, y + 4, tx + 5, y + 12, RED, 2)

def pic_markets(img, x, y, w, h):
    img.rect(x, y, w, h, (255, 255, 255))
    img.rect(x, y + h - 14, w, 2, INK)
    for i, bh in enumerate((26, 20, 24, 12, 16, 6)):
        bx = x + 8 + i * 13
        img.rect(bx, y + h - 14 - bh, 8, bh, (120, 150, 190) if i < 3 else RED)
    pts = [(x + 6, y + 8), (x + 20, y + 16), (x + 34, y + 14), (x + 48, y + 26),
           (x + 62, y + 24), (x + w - 6, y + h - 18)]
    img.polyline(pts, RED, 3)
    img.tri([(x + w - 14, y + h - 22), (x + w - 4, y + h - 22), (x + w - 9, y + h - 12)], RED)

def pic_space(img, x, y, w, h):
    img.rect(x, y, w, h, (12, 16, 34))
    for sx, sy in ((6, 8), (20, 4), (34, 12), (52, 6), (66, 14), (12, 22), (44, 20), (72, 26)):
        img.disc(x + sx, y + sy, 1, (255, 255, 255))
    img.disc(x + w - 20, y + h // 2 + 6, 13, (214, 130, 60))   # Mercury
    img.disc(x + w - 24, y + h // 2 + 2, 3, (170, 95, 40))
    img.disc(x + w - 16, y + h // 2 + 10, 2, (170, 95, 40))
    img.rect(x + 10, y + h // 2 - 12, 16, 8, (200, 200, 210))  # craft body
    img.rect(x + 2, y + h // 2 - 10, 8, 4, BLUE)
    img.rect(x + 26, y + h // 2 - 10, 8, 4, BLUE)
    img.line(x + 26, y + h // 2 - 8, x + w - 32, y + h // 2 + 4, (255, 210, 90), 1)

def pic_flags(img, x, y, w, h):
    img.rect(x, y, w, h, (235, 235, 235))
    hw = w // 2
    img.rect(x + 4, y + 6, hw - 8, h - 12, (0, 51, 153))       # EU
    for k in range(8):
        a = k * math.pi / 4
        img.disc(x + 4 + (hw - 8) // 2 + int(9 * math.cos(a)),
                 y + 6 + (h - 12) // 2 + int(9 * math.sin(a)), 1, (255, 210, 0))
    ux, uw = x + hw + 2, hw - 6
    img.rect(ux, y + 6, uw, h - 12, (1, 33, 105))              # UK
    img.line(ux, y + 6, ux + uw, y + h - 6, (255, 255, 255), 3)
    img.line(ux + uw, y + 6, ux, y + h - 6, (255, 255, 255), 3)
    img.rect(ux + uw // 2 - 2, y + 6, 4, h - 12, (255, 255, 255))
    img.rect(ux, y + 6 + (h - 12) // 2 - 2, uw, 4, (255, 255, 255))
    img.rect(ux + uw // 2 - 1, y + 6, 2, h - 12, (200, 16, 46))
    img.rect(ux, y + 6 + (h - 12) // 2 - 1, uw, 2, (200, 16, 46))

def pic_cpi(img, x, y, w, h):
    img.rect(x, y, w, h, (255, 248, 220))
    # Price tag: white pentagon with a pointed left end, gold border.
    tag = [(x + 30, y + 14), (x + w - 8, y + 14), (x + w - 8, y + h - 14),
           (x + 30, y + h - 14), (x + 12, y + h // 2)]
    img.poly(tag, (255, 255, 255))
    img.polyline(tag + [tag[0]], GOLD, 2)
    img.disc(x + 34, y + h // 2, 3, INK)
    # Up arrow in the middle of the tag.
    ax = x + w // 2 + 14
    img.line(ax, y + h - 22, ax, y + 22, RED, 3)
    img.line(ax, y + 22, ax - 8, y + 32, RED, 3)
    img.line(ax, y + 22, ax + 8, y + 32, RED, 3)

def pic_rates(img, x, y, w, h):
    img.rect(x, y, w, h, (228, 232, 238))
    img.tri([(x + 6, y + 16), (x + w - 6, y + 16), (x + w // 2, y + 4)], (120, 130, 150))
    for i in range(4):
        cx = x + 12 + i * ((w - 24) // 3)
        img.rect(cx - 3, y + 20, 6, h - 30, (250, 250, 250))
        img.border(cx - 3, y + 20, 6, h - 30, INK, 1)
    img.rect(x + 6, y + h - 12, w - 12, 5, (120, 130, 150))

def pic_cricket(img, x, y, w, h):
    img.rect(x, y, w, h, (210, 232, 190))
    img.rect(x, y + h - 12, w, 12, (170, 140, 100))           # pitch strip
    for sx in (14, 22, 30):                                    # stumps
        img.rect(x + sx, y + h - 30, 5, 18, (250, 240, 210))
        img.border(x + sx, y + h - 30, 5, 18, INK, 1)
    img.rect(x + 14, y + h - 33, 21, 3, (250, 240, 210))       # bails
    # Bat: leaning blade with a handle.
    img.poly([(x + 52, y + 8), (x + 60, y + 10), (x + 46, y + h - 22),
              (x + 38, y + h - 24)], (222, 184, 120))
    img.polyline([(x + 52, y + 8), (x + 60, y + 10), (x + 46, y + h - 22),
                  (x + 38, y + h - 24), (x + 52, y + 8)], (150, 110, 60), 1)
    img.line(x + 56, y + 8, x + 62, y + 2, (150, 110, 60), 3)
    img.disc(x + 66, y + 16, 6, RED)                           # ball
    img.line(x + 62, y + 12, x + 70, y + 20, (255, 255, 255), 1)

def pic_floods(img, x, y, w, h):
    img.rect(x, y, w, h, (200, 210, 220))
    img.rect(x + 12, y + h - 30, 26, 18, (240, 220, 190))      # house
    img.tri([(x + 8, y + h - 30), (x + 42, y + h - 30), (x + 25, y + h - 44)], RED)
    img.rect(x + 22, y + h - 22, 8, 10, (90, 70, 50))
    img.rect(x, y + h - 16, w, 16, (70, 120, 190))             # water
    img.line(x + 4, y + h - 12, x + w - 4, y + h - 12, (255, 255, 255), 1)
    img.line(x + 4, y + h - 8, x + w - 4, y + h - 8, (255, 255, 255), 1)
    for dx in (52, 62, 72):
        img.line(x + dx, y + 6, x + dx - 2, y + 12, BLUE, 1)

def pic_boat(img, x, y, w, h):
    img.rect(x, y, w, h, SKY)
    img.rect(x, y + h - 22, w, 22, SEA2)
    for k in range(4):
        wx = x + 6 + k * 20
        img.line(wx, y + h - 16, wx + 8, y + h - 12, (255, 255, 255), 2)
        img.line(wx + 8, y + h - 12, wx + 16, y + h - 16, (255, 255, 255), 2)
    img.tri([(x + 18, y + h - 24), (x + 62, y + h - 24), (x + 40, y + h - 34)], (120, 80, 50))
    img.line(x + 40, y + h - 34, x + 40, y + 8, (120, 80, 50), 2)
    img.tri([(x + 42, y + 10), (x + 42, y + h - 36), (x + 62, y + h - 36)], (240, 240, 240))

def pic_strike(img, x, y, w, h):
    img.rect(x, y, w, h, (238, 228, 210))
    for i, hx in enumerate((14, 32, 50, 68)):
        img.disc(x + hx, y + h - 26, 7, (200, 170, 140))
        img.rect(x + hx - 9, y + h - 20, 18, 12, (60 + i * 20, 90, 140))
    img.rect(x + 8, y + 6, 26, 14, (255, 255, 255))
    img.border(x + 8, y + 6, 26, 14, INK, 1)
    img.line(x + 21, y + 20, x + 21, y + 34, INK, 2)
    img.rect(x + 46, y + 4, 26, 14, (255, 255, 255))
    img.border(x + 46, y + 4, 26, 14, INK, 1)
    img.line(x + 59, y + 18, x + 59, y + 32, INK, 2)
    img.line(x + 12, y + 12, x + 30, y + 12, RED, 2)
    img.line(x + 50, y + 10, x + 68, y + 10, BLUE, 2)

def pic_pill(img, x, y, w, h):
    img.rect(x, y, w, h, (235, 240, 250))
    img.rect(x + 10, y + 12, 56, 16, (255, 255, 255))
    img.border(x + 10, y + 12, 56, 16, INK, 1)
    img.rect(x + 10, y + 12, 28, 16, RED)
    img.disc(x + 10, y + 20, 8, RED)
    img.disc(x + 66, y + 20, 8, (255, 255, 255))
    img.circle(x + 66, y + 20, 8, INK, 1)
    img.disc(x + 24, y + h - 14, 9, (250, 200, 140))
    img.disc(x + 24, y + h - 14, 4, (200, 90, 60))
    img.disc(x + 52, y + h - 12, 7, (250, 200, 140))
    img.disc(x + 52, y + h - 12, 3, (200, 90, 60))

PICS = {
    'cyclone': pic_cyclone, 'missiles': pic_missiles, 'cop': pic_cop,
    'markets': pic_markets, 'space': pic_space, 'flags': pic_flags,
    'cpi': pic_cpi, 'rates': pic_rates, 'cricket': pic_cricket,
    'floods': pic_floods, 'boat': pic_boat, 'strike': pic_strike,
    'pill': pic_pill,
}

# -------------------------------------------------------------- map -------
# Coarse continent outlines in (lon, lat).
CONTINENTS = [
[(-168,66),(-155,71),(-140,70),(-130,71),(-120,72),(-110,73),(-95,80),(-85,76),(-80,73),(-75,72),(-65,60),(-60,55),(-55,47),(-60,45),(-65,43),(-70,42),(-75,38),(-76,35),(-80,32),(-81,26),(-84,24),(-85,20),(-87,15),(-90,14),(-92,15),(-95,18),(-97,22),(-100,25),(-105,22),(-110,25),(-114,29),(-117,33),(-122,37),(-124,42),(-124,48),(-130,55),(-140,60),(-150,61),(-160,58),(-165,60)],
[(-79,9),(-77,5),(-75,0),(-72,-4),(-70,-8),(-70,-15),(-70,-22),(-70,-30),(-70,-38),(-72,-45),(-70,-52),(-68,-55),(-65,-50),(-62,-42),(-58,-35),(-52,-32),(-48,-28),(-40,-22),(-38,-15),(-35,-9),(-38,-5),(-44,-3),(-50,0),(-55,5),(-60,8),(-65,10),(-70,11),(-75,10)],
[(-17,15),(-16,20),(-12,25),(-8,30),(-5,35),(0,36),(5,37),(10,37),(15,32),(20,32),(25,31),(30,31),(32,30),(35,28),(38,22),(40,15),(43,12),(48,11),(51,10),(50,5),(45,0),(40,-5),(40,-12),(35,-18),(32,-25),(28,-32),(20,-35),(16,-30),(14,-22),(12,-15),(12,-8),(10,-2),(8,4),(4,6),(-2,5),(-8,5),(-12,8),(-15,11)],
[(-10,36),(-9,38),(-9,43),(-4,44),(-2,47),(-1,49),(2,51),(5,53),(8,55),(10,57),(12,55),(18,56),(20,58),(22,60),(25,62),(28,65),(30,68),(35,68),(40,67),(45,68),(50,69),(55,70),(60,70),(65,71),(70,72),(75,73),(80,73),(85,74),(90,75),(95,76),(100,76),(105,77),(110,76),(115,73),(120,73),(125,72),(130,71),(135,72),(140,72),(145,72),(150,70),(155,69),(160,69),(165,67),(170,66),(175,65),(178,64),(175,62),(170,60),(165,60),(160,58),(155,55),(150,59),(145,59),(142,55),(140,50),(138,46),(135,43),(132,40),(130,38),(127,36),(126,33),(122,31),(120,28),(118,25),(112,22),(108,18),(105,12),(103,8),(100,6),(98,10),(95,15),(92,20),(90,22),(88,22),(85,20),(82,17),(80,14),(77,8),(75,10),(73,16),(70,20),(66,25),(62,25),(58,26),(55,26),(52,27),(50,29),(48,30),(46,32),(44,35),(42,38),(40,38),(38,36),(36,36),(33,36),(30,36),(27,37),(24,38),(22,39),(20,40),(18,40),(16,40),(14,42),(12,44),(10,44),(8,43),(6,43),(3,43),(0,40),(-2,37),(-5,36),(-8,37)],
[(113,-22),(114,-28),(115,-33),(118,-35),(122,-34),(126,-32),(130,-32),(132,-32),(135,-35),(138,-35),(140,-38),(143,-39),(146,-39),(149,-37),(150,-35),(153,-32),(153,-27),(151,-24),(149,-20),(146,-19),(143,-15),(142,-11),(141,-13),(138,-14),(136,-12),(134,-12),(132,-11),(130,-13),(127,-14),(124,-15),(121,-17),(118,-20),(115,-21)],
[(-5,50),(-3,53),(-5,56),(-3,58),(-1,57),(0,53),(1,51),(-2,50)],
[(130,31),(132,33),(134,34),(136,34),(138,35),(139,36),(140,38),(141,40),(141,42),(143,44),(145,44),(143,42),(141,40),(140,38),(139,36),(137,35),(135,33),(132,32)],
[(167,-45),(168,-44),(170,-42),(172,-41),(174,-39),(175,-37),(177,-38),(178,-37),(176,-39),(174,-41),(172,-43),(170,-44),(168,-46)],
[(-55,60),(-48,60),(-42,62),(-38,65),(-32,68),(-28,70),(-22,72),(-20,74),(-25,76),(-35,77),(-45,76),(-55,74),(-58,70),(-55,64)],
[(-22,64),(-18,63),(-14,64),(-15,66),(-20,66),(-24,65)],
[(44,-16),(47,-15),(50,-16),(49,-20),(47,-24),(44,-25),(43,-20)],
[(95,5),(98,3),(100,0),(103,-2),(105,-5),(108,-6),(110,-7),(113,-8),(116,-8),(119,-9),(122,-10),(125,-9),(128,-7),(131,-3),(134,-3),(137,-2),(140,-4),(141,-8),(138,-8),(135,-7),(132,-4),(129,-2),(126,0),(123,1),(120,0),(117,1),(114,0),(111,0),(108,0),(105,0),(102,2),(99,4),(96,5)],
[(131,-1),(134,-2),(137,-3),(140,-4),(143,-5),(146,-6),(149,-8),(150,-10),(147,-9),(144,-8),(141,-8),(138,-7),(135,-5),(132,-2)],
]

# ---------------------------------------------------------------- data ----
# Leads: (number, tag, headline, [sub-lines], picture, lon, lat)
# lon/lat None = in space, shown in the map legend instead of a pin.
LEADS = [
 (1, "01 \u00b7 KYIV, UKRAINE \u00b7 MISSILES", "BRIDGES HIT IN BIGGEST RAID",
  ["About 100 missiles, 404 drones", "overnight; 3 bridges hit, 6 killed"],
  'missiles', 30.5, 50.4),
 (2, "02 \u00b7 ODISHA, INDIA \u00b7 CYCLONE", "CYCLONE AKVAN SLAMS COAST",
  ["300,000 evacuated as storm", "makes landfall near Gopalpur"],
  'cyclone', 85.0, 19.5),
 (3, "03 \u00b7 ASIA \u00b7 MARKETS", "ASIA MARKETS IN FREEFALL",
  ["Nikkei -4.8%, Kospi -5.2%", "Taiwan -17% in worst week since 1991"],
  'markets', 121.5, 25.0),
 (4, "04 \u00b7 ANTALYA \u00b7 COP31", "CLIMATE TALKS DEADLOCKED",
  ["Draft drops fossil-fuel phase-out", "$120bn finance gap on final day"],
  'cop', 30.7, 36.9),
 (5, "05 \u00b7 BRUSSELS \u00b7 EU-UK", "BRITAIN AND EU INK RESET",
  ["Youth mobility both ways", "100,000 places; food, trade"],
  'flags', 4.35, 50.85),
 (6, "06 \u00b7 SPACE \u00b7 MERCURY", "BEPICOLOMBO NEARS MERCURY",
  ["Insertion set for Saturday", "after an eight-year trip"],
  'space', None, None),
 (7, "07 \u00b7 TOKYO \u00b7 INFLATION", "PRICES UP, RATE HIKE LOOMS",
  ["CPI 2.3%; core 2.2%", "BoJ hike seen 17-18 Dec"],
  'cpi', 139.7, 35.7),
 (8, "08 \u00b7 BEIJING \u00b7 RATES", "CHINA HOLDS RATES AGAIN",
  ["Loan rate 3.0%, 18th month", "5-year rate 3.5%"],
  'rates', 116.4, 39.9),
 (9, "09 \u00b7 WELLINGTON \u00b7 CRICKET", "PHILLIPS MAKES HISTORY",
  ["Phillips 118; Nicholls 175*", "a first in all 3 formats"],
  'cricket', 174.8, -41.3),
 (10, "10 \u00b7 FLORIDA, USA \u00b7 FLOODS", "RIVER STAYS ABOVE RECORD",
  ["Emergency widened to 22 counties", "St Johns at 18.1 ft; schools shut"],
  'floods', -80.7, 28.4),
 (11, "11 \u00b7 SENEGAL \u00b7 BOAT", "BOAT CAPSIZES; 4 DEAD",
  ["Dozens missing off Yenne", "at least 50 were aboard"],
  'boat', -17.3, 14.7),
 (12, "12 \u00b7 ROME \u00b7 STRIKE", "ITALY STOPS FOR A DAY",
  ["General strike in 100+ cities", "against Meloni's EUR 26bn budget"],
  'strike', 12.5, 41.9),
 (13, "13 \u00b7 BARCELONA \u00b7 CANCER", "PILL SHRINKS TUMOURS",
  ["Daraxonrasib + chemo: 61% respond", "in pancreatic cancer trial"],
  'pill', 2.17, 41.4),
]

LIST = [
 "SEOUL \u00b7 Ruling party adopts chief-justice impeachment (Korea JoongAng Daily)",
 "AMAZON \u00b7 Lula visits ailing Raoni; 362,000 ha recognised (Al Jazeera)",
 "IOWA \u00b7 Army postpones lead-azide blast to Monday (AP)",
 "TAIPEI \u00b7 Short-sell curbs take effect; Taiex -2,393 (Reuters)",
 "TURIN \u00b7 Medvedev v Tiafoe decides last semi-final place (ATP Tour)",
 "DOHA \u00b7 U-17 World Cup day two: Spain, Italy, Morocco open (FIFA)",
 "CANBERRA \u00b7 CBO: AUKUS sub sales would thin US fleet (The Guardian)",
 "HORMUZ \u00b7 Ship attacks reach 18 in November (Times of India)",
 "TOKYO \u00b7 13,000 rally at the Diet (IANS)",
 "SYDNEY \u00b7 Man charged with terrorism offences (Reuters)",
 "NEW DELHI \u00b7 Pakistan minister arrives for SCO forum (APP)",
 "DELHI \u00b7 South Africa reach T20 World Cup semi-final (BBC Sport)",
 "HONG KONG \u00b7 Satwik-Chirag, Lakshya Sen into Open semis (IANS)",
 "KUALA LUMPUR \u00b7 Malaysia to resettle 10,000 Rohingya (Reuters)",
 "PORT-AU-PRINCE \u00b7 Haiti police kill 34 gang suspects (Reuters)",
 "CALIFORNIA \u00b7 Magnitude 5.1 quake near Monterey (USGS)",
 "JAKARTA \u00b7 Prabowo, Xi discuss South China Sea (Reuters)",
 "RIYADH \u00b7 Houthi missile damages tower (Reuters)",
 "NAIROBI \u00b7 Kenya discharges last Ebola patient (One Turn)",
 "WORLD \u00b7 World Children's Day marked (UNICEF)",
 "SEOUL \u00b7 Samsung names new memory chip chief (Reuters)",
 "NEW YORK \u00b7 US stocks fall for a fifth day (Reuters)",
 "WORLD \u00b7 Signal blocks screenshots from AI agents (Reuters)",
]

STATS = [
 ("300,000", "EVACUATED IN ODISHA"),
 ("100", "MISSILES AT KYIV"),
 ("-17%", "TAIEX IN A WEEK"),
 ("2.3%", "JAPAN CPI, OCTOBER"),
 ("175*", "NICHOLLS, NOT OUT"),
 ("8 YRS", "BEPICOLOMBO TO MERCURY"),
]

HEADLINE_STRIP = "KYIV BRIDGES HIT \u00b7 ASIA ROUT \u00b7 CYCLONE AKVAN \u00b7 COP31 DEADLOCK"

REGIONS = [
 ("ASIA-PACIFIC", 13), ("EUROPE", 6), ("AMERICAS", 6), ("MIDEAST", 3),
 ("AFRICA", 2), ("OCEANIA", 3), ("WORLD/SPACE", 3),
]

DATECHECK_TITLE = "DATE CHECK \u2014 NOT FRIDAY: FIRST REPORTED THURSDAY 19 NOVEMBER"
DATECHECK = [
 "Shenzhen summit \u00b7 Anthropic IPO $83 \u00b7 ICJ: Myanmar genocide \u00b7 GTA VI launch \u00b7 Bukele third term",
 "Pentagon: Iran war $48.3bn \u00b7 Greenland 109-0 \u00b7 Tonga emergency \u00b7 Indonesia asset law \u00b7 Fiona dies",
]

FOOTER = ("Every story here happened, or was first reported, on Friday 20 November "
          "2026 in at least one time zone. Claims are attributed, not stated as fact. "
          "Sources: Reuters, AP, BBC, Al Jazeera, AFP, IANS, NZ Herald, EORTC, ATP "
          "Tour, FIFA, USGS, EEAS, BCCI, NWS, IMD, UN News.")

# --------------------------------------------------------------- layout ---
MARGIN = 16
CW = W - 2 * MARGIN

def draw_lead(img, x, y, w, h, lead):
    num, tag, headline, subs, pic, lon, lat = lead
    img.border(x, y, w, h, RULE, 1)
    img.rect(x + 1, y + 1, w - 2, h - 2, (255, 255, 255))
    pic_h = 52 if w < 220 else 58
    PICS[pic](img, x + 5, y + 5, w - 10, pic_h)
    ty = y + 5 + pic_h + 5
    draw_text(img, x + 8, ty, tag, 1, RED)
    hy = ty + 11
    lines = wrap_text(headline, w - 16, 2)
    for ln in lines:
        draw_text(img, x + 8, hy, ln, 2, INK)
        hy += 15
    for s in subs:
        for ln in wrap_text(s, w - 16, 1):
            draw_text(img, x + 8, hy, ln, 1, INK)
            hy += 10

def draw_map(img, x, y, w, h):
    img.border(x, y, w, h, RULE, 1)
    img.rect(x + 1, y + 1, w - 2, h - 2, (255, 255, 255))
    draw_text(img, x + 8, y + 7, "WHERE IT HAPPENED", 1, INK)
    mx, my = x + 8, y + 26
    mw, mh = w - 16, h - 26 - 22
    img.rect(mx, my, mw, mh, SEA)
    img.border(mx, my, mw, mh, RULE, 1)
    def proj(lon, lat):
        return (mx + int((lon + 180.0) / 360.0 * mw),
                my + int((75.0 - lat) / 135.0 * mh))
    for cont in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in cont]
        img.poly(pts, LAND)
        img.polyline(pts + [pts[0]], LANDB, 1)
    placed = []
    for num, tag, headline, subs, pic, lon, lat in LEADS:
        if lon is None:
            continue
        ox, oy = proj(lon, lat)
        px, py = ox, oy
        # Try small offsets around the true point; take the first that
        # does not collide with a pin already placed. One nudge at most.
        for dx, dy in ((0, 0), (13, 8), (-13, 8), (13, -8), (-13, -8),
                       (0, 15), (0, -15), (18, 0), (-18, 0)):
            cx, cy = ox + dx, oy + dy
            if all((cx - qx) ** 2 + (cy - qy) ** 2 >= 18 * 18
                   for qx, qy in placed):
                px, py = cx, cy
                break
        if (px, py) != (ox, oy):
            img.line(ox, oy, px, py, RED, 1)
        placed.append((px, py))
        img.disc(px, py, 7, RED)
        img.circle(px, py, 7, (255, 255, 255), 1)
        s = str(num)
        draw_text(img, px - text_w(s, 1) // 2, py - 3, s, 1, (255, 255, 255))
    draw_text(img, x + 8, y + h - 16,
              "5 = BEPICOLOMBO, MERCURY (IN SPACE) \u00b7 PINS 1-13 = LEAD STORIES",
              1, GREY)

def build():
    img = Img(W, H, PAPER)
    # Top line.
    draw_text(img, MARGIN, 9, "THE WORLD IN ONE DAY", 2, INK)
    right = "FRIDAY'S NEWS \u00b7 ONE PAGE \u00b7 36 STORIES \u00b7 6 CONTINENTS"
    draw_text(img, W - MARGIN - text_w(right, 1), 13, right, 1, GREY)
    img.hline(MARGIN, 28, CW, INK, 3)
    # Masthead.
    draw_text_center(img, W // 2, 36, "Friday 20 November 2026", 5, INK)
    img.hline(MARGIN, 78, CW, INK, 1)
    img.hline(MARGIN, 81, CW, INK, 2)
    # Headline strip.
    draw_text_center(img, W // 2, 90, HEADLINE_STRIP, 2, RED)
    img.hline(MARGIN, 110, CW, RULE, 1)
    # Stats strip: six boxes.
    gap, bw = 8, (CW - 5 * 8) // 6
    sx = MARGIN + (CW - (6 * bw + 5 * gap)) // 2
    for i, (num, label) in enumerate(STATS):
        bx = sx + i * (bw + gap)
        img.border(bx, 116, bw, 38, RULE, 1)
        img.rect(bx + 1, 117, bw - 2, 36, (255, 255, 255))
        draw_text_center(img, bx + bw // 2, 120, num, 3, RED)
        draw_text_center(img, bx + bw // 2, 142, label, 1, GREY)
    # Region tags.
    tags = ["%s %d" % (name, n) for name, n in REGIONS]
    widths = [text_w(t, 1) + 14 for t in tags]
    total = sum(widths) + 10 * (len(tags) - 1)
    tx = MARGIN + (CW - total) // 2
    for t, tw in zip(tags, widths):
        img.border(tx, 160, tw, 16, RULE, 1)
        draw_text(img, tx + 7, 164, t, 1, INK)
        tx += tw + 10
    # Leads: rows of 4, 5, 4.
    rows = [LEADS[0:4], LEADS[4:9], LEADS[9:13]]
    row_y = [182, 320, 458]
    row_h = [134, 134, 138]
    for leads, ry, rh in zip(rows, row_y, row_h):
        n = len(leads)
        lw = (CW - (n - 1) * 8) // n
        for i, lead in enumerate(leads):
            lx = MARGIN + i * (lw + 8)
            draw_lead(img, lx, ry, lw, rh, lead)
    # Map (left) and list (right).
    my = 602
    mh = 306
    draw_map(img, MARGIN, my, 482, mh)
    lx, lw = MARGIN + 490, CW - 490
    img.border(lx, my, lw, mh, RULE, 1)
    img.rect(lx + 1, my + 1, lw - 2, mh - 2, (255, 255, 255))
    draw_text(img, lx + 8, my + 7, "ALSO ON FRIDAY 20 NOVEMBER \u2014 23 MORE STORIES", 1, INK)
    img.hline(lx + 8, my + 22, lw - 16, RULE, 1)
    ly = my + 28
    for item in LIST:
        draw_text(img, lx + 8, ly, item, 1, INK)
        ly += 12
    # Date-check strip.
    dy = 914
    img.rect(MARGIN, dy, CW, 44, DARK)
    draw_text(img, MARGIN + 8, dy + 5, DATECHECK_TITLE, 1, (255, 210, 90))
    draw_text(img, MARGIN + 8, dy + 17, DATECHECK[0], 1, CREAM)
    draw_text(img, MARGIN + 8, dy + 29, DATECHECK[1], 1, CREAM)
    # Footer.
    fy = 966
    for ln in wrap_text(FOOTER, CW, 1):
        draw_text(img, MARGIN, fy, ln, 1, GREY)
        fy += 11
    draw_text_center(img, W // 2, fy + 4, "THE WORLD IN ONE DAY \u00b7 FRIDAY 20 NOVEMBER 2026",
                     1, GREY)
    return img

def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    img = build()
    data = png_bytes(img)
    with open(os.path.join(outdir, "entry.png"), "wb") as f:
        f.write(data)

if __name__ == "__main__":
    main()
