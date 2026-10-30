"""Портреты для разговоров: 128x144, слои в материальной кодировке (как у фигур), игра красит их палитрой человека.

Лицо анфас, чуть вполоборота, свет слева сверху. Слои: плечи и одежда (по типу верха), голова (3 формы),
глаза, нос, рот, брови (по 2–3 варианта), морщины, волосы сзади и спереди, борода, очки, шапки, шарф.
Затенение плавное по нормали части, затем квантуется ступенями — пиксель-арт без мыла.

Запуск: python3 gen_portraits.py <папка assets>  ->  assets/portrait/<слой>.png
"""
import sys, os, math
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "art"))
from common import (SKIN, HAIR, TOP, BOTTOM, SHOES, HAT, ACC, EYE, WHITE, METAL, TOP2, ACC2)   # noqa: E402

W, H = 128, 144
YY, XX = np.mgrid[0:H, 0:W].astype(float)
XX += 0.5
YY += 0.5
CX, CY = 64.0, 60.0          # центр лица
LIGHT = np.array([-0.55, -0.65, 0.52])
LIGHT = LIGHT / np.linalg.norm(LIGHT)


def ellipse(c, rx, ry):
    return ((XX - c[0]) / rx) ** 2 + ((YY - c[1]) / ry) ** 2 <= 1.0


def poly(pts):
    im = Image.new("L", (W, H), 0)
    ImageDraw.Draw(im).polygon([(x - 0.5, y - 0.5) for x, y in pts], fill=255)
    return np.array(im) > 0


def capsule(a, b, r1, r2=None):
    r2 = r1 if r2 is None else r2
    dx, dy = b[0] - a[0], b[1] - a[1]
    l2 = dx * dx + dy * dy + 1e-9
    t = np.clip(((XX - a[0]) * dx + (YY - a[1]) * dy) / l2, 0, 1)
    d = np.hypot(XX - (a[0] + t * dx), YY - (a[1] + t * dy))
    return d <= r1 + (r2 - r1) * t


def rect(x0, y0, x1, y1):
    return (XX >= x0) & (XX < x1) & (YY >= y0) & (YY < y1)


def mirror(m):
    """маска, симметричная относительно оси лица"""
    return m | m[:, ::-1]


class Layer:
    def __init__(self):
        self.mat = np.full((H, W), -1, int)
        self.lv = np.zeros((H, W))
        self.part = np.full((H, W), -1, int)
        self.n = 0

    def fill(self, mask, mat, base=0.84, c=None, r=None, amp=0.16, steps=0.045, flat=False):
        """Объём по сфере (центр c, радиусы r): нормаль из положения пикселя, свет слева сверху."""
        pid = self.n
        self.n += 1
        lv = np.full((H, W), base)
        if not flat:
            if c is None:
                ys, xs = np.nonzero(mask)
                if len(xs) == 0:
                    return pid
                c = ((xs.min() + xs.max() + 1) / 2, (ys.min() + ys.max() + 1) / 2)
                r = (max(2, (xs.max() - xs.min() + 1) / 2), max(2, (ys.max() - ys.min() + 1) / 2))
            nx = np.clip((XX - c[0]) / r[0], -1, 1)
            ny = np.clip((YY - c[1]) / r[1], -1, 1)
            nz = np.sqrt(np.clip(1 - nx * nx * 0.7 - ny * ny * 0.7, 0.05, 1))
            dot = nx * LIGHT[0] + ny * LIGHT[1] + nz * LIGHT[2]
            lv = base + amp * (dot - 0.55) * 1.6
            lv = np.round(lv / steps) * steps
        self.mat[mask] = mat
        self.lv[mask] = np.clip(lv[mask], 0.3, 1.0)
        self.part[mask] = pid
        return pid

    def px(self, x, y, mat, lv):
        x, y = int(math.floor(x)), int(math.floor(y))
        if 0 <= x < W and 0 <= y < H:
            self.mat[y, x] = mat
            self.lv[y, x] = lv

    def dk(self, x, y, k=0.1):
        x, y = int(math.floor(x)), int(math.floor(y))
        if 0 <= x < W and 0 <= y < H and self.mat[y, x] >= 0:
            self.lv[y, x] = max(0.3, self.lv[y, x] - k)

    def lt(self, x, y, k=0.1):
        x, y = int(math.floor(x)), int(math.floor(y))
        if 0 <= x < W and 0 <= y < H and self.mat[y, x] >= 0:
            self.lv[y, x] = min(1.0, self.lv[y, x] + k)

    def paint(self, mask, mat, lv):
        sel = mask
        self.mat[sel] = mat
        self.lv[sel] = lv

    def shade_mask(self, mask, k):
        sel = mask & (self.mat >= 0)
        self.lv[sel] = np.clip(self.lv[sel] + k, 0.3, 1.0)

    def line(self, a, b, fn, *args):
        n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1]))) + 1
        for i in range(n + 1):
            t = i / max(1, n)
            fn(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, *args)

    def outline(self, lv=0.36, inner=True):
        occ = self.mat >= 0
        edge = np.zeros_like(occ)
        inn = np.zeros_like(occ)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nb = np.zeros_like(occ)
            pn = np.full((H, W), -1, int)
            ys = slice(max(0, -dy), H - max(0, dy))
            yd = slice(max(0, dy), H - max(0, -dy))
            xs = slice(max(0, -dx), W - max(0, dx))
            xd = slice(max(0, dx), W - max(0, -dx))
            nb[yd, xd] = occ[ys, xs]
            pn[yd, xd] = self.part[ys, xs]
            edge |= occ & ~nb
            inn |= occ & (pn >= 0) & (pn < self.part)
        keep = np.isin(self.mat, (EYE, WHITE))
        self.lv[edge & ~keep] = lv
        if inner:
            sel = inn & ~edge & ~keep
            self.lv[sel] = np.minimum(self.lv[sel] - 0.12, self.lv[sel])

    def image(self):
        a = np.zeros((H, W, 4), np.uint8)
        occ = self.mat >= 0
        a[..., 0][occ] = (self.mat[occ] * 16 + 8).astype(np.uint8)
        a[..., 1][occ] = np.clip(self.lv[occ] * 255, 0, 255).astype(np.uint8)
        a[..., 3][occ] = 255
        return Image.fromarray(a, "RGBA")


