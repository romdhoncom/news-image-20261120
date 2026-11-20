#!/usr/bin/env python3
"""Sum up Friday 20 November 2026 in one image.

A newspaper front page drawn entirely in code: own raster, own 5x7 bitmap
font, own PNG encoder. Pure Python 3 standard library only. No network, no
clock, no randomness: the same bytes every run.

Writes entry.png to $MAKEFUN_OUTPUT_DIR (default /output).
"""
import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (247, 243, 232)
WHITE = (255, 255, 255)
INK = (26, 26, 26)
GREY = (90, 90, 90)
RED = (178, 34, 34)
BLUE = (31, 78, 121)
SKY = (196, 208, 220)
RIVER = (70, 110, 150)
SEA = (46, 98, 150)
ORANGE = (230, 120, 40)
YELLOW = (240, 200, 80)
DARK = (40, 44, 52)

# 5x7 bitmap font: each glyph is 7 rows of 5 characters ('#' = on).
FONT = {
    'A': [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    'B': ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    'C': [".####", "#....", "#....", "#....", "#....", "#....", ".####"],
    'D': ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    'E': ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    'F': ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    'G': [".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."],
    'H': ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    'I': ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"],
    'J': ["..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."],
    'K': ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    'L': ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    'M': ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    'N': ["#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"],
    'O': [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    'P': ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    'Q': [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    'R': ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    'S': [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    'T': ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    'U': ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    'V': ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    'W': ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    'X': ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    'Y': ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    'Z': ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    '0': [".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."],
    '1': ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    '2': [".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"],
    '3': ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    '4': ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    '5': ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    '6': [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
    '7': ["#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."],
    '8': [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    '9': [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
    ' ': [".....", ".....", ".....", ".....", ".....", ".....", "....."],
    '.': [".....", ".....", ".....", ".....", ".....", ".##..", ".##.."],
    ',': [".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."],
    ':': [".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."],
    ';': [".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."],
    '!': ["..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."],
    '?': [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
    "'": ["..#..", "..#..", ".....", ".....", ".....", ".....", "....."],
    '"': [".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."],
    '-': [".....", ".....", ".....", "#####", ".....", ".....", "....."],
    '/': ["....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."],
    '%': ["##..#", "##.#.", "...#.", "..#..", ".#...", "#.##.", "#..##"],
    '$': ["..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."],
    '(': ["...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"],
    ')': ["##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."],
    '&': [".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"],
    '+': [".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."],
    '=': [".....", ".....", "#####", ".....", "#####", ".....", "....."],
}

canvas = bytearray(W * H * 3)


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        canvas[i], canvas[i + 1], canvas[i + 2] = c


def rect(x, y, w, h, c):
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            px(xx, yy, c)


def line(x0, y0, x1, y1, c):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        px(x0, y0, c)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def circle(cx, cy, r, c):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                px(xx, yy, c)


def ring(cx, cy, r, t, c):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            d = (xx - cx) ** 2 + (yy - cy) ** 2
            if (r - t) ** 2 <= d <= r * r:
                px(xx, yy, c)


def tri(x0, y0, x1, y1, x2, y2, c):
    # Filled triangle by scanline.
    ys = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
    (ax, ay), (bx, by), (cx, cy) = ys
    def edge(xa, ya, xb, yb, y):
        if yb == ya:
            return xa
        return xa + (xb - xa) * (y - ya) / (yb - ya)
    for y in range(ay, cy + 1):
        if y < by:
            xa = edge(ax, ay, bx, by, y)
            xb = edge(ax, ay, cx, cy, y)
        else:
            xa = edge(bx, by, cx, cy, y)
            xb = edge(ax, ay, cx, cy, y)
        for x in range(int(min(xa, xb)), int(max(xa, xb)) + 1):
            px(x, y, c)


def text(s, x, y, scale, c):
    cx = x
    for ch in s:
        g = FONT.get(ch, FONT[' '])
        for r in range(7):
            for col in range(5):
                if g[r][col] == '#':
                    rect(cx + col * scale, y + r * scale, scale, scale, c)
        cx += 6 * scale


def text_w(s, scale):
    return len(s) * 6 * scale - scale


def text_center(s, cx, y, scale, c):
    text(s, cx - text_w(s, scale) // 2, y, scale, c)


# ---------------------------------------------------------------- panels

def panel_frame(x, y, w, h):
    rect(x, y, w, h, WHITE)
    # 1px ink border
    rect(x, y, w, 2, INK)
    rect(x, y + h - 2, w, 2, INK)
    rect(x, y, 2, h, INK)
    rect(x + w - 2, y, 2, h, INK)


def pic_kyiv(x, y, w, h):
    # Sky, skyline, river, broken bridge, smoke.
    rect(x, y, w, h, SKY)
    # skyline blocks
    rect(x + 20, y + 62, 60, 48, DARK)
    rect(x + 95, y + 44, 44, 66, DARK)
    rect(x + 150, y + 70, 70, 40, DARK)
    rect(x + 300, y + 52, 52, 58, DARK)
    rect(x + 366, y + 68, 64, 42, DARK)
    rect(x + 436, y + 40, 34, 70, DARK)
    # windows in a neat grid on each block
    for bx, by, bw, bh in ((20, 62, 60, 48), (95, 44, 44, 66),
                           (150, 70, 70, 40), (300, 52, 52, 58),
                           (366, 68, 64, 42), (436, 40, 34, 70)):
        for wx in range(bx + 10, bx + bw - 6, 16):
            for wy in range(by + 10, by + bh - 8, 16):
                rect(x + wx, y + wy, 5, 6, (240, 220, 120))
    # river
    rect(x, y + 110, w, h - 110, RIVER)
    # bridge deck: two spans with a gap in the middle
    rect(x + 10, y + 96, 190, 10, INK)
    rect(x + 270, y + 96, 190, 10, INK)
    # broken ends (jagged)
    tri(x + 200, y + 96, x + 224, y + 96, x + 212, y + 112, INK)
    tri(x + 270, y + 96, x + 246, y + 96, x + 258, y + 112, INK)
    # pillars
    rect(x + 60, y + 106, 10, 34, INK)
    rect(x + 150, y + 106, 10, 34, INK)
    rect(x + 320, y + 106, 10, 34, INK)
    rect(x + 410, y + 106, 10, 34, INK)
    # smoke over the gap
    circle(x + 235, y + 66, 16, (120, 120, 120))
    circle(x + 222, y + 52, 11, (140, 140, 140))
    circle(x + 250, y + 48, 9, (160, 160, 160))
    # explosion flash at the gap
    circle(x + 235, y + 96, 8, ORANGE)
    circle(x + 235, y + 96, 4, YELLOW)


def pic_markets(x, y, w, h):
    rect(x, y, w, h, WHITE)
    # grid
    for gx in range(x + 30, x + w, 44):
        line(gx, y + 8, gx, y + h - 8, (225, 225, 225))
    for gy in range(y + 16, y + h, 26):
        line(x + 8, gy, x + w - 8, gy, (225, 225, 225))
    # falling line, left to right
    pts = [(x + 16, y + 22), (x + 70, y + 34), (x + 120, y + 30),
           (x + 175, y + 58), (x + 230, y + 66), (x + 285, y + 92),
           (x + 340, y + 96), (x + 395, y + 118), (x + 440, y + 126)]
    for a, b in zip(pts, pts[1:]):
        line(a[0], a[1], b[0], b[1], RED)
        line(a[0], a[1] + 1, b[0], b[1] + 1, RED)
        line(a[0], a[1] + 2, b[0], b[1] + 2, RED)
    # arrowhead at the end
    tri(x + 440, y + 126, x + 420, y + 116, x + 424, y + 134, RED)
    # candlesticks falling
    for i, (bx, by, bh) in enumerate([(40, 30, 26), (110, 48, 30),
                                      (185, 66, 34), (260, 84, 36),
                                      (335, 100, 38), (405, 116, 30)]):
        rect(x + bx, y + by, 18, bh, (200, 60, 60))
        line(x + bx + 9, y + by - 10, x + bx + 9, y + by + bh + 10, (200, 60, 60))


def pic_gta(x, y, w, h):
    # Sunset bands
    for i in range(h):
        t = i / h
        if t < 0.35:
            c = (250, 160, 90)
        elif t < 0.6:
            c = (245, 120, 110)
        elif t < 0.8:
            c = (150, 80, 140)
        else:
            c = (60, 50, 110)
        rect(x, y + i, w, 1, c)
    # sun
    circle(x + 350, y + 58, 26, (255, 230, 140))
    # palm silhouettes
    line(x + 70, y + 132, x + 78, y + 60, DARK)
    for dx, dy in [(-34, -12), (-20, -26), (0, -30), (20, -24), (34, -10)]:
        line(x + 78, y + 60, x + 78 + dx, y + 60 + dy, DARK)
    line(x + 420, y + 132, x + 412, y + 74, DARK)
    for dx, dy in [(-26, -10), (-14, -20), (2, -24), (16, -18), (26, -8)]:
        line(x + 412, y + 74, x + 412 + dx, y + 74 + dy, DARK)
    # road
    rect(x, y + 118, w, h - 118, (30, 30, 36))
    line(x, y + 128, x + w, y + 128, (240, 200, 60))
    # car
    rect(x + 170, y + 96, 130, 22, (220, 40, 60))
    rect(x + 200, y + 82, 70, 16, (220, 40, 60))
    rect(x + 208, y + 86, 24, 10, (180, 220, 240))
    rect(x + 238, y + 86, 24, 10, (180, 220, 240))
    circle(x + 196, y + 118, 9, INK)
    circle(x + 274, y + 118, 9, INK)
    circle(x + 196, y + 118, 4, (200, 200, 200))
    circle(x + 274, y + 118, 4, (200, 200, 200))
    # big VI in the sky
    text("VI", x + 200, y + 18, 5, WHITE)


def pic_sydney(x, y, w, h):
    rect(x, y, w, h, (232, 226, 210))
    # courthouse: pediment, columns, steps
    tri(x + 120, y + 22, x + 350, y + 22, x + 235, y + 62, (120, 110, 95))
    rect(x + 120, y + 62, 230, 8, (120, 110, 95))
    for cx in (140, 195, 250, 305):
        rect(x + cx, y + 70, 16, 52, (200, 192, 172))
    rect(x + 120, y + 122, 230, 8, (120, 110, 95))
    rect(x + 110, y + 130, 250, 5, (150, 142, 126))
    # flag pole and flag
    line(x + 235, y + 4, x + 235, y + 22, INK)
    rect(x + 235, y + 6, 26, 12, RED)
    # gavel block
    rect(x + 380, y + 100, 34, 10, (90, 70, 50))
    rect(x + 392, y + 84, 8, 18, (90, 70, 50))


def pic_senegal(x, y, w, h):
    rect(x, y, w, h, SEA)
    # waves
    for wy in (30, 62, 94, 122):
        for wx in range(0, w, 46):
            line(x + wx, y + wy, x + wx + 22, y + wy - 8, WHITE)
            line(x + wx + 22, y + wy - 8, x + wx + 44, y + wy, WHITE)
    # capsized boat: tilted hull, half under water
    tri(x + 150, y + 78, x + 320, y + 96, x + 150, y + 108, (110, 60, 30))
    rect(x + 150, y + 78, 170, 8, (110, 60, 30))
    line(x + 300, y + 96, x + 330, y + 60, (110, 60, 30))
    line(x + 300, y + 96, x + 336, y + 66, (110, 60, 30))
    # lifebuoy
    ring(x + 90, y + 100, 20, 8, ORANGE)
    rect(x + 82, y + 78, 16, 6, WHITE)
    rect(x + 82, y + 116, 16, 6, WHITE)
    rect(x + 68, y + 92, 6, 16, WHITE)
    rect(x + 106, y + 92, 6, 16, WHITE)
    # second small boat in the distance
    rect(x + 380, y + 66, 60, 10, DARK)
    line(x + 408, y + 66, x + 408, y + 46, DARK)


def pic_tokyo(x, y, w, h):
    rect(x, y, w, h, (226, 232, 238))
    # Diet building silhouette
    rect(x + 150, y + 10, 170, 62, (140, 148, 158))
    tri(x + 150, y + 10, x + 320, y + 10, x + 235, y + 1, (120, 128, 140))
    rect(x + 225, y + 34, 20, 38, (90, 98, 110))
    # placards held up at the sides, clear of the building
    for px0 in (40, 430):
        line(x + px0, y + 96, x + px0, y + 70, INK)
        rect(x + px0 - 22, y + 48, 44, 22, WHITE)
        line(x + px0 - 18, y + 54, x + px0 + 18, y + 54, RED)
        line(x + px0 - 18, y + 62, x + px0 + 10, y + 62, INK)
    # crowd: rows of heads and shoulders below the building
    for row, ry in enumerate((100, 118)):
        for i in range(9):
            cx = x + 30 + i * 48 + (24 if row else 0)
            circle(cx, y + ry, 8, [(200, 60, 60), (40, 80, 140), (60, 140, 80),
                                   (220, 160, 40), (120, 60, 140)][(i + row) % 5])
            rect(cx - 11, y + ry + 8, 22, 12, DARK)


PANELS = [
    ("KYIV BRIDGES HIT", "OVERNIGHT STRIKES", "3 DNIPRO SPANS DAMAGED", pic_kyiv),
    ("ASIA MARKETS ROUT", "WORST WEEK SINCE 2020", "TAIWAN -16% IN A WEEK", pic_markets),
    ("GTA VI: $2.36BN DAY", "24.6M COPIES SOLD", "SENSOR TOWER ESTIMATE", pic_gta),
    ("SYDNEY TERROR CHARGE", "MAN HELD AFTER RAID", "POLICE RAID IN SYDNEY", pic_sydney),
    ("BOAT CAPSIZES", "OFF SENEGAL: 4 DEAD", "50 ABOARD, SEARCH GOES ON", pic_senegal),
    ("13,000 RALLY", "IN TOKYO", "DEFEND THE CONSTITUTION", pic_tokyo),
]


def draw():
    rect(0, 0, W, H, PAPER)
    # Masthead
    text_center("THE WORLD IN ONE DAY", W // 2, 24, 4, INK)
    text_center("FRIDAY 20 NOVEMBER 2026", W // 2, 66, 3, RED)
    rect(16, 102, W - 32, 3, INK)
    rect(16, 108, W - 32, 1, INK)
    # Grid of six panels: 2 columns x 3 rows
    pw, ph = 490, 268
    gx0, gy0 = 16, 124
    for i, (l1, l2, sub, pic) in enumerate(PANELS):
        col, row = i % 2, i // 2
        x = gx0 + col * (pw + 12)
        y = gy0 + row * (ph + 12)
        panel_frame(x, y, pw, ph)
        pic(x + 10, y + 10, pw - 20, 140)
        text_center(l1, x + pw // 2, y + 164, 3, INK)
        text_center(l2, x + pw // 2, y + 190, 3, INK)
        rect(x + 60, y + 218, pw - 120, 2, (200, 200, 200))
        text_center(sub, x + pw // 2, y + 230, 2, GREY)
    # Bottom strip
    rect(16, 964, W - 32, 44, INK)
    text_center("SIX STORIES FROM FIVE CONTINENTS - ONE DAY IN THE WORLD",
                W // 2, 978, 2, WHITE)


def png_bytes():
    raw = b"".join(b"\x00" + bytes(canvas[y * W * 3:(y + 1) * W * 3])
                   for y in range(H))

    def chunk(typ, data):
        c = struct.pack(">I", len(data)) + typ + data
        return c + struct.pack(">I", zlib.crc32(typ + data) & 0xffffffff)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))


def main():
    draw()
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "entry.png"), "wb") as f:
        f.write(png_bytes())


if __name__ == "__main__":
    main()
