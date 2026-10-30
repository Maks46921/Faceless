"""Люди в двойной плотности: кадр 84x108, слои одежды в материальной кодировке (как в 2.0, но вдвое детальнее).

Позы те же, что в tools/art/gen_chars.py (57 кадров), скелет переводится в 2x и подгоняется под
телосложение: m — обычное, s — невысокое и худое, t — высокое, h — плотное, k — коренастое.
Каждая часть рисуется маской по скелету и сама затеняется (свет спереди сверху), потом обводка
по краю слоя и тёмная линия, где передняя часть лежит на задней, и ручные детали (пуговицы, швы, лицо).

Запуск: python3 gen_chars2x.py <папка assets>   ->  assets/fig2/<телосложение>/<слой>.png, assets/fig2/frames.txt
"""
import sys, os, math
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "art"))
import gen_chars as G0                                    # noqa: E402
from common import (SKIN, HAIR, TOP, BOTTOM, SHOES, HAT, ACC, EYE, WHITE, METAL, TOP2, ACC2)   # noqa: E402

SW, SH = 84, 108          # кадр: по высоте с запасом (высокие в шляпах), по ширине — только сколько надо
GROUND = 104
CX = 40
YY, XX = np.mgrid[0:SH, 0:SW].astype(float)
XX += 0.5
YY += 0.5

# уровни яркости (в шейдере ×1.25)
L_OUT, L_SH, L_MID, L_BASE, L_HI = 0.40, 0.62, 0.76, 0.86, 0.98

# телосложение: высота (тянет скелет вверх от земли), ширина (толщина тела и конечностей)
BUILDS = {"m": (1.0, 1.0), "s": (0.88, 0.86), "t": (1.12, 0.98), "h": (1.0, 1.26), "k": (0.9, 1.18)}
WM = 1.3                  # общая полнота: в 2x фигура плотнее, чем вдвое увеличенная старая

NO_HAND_ITEMS = ("climb", "carry", "lie", "slump", "strangle", "push", "choke", "cower", "phone", "smoke", "jump", "fall")


# ---------------- маски ----------------

def capsule(a, b, r1, r2=None):
    r2 = r1 if r2 is None else r2
    ax, ay = a
    bx, by = b
    dx, dy = bx - ax, by - ay
    l2 = dx * dx + dy * dy + 1e-9
    t = np.clip(((XX - ax) * dx + (YY - ay) * dy) / l2, 0, 1)
    d = np.hypot(XX - (ax + t * dx), YY - (ay + t * dy))
    return d <= r1 + (r2 - r1) * t


def ellipse(c, rx, ry):
    return ((XX - c[0]) / rx) ** 2 + ((YY - c[1]) / ry) ** 2 <= 1.0


def poly(pts):
    from PIL import ImageDraw
    im = Image.new("L", (SW, SH), 0)
    ImageDraw.Draw(im).polygon([(x - 0.5, y - 0.5) for x, y in pts], fill=255)
    return np.array(im) > 0


def rect(x0, y0, x1, y1):
    return (XX >= x0) & (XX < x1) & (YY >= y0) & (YY < y1)


def shifted(m, dx, dy):
    out = np.zeros_like(m)
    ys = slice(max(0, -dy), SH - max(0, dy))
    yd = slice(max(0, dy), SH - max(0, -dy))
    xs = slice(max(0, -dx), SW - max(0, dx))
    xd = slice(max(0, dx), SW - max(0, -dx))
    out[yd, xd] = m[ys, xs]
    return out


# ---------------- холст слоя ----------------

class Layer:
    def __init__(self, face=1):
        self.mat = np.full((SH, SW), -1, int)
        self.lv = np.zeros((SH, SW))
        self.part = np.full((SH, SW), -1, int)
        self.n = 0
        self.face = face          # куда смотрит лицо (1 вправо, -1 назад)

    def fill(self, mask, mat, base=L_BASE, flat=False, hi=True):
        """Часть с объёмом: край к свету светлее, край от света темнее (свет спереди сверху)."""
        pid = self.n
        self.n += 1
        lv = np.full((SH, SW), base)
        if not flat:
            lx, ly = 1, -1
            lit = mask & ~shifted(mask, -lx, -ly)
            d1 = mask & ~shifted(mask, lx, ly)
            d2 = mask & ~shifted(mask, 2 * lx, 2 * ly) & ~d1
            lv[d2] = base - 0.06
            lv[d1] = base - 0.12
            if hi:
                lv[lit & ~d1] = min(L_HI, base + 0.1)
        self.mat[mask] = mat
        self.lv[mask] = lv[mask]
        self.part[mask] = pid
        return pid

    def px(self, x, y, mat, lv):
        x, y = int(math.floor(x)), int(math.floor(y))
        if 0 <= x < SW and 0 <= y < SH:
            self.mat[y, x] = mat
            self.lv[y, x] = lv

    def dk(self, x, y, k=0.1):
        x, y = int(math.floor(x)), int(math.floor(y))
        if 0 <= x < SW and 0 <= y < SH and self.mat[y, x] >= 0:
            self.lv[y, x] = max(L_OUT, self.lv[y, x] - k)

    def lt(self, x, y, k=0.1):
        x, y = int(math.floor(x)), int(math.floor(y))
        if 0 <= x < SW and 0 <= y < SH and self.mat[y, x] >= 0:
            self.lv[y, x] = min(L_HI, self.lv[y, x] + k)

    def line(self, a, b, fn, *args):
        n = int(max(abs(b[0] - a[0]), abs(b[1] - a[1]))) + 1
        for i in range(n + 1):
            t = i / max(1, n)
            fn(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, *args)

    def outline(self, skip=(EYE, WHITE)):
        occ = self.mat >= 0
        edge = np.zeros_like(occ)
        inner = np.zeros_like(occ)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nb = shifted(occ, dx, dy)
            edge |= occ & ~nb
            pn = np.full((SH, SW), -1, int)
            ys = slice(max(0, -dy), SH - max(0, dy))
            yd = slice(max(0, dy), SH - max(0, -dy))
            xs = slice(max(0, -dx), SW - max(0, dx))
            xd = slice(max(0, dx), SW - max(0, -dx))
            pn[yd, xd] = self.part[ys, xs]
            inner |= occ & (pn >= 0) & (pn < self.part)
        keep = np.isin(self.mat, skip)
        self.lv[edge & ~keep] = L_OUT
        sel = inner & ~edge & ~keep
        self.lv[sel] = np.minimum(self.lv[sel], L_SH)

    def image(self):
        a = np.zeros((SH, SW, 4), np.uint8)
        occ = self.mat >= 0
        a[..., 0][occ] = (self.mat[occ] * 16 + 8).astype(np.uint8)
        a[..., 1][occ] = np.clip(self.lv[occ] * 255, 0, 255).astype(np.uint8)
        a[..., 3][occ] = 255
        return Image.fromarray(a, "RGBA")


