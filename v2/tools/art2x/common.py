"""Общие помощники пиксельной графики «Без лица» 2.0.

Персонажи рисуются в «материальной» кодировке: R = номер материала * 16 + 8, G = яркость (0..255),
игра красит их шейдером палитры (res://shaders/figure.gdshader). Остальная графика рисуется обычным цветом.
"""
from PIL import Image, ImageDraw
import math, random

# материалы фигуры
SKIN, HAIR, TOP, BOTTOM, SHOES, HAT, ACC, EYE, WHITE, METAL, TOP2, ACC2 = range(12)

# уровни яркости (в шейдере умножаются на 1.25)
OUT = 0.42
SH = 0.66
MID = 0.80
BASE = 0.88
HI = 1.0


def mat_px(m, s):
    return (m * 16 + 8, max(0, min(255, int(s * 255))), 0, 255)


import k2
k2.install()


def new(w, h):
    return k2.mark(Image.new("RGBA", (w * k2.K, h * k2.K), (0, 0, 0, 0)))


def thick_line(d, p1, p2, w, col):
    """Толстая линия с круглыми концами, без сглаживания."""
    x1, y1 = p1
    x2, y2 = p2
    d.line([(x1, y1), (x2, y2)], fill=col, width=w)
    r = (w - 1) / 2.0
    if w > 1:
        d.ellipse([x1 - r, y1 - r, x1 + r, y1 + r], fill=col)
        d.ellipse([x2 - r, y2 - r, x2 + r, y2 + r], fill=col)


def inner_outline(img, shade=OUT, only_mat=None):
    """Тёмная обводка по внутреннему краю непрозрачной области слоя (в материальной кодировке)."""
    w, h = img.size
    px = img.load()
    src = img.copy().load()
    for y in range(h):
        for x in range(w):
            p = src[x, y]
            if p[3] == 0:
                continue
            m = p[0] // 16
            if only_mat is not None and m not in only_mat:
                continue
            if m in (EYE, WHITE):
                continue
            edge = False
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if nx < 0 or ny < 0 or nx >= w or ny >= h or src[nx, ny][3] == 0:
                    edge = True
                    break
            if edge:
                px[x, y] = (p[0], int(min(p[1], shade * 255)), 0, 255)


def shade_rect(img, box, mat, shade):
    d = ImageDraw.Draw(img)
    d.rectangle(box, fill=mat_px(mat, shade))


# ---------- обычная палитра для мира ----------

def hexc(s, a=255):
    s = s.lstrip("#")
    if len(s) == 3:
        s = "".join(ch * 2 for ch in s)
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16), a)


def mul(c, k, a=None):
    return (max(0, min(255, int(c[0] * k))), max(0, min(255, int(c[1] * k))), max(0, min(255, int(c[2] * k))),
            c[3] if a is None else a)


def mix(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(4))


def noise_fill(img, box, base, amp, rnd, step=1):
    """Заливка с мелким шумом (кирпич, бетон)."""
    px = img.load()
    x0, y0, x1, y1 = box
    if k2.is_k(img):
        x0, y0, x1, y1 = (v * k2.K for v in box)
    for y in range(y0, y1):
        for x in range(x0, x1):
            k = 1.0 + (rnd.random() - 0.5) * amp
            px[x, y] = mul(base, k)


def rect(img, box, col):
    """box включительно: x0,y0,x1,y1"""
    ImageDraw.Draw(img).rectangle(box, fill=col)


def hline(img, x0, x1, y, col):
    ImageDraw.Draw(img).line([(x0, y), (x1, y)], fill=col)


def vline(img, x, y0, y1, col):
    ImageDraw.Draw(img).line([(x, y0), (x, y1)], fill=col)


def put(img, x, y, col):
    w, h = img.size
    if 0 <= x < w and 0 <= y < h:
        img.putpixel((x, y), col)