# ---------------- лицо ----------------

FACES = {   # полуширина скул, полуширина челюсти, высота лица, подбородок
    0: (25.0, 18.0, 33.0, 9.0),      # овальное
    1: (27.5, 23.0, 31.0, 11.0),     # круглое, широкое
    2: (23.5, 15.5, 35.0, 7.0),      # вытянутое, скуластое
}


def face_mask(f):
    cw, jw, fh, ch = FACES[f]
    top = CY - fh * 0.62
    pts = [(CX - cw * 0.92, top + 8), (CX - cw, CY - 4), (CX - cw * 0.96, CY + 8), (CX - jw, CY + fh * 0.62),
           (CX - ch, CY + fh * 0.92), (CX, CY + fh * 0.98), (CX + ch, CY + fh * 0.92), (CX + jw, CY + fh * 0.62),
           (CX + cw * 0.96, CY + 8), (CX + cw, CY - 4), (CX + cw * 0.92, top + 8)]
    return poly(pts) | ellipse((CX, top + 14), cw * 0.95, 16)


def layer_head(f):
    L = Layer()
    cw, jw, fh, ch = FACES[f]
    # шея
    neck = poly([(CX - jw * 0.66, CY + fh * 0.5), (CX + jw * 0.66, CY + fh * 0.5), (CX + jw * 0.8, CY + fh + 22), (CX - jw * 0.8, CY + fh + 22)])
    L.fill(neck, SKIN, 0.74, c=(CX, CY + fh), r=(jw * 0.7, 30), amp=0.1)
    # тень от подбородка на шее
    L.shade_mask(neck & ellipse((CX + 3, CY + fh * 0.98), jw * 0.9, 9), -0.1)
    # уши
    for s in (-1, 1):
        L.fill(ellipse((CX + s * (cw + 1.5), CY + 2), 4.2, 8.5), SKIN, 0.8)
    face = face_mask(f)
    L.fill(face, SKIN, 0.88, c=(CX - 2, CY - 2), r=(cw * 1.05, fh * 1.05), amp=0.2)
    L.outline()
    # раковины ушей, лёгкий румянец скул (теплее — светлее), впадины висков
    for s in (-1, 1):
        L.line((CX + s * (cw + 1.5), CY - 3), (CX + s * (cw + 1.0), CY + 6), L.dk, 0.12)
    L.shade_mask(ellipse((CX - cw * 0.55, CY + 9), 6, 4), 0.04)
    L.shade_mask(ellipse((CX + cw * 0.6, CY + 9), 6, 4), -0.03)
    L.shade_mask(ellipse((CX + cw * 0.95, CY - 8), 4, 9), -0.05)
    return L