# ---------------- скелет ----------------

def to2x(p, build):
    """Поза из 48 px -> 96 px с телосложением: рост тянет точки от земли вверх."""
    hk, _ = BUILDS[build]
    q = {}
    for k, v in p.items():
        if isinstance(v, tuple) and len(v) == 2:
            x = CX + (v[0] - 24) * 2
            y = GROUND - (G0.GROUND - v[1]) * 2 * hk
            q[k] = (x, y)
        else:
            q[k] = v
    # голова не тянется: держим её на прежнем расстоянии от плеч
    sh0 = p["sh"]
    hd0 = p["head"]
    q["head"] = (q["sh"][0] + (hd0[0] - sh0[0]) * 2, q["sh"][1] + (hd0[1] - sh0[1]) * 2 - 2)
    return q


class Ctx:
    def __init__(self, p, build, fname):
        self.p = p
        self.build = build
        self.wk = BUILDS[build][1] * WM
        self.hk = BUILDS[build][0]
        self.fname = fname
        self.face = p.get("hd", 1)

    def __getitem__(self, k):
        return self.p[k]


def H(c, dx, dy=0.0):
    """точка у головы: dx вперёд по взгляду."""
    hx, hy = c["head"]
    return (hx + dx * c.face, hy + dy)


def head_mask(c):
    hx, hy = c["head"]
    f = c.face
    m = ellipse((hx, hy), 7.0, 8.0)
    # челюсть и подбородок вперёд
    m |= poly([(hx + 1 * f, hy + 1), (hx + 6.2 * f, hy + 2.5), (hx + 5.4 * f, hy + 6.6), (hx + 1.5 * f, hy + 8.0), (hx - 2 * f, hy + 6.5)])
    return m


# ---------------- слои ----------------

def layer_body(c):
    L = Layer()
    hx, hy = c["head"]
    sx, sy = c["sh"]
    f = c.face
    L.fill(capsule((sx + 1.5 * f, sy - 1), (hx, hy + 5), 3.1 * min(1.15, c.wk), 2.8), SKIN, L_MID, hi=False)
    head = head_mask(c)
    nose = poly([H(c, 5.4, -2.2), H(c, 8.4, 2.4), H(c, 6.0, 3.0)])
    L.fill(head | nose, SKIN)
    # ухо на затылочной стороне
    L.fill(ellipse(H(c, -1.6, 0.6), 1.5, 2.3), SKIN, L_MID, hi=False)
    L.outline()
    # лицо: глаз (белок + зрачок), веко, рот, щека, ноздря
    ex, ey = H(c, 3.0, -0.6)
    L.px(ex, ey, WHITE, 0.82)
    L.px(ex + f, ey, EYE, 0.25)
    L.px(ex + f, ey - 1, SKIN, L_SH)
    L.px(ex, ey - 1, SKIN, L_MID)
    L.px(*H(c, 5.6, 2.6), SKIN, L_SH)              # ноздря
    for dx in (3.2, 4.2):
        L.px(*H(c, dx, 4.6), SKIN, L_SH)            # рот
    L.px(*H(c, 2.0, 2.4), SKIN, L_MID)              # скула
    L.px(*H(c, -1.6, 0.6), SKIN, L_SH)              # раковина уха
    return L


def layer_wrinkles(c):
    """Морщины и седая щетина бровей у стариков: отдельный слой поверх лица."""
    L = Layer()
    f = c.face
    for dx, dy in ((1.6, 2.0), (2.2, 3.4), (4.4, -2.6), (5.2, -2.6), (0.6, -3.8), (2.4, -4.2)):
        L.px(*H(c, dx, dy), SKIN, L_SH)
    L.px(*H(c, 4.8, 6.2), SKIN, L_SH)
    return L


