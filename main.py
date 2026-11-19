#!/usr/bin/env python3
"""The World Today - Thursday 19 November 2026 in one image.

Draws a 1024x1024 newspaper front page summing up the day's world news
and encodes it as a PNG with a hand-rolled encoder. Standard library only,
no network, fully deterministic: two runs produce byte-identical output.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---- palette ---------------------------------------------------------------
PAPER = (247, 243, 232)
INK = (18, 18, 18)
NAVY = (20, 33, 61)
NAVY2 = (28, 46, 84)
RED = (185, 28, 28)
RED2 = (220, 38, 38)
GOLD = (201, 162, 39)
WHITE = (255, 255, 255)
SKY = (168, 205, 232)
SKY2 = (120, 175, 215)
GREY = (120, 120, 118)
LGREY = (228, 226, 218)
DARK = (40, 40, 40)
YELLOW = (250, 204, 21)
GREEN = (34, 120, 60)
TEAL = (14, 116, 144)
ORANGE = (234, 88, 12)
BROWN = (120, 72, 20)
SKIN1 = (232, 190, 150)
SKIN2 = (205, 160, 120)
SKIN3 = (240, 205, 170)

# ---- canvas ----------------------------------------------------------------
px = bytearray(W * H * 3)


def set_px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        px[i], px[i + 1], px[i + 2] = c


def fill_rect(x, y, w, h, c):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            px[i], px[i + 1], px[i + 2] = c


def rect(x, y, w, h, c, t=1):
    fill_rect(x, y, w, t, c)
    fill_rect(x, y + h - t, w, t, c)
    fill_rect(x, y, t, h, c)
    fill_rect(x + w - t, y, t, h, c)


def hline(x, y, w, c, t=1):
    fill_rect(x, y, w, t, c)


def vline(x, y, h, c, t=1):
    fill_rect(x, y, t, h, c)


def line(x0, y0, x1, y1, c, t=1):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        for a in range(t):
            for b in range(t):
                set_px(x0 + a, y0 + b, c)
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
    for yy in range(-r, r + 1):
        dx = int((r * r - yy * yy) ** 0.5)
        for xx in range(-dx, dx + 1):
            set_px(cx + xx, cy + yy, c)


def ring(cx, cy, r, c, t=2):
    for yy in range(-r, r + 1):
        for xx in range(-r, r + 1):
            d = (xx * xx + yy * yy) ** 0.5
            if r - t < d <= r:
                set_px(cx + xx, cy + yy, c)


def triangle(x0, y0, x1, y1, x2, y2, c):
    # filled triangle by scanlines
    pts = sorted([(x0, y0), (x1, y1), (x2, y2)], key=lambda p: p[1])
    (ax, ay), (bx, by), (cx, cy) = pts
    for y in range(ay, cy + 1):
        if y < by:
            xa = ax + (bx - ax) * (y - ay) / max(1, by - ay)
        else:
            xa = bx + (cx - bx) * (y - by) / max(1, cy - by)
        xb = ax + (cx - ax) * (y - ay) / max(1, cy - ay)
        lo, hi = int(min(xa, xb)), int(max(xa, xb))
        for x in range(lo, hi + 1):
            set_px(x, y, c)


def starburst(cx, cy, r, c, n=8):
    import math
    for k in range(n):
        a = 2 * math.pi * k / n
        line(cx, cy, int(cx + r * math.cos(a)), int(cy + r * math.sin(a)), c, 3)
    circle(cx, cy, max(2, r // 3), c)

# ---- 5x7 bitmap font (hand-typed) ------------------------------------------
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    "\u00b7": ("00000", "00000", "00000", "01100", "01100", "00000", "00000"),
}


def text_w(s, scale):
    return len(s) * 6 * scale


def draw_text(x, y, s, scale, c):
    cx = x
    for ch in s:
        g = FONT.get(ch.upper(), FONT[" "])
        for row in range(7):
            for col in range(5):
                if g[row][col] == "1":
                    fill_rect(cx + col * scale, y + row * scale, scale, scale, c)
        cx += 6 * scale
    return cx


def draw_text_center(x, y, w, s, scale, c):
    tw = text_w(s, scale)
    draw_text(x + (w - tw) // 2, y, s, scale, c)


def wrap(s, scale, max_w):
    words = s.split(" ")
    lines, cur = [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if text_w(trial, scale) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def para(x, y, s, scale, max_w, c, lh=None):
    lh = lh or (7 * scale + 4)
    for ln in wrap(s, scale, max_w):
        draw_text(x, y, ln, scale, c)
        y += lh
    return y

# ---- icons -----------------------------------------------------------------
def icon_bridge(x, y, w, h):
    fill_rect(x, y, w, h, (190, 220, 240))
    # water
    fill_rect(x, y + h - 18, w, 18, (40, 110, 180))
    for k in range(4):
        hline(x + 8 + k * 30, y + h - 12 + (k % 2) * 4, 20, WHITE, 2)
    # towers
    fill_rect(x + w // 4 - 4, y + 14, 8, h - 30, DARK)
    fill_rect(x + 3 * w // 4 - 4, y + 14, 8, h - 30, DARK)
    # deck + arch
    hline(x + 6, y + h - 34, w - 12, DARK, 4)
    line(x + 6, y + h - 34, x + w // 2, y + 18, DARK, 3)
    line(x + w - 6, y + h - 34, x + w // 2, y + 18, DARK, 3)
    # blast
    starburst(x + w // 2, y + 16, 16, YELLOW)
    starburst(x + w // 2, y + 16, 9, RED2)


def icon_ipo(x, y, w, h):
    fill_rect(x, y, w, h, (220, 240, 220))
    bars = [18, 26, 22, 34, 44, 54]
    bw = w // 8
    for i, bh in enumerate(bars):
        bx = x + 10 + i * (bw + 6)
        fill_rect(bx, y + h - 10 - bh, bw, bh, GREEN if i < 5 else GOLD)
    line(x + 8, y + h - 26, x + w - 8, y + 12, RED2, 3)
    triangle(x + w - 22, y + 6, x + w - 6, y + 8, x + w - 14, y + 20, RED2)
    draw_text(x + 8, y + 4, "$", 2, DARK)


def icon_capitol(x, y, w, h):
    fill_rect(x, y, w, h, (225, 228, 240))
    cx = x + w // 2
    # dome: a filled semicircle, radius 26, base at y+30
    import math
    for dy in range(0, 27):
        hw = int(math.sqrt(26 * 26 - dy * dy))
        fill_rect(cx - hw, y + 30 - dy, hw * 2, 1, NAVY2)
    fill_rect(cx - 2, y + 0, 4, 5, GOLD)  # finial on top of the dome
    # drum + columns
    fill_rect(cx - 30, y + 30, 60, 8, NAVY2)
    for i in range(5):
        fill_rect(cx - 34 + i * 15, y + 38, 7, h - 48, WHITE)
        rect(cx - 34 + i * 15, y + 38, 7, h - 48, NAVY2, 1)
    fill_rect(cx - 40, y + h - 12, 80, 8, NAVY2)


def icon_voyager(x, y, w, h):
    fill_rect(x, y, w, h, (16, 20, 48))
    import math
    for k in range(14):
        sx = x + (k * 37) % (w - 8) + 4
        sy = y + (k * 23) % (h - 8) + 4
        set_px(sx, sy, WHITE)
        set_px(sx + 1, sy, WHITE)
    # trajectory
    for k in range(0, w - 40, 8):
        fill_rect(x + 10 + k, y + h - 14 - k // 3, 5, 2, GOLD)
    # dish craft
    cx, cy = x + w - 42, y + 26
    triangle(cx - 4, cy + 4, cx + 22, cy - 10, cx + 26, cy + 8, (200, 200, 210))
    line(cx, cy, cx - 18, cy + 16, WHITE, 2)
    fill_rect(cx - 22, cy + 14, 10, 6, YELLOW)
    circle(cx + 2, cy - 2, 5, WHITE)


def icon_gta(x, y, w, h):
    fill_rect(x, y, w, h, (255, 190, 120))
    circle(x + w - 34, y + 20, 14, YELLOW)
    ring(x + w - 34, y + 20, 18, ORANGE, 2)
    # skyline (kept short so the "VI" label stays clear of the towers)
    hs = [26, 38, 30, 44, 34, 24]
    bw = w // 7
    for i, bh in enumerate(hs):
        bx = x + 6 + i * (bw + 3)
        fill_rect(bx, y + h - 8 - bh, bw, bh, (30, 30, 46))
        fill_rect(bx + 3, y + h - 4 - bh, 3, 3, YELLOW)
        fill_rect(bx + 3, y + h - 12 - bh, 3, 3, YELLOW)
    # road
    fill_rect(x, y + h - 8, w, 8, DARK)
    for k in range(0, w, 24):
        fill_rect(x + k, y + h - 5, 12, 2, YELLOW)
    draw_text(x + 8, y + 4, "VI", 3, (30, 30, 46))


def icon_tank(x, y, w, h):
    fill_rect(x, y, w, h, (222, 214, 190))
    # ground
    fill_rect(x, y + h - 14, w, 14, (150, 130, 90))
    # hull + turret + barrel
    fill_rect(x + w // 2 - 34, y + h - 40, 78, 24, (70, 90, 50))
    fill_rect(x + w // 2 - 16, y + h - 56, 36, 18, (70, 90, 50))
    line(x + w // 2 + 18, y + h - 50, x + w - 8, y + h - 58, (50, 66, 38), 4)
    for i in range(4):
        circle(x + w // 2 - 26 + i * 18, y + h - 18, 7, DARK)
        circle(x + w // 2 - 26 + i * 18, y + h - 18, 3, GREY)
    # dust
    for k in range(5):
        circle(x + 14 + k * 8, y + h - 26 - (k % 2) * 6, 3, (180, 165, 130))


def draw_hero_art(x, y, w, h):
    # sky
    fill_rect(x, y, w, h, SKY)
    fill_rect(x, y, w, h // 2, SKY2)
    circle(x + w - 46, y + 30, 20, YELLOW)
    # Shenzhen skyline
    towers = [(0, 70), (34, 96), (72, 120), (112, 84), (150, 108), (190, 64),
              (226, 92), (262, 78), (296, 104), (330, 88)]
    for tx, th in towers:
        fill_rect(x + tx, y + h - 92 - th, 30, th + 92, NAVY2)
    fill_rect(x, y + h - 92, w, 92, (200, 205, 215))
    # red carpet
    fill_rect(x, y + h - 34, w, 34, RED)
    fill_rect(x, y + h - 34, w, 4, GOLD)
    # three leaders shaking hands
    def figure(fx, skin, suit, hair):
        circle(fx, y + h - 108, 15, skin)
        # hair
        fill_rect(fx - 15, y + h - 122, 30, 8, hair)
        fill_rect(fx - 15, y + h - 122, 30, 5, hair)
        # suit body
        fill_rect(fx - 20, y + h - 92, 40, 60, suit)
        fill_rect(fx - 4, y + h - 92, 8, 60, WHITE)
        triangle(fx - 4, y + h - 92, fx + 4, y + h - 92, fx, y + h - 76, RED2)
    figure(x + 78, SKIN1, NAVY, (200, 200, 200))
    figure(x + w // 2, SKIN2, DARK, (30, 30, 30))
    figure(x + w - 78, SKIN3, (60, 60, 70), (180, 150, 90))
    # arms meeting at centre
    line(x + 96, y + h - 76, x + w // 2 - 8, y + h - 62, NAVY, 4)
    line(x + w - 96, y + h - 76, x + w // 2 + 8, y + h - 62, (60, 60, 70), 4)
    line(x + w // 2 - 22, y + h - 84, x + w // 2 + 22, y + h - 58, DARK, 4)
    circle(x + w // 2, y + h - 70, 7, SKIN2)
    # caption
    fill_rect(x, y + h - 22, 150, 18, INK)
    draw_text(x + 8, y + h - 19, "SHENZHEN, CHINA", 1, WHITE)

# ---- page ------------------------------------------------------------------
def draw_page():
    fill_rect(0, 0, W, H, PAPER)
    # masthead
    fill_rect(0, 0, W, 104, NAVY)
    fill_rect(0, 104, W, 6, GOLD)
    draw_text_center(0, 26, W, "THE WORLD TODAY", 6, WHITE)
    draw_text_center(0, 76, W, "ONE DAY  -  ONE IMAGE  -  THE WORLD'S NEWS", 2, GOLD)
    # date band
    fill_rect(0, 110, W, 44, RED)
    draw_text_center(0, 121, W, "THURSDAY 19 NOVEMBER 2026", 3, WHITE)
    # hero
    hx, hy, hw, hh = 24, 168, 976, 272
    fill_rect(hx, hy, hw, hh, WHITE)
    rect(hx, hy, hw, hh, INK, 3)
    draw_hero_art(hx + 3, hy + 3, 380, hh - 6)
    vline(hx + 386, hy + 3, hh - 6, INK, 2)
    tx = hx + 404
    draw_text(tx, hy + 16, "LEAD STORY", 2, RED2)
    hline(tx, hy + 36, 150, RED2, 3)
    para(tx, hy + 50, "TRUMP, XI AND PUTIN MEET IN SHENZHEN", 4, 560, INK, 36)
    para(tx, hy + 168,
         "The three leaders shake hands in Shenzhen at a regional summit. "
         "Xi hugged Trump on the tarmac on arrival. A trilateral meeting "
         "is expected on Thursday.", 2, 556, DARK, 19)
    # tiles
    tiles = [
        ("CRIMEAN BRIDGE ATTACKED AGAIN",
         "Russia says the bridge was attacked again, in reports on Thursday.",
         icon_bridge),
        ("ANTHROPIC IPO: $81.3BN, BIGGEST EVER",
         "The Claude-maker raises $81.3bn and is poised for a debut worth "
         "more than $1.4tn.", icon_ipo),
        ("JEFFRIES SET TO BE FIRST BLACK HOUSE SPEAKER",
         "Democrats nominate Hakeem Jeffries, set to become the first "
         "African-American Speaker.", icon_capitol),
        ("VOYAGER 1 HITS ONE LIGHT-DAY",
         "After almost 50 years in space, NASA's Voyager 1 reaches a record "
         "one light-day from Earth.", icon_voyager),
        ("GTA VI ROLLOUT BEGINS",
         "Gamers enter Vice City as Grand Theft Auto VI begins its global "
         "rollout.", icon_gta),
        ("ISRAEL GROUND OPERATION IN GAZA",
         "Israeli troops and tanks advance across the Gaza ceasefire line "
         "in a rare ground operation.", icon_tank),
    ]
    tw, th = 320, 184
    gx, gy = 24, 456
    for i, (head, body, icon) in enumerate(tiles):
        cx = gx + (i % 3) * (tw + 8)
        cy = gy + (i // 3) * (th + 8)
        fill_rect(cx, cy, tw, th, WHITE)
        rect(cx, cy, tw, th, INK, 2)
        icon(cx + 2, cy + 2, tw - 4, 62)
        hline(cx + 2, cy + 64, tw - 4, INK, 2)
        para(cx + 10, cy + 72, head, 2, tw - 20, INK, 17)
        nlines = len(wrap(head, 2, tw - 20))
        para(cx + 10, cy + 72 + nlines * 17 + 4, body, 2, tw - 20, DARK, 17)
    # ticker
    ty = 856
    fill_rect(0, ty, W, 84, NAVY)
    fill_rect(0, ty, 96, 84, RED)
    draw_text(12, ty + 18, "LATEST", 2, WHITE)
    draw_text(12, ty + 40, "NEWS", 2, WHITE)
    draw_text(12, ty + 62, "19 NOV", 2, GOLD)
    ticker1 = ("Van Gogh sells for record $190.4m  \u00b7  Myanmar faces UN "
               "genocide verdict")
    ticker2 = ("Cyclone Akvan nears India's east coast  \u00b7  EU proposes "
               "45bn Ukraine loan")
    ticker3 = "Estonia plans to close its border with Russia"
    draw_text(112, ty + 12, ticker1, 2, WHITE)
    draw_text(112, ty + 38, ticker2, 2, GOLD)
    draw_text(112, ty + 64, ticker3, 2, WHITE)
    # footer
    draw_text_center(0, 956, W,
                     "SOURCES: BBC  -  NYT  -  AL JAZEERA  -  NDTV", 2, GREY)
    draw_text_center(0, 984, W,
                     "DRAWN BY CODE  -  THURSDAY 19 NOVEMBER 2026", 2, GREY)

# ---- PNG encoder -----------------------------------------------------------
def png_bytes():
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw.extend(px[y * W * 3:(y + 1) * W * 3])
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    draw_page()
    data = png_bytes()
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes)" % (os.path.join(out_dir, "entry.png"),
                                    len(data)))


if __name__ == "__main__":
    main()