def layer_eyes(n, female):
    L = Layer()
    ey = CY - 3
    for s in (-1, 1):
        ex = CX + s * 11
        w = 6.0 if n != 1 else 6.4
        h = 2.6 if n == 1 else (3.6 if n == 0 else 3.0)
        white = ellipse((ex, ey), w, h)
        L.fill(white, WHITE, 0.82, flat=True)
        iris = ellipse((ex + 0.8, ey + 0.2), 2.6, min(h, 2.9))
        L.paint(iris & white, EYE, 0.55)
        L.paint(ellipse((ex + 0.8, ey + 0.3), 1.3, 1.4) & white, EYE, 0.18)
        L.px(ex - 0.2, ey - 1, WHITE, 1.0)           # блик
        # веко сверху и складка
        for x in range(int(ex - w), int(ex + w) + 1):
            dy = h * math.sqrt(max(0, 1 - ((x + 0.5 - ex) / w) ** 2))
            L.px(x, ey - dy - 0.5, SKIN, 0.42)
            if n == 2:
                L.px(x, ey - dy - 2.0, SKIN, 0.6)     # тяжёлое веко
                L.px(x, ey - dy + 0.6, SKIN, 0.66)
            elif n == 0:
                L.px(x, ey - dy - 2.5, SKIN, 0.7)
        # нижнее веко
        for x in range(int(ex - w + 2), int(ex + w - 1)):
            dy = h * math.sqrt(max(0, 1 - ((x + 0.5 - ex) / w) ** 2))
            L.px(x, ey + dy + 0.4, SKIN, 0.7)
        if female:
            L.px(ex - s * 0 + w * s, ey - 2, EYE, 0.2)
            L.px(ex + w * s + s, ey - 3, EYE, 0.2)
            for x in range(int(ex - w + 1), int(ex + w)):
                dy = h * math.sqrt(max(0, 1 - ((x + 0.5 - ex) / w) ** 2))
                L.px(x, ey - dy - 0.5, EYE, 0.22)
    return L


def layer_nose(n):
    L = Layer()
    if n == 0:     # прямой
        bridge = poly([(CX - 2, CY - 2), (CX + 2, CY - 2), (CX + 4, CY + 12), (CX - 4, CY + 12)])
        tip = ellipse((CX, CY + 13), 5, 3.4)
    elif n == 1:   # широкий, картошкой
        bridge = poly([(CX - 2.5, CY - 2), (CX + 2.5, CY - 2), (CX + 5, CY + 11), (CX - 5, CY + 11)])
        tip = ellipse((CX, CY + 13), 6.8, 4.4)
    else:          # с горбинкой, длинный
        bridge = poly([(CX - 2, CY - 3), (CX + 3, CY - 3), (CX + 5, CY + 6), (CX + 4, CY + 14), (CX - 3, CY + 14)])
        tip = ellipse((CX + 0.5, CY + 14.5), 4.6, 3.2)
    m = bridge | tip
    L.fill(m, SKIN, 0.9, c=(CX - 2, CY + 8), r=(6, 10), amp=0.18)
    # тень справа от спинки, ноздри, тень под носом
    for y in range(int(CY), int(CY + 12)):
        L.dk(CX + 3 + (y - CY) * 0.15, y, 0.12)
    nw = {0: 4.0, 1: 5.4, 2: 3.6}[n]
    L.px(CX - nw + 1, CY + 14 + (1 if n == 2 else 0), SKIN, 0.45)
    L.px(CX + nw - 1, CY + 14 + (1 if n == 2 else 0), SKIN, 0.45)
    L.px(CX - 1, CY + 11, SKIN, 1.0)
    for x in range(int(CX - nw), int(CX + nw + 1)):
        L.px(x, CY + 17 + (1 if n == 2 else 0), SKIN, 0.7)
    return L


def layer_mouth(n, female):
    L = Layer()
    my = CY + 22
    w = 8.0 if not female else 7.2
    for x in range(int(CX - w), int(CX + w) + 1):
        k = (x + 0.5 - CX) / w
        dy = (0.8 * k * k if n == 0 else -0.6 * k * k + 0.6)
        L.px(x, my + dy, SKIN, 0.42)
        if female:
            L.px(x, my + dy - 1, ACC2 if False else SKIN, 0.62)
            if abs(k) < 0.8:
                L.px(x, my + dy + 1, SKIN, 0.64)
                L.px(x, my + dy + 2, SKIN, 0.72)
        else:
            if abs(k) < 0.6:
                L.px(x, my + dy + 2, SKIN, 0.74)
    # ямка над губой и под губой
    L.px(CX, my - 3, SKIN, 0.78)
    L.px(CX, my + 5, SKIN, 0.76)
    L.px(CX + 1, my + 5, SKIN, 0.76)
    return L


def layer_brows(n):
    L = Layer()
    for s in (-1, 1):
        x0, x1 = CX + s * 4, CX + s * 18
        for i in range(15):
            t = i / 14
            x = x0 + (x1 - x0) * t
            y = CY - 10 - math.sin(t * math.pi) * 2.6 + t * 0.8
            th = (2.6 if n == 1 else 1.6) * (1 - t * 0.4)
            for k in range(int(round(th)) + 1):
                L.px(x, y + k - th / 2, HAIR, 0.62 if k == 0 else 0.5)
    return L