def leg_parts(c, side):
    hip = c["hip"]
    k, fo = c["k" + side], c["f" + side]
    w = c.wk
    return hip, k, fo, w


def foot_mask(c, side, length=8.6, h=2.5):
    k, fo = c["k" + side], c["f" + side]
    fwd = 1.0
    toe = (fo[0] + length * 0.75 * fwd, fo[1] + 0.6)
    heel = (fo[0] - 2.2, fo[1] + 0.6)
    return capsule(heel, toe, h, h * 0.78), toe


def layer_legs(c, kind):
    L = Layer()
    hip = c["hip"]
    w = c.wk
    for side, base in (("b", L_MID), ("f", L_BASE)):
        k, fo = c["k" + side], c["f" + side]
        if kind == "pants":
            L.fill(capsule(hip, k, 4.6 * w, 4.0 * w) | capsule(k, fo, 3.9 * w, 3.1 * w), BOTTOM, base)
        elif kind == "jeans":
            L.fill(capsule(hip, k, 4.4 * w, 3.8 * w) | capsule(k, fo, 3.6 * w, 3.0 * w), BOTTOM, base)
        else:   # юбка: ноги в чулках
            L.fill(capsule(hip, k, 3.4 * w, 2.8 * w) | capsule(k, fo, 2.6 * w, 2.0 * w), ACC2, base - 0.04)
    if kind == "skirt":
        kf, kb = c["kf"], c["kb"]
        hx, hy = hip
        hem = max(kf[1], kb[1]) - 1
        L.fill(poly([(hx - 6 * w, hy - 3), (hx + 6 * w, hy - 3), (max(kf[0], kb[0]) + 6 * w, hem),
                     ((kf[0] + kb[0]) / 2, hem + 1), (min(kf[0], kb[0]) - 6 * w, hem)]), BOTTOM)
    L.outline()
    # стрелки на брюках, швы на джинсах, подол юбки
    if kind in ("pants", "jeans"):
        k, fo = c["kf"], c["ff"]
        L.line((k[0] + 1.5, k[1] + 1), (fo[0] + 1.5, fo[1] - 3), L.lt, 0.06 if kind == "pants" else 0.0)
        if kind == "jeans":
            L.line((hip[0] + 2, hip[1] + 2), (k[0] + 2.5, k[1]), L.lt, 0.08)
            L.line((k[0] + 2.5, k[1]), (fo[0] + 2.5, fo[1] - 3), L.lt, 0.08)
    if kind == "skirt":
        kf, kb = c["kf"], c["kb"]
        hem = max(kf[1], kb[1]) - 2
        for x in range(int(min(kf[0], kb[0]) - 4), int(max(kf[0], kb[0]) + 5), 3):
            L.dk(x, hem - 1, 0.08)
    return L


def layer_shoes(c, kind):
    L = Layer()
    for side, base in (("b", L_MID), ("f", L_BASE)):
        m, toe = foot_mask(c, side)
        if kind == "boots":
            k, fo = c["k" + side], c["f" + side]
            mid = (fo[0] + (k[0] - fo[0]) * 0.55, fo[1] + (k[1] - fo[1]) * 0.55)
            m |= capsule(fo, mid, 3.3, 3.6)
        L.fill(m, SHOES, base)
    L.outline()
    for side in ("f",):
        fo = c["f" + side]
        L.lt(fo[0] + 3, fo[1] - 1)
        L.lt(fo[0] + 4, fo[1] - 1)
        if kind == "low":
            L.px(fo[0] + 1, fo[1] - 1.5, SHOES, L_SH)      # шнуровка
    return L


def torso_mask(c, kind):
    w = c.wk
    sx, sy = c["sh"]
    hx, hy = c["hip"]
    kf, kb = c["kf"], c["kb"]
    f = 1
    front = lambda d: d * w
    shoulders = ellipse((sx - 0.5, sy + 3), 7.6 * w, 5.0)
    if kind in ("coat", "trench", "robe", "fur", "dress"):
        long_ = {"coat": 4, "trench": 3, "robe": -1, "fur": -10, "dress": -4}[kind]
        hem = max(kf[1], kb[1]) + long_
        back_hem = min(hx - 9 * w, min(kf[0], kb[0]) - 5)
        front_hem = max(hx + 9 * w, max(kf[0], kb[0]) + 5.5)
        if kind == "fur":
            back_hem, front_hem = hx - 8.5 * w, hx + 8.5 * w
        m = poly([(sx - 5, sy - 3), (sx - 8 * w, sy + 2), (sx - 8.6 * w, sy + 11), (hx - 7.6 * w, hy - 3),
                  (back_hem, hem), ((back_hem + front_hem) / 2, hem + 1), (front_hem, hem - 0.5),
                  (hx + 8.2 * w, hy - 3), (sx + 7.8 * w, sy + 11), (sx + 7.4 * w, sy + 2), (sx + 5, sy - 3)])
        return m | shoulders
    down = {"parka": 5, "jacket": 4, "uniform": 4, "apron": 3, "suit": 4, "tracksuit": 3, "cardigan": 4}.get(kind, 2)
    bulk = 1.0 + (0.12 if kind == "parka" else 0.0)
    m = poly([(sx - 5, sy - 3), (sx - 8 * w * bulk, sy + 2), (sx - 8.2 * w * bulk, sy + 10), (hx - 7.8 * w * bulk, hy + down),
              (hx + 8.2 * w * bulk, hy + down), (sx + 7.6 * w * bulk, sy + 10), (sx + 7.2 * w * bulk, sy + 2), (sx + 5, sy - 3)])
    # живот у плотных
    if w > 1.15:
        m |= ellipse((hx + 3 * w, hy - 6), 7.6 * w, 7.0)
    return m | shoulders


def layer_torso(c, kind):
    L = Layer()
    w = c.wk
    sx, sy = c["sh"]
    hx, hy = c["hip"]
    kf, kb = c["kf"], c["kb"]
    m = torso_mask(c, kind)
    under = {"suit": WHITE, "cardigan": TOP2, "jacket": TOP2}.get(kind)
    L.fill(m, TOP)
    if kind == "fur":
        L.fill(ellipse((sx + 1, sy - 0.5), 7.6 * w, 4.2), ACC, L_BASE)        # меховой воротник
        L.fill(rect(hx - 9 * w, hy + 5, hx + 9 * w, hy + 9) & m, ACC, L_MID)  # опушка подола
    if kind == "parka":
        L.fill(ellipse((sx - 5, sy - 2), 4.8, 3.8), ACC, L_HI - 0.04)         # мех капюшона
    if kind == "tracksuit":
        L.fill(capsule((sx + 6.6 * w, sy + 2), (hx + 7.2 * w, hy + 2), 1.0) & m, TOP2, L_HI)
    if kind == "apron":
        L.fill(poly([(sx + 1, sy + 7), (sx + 7.4 * w, sy + 7), (hx + 8 * w, hy + 12), (hx + 1, hy + 12)]), TOP2)
    L.outline()
    # ---- детали ----
    frontx = lambda y: sx + 6.2 * w + (hx + 6.8 * w - sx - 6.2 * w) * (y - sy) / max(1, hy - sy)
    if kind in ("coat", "trench", "robe", "uniform", "suit", "jacket", "cardigan", "fur", "dress"):
        # борт
        y0, y1 = int(sy + 4), int(hy + (8 if kind in ("coat", "trench", "robe", "dress") else 3))
        for y in range(y0, y1):
            L.dk(frontx(y) - 1.5, y, 0.12)
    if kind in ("coat", "trench", "uniform", "suit", "jacket", "robe", "cardigan"):
        n = 3 if kind in ("coat", "trench", "uniform", "robe") else 2
        for i in range(n):
            y = sy + 7 + i * (hy - sy - 3) / n
            L.px(frontx(y) - 3, y, METAL if kind == "uniform" else ACC2, 0.55)
    if under is not None:
        # вырез: рубашка или свитер под пиджаком
        for i in range(6):
            y = sy - 1 + i
            for x in range(int(sx + 1), int(sx + 1 + max(1, 4 - i * 0.6))):
                L.px(x + i * 0.4, y, under, L_HI if i < 2 else L_BASE)
        if kind == "suit":
            for i in range(7):
                L.px(sx + 2.6 + i * 0.25, sy + 1 + i, ACC2, L_BASE if i % 3 else L_MID)     # галстук
    if kind in ("coat", "trench", "dress"):
        # пояс и складки подола
        for x in range(int(hx - 7 * w), int(hx + 8 * w)):
            L.dk(x, hy - 2, 0.12)
        if kind == "trench":
            L.px(hx + 2, hy - 2, METAL, L_HI)
            L.px(hx + 3, hy - 2, METAL, L_MID)
        hem = max(kf[1], kb[1])
        L.line((hx - 1, hy + 2), (hx - 4, hem - 1), L.dk, 0.1)
        L.line((hx + 4, hy + 4), (hx + 6, hem - 2), L.dk, 0.06)
    if kind in ("coat", "trench", "uniform", "jacket", "suit"):
        # карман
        for x in range(int(hx + 1), int(hx + 6)):
            L.dk(x, hy - 6, 0.12)
        # воротник-лацкан
        L.line((sx + 2, sy - 2), (sx + 5, sy + 6), L.lt, 0.1)
    if kind == "uniform":
        for x in range(int(hx - 6 * w), int(hx + 7 * w)):
            L.px(x, hy - 1, METAL, L_MID)
        L.px(sx - 1, sy, ACC2, L_HI)
        L.px(sx, sy, ACC2, L_HI)
        L.px(sx + 4, sy + 6, ACC2, L_HI)     # значок
    if kind == "sweater":
        for y in range(int(sy + 2), int(hy + 2), 3):
            for x in range(int(sx - 6 * w), int(sx + 7 * w), 2):
                L.dk(x + (y // 3) % 2, y, 0.05)
        for x in range(int(hx - 7 * w), int(hx + 8 * w)):
            L.dk(x, hy + 1, 0.08)
        for x in range(int(sx - 2), int(sx + 4)):
            L.lt(x, sy - 2, 0.06)
    if kind == "parka":
        L.line((sx - 7 * w, sy + 12), (hx + 8 * w, sy + 13), L.dk, 0.1)
        L.line((frontx(sy + 4) - 2, sy + 2), (frontx(hy) - 2, hy + 4), L.dk, 0.12)
    if kind == "shirt":
        for y in range(int(sy + 3), int(hy), 4):
            L.px(frontx(y) - 2, y, WHITE, L_MID)
    return L


def layer_arm(c, side, kind):
    L = Layer()
    w = c.wk
    sh = c["sh"]
    e, h = c["e" + side], c["h" + side]
    base = L_BASE if side == "f" else L_MID
    r = 3.8 * w * (1.15 if kind == "puffy" else 1.0)
    sleeve = capsule((sh[0] - 1, sh[1] + 1.5), e, r, r * 0.92) | capsule(e, h, r * 0.92, r * 0.8)
    L.fill(sleeve, TOP, base)
    dx, dy = h[0] - e[0], h[1] - e[1]
    n = math.hypot(dx, dy) + 1e-6
    hand_c = (h[0] + dx / n * 2.4, h[1] + dy / n * 2.4)
    L.fill(ellipse(hand_c, 2.3, 2.6), SKIN, base)
    L.outline()
    # манжета и складка на локте
    L.line((h[0] - dy / n * 3, h[1] + dx / n * 3), (h[0] + dy / n * 3, h[1] - dx / n * 3), L.dk, 0.14)
    L.dk(e[0], e[1], 0.08)
    L.dk(e[0] + 1, e[1] + 1, 0.06)
    return L


def hair_mask(c, kind):
    f = c.face
    hx, hy = c["head"]
    cap = ellipse(H(c, -0.6, -2.6), 6.8, 5.6) & (YY < hy - 1.2 + 0 * XX)
    back = poly([H(c, -6.8, -3), H(c, -1.2, -3), H(c, -1.0, 2.0), H(c, -6.0, 2.5)])
    if kind == "short":
        return cap | (back & (YY < hy + 1.5))
    if kind == "crop":
        return ellipse(H(c, -0.6, -3.4), 6.6, 4.6) & (YY < hy - 3.0)
    if kind == "side":
        return cap | (back & (YY < hy + 1.5)) | ellipse(H(c, 2.6, -5.4), 4.4, 2.6)
    if kind == "receding":
        return (ellipse(H(c, -1.6, -1.6), 6.0, 4.6) & (YY < hy + 1.5) & ((XX - hx) * f < 0.5)) | (back & (YY < hy + 1))
    if kind == "bob":
        return cap | poly([H(c, -7.4, -3), H(c, 1.0, -3), H(c, 0.6, 6.0), H(c, -6.8, 6.4)]) | ellipse(H(c, 3.6, -4.2), 3.6, 2.4)
    if kind == "long":
        return cap | poly([H(c, -7.6, -3), H(c, -0.4, -3), H(c, -1.4, 13.0), H(c, -7.2, 13.5)])
    if kind == "bun":
        return cap | (back & (YY < hy + 1)) | ellipse(H(c, -6.2, -6.4), 3.2, 3.0)
    if kind == "pony":
        return cap | (back & (YY < hy)) | capsule(H(c, -6.4, -3.4), H(c, -8.6, 7.0), 2.0, 1.4)
    if kind == "braid":
        return cap | (back & (YY < hy)) | capsule(H(c, -5.6, -1), H(c, -6.6, 14.0), 2.2, 1.6)
    if kind == "curly":
        m = cap | (back & (YY < hy + 2.5))
        for ang in range(200, 361, 26):
            r = math.radians(ang)
            m |= ellipse((hx + 6.2 * math.cos(r), hy - 2.4 + 6.0 * math.sin(r)), 2.4, 2.4)
        return m & (YY < hy + 3)
    if kind == "perm":
        m = ellipse(H(c, -1.4, -2.2), 8.6, 7.4) & ~(ellipse(H(c, 3.4, 1.8), 4.6, 6.0))
        return m & (YY < hy + 5)
    if kind == "bald":
        return back & (YY > hy - 2.0) & (YY < hy + 1.2)
    return cap


def layer_hair(c, kind):
    L = Layer()
    m = hair_mask(c, kind) & ~ellipse(H(c, 3.0, 1.2), 3.2, 4.0)     # лицо не закрывать
    L.fill(m, HAIR)
    L.outline()
    hx, hy = c["head"]
    # пряди
    if kind in ("short", "side", "long", "bob", "pony", "bun", "braid"):
        for i in range(-4, 4, 2):
            L.line(H(c, i, -7.0), H(c, i - 1.4, -3.4), L.dk, 0.07)
    if kind in ("curly", "perm"):
        for y in range(int(hy - 9), int(hy + 5), 2):
            for x in range(int(hx - 9), int(hx + 9), 3):
                L.dk(x + (y // 2) % 2 * 1.5, y, 0.08)
    if kind == "braid":
        for i in range(5):
            L.dk(*H(c, -6.0 - i * 0.18, 1.0 + i * 2.6), 0.14)
    # бровь (лежит на лице, поэтому рисуется в слое волос)
    L.px(*H(c, 2.6, -2.6), HAIR, L_MID)
    L.px(*H(c, 3.6, -2.8), HAIR, L_MID)
    L.px(*H(c, 4.6, -2.6), HAIR, L_SH)
    return L


def layer_beard(c, kind):
    L = Layer()
    if kind == "full":
        m = (poly([H(c, -0.6, 1.0), H(c, 6.4, 2.6), H(c, 5.8, 7.6), H(c, 2.6, 10.4), H(c, -1.0, 6.0)]))
        L.fill(m & ~ellipse(H(c, 4.0, 4.6), 1.6, 0.9), HAIR, L_MID)
        L.outline()
    elif kind == "goatee":
        L.fill(ellipse(H(c, 4.4, 6.8), 1.8, 2.4), HAIR, L_MID)
        L.outline()
        L.px(*H(c, 3.4, 3.8), HAIR, L_SH)
        L.px(*H(c, 5.4, 3.8), HAIR, L_SH)
    elif kind == "mustache":
        for dx in (2.8, 3.8, 4.8, 5.6):
            L.px(*H(c, dx, 3.6), HAIR, L_MID if dx < 5 else L_SH)
        L.px(*H(c, 2.4, 4.4), HAIR, L_SH)
    elif kind == "stubble":
        for dx, dy in ((0.4, 3.0), (1.6, 4.4), (2.6, 5.6), (3.8, 6.6), (5.0, 6.0), (1.0, 5.4), (2.0, 6.6), (4.4, 5.0), (-0.4, 4.4)):
            L.px(*H(c, dx, dy), HAIR, L_SH)
    return L


def layer_glasses(c):
    L = Layer()
    f = c.face
    for x in (2.0, 3.0, 4.0, 5.0):
        L.px(*H(c, x, -1.8), METAL, 0.32)
        L.px(*H(c, x, 0.6), METAL, 0.32)
    L.px(*H(c, 1.8, -0.6), METAL, 0.32)
    L.px(*H(c, 5.2, -0.6), METAL, 0.32)
    L.px(*H(c, 4.2, -0.8), WHITE, 0.9)
    L.line(H(c, 1.6, -1.2), H(c, -1.4, -0.4), L.px, METAL, 0.3)
    return L


def layer_hat(c, kind):
    L = Layer()
    hx, hy = c["head"]
    if kind == "fedora":
        crown = poly([H(c, -5.6, -4), H(c, -5.0, -10.6), H(c, -1, -11.8), H(c, 3.6, -11.4), H(c, 5.8, -9.6), H(c, 6.2, -4.2)])
        brim = capsule(H(c, -8.0, -4.2), H(c, 8.8, -4.6), 1.2)
        L.fill(crown | brim, HAT)
        L.outline()
        for x in range(-5, 6):
            L.px(*H(c, x, -5.6), ACC2, L_SH)
        L.dk(*H(c, -1, -11), 0.1)
    elif kind == "cap":
        L.fill(ellipse(H(c, -0.4, -6.0), 6.6, 3.6) & (YY < hy - 3.4), HAT)
        L.fill(capsule(H(c, 4.0, -3.8), H(c, 9.6, -3.4), 1.0), HAT, L_SH)
        L.outline()
        L.px(*H(c, -0.4, -9.2), HAT, L_HI)
    elif kind == "flatcap":
        L.fill(poly([H(c, -6.6, -3.6), H(c, -5.0, -8.4), H(c, 3.0, -9.2), H(c, 9.4, -5.6), H(c, 9.0, -3.6)]), HAT)
        L.outline()
        L.line(H(c, -4.0, -7.6), H(c, 7.4, -4.6), L.dk, 0.08)
        L.px(*H(c, 1.0, -8.6), HAT, L_HI)
    elif kind == "beret":
        L.fill(ellipse(H(c, -1.4, -6.0), 7.6, 3.4), HAT)
        L.outline()
        L.px(*H(c, 0.0, -9.6), HAT, L_MID)
        L.px(*H(c, 0.0, -10.4), HAT, L_SH)
    elif kind == "ushanka":
        L.fill(ellipse(H(c, -0.4, -6.4), 7.6, 5.0) & (YY < hy - 3), HAT)
        L.fill(poly([H(c, -7.6, -5), H(c, -2.6, -5), H(c, -2.0, 3.6), H(c, -7.0, 3.0)]), HAT, L_MID)
        L.fill(capsule(H(c, -7.4, -4.0), H(c, 7.8, -4.0), 1.6), HAT, L_HI - 0.04)
        L.outline()
        for x in range(-6, 7, 2):
            L.dk(*H(c, x, -8.6), 0.08)
    elif kind == "fur_hat":
        L.fill(rect(hx - 7, hy - 13, hx + 7.4, hy - 3.6) | ellipse((hx, hy - 13), 7, 1.6), HAT)
        L.outline()
        for y in range(int(hy - 12), int(hy - 4), 2):
            for x in range(int(hx - 6), int(hx + 7), 2):
                L.dk(x + (y // 2) % 2, y, 0.08)
    elif kind == "hood":
        L.fill(poly([H(c, -8.0, -6), H(c, -2, -10.6), H(c, 4.6, -9.4), H(c, 6.4, -4.2), H(c, 3.2, -3.6),
                     H(c, -1.0, 0.0), H(c, -1.2, 8.4), H(c, -8.4, 8.0)]), HAT)
        L.outline()
        L.line(H(c, 4.0, -8.6), H(c, 2.4, -3.8), L.dk, 0.12)
    elif kind == "police":
        L.fill(poly([H(c, -6.2, -4), H(c, -6.6, -10.2), H(c, 7.8, -11.6), H(c, 6.6, -4)]), HAT)
        L.fill(rect(hx - 6.2, hy - 6, hx + 6.6, hy - 3.8), ACC2, L_BASE)
        L.fill(capsule(H(c, 4.6, -3.6), H(c, 9.8, -3.0), 1.0), METAL, 0.3)
        L.outline()
        L.px(*H(c, 3.0, -8.6), WHITE, L_HI)
        L.px(*H(c, 3.0, -7.6), ACC2, L_HI)
    elif kind == "beanie":
        L.fill(ellipse(H(c, -0.6, -5.4), 6.8, 6.4) & (YY < hy - 2.4), HAT)
        L.fill(rect(hx - 7, hy - 5, hx + 7, hy - 2.4) & ellipse(H(c, -0.6, -4), 7.4, 6), HAT, L_MID)
        L.fill(ellipse(H(c, -1.6, -12.2), 1.8, 1.6), HAT, L_HI)
        L.outline()
        for x in range(-6, 7, 2):
            L.dk(*H(c, x, -3.6), 0.1)
    elif kind == "kerchief":
        L.fill(poly([H(c, -7.6, -3), H(c, -4.4, -9.6), H(c, 3.0, -9.8), H(c, 5.6, -4.6), H(c, 2.6, -2.6),
                     H(c, -1.4, 2.0), H(c, -1.0, 8.4), H(c, -7.0, 7.4)]), HAT)
        L.fill(poly([H(c, 1.0, 7.0), H(c, 4.6, 7.8), H(c, 2.4, 10.6)]), HAT, L_MID)
        L.outline()
        for i in range(0, 12, 3):
            L.px(*H(c, -5 + i * 0.6, -7 + i * 0.4), ACC, L_HI)
    elif kind == "helmet":
        L.fill(ellipse(H(c, 0, -5.8), 7.4, 5.6) & (YY < hy - 3.6), HAT)
        L.fill(capsule(H(c, -8, -3.8), H(c, 8.6, -3.8), 1.1), HAT, L_MID)
        L.outline()
        L.line(H(c, 0, -11), H(c, 0, -4.6), L.lt, 0.12)
    return L


def layer_scarf(c):
    L = Layer()
    sx, sy = c["sh"]
    L.fill(ellipse((sx + 1.6, sy - 2.6), 6.6 * min(1.15, c.wk), 3.4), ACC)
    L.fill(capsule((sx + 4.0, sy - 1), (sx + 6.0, sy + 10), 2.0, 1.6), ACC, L_MID)
    L.outline()
    for y in range(int(sy + 2), int(sy + 10), 3):
        L.px(sx + 5, y, ACC2, L_BASE)
    return L


def layer_item(c, kind):
    L = Layer()
    fn = c.fname
    hf = c["hf"]
    sx, sy = c["sh"]
    hip = c["hip"]
    if kind in ("briefcase", "umbrella", "stringbag") and fn in NO_HAND_ITEMS:
        return L
    if kind == "briefcase":
        x, y = hf[0], hf[1] + 5
        L.fill(rect(x - 7, y, x + 7, y + 11) & ~(rect(x - 7, y, x - 6, y + 1) | rect(x + 6, y, x + 7, y + 1)), ACC)
        L.outline()
        for xx in range(int(x - 2), int(x + 3)):
            L.px(xx, y - 2, ACC, L_SH)
        L.px(x - 2, y - 1, ACC, L_SH)
        L.px(x + 2, y - 1, ACC, L_SH)
        for xx in range(int(x - 6), int(x + 6)):
            L.dk(xx, y + 3, 0.1)
        L.px(x, y + 3, METAL, L_HI)
    elif kind == "stringbag":     # авоська с апельсинами и батоном
        x, y = hf[0], hf[1] + 4
        L.fill(ellipse((x, y + 8), 5.6, 6.2), ACC2, L_BASE)
        L.fill(capsule((x - 3, y + 2), (x + 2, y + 14), 1.8), WHITE, L_MID)
        L.outline()
        for yy in range(int(y + 3), int(y + 14), 2):
            for xx in range(int(x - 5), int(x + 6), 2):
                L.px(xx + (yy // 2) % 2, yy, METAL, 0.45)
        L.line((x, y - 2), (x - 2, y + 3), L.px, METAL, 0.45)
    elif kind == "umbrella":
        x, y = hf
        L.line((x, y), (x + 4, y + 24), L.px, ACC, L_MID)
        L.line((x + 1, y), (x + 5, y + 24), L.px, ACC, L_SH)
        L.px(x - 1, y - 1, ACC, L_MID)
        L.px(x + 5, y + 25, METAL, L_MID)
    elif kind == "umbrella_open":
        if fn in ("climb", "lie", "slump", "jump", "fall"):
            return L
        hx, hy = c["head"]
        top = hy - 28
        m = ellipse((hx, top + 12), 22, 12) & (YY < top + 12)
        L.fill(m, ACC)
        L.outline()
        for i in range(-18, 19, 9):
            L.line((hx, top + 1), (hx + i, top + 11), L.dk, 0.08)
        L.line((hx, top + 12), (hx + 2, sy + 8), L.px, METAL, 0.5)
    elif kind == "bag":
        if fn == "lie":
            return L
        L.line((sx + 2, sy), (hip[0] - 6, hip[1] - 4), L.px, ACC, L_SH)
        L.fill(rect(hip[0] - 13, hip[1] - 6, hip[0] - 3, hip[1] + 4), ACC)
        L.outline()
        L.px(hip[0] - 8, hip[1] - 3, METAL, L_HI)
    elif kind == "backpack":
        if fn == "lie":
            return L
        L.fill(rect(sx - 14, sy + 2, sx - 6, sy + 21), ACC)
        L.outline()
        L.line((sx - 14, sy + 11), (sx - 6, sy + 11), L.dk, 0.12)
    elif kind == "paper":
        if fn not in ("idle", "sit", "walk"):
            return L
        x, y = hf
        L.fill(rect(x - 2, y - 9, x + 6, y + 2), WHITE, L_MID)
        L.outline()
        for yy in range(int(y - 7), int(y), 2):
            L.line((x - 1, yy), (x + 4, yy), L.px, METAL, 0.4)
    elif kind == "cig":
        if fn != "smoke":
            return L
        x, y = hf
        L.line((x + 1, y - 2), (x + 6, y - 2), L.px, WHITE, L_HI)
        L.px(x + 6, y - 2, ACC2, L_HI)
    elif kind == "phone":
        if fn != "phone":
            return L
        x, y = hf
        L.fill(rect(x, y - 5, x + 3, y + 3), METAL, 0.3, flat=True)
    elif kind == "cane":
        if fn in ("climb", "lie", "slump", "jump", "fall", "carry", "strangle", "push", "sit", "choke", "cower", "phone", "smoke"):
            return L
        x, y = hf
        L.line((x, y), (x + 6, GROUND), L.px, ACC, L_MID)
        L.line((x + 1, y), (x + 7, GROUND), L.px, ACC, L_SH)
        L.line((x - 4, y), (x, y), L.px, ACC, L_MID)
    elif kind == "flashlight":
        if fn in ("lie", "slump", "climb"):
            return L
        x, y = hf
        L.fill(rect(x - 2, y - 2, x + 6, y + 1), METAL, L_MID)
        L.px(x + 6, y - 1, WHITE, L_HI)
    return L


# ---------------- сборка ----------------



def render(fn, p, fname, build):
    """Лежачий кадр рисуется стоя (поза LIE_SRC): игра сама кладёт его, поворачивая фигуру на 90°."""
    if p == "LIE":
        return fn(Ctx(to2x(G0.LIE_SRC, build), build, "lie")).image()
    return fn(Ctx(to2x(p, build), build, fname)).image()


TORSOS = ("shirt", "jacket", "coat", "sweater", "apron", "uniform", "parka", "robe", "trench", "suit", "tracksuit", "cardigan", "fur", "dress")
HAIRS = ("short", "crop", "side", "receding", "bob", "long", "bun", "pony", "braid", "bald", "curly", "perm")
HATS = ("fedora", "cap", "flatcap", "beret", "ushanka", "fur_hat", "hood", "police", "beanie", "kerchief", "helmet")
ITEMS = ("briefcase", "stringbag", "umbrella", "umbrella_open", "bag", "backpack", "paper", "cig", "phone", "cane", "flashlight")

LAYERS = {
    "body": layer_body,
    "wrinkles": layer_wrinkles,
    "armb": lambda c: layer_arm(c, "b", ""),
    "armf": lambda c: layer_arm(c, "f", ""),
    "armb_puffy": lambda c: layer_arm(c, "b", "puffy"),
    "armf_puffy": lambda c: layer_arm(c, "f", "puffy"),
    "scarf": layer_scarf,
    "glasses": layer_glasses,
    "shoes_low": lambda c: layer_shoes(c, "low"),
    "shoes_boots": lambda c: layer_shoes(c, "boots"),
}
for k in ("pants", "jeans", "skirt"):
    LAYERS["legs_" + k] = (lambda kk: lambda c: layer_legs(c, kk))(k)
for k in TORSOS:
    LAYERS["torso_" + k] = (lambda kk: lambda c: layer_torso(c, kk))(k)
for k in HAIRS:
    LAYERS["hair_" + k] = (lambda kk: lambda c: layer_hair(c, kk))(k)
for k in ("full", "goatee", "mustache", "stubble"):
    LAYERS["beard_" + k] = (lambda kk: lambda c: layer_beard(c, kk))(k)
for k in HATS:
    LAYERS["hat_" + k] = (lambda kk: lambda c: layer_hat(c, kk))(k)
for k in ITEMS:
    LAYERS["item_" + k] = (lambda kk: lambda c: layer_item(c, kk))(k)


def main(out, only=None):
    builds = list(BUILDS) if not only else only
    for b in builds:
        d = os.path.join(out, "fig2", b)
        os.makedirs(d, exist_ok=True)
        for name, fn in LAYERS.items():
            sheet = Image.new("RGBA", (SW * G0.NFR, SH), (0, 0, 0, 0))
            for i, (fname, p) in enumerate(G0.FRAMES):
                fr = render(fn, p, fname, b)
                sheet.paste(fr, (i * SW, 0), fr)
            sheet.save(os.path.join(d, name + ".png"), optimize=True)
        print("build", b, "layers", len(LAYERS))
    anims = {}
    for i, (fname, p) in enumerate(G0.FRAMES):
        anims.setdefault(fname, []).append(i)
    with open(os.path.join(out, "fig2", "frames.txt"), "w") as f:
        for k, v in anims.items():
            f.write("%s %s\n" % (k, ",".join(str(x) for x in v)))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "../../assets", sys.argv[2:] or None)