def layer_wrinkles():
    L = Layer()
    for y in (CY - 19, CY - 15):                         # лоб
        for x in range(int(CX - 12), int(CX + 12)):
            L.px(x, y + 0.6 * math.sin(x * 0.4), SKIN, 0.68)
    for s in (-1, 1):
        L.line((CX + s * 7, CY + 12), (CX + s * 11, CY + 22), L.px, SKIN, 0.66)   # носогубные
        L.line((CX + s * 17, CY - 2), (CX + s * 20, CY - 4), L.px, SKIN, 0.66)    # гусиные лапки
        L.line((CX + s * 17, CY + 0), (CX + s * 20, CY + 1), L.px, SKIN, 0.68)
        L.line((CX + s * 8, CY + 2), (CX + s * 13, CY + 3), L.px, SKIN, 0.7)      # мешки
    return L


# ---------------- волосы ----------------

def hair_masks(kind, f):
    """(сзади головы, спереди) маски волос."""
    cw, jw, fh, ch = FACES[f]
    top = CY - fh * 0.62
    crown = ellipse((CX, top + 10), cw + 3, 18)
    above = YY < top + 13
    fringe = poly([(CX - cw - 1, top + 16), (CX - cw + 2, top + 2), (CX, top - 4), (CX + cw - 2, top + 2), (CX + cw + 1, top + 16),
                   (CX + cw * 0.5, top + 10), (CX - cw * 0.2, top + 13)])
    sides = (rect(CX - cw - 3, top + 8, CX - cw + 3, CY - 2) | rect(CX + cw - 3, top + 8, CX + cw + 3, CY - 2)) & ellipse((CX, CY - 6), cw + 3, 30)
    back = np.zeros((H, W), bool)
    front = np.zeros((H, W), bool)
    if kind in ("short", "side", "crop", "receding", "bald"):
        front = (crown & above) | sides
        if kind == "side":
            front |= poly([(CX - cw, top + 12), (CX - 6, top - 2), (CX + cw + 1, top + 6), (CX + cw - 2, top + 15), (CX - 4, top + 8)])
        if kind == "crop":
            front = crown & (YY < top + 8) | (sides & (YY < CY - 8))
        if kind == "receding":
            front = (sides | (crown & (YY < top + 4))) & ~ellipse((CX + 2, top + 6), cw * 0.75, 8)
        if kind == "bald":
            front = sides & (YY > CY - 18)
    elif kind == "bob":
        back = ellipse((CX, CY - 4), cw + 7, fh * 0.95) & (YY < CY + 16)
        front = fringe | sides
    elif kind == "long":
        back = (ellipse((CX, CY - 4), cw + 7, fh) | rect(CX - cw - 7, CY - 4, CX + cw + 7, CY + 50)) & (YY < CY + 52)
        front = fringe | sides
    elif kind in ("bun", "pony", "braid"):
        back = ellipse((CX, CY - 6), cw + 4, fh * 0.8) & (YY < CY - 8)
        if kind == "bun":
            back |= ellipse((CX, top - 4), 10, 8)
        if kind == "pony":
            back |= capsule((CX + cw * 0.6, top + 4), (CX + cw + 10, CY + 18), 5, 3)
        if kind == "braid":
            back |= capsule((CX - cw * 0.5, CY - 8), (CX - cw - 6, CY + 40), 4.5, 3.4)
        front = poly([(CX - cw - 1, top + 16), (CX - cw + 2, top + 2), (CX, top - 3), (CX + cw - 2, top + 2), (CX + cw + 1, top + 16),
                      (CX + 4, top + 6), (CX - 4, top + 6)]) | sides
    elif kind == "curly":
        m = np.zeros((H, W), bool)
        for ang in range(180, 361, 18):
            r = math.radians(ang)
            m |= ellipse((CX + (cw + 2) * math.cos(r), top + 12 + 18 * math.sin(r)), 6, 6)
        front = (m | (crown & above)) & (YY < CY - 2)
    elif kind == "perm":
        m = np.zeros((H, W), bool)
        for ang in range(150, 391, 16):
            r = math.radians(ang)
            m |= ellipse((CX + (cw + 6) * math.cos(r), CY - 8 + 26 * math.sin(r)), 8, 8)
        back = m & (YY < CY + 18)
        front = (crown & above) | (fringe & (YY < top + 12))
    return back, front


def layer_hair(kind, f, part):
    L = Layer()
    back, front = hair_masks(kind, f)
    m = back if part == "b" else front
    if not m.any():
        return L
    cw, jw, fh, ch = FACES[f]
    L.fill(m, HAIR, 0.8 if part == "b" else 0.86, c=(CX - 3, CY - 14), r=(cw + 8, fh + 6), amp=0.22)
    L.outline()
    # пряди: тёмные штрихи по направлению роста
    rnd = np.random.default_rng(len(kind) * 7 + (1 if part == "b" else 0))
    ys, xs = np.nonzero(m)
    for _ in range(int(len(xs) / 14)):
        i = rnd.integers(len(xs))
        x, y = xs[i], ys[i]
        ang = math.atan2(y - (CY - 40), x - CX)
        for k in range(4):
            L.dk(x + math.cos(ang) * k, y + math.sin(ang) * k, 0.07)
    if kind in ("curly", "perm"):
        for _ in range(int(len(xs) / 10)):
            i = rnd.integers(len(xs))
            L.lt(xs[i], ys[i], 0.08)
    return L


def layer_beard(kind, f):
    L = Layer()
    cw, jw, fh, ch = FACES[f]
    my = CY + 22
    if kind == "full":
        m = face_mask(f) & (YY > CY + 8) & ~ellipse((CX, my + 1), 8, 3.4) & ~ellipse((CX, CY + 12), 7, 6)
        m |= ellipse((CX, CY + fh * 0.98), jw * 0.8, 9) & (YY > CY + 10)
        L.fill(m, HAIR, 0.78, amp=0.16)
        L.outline()
        rnd = np.random.default_rng(3)
        ys, xs = np.nonzero(m)
        for _ in range(len(xs) // 8):
            i = rnd.integers(len(xs))
            L.dk(xs[i], ys[i], 0.08)
            L.dk(xs[i], ys[i] + 1, 0.06)
    elif kind == "goatee":
        L.fill(ellipse((CX, my + 8), 6, 6) & (YY > my + 3), HAIR, 0.78)
        L.fill(capsule((CX - 8, my - 2.5), (CX + 8, my - 2.5), 1.6), HAIR, 0.74)
        L.outline()
    elif kind == "mustache":
        L.fill(poly([(CX - 10, my), (CX - 6, my - 5), (CX, my - 4.4), (CX + 6, my - 5), (CX + 10, my), (CX + 5, my - 2), (CX, my - 2.4),
                     (CX - 5, my - 2)]), HAIR, 0.8)
        L.outline()
    elif kind == "stubble":
        m = face_mask(f) & (YY > CY + 12) & ~ellipse((CX, my + 1), 8, 2.6) & ~ellipse((CX, CY + 13), 6, 4)
        rnd = np.random.default_rng(5)
        ys, xs = np.nonzero(m)
        for i in range(len(xs)):
            if rnd.random() < 0.33:
                L.px(xs[i], ys[i], HAIR, 0.5 + rnd.random() * 0.15)
    return L


def layer_glasses():
    L = Layer()
    ey = CY - 3
    for s in (-1, 1):
        ex = CX + s * 11
        ring = ellipse((ex, ey), 9, 7) & ~ellipse((ex, ey), 7.6, 5.6)
        L.paint(ring, METAL, 0.34)
        L.px(ex - 3, ey - 3, WHITE, 1.0)
        L.px(ex - 2, ey - 4, WHITE, 0.9)
        L.line((ex + s * 9, ey - 2), (ex + s * 15, ey - 3), L.px, METAL, 0.34)
    L.line((CX - 3, ey - 3), (CX + 3, ey - 3), L.px, METAL, 0.4)
    return L


# ---------------- шапки ----------------

def layer_hat(kind, f):
    L = Layer()
    cw, jw, fh, ch = FACES[f]
    top = CY - fh * 0.62
    if kind == "fedora":
        crown = poly([(CX - cw + 2, top + 8), (CX - cw + 5, top - 16), (CX - 8, top - 22), (CX + 10, top - 22), (CX + cw - 4, top - 16),
                      (CX + cw - 1, top + 8)])
        L.fill(crown, HAT, 0.84)
        L.fill(ellipse((CX, top + 9), cw + 16, 5), HAT, 0.74, amp=0.1)
        L.fill(rect(CX - cw + 2, top + 1, CX + cw - 1, top + 7), ACC2, 0.6, amp=0.08)
        L.outline()
        L.line((CX - 2, top - 21), (CX + 1, top - 12), L.dk, 0.12)
    elif kind in ("cap", "police"):
        L.fill(ellipse((CX, top + 3), cw + 6, 13) & (YY < top + 9), HAT, 0.84)
        L.fill(ellipse((CX + 2, top + 11), cw + 4, 4.2) & (YY > top + 9), HAT if kind == "cap" else METAL, 0.6 if kind == "cap" else 0.3)
        if kind == "police":
            L.fill(rect(CX - cw - 4, top + 2, CX + cw + 4, top + 8) & ellipse((CX, top + 3), cw + 6, 13), ACC2, 0.8)
            L.fill(ellipse((CX, top - 2), 3.5, 3.5), WHITE, 0.95)
        L.outline()
    elif kind == "flatcap":
        L.fill(poly([(CX - cw - 4, top + 9), (CX - cw, top - 6), (CX - 4, top - 11), (CX + cw + 2, top - 6), (CX + cw + 10, top + 6),
                     (CX + cw + 6, top + 10)]), HAT, 0.84)
        L.outline()
        L.line((CX - cw + 2, top - 3), (CX + cw + 4, top + 2), L.dk, 0.1)
        L.px(CX - 2, top - 9, HAT, 1.0)
    elif kind == "beret":
        L.fill(ellipse((CX - 4, top - 1), cw + 9, 11), HAT, 0.84)
        L.fill(ellipse((CX + 2, top - 13), 2, 2.4), HAT, 0.7)
        L.outline()
    elif kind in ("ushanka", "fur_hat"):
        if kind == "ushanka":
            for s in (-1, 1):
                L.fill(poly([(CX + s * (cw - 4), top + 6), (CX + s * (cw + 7), top + 6), (CX + s * (cw + 6), CY + 18),
                             (CX + s * (cw - 2), CY + 16)]), HAT, 0.76)
            L.fill(ellipse((CX, top - 2), cw + 7, 15) & (YY < top + 6), HAT, 0.84)
            L.fill(rect(CX - cw - 7, top + 1, CX + cw + 7, top + 9), HAT, 0.92, amp=0.1)
        else:
            L.fill(rect(CX - cw - 3, top - 22, CX + cw + 3, top + 9) | ellipse((CX, top - 22), cw + 3, 4), HAT, 0.84)
        L.outline()
        rnd = np.random.default_rng(9)
        ys, xs = np.nonzero(L.mat >= 0)
        for _ in range(len(xs) // 5):
            i = rnd.integers(len(xs))
            L.dk(xs[i], ys[i], 0.08)
            L.lt(xs[i] - 1, ys[i] - 1, 0.06)
    elif kind == "beanie":
        L.fill(ellipse((CX, top + 4), cw + 4, 20) & (YY < top + 10), HAT, 0.84)
        L.fill(rect(CX - cw - 5, top + 3, CX + cw + 5, top + 11) & ellipse((CX, top + 4), cw + 6, 22), HAT, 0.74)
        L.fill(ellipse((CX, top - 17), 5, 4.4), HAT, 0.92)
        L.outline()
        for x in range(int(CX - cw - 4), int(CX + cw + 5), 3):
            L.line((x, top + 4), (x, top + 10), L.dk, 0.08)
    elif kind in ("hood", "kerchief"):
        outer = ellipse((CX, CY - 2), cw + 10, fh + 8) & ~(ellipse((CX, CY + 4), cw + 1, fh + 1) & (YY > top + 6))
        outer &= YY < CY + (30 if kind == "hood" else 34)
        L.fill(outer, HAT, 0.82)
        if kind == "kerchief":
            L.fill(poly([(CX - 6, CY + fh * 0.95), (CX + 6, CY + fh * 0.95), (CX + 2, CY + fh + 12), (CX - 3, CY + fh + 12)]), HAT, 0.7)
        L.outline()
        if kind == "kerchief":
            rnd = np.random.default_rng(11)
            ys, xs = np.nonzero(outer)
            for _ in range(len(xs) // 40):
                i = rnd.integers(len(xs))
                for dx, dy in ((0, 0), (1, 0), (0, 1), (-1, 0), (0, -1)):
                    L.px(xs[i] + dx, ys[i] + dy, ACC, 0.9 if (dx, dy) != (0, 0) else 1.0)
    elif kind == "helmet":
        L.fill(ellipse((CX, top + 4), cw + 7, 20) & (YY < top + 8), HAT, 0.86)
        L.fill(ellipse((CX, top + 8), cw + 12, 3.4), HAT, 0.7)
        L.outline()
        L.line((CX, top - 15), (CX, top + 5), L.lt, 0.12)
    return L


# ---------------- плечи и одежда ----------------

SHOULDER_Y = 101


def shoulders(width=60, drop=17):
    sy = SHOULDER_Y - 2
    body = poly([(CX - 20, sy), (CX + 20, sy), (CX + width - 12, sy + 6), (CX + width - 3, sy + drop),
                 (CX + width, H + 2), (CX - width, H + 2), (CX - width + 3, sy + drop), (CX - width + 12, sy + 6)])
    for s in (-1, 1):
        body |= ellipse((CX + s * (width - 13), sy + drop), 13, drop - 3) & (YY > sy + 4)
    return body & (YY > sy)


def layer_clothes(kind):
    L = Layer()
    sh = shoulders(63 if kind in ("parka", "fur") else 59)
    L.fill(sh, TOP, 0.84, c=(CX - 8, SHOULDER_Y + 20), r=(64, 40), amp=0.2)
    neck_l = (CX - 12, SHOULDER_Y - 2)
    neck_r = (CX + 12, SHOULDER_Y - 2)
    if kind in ("coat", "trench", "jacket", "suit", "uniform", "robe"):
        under = WHITE if kind in ("suit", "robe", "uniform") else TOP2
        L.fill(poly([neck_l, neck_r, (CX + 6, H), (CX - 6, H)]), under, 0.86, amp=0.08)
        if kind == "suit":
            L.fill(poly([(CX - 3, SHOULDER_Y + 2), (CX + 3, SHOULDER_Y + 2), (CX + 5, H), (CX - 5, H)]), ACC2, 0.76)
            L.fill(poly([(CX - 4, SHOULDER_Y - 1), (CX + 4, SHOULDER_Y - 1), (CX + 3, SHOULDER_Y + 4), (CX - 3, SHOULDER_Y + 4)]), ACC2, 0.68)
        # лацканы
        for s in (-1, 1):
            lap = poly([(CX + s * 12, SHOULDER_Y - 4), (CX + s * 22, SHOULDER_Y + 2), (CX + s * 13, SHOULDER_Y + 22), (CX + s * 6, H)])
            L.fill(lap & sh, TOP, 0.9 if s < 0 else 0.76, amp=0.06)
        if kind == "trench":
            for s in (-1, 1):
                L.fill(rect(CX + s * 30 - 5, SHOULDER_Y + 4, CX + s * 30 + 5, SHOULDER_Y + 9) & sh, TOP, 0.72)
        L.outline()
        for y in (SHOULDER_Y + 26, SHOULDER_Y + 36):
            L.px(CX - 9, y, ACC2 if kind != "uniform" else METAL, 0.9)
            L.px(CX - 9, y + 1, ACC2 if kind != "uniform" else METAL, 0.6)
        if kind == "uniform":
            for s in (-1, 1):
                L.fill(rect(CX + s * 34 - 8, SHOULDER_Y + 4, CX + s * 34 + 8, SHOULDER_Y + 9), ACC2, 0.8, flat=True)
            L.px(CX + 20, SHOULDER_Y + 20, ACC2, 1.0)
    elif kind in ("sweater", "tracksuit", "shirt", "dress", "apron"):
        if kind == "sweater":
            L.fill(capsule((CX - 13, SHOULDER_Y - 2), (CX + 13, SHOULDER_Y - 2), 6), TOP, 0.9, amp=0.1)
            L.outline()
            for x in range(int(CX - 18), int(CX + 19), 2):
                L.line((x, SHOULDER_Y - 6), (x, SHOULDER_Y + 2), L.dk, 0.08)
        elif kind == "tracksuit":
            L.outline()
            L.line((CX, SHOULDER_Y - 2), (CX, H), L.px, METAL, 0.6)
            for s in (-1, 1):
                L.line((CX + s * 26, SHOULDER_Y + 6), (CX + s * 50, SHOULDER_Y + 26), L.px, TOP2, 0.95)
                L.line((CX + s * 27, SHOULDER_Y + 8), (CX + s * 51, SHOULDER_Y + 28), L.px, TOP2, 0.8)
        elif kind == "shirt":
            for s in (-1, 1):
                L.fill(poly([(CX, SHOULDER_Y + 4), (CX + s * 14, SHOULDER_Y - 5), (CX + s * 18, SHOULDER_Y + 6), (CX + s * 4, SHOULDER_Y + 12)]),
                       TOP, 0.94, amp=0.06)
            L.outline()
            for y in range(int(SHOULDER_Y + 14), H, 9):
                L.px(CX, y, WHITE, 0.8)
        elif kind == "dress":
            L.fill(ellipse((CX, SHOULDER_Y - 1), 14, 7) & (YY > SHOULDER_Y - 2), SKIN, 0.8)
            L.outline()
        elif kind == "apron":
            L.fill(rect(CX - 20, SHOULDER_Y + 8, CX + 20, H) & sh, TOP2, 0.9)
            for s in (-1, 1):
                L.fill(capsule((CX + s * 18, SHOULDER_Y + 10), (CX + s * 16, SHOULDER_Y - 4), 2.4), TOP2, 0.86)
            L.outline()
    elif kind in ("parka", "fur"):
        ring = ellipse((CX, SHOULDER_Y + 2), 30, 11) & ~ellipse((CX, SHOULDER_Y - 3), 16, 6)
        L.fill(ring, ACC, 0.9, amp=0.14)
        L.outline()
        rnd = np.random.default_rng(13)
        ys, xs = np.nonzero(ring)
        for _ in range(len(xs) // 4):
            i = rnd.integers(len(xs))
            L.dk(xs[i], ys[i], 0.1)
        if kind == "parka":
            L.line((CX, SHOULDER_Y + 10), (CX, H), L.px, METAL, 0.55)
            L.line((CX - 40, SHOULDER_Y + 30), (CX + 40, SHOULDER_Y + 30), L.dk, 0.08)
    elif kind == "cardigan":
        L.fill(poly([neck_l, neck_r, (CX + 3, H), (CX - 3, H)]) & sh, TOP2, 0.88)
        L.fill(ellipse((CX, SHOULDER_Y - 1), 13, 5) & (YY > SHOULDER_Y - 3), TOP2, 0.92)
        L.outline()
        for y in range(int(SHOULDER_Y + 14), H, 10):
            L.px(CX - 5, y, ACC2, 0.8)
    else:
        L.outline()
    return L


def layer_scarf():
    L = Layer()
    m = ellipse((CX, SHOULDER_Y - 2), 24, 8) | capsule((CX + 10, SHOULDER_Y), (CX + 14, SHOULDER_Y + 30), 5, 4)
    L.fill(m, ACC, 0.84)
    L.outline()
    for y in range(int(SHOULDER_Y + 6), int(SHOULDER_Y + 32), 4):
        L.line((CX + 9, y), (CX + 18, y), L.px, ACC2, 0.7)
    return L


TORSOS = ("shirt", "jacket", "coat", "sweater", "apron", "uniform", "parka", "robe", "trench", "suit", "tracksuit", "cardigan", "fur", "dress")
HAIRS = ("short", "crop", "side", "receding", "bob", "long", "bun", "pony", "braid", "bald", "curly", "perm")
HATS = ("fedora", "cap", "flatcap", "beret", "ushanka", "fur_hat", "hood", "police", "beanie", "kerchief", "helmet")


def main(out):
    d = os.path.join(out, "portrait")
    os.makedirs(d, exist_ok=True)
    save = lambda L, nm: L.image().save(os.path.join(d, nm + ".png"), optimize=True)
    for f in FACES:
        save(layer_head(f), "head%d" % f)
        for k in HAIRS:
            save(layer_hair(k, f, "b"), "hairb_%s_%d" % (k, f))
            save(layer_hair(k, f, "f"), "hair_%s_%d" % (k, f))
        for k in ("full", "goatee", "mustache", "stubble"):
            save(layer_beard(k, f), "beard_%s_%d" % (k, f))
        for k in HATS:
            save(layer_hat(k, f), "hat_%s_%d" % (k, f))
    for n in range(3):
        save(layer_eyes(n, False), "eyes%d_m" % n)
        save(layer_eyes(n, True), "eyes%d_f" % n)
        save(layer_nose(n), "nose%d" % n)
    for n in range(2):
        save(layer_mouth(n, False), "mouth%d_m" % n)
        save(layer_mouth(n, True), "mouth%d_f" % n)
        save(layer_brows(n), "brows%d" % n)
    save(layer_wrinkles(), "wrinkles")
    save(layer_glasses(), "glasses")
    save(layer_scarf(), "scarf")
    for k in TORSOS:
        save(layer_clothes(k), "clothes_" + k)
    print("portrait layers:", len(os.listdir(d)))


def compose(assets, look, pal):
    """Сборка портрета для превью (тот же порядок, что в игре)."""
    from preview_chars2x import colorize
    names = portrait_layers(look)
    img = Image.new("RGBA", (W, H), (40, 40, 46, 255))
    for nm in names:
        p = os.path.join(assets, "portrait", nm + ".png")
        if os.path.exists(p):
            img.alpha_composite(colorize(Image.open(p), pal))
    return img


def portrait_layers(l):
    """Порядок слоёв портрета; повторён в Talk.portrait_layers()."""
    f = l.get("face", 0)
    hat = l.get("hat", "")
    hair = l.get("hair", "short")
    covered = hat in ("hood", "kerchief", "ushanka", "fur_hat", "helmet", "beanie")
    out = []
    if not covered:
        out.append("hairb_%s_%d" % (hair, f))
    out.append("head%d" % f)
    out.append("clothes_" + l.get("torso", "coat"))
    sx = "f" if l.get("female") else "m"
    out += ["eyes%d_%s" % (l.get("eyes", 0), sx), "nose%d" % l.get("nose", 0), "mouth%d_%s" % (l.get("mouth", 0), sx)]
    if l.get("age", 1) == 2:
        out.append("wrinkles")
    if l.get("beard"):
        out.append("beard_%s_%d" % (l["beard"], f))
    out.append("brows%d" % l.get("brows", 0))
    if not covered or hair in ("bob", "long", "perm"):
        out.append("hair_%s_%d" % (hair, f))
    if l.get("glasses"):
        out.append("glasses")
    if l.get("scarf"):
        out.append("scarf")
    if hat:
        out.append("hat_%s_%d" % (hat, f))
    return out


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "../../assets")
