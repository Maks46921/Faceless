"""Ручная перерисовка главных тайлов на мелком пикселе (32×32 вместо 16×16).

Фасады (кирпич, силикатный кирпич, панель, бетон, штукатурка, гранит) с окнами, карнизами,
поясами и цоколями, земля, тротуар, асфальт, газон, гравий, перекрытия.
Вызывается после gen_tiles: replace(tiles) подменяет картинки по именам.
"""
import random
import numpy as np
from PIL import Image
import k2

T = 32
R = random.Random(5)
NP = np.random.default_rng(5)


def hx(s):
    s = s.lstrip("#")
    return np.array([int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)], float)


def canvas(w=T, h=T, c=None):
    a = np.zeros((h, w, 4), float)
    if c is not None:
        a[..., :3] = c
        a[..., 3] = 255
    return a


def blotch(w, h, cells=4, seed=0):
    """Бесшовный мягкий шум 0..1 (пятна штукатурки, грязь)."""
    g = np.random.default_rng(seed).random((cells, cells))
    big = np.tile(g, (3, 3))
    im = Image.fromarray((big * 255).astype(np.uint8), "L").resize((w * 3, h * 3), Image.BICUBIC)
    a = np.array(im, float)[h:2 * h, w:2 * w] / 255.0
    return (a - a.min()) / max(1e-6, a.max() - a.min())


def grain(a, amp, seed=0, mask=None):
    n = 1 + (np.random.default_rng(seed).random(a.shape[:2]) - 0.5) * amp
    if mask is not None:
        n = np.where(mask, n, 1)
    a[..., :3] *= n[..., None]


def fill(a, x0, y0, x1, y1, c, alpha=255):
    """включительно"""
    a[y0:y1 + 1, x0:x1 + 1, :3] = c
    a[y0:y1 + 1, x0:x1 + 1, 3] = alpha


def mulr(a, x0, y0, x1, y1, k):
    a[y0:y1 + 1, x0:x1 + 1, :3] *= k


def px(a, x, y, c, alpha=255):
    h, w = a.shape[:2]
    if 0 <= x < w and 0 <= y < h:
        a[y, x, :3] = c
        a[y, x, 3] = alpha


def mpx(a, x, y, k):
    h, w = a.shape[:2]
    x %= w
    y %= h
    a[y, x, :3] *= k


def specks(a, n, k, seed, size=1, region=None):
    r = random.Random(seed)
    h, w = a.shape[:2]
    x0, y0, x1, y1 = region or (0, 0, w - 1, h - 1)
    for _ in range(n):
        x, y = r.randint(x0, x1), r.randint(y0, y1)
        kk = k if not isinstance(k, tuple) else r.uniform(*k)
        for dy in range(size):
            for dx in range(size):
                mpx(a, x + dx, y + dy, kk)


def to_img(a):
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")
    return k2.mark(im)


# ---------------- стены ----------------

def wall_brick(c, mortar, seed, rowphase=0):
    a = canvas(c=mortar)
    grain(a, 0.12, seed)
    r = random.Random(seed)
    for row in range(4):
        y0 = row * 8 + rowphase
        off = 0 if row % 2 == 0 else 8
        for i in range(-1, 3):
            x0 = off + i * 16
            k = r.uniform(0.86, 1.1)
            tone = c * k
            for y in range(y0, y0 + 7):
                for x in range(x0 + 1, x0 + 16):
                    yy, xx = y % T, x % T
                    a[yy, xx, :3] = tone
                    a[yy, xx, 3] = 255
            # объём кирпича: верх светлее, низ и правый край темнее
            for x in range(x0 + 1, x0 + 16):
                mpx(a, x, y0, 1.14)
                mpx(a, x, y0 + 6, 0.82)
            for y in range(y0, y0 + 7):
                mpx(a, x0 + 15, y, 0.88)
                mpx(a, x0 + 1, y, 1.05)
            # сколы и поры
            for _ in range(r.randint(1, 3)):
                mpx(a, r.randint(x0 + 2, x0 + 14), r.randint(y0 + 1, y0 + 5), r.choice((0.78, 0.85, 1.12)))
            if r.random() < 0.3:
                cx = r.choice((x0 + 1, x0 + 15))
                mpx(a, cx, y0, 0.7)
                mpx(a, cx, y0 + 1, 0.8)
        # тень раствора под кирпичом
        for x in range(T):
            mpx(a, x, y0 + 7, 0.78)
    grain(a, 0.06, seed + 1)
    return a


def wall_panel(c, seed, boards=False):
    a = canvas(c=c)
    b = blotch(T, T, 4, seed)
    a[..., :3] *= (0.94 + 0.1 * b)[..., None]
    grain(a, 0.1, seed)
    specks(a, 14, (0.78, 0.88), seed, 1)          # поры бетона
    specks(a, 5, 1.1, seed + 3, 1)
    if boards:                                     # следы опалубки
        for y in (7, 15, 23):
            for x in range(T):
                mpx(a, x, y, 0.93)
                mpx(a, x, y + 1, 1.04)
    # шов панели: тёмная щель + светлый герметик + тень
    for i in range(T):
        a[T - 2, i, :3] = c * 0.55
        a[T - 1, i, :3] = c * 0.78
        a[i, T - 2, :3] = c * 0.55
        a[i, T - 1, :3] = c * 0.8
        mpx(a, i, 0, 1.06)
        mpx(a, 0, i, 1.05)
    # потёк от шва
    for y in range(0, 12):
        mpx(a, 10, y, 0.95 - 0.004 * y)
    return a


def wall_stucco(c, seed):
    a = canvas(c=c)
    b = blotch(T, T, 5, seed)
    a[..., :3] *= (0.9 + 0.16 * b)[..., None]
    grain(a, 0.09, seed)
    specks(a, 10, (0.86, 0.94), seed, 1)
    specks(a, 6, 1.08, seed + 1, 1)
    return a


def wall_granite(c, seed):
    a = canvas(c=c)
    b = blotch(T, T, 6, seed)
    a[..., :3] *= (0.9 + 0.14 * b)[..., None]
    r = random.Random(seed)
    for _ in range(70):
        x, y = r.randrange(T), r.randrange(T)
        col = r.choice((c * 1.35, c * 0.7, c * np.array([1.25, 1.05, 1.0]), c * 0.85))
        a[y, x, :3] = col
    # плита: полированный блик и шов
    for i in range(T):
        a[T - 1, i, :3] = c * 0.6
        a[i, T - 1, :3] = c * 0.68
        mpx(a, i, 0, 1.12)
    for i in range(6):
        mpx(a, 4 + i, 3 + i, 1.12)
    return a


# ---------------- окна ----------------

GLASS = hx("3a4a58")


def glass_area(a, x0, y0, x1, y1, alpha=125, seed=0):
    h = y1 - y0 + 1
    for y in range(y0, y1 + 1):
        t = (y - y0) / max(1, h - 1)
        base = GLASS * (1.25 - 0.4 * t)          # отражение неба: верх светлее
        for x in range(x0, x1 + 1):
            c = base.copy()
            d = (x - x0) + (y - y0)
            if d % 23 in (0, 1, 2):
                c = c * 1.35
            elif d % 23 == 3:
                c = c * 1.15
            a[y, x, :3] = c
            a[y, x, 3] = alpha
    # тень от рамы в верхнем и левом крае стекла
    for x in range(x0, x1 + 1):
        a[y0, x, :3] *= 0.7
    for y in range(y0, y1 + 1):
        a[y, x0, :3] *= 0.8


def curtain(a, x0, y0, x1, y1, col, seed, alpha=190):
    """занавеска в углу стекла: складки"""
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            k = 1.0 + 0.12 * np.sin((x - x0) * 1.6)
            a[y, x, :3] = col * k
            a[y, x, 3] = alpha
    for y in range(y0, y1 + 1):
        a[y, x1, :3] *= 0.8


def frame_rect(a, x0, y0, x1, y1, c, w=2):
    """рама с объёмом: внешний край светлее сверху/слева"""
    for k in range(w):
        for x in range(x0 + k, x1 - k + 1):
            a[y0 + k, x, :3] = c * (1.25 if k == 0 else 1.0)
            a[y1 - k, x, :3] = c * (0.75 if k == 0 else 0.9)
            a[y0 + k, x, 3] = a[y1 - k, x, 3] = 255
        for y in range(y0 + k, y1 - k + 1):
            a[y, x0 + k, :3] = c * (1.15 if k == 0 else 1.0)
            a[y, x1 - k, :3] = c * (0.78 if k == 0 else 0.9)
            a[y, x0 + k, 3] = a[y, x1 - k, 3] = 255


def bar(a, x0, y0, x1, y1, c):
    fill(a, x0, y0, x1, y1, c)
    if x1 - x0 >= y1 - y0:
        a[y0, x0:x1 + 1, :3] = c * 1.2
        a[y1, x0:x1 + 1, :3] = c * 0.75
    else:
        a[y0:y1 + 1, x0, :3] = c * 1.15
        a[y0:y1 + 1, x1, :3] = c * 0.75


def window_std(wall, c, frame, seed, curtain_col):
    """окно панельки/кирпичного дома 64×64: откос, рама, форточка, подоконник, отлив"""
    a = np.concatenate([np.concatenate([wall, wall], 1)] * 2, 0).copy()
    # проём с тенью откоса
    fill(a, 9, 7, 54, 55, c * 0.42)
    fill(a, 9, 7, 54, 9, c * 0.3)
    fill(a, 9, 7, 11, 55, c * 0.34)
    frame_rect(a, 11, 9, 53, 54, frame, 2)
    glass_area(a, 13, 11, 51, 52, 125, seed)
    curtain(a, 13, 11, 18, 52, curtain_col, seed)
    curtain(a, 46, 11, 51, 52, curtain_col, seed + 1)
    # импост и форточка
    bar(a, 31, 11, 33, 52, frame)
    bar(a, 13, 24, 31, 25, frame)
    frame_rect(a, 15, 13, 29, 22, frame * 0.95, 1)
    a[15, 23, :3] = hx("c8c0a8")                 # ручка
    a[38, 34, :3] = hx("c8c0a8")
    a[39, 34, :3] = hx("c8c0a8")
    # подоконник-отлив: светлый верх, тень под ним
    bar(a, 7, 55, 56, 57, c * 1.18)
    a[55, 7:57, :3] = c * 1.35
    fill(a, 8, 58, 55, 59, c * 0.62)
    a[60, 9:55, :3] *= 0.85
    # потёк под подоконником
    for y in range(60, 64):
        mpx(a, 20, y, 0.9)
        mpx(a, 43, y, 0.92)
    return a


def window_stucco(wall, c, seed):
    """арочное окно сталинки с наличником, замковым камнем и балясиной под подоконником"""
    a = np.concatenate([np.concatenate([wall, wall], 1)] * 2, 0).copy()
    fr = hx("e2dccb")
    yy, xx = np.mgrid[0:64, 0:64]
    cx = 31.5
    # наличник: полоса вокруг проёма
    outer = ((xx >= 6) & (xx <= 57) & (yy >= 14) & (yy <= 58)) | (((xx - cx) / 26) ** 2 + ((yy - 15) / 13) ** 2 <= 1)
    inner = ((xx >= 11) & (xx <= 52) & (yy >= 15) & (yy <= 56)) | (((xx - cx) / 21) ** 2 + ((yy - 15.5) / 9.5) ** 2 <= 1)
    a[outer & ~inner, :3] = fr
    a[outer & ~inner, 3] = 255
    edge = outer & ~np.roll(outer, -1, 0)
    a[edge & ~inner, :3] = fr * 0.7
    top = outer & ~np.roll(outer, 1, 0)
    a[top & ~inner, :3] = fr * 1.08
    # тень под наличником на стене
    sh = np.roll(outer, 1, 0) & ~outer
    a[sh, :3] *= 0.8
    # стекло
    a[inner, :3] = c * 0.35
    a[inner, 3] = 255
    gl = ((xx >= 13) & (xx <= 50) & (yy >= 16) & (yy <= 54)) | (((xx - cx) / 19) ** 2 + ((yy - 16) / 8) ** 2 <= 1)
    for y in range(64):
        for x in range(64):
            if gl[y, x]:
                t = (y - 8) / 48
                base = GLASS * (1.3 - 0.45 * t)
                if ((x + y) % 23) in (0, 1, 2):
                    base = base * 1.35
                a[y, x, :3] = base
                a[y, x, 3] = 125
    # переплёт: центральный и поперечный, радиальные в арке
    for y in range(8, 55):
        if gl[y, 31] or gl[y, 32]:
            a[y, 31:33, :3] = fr * np.array([[1.05], [0.85]])
            a[y, 31:33, 3] = 255
    a[27:29, 13:51, :3] = fr
    a[28, 13:51, :3] = fr * 0.85
    a[27:29, 13:51, 3] = 255
    for t in np.linspace(0, 1, 14):
        for sx in (-1, 1):
            x = int(round(cx + sx * 19 * t * 0.75))
            y = int(round(16 - 8 * t * 0.55))
            if gl[y, x]:
                a[y, x, :3] = fr
                a[y, x, 3] = 255
    # замковый камень
    poly = (yy >= 1) & (yy <= 9) & (np.abs(xx - cx) <= 3 + (9 - yy) * 0.0 + (yy - 1) * 0.25)
    a[poly, :3] = fr * 1.05
    a[poly, 3] = 255
    a[poly & (xx > cx), :3] = fr * 0.85
    # подоконник с профилем и кронштейнами
    bar(a, 4, 57, 59, 59, fr * 1.02)
    a[60, 5:59, :3] = fr * 0.6
    for x in (9, 54):
        fill(a, x - 1, 60, x + 1, 63, fr * 0.9)
        a[60:64, x + 1, :3] = fr * 0.7
    return a


def window_granite(wall, c, seed):
    """стеклянный проём гранитного дома: тонкая металлическая рама"""
    a = np.concatenate([np.concatenate([wall, wall], 1)] * 2, 0).copy()
    fr = hx("2e2c2b")
    fill(a, 2, 2, 61, 61, fr)
    frame_rect(a, 2, 2, 61, 61, fr * 1.4, 1)
    glass_area(a, 4, 4, 59, 59, 108, seed)
    bar(a, 30, 4, 32, 59, fr * 1.3)
    bar(a, 4, 40, 59, 41, fr * 1.3)
    curtain(a, 4, 4, 9, 39, hx("a89c80"), seed, 160)
    return a


# ---------------- карнизы, пояса, цоколи ----------------

def cornice(wall, c):
    a = wall.copy()
    # многоступенчатый профиль: полка, выкружка, сухарики
    bar(a, 0, 18, 31, 19, c * 1.25)
    fill(a, 0, 20, 31, 21, c * 0.82)
    fill(a, 0, 22, 31, 31, c * 0.72)
    for x in range(1, T, 6):                      # сухарики
        fill(a, x, 23, x + 3, 27, c * 0.95)
        a[23, x:x + 4, :3] = c * 1.1
        a[28, x:x + 4, :3] = c * 0.55
    a[29, :, :3] = c * 1.05
    a[30, :, :3] = c * 0.6
    a[31, :, :3] = c * 0.5
    grain(a, 0.05, 9)
    return a


def belt(wall, c):
    a = wall.copy()
    fill(a, 0, 25, 31, 25, c * 1.3)
    fill(a, 0, 26, 31, 28, c * 1.1)
    fill(a, 0, 29, 31, 29, c * 0.7)
    a[30:32, :, :3] *= 0.85
    return a


def plinth(c, seed):
    a = canvas(c=c * 0.62)
    b = blotch(T, T, 4, seed)
    a[..., :3] *= (0.9 + 0.15 * b)[..., None]
    grain(a, 0.14, seed)
    # рустованные блоки
    for y0 in (2, 17):
        off = 0 if y0 == 2 else 8
        for x0 in range(off - 16, T, 16):
            for x in range(x0, x0 + 16):
                mpx(a, x, y0, 1.18)
                mpx(a, x, y0 + 14, 0.65)
            for y in range(y0, y0 + 15):
                mpx(a, x0, y, 1.1)
                mpx(a, x0 + 15, y, 0.7)
    a[0, :, :3] = c * 0.95
    a[1, :, :3] = c * 0.75
    specks(a, 12, (0.7, 0.85), seed, 1)
    # брызги грязи снизу
    for x in range(T):
        for y in range(26, 32):
            if R.random() < 0.15 + (y - 26) * 0.08:
                mpx(a, x, y, 0.82)
    return a


# ---------------- земля и улица ----------------

def earth(seed, c=hx("4a3f36")):
    a = canvas(c=c)
    b = blotch(T, T, 5, seed)
    a[..., :3] *= (0.85 + 0.25 * b)[..., None]
    grain(a, 0.22, seed)
    r = random.Random(seed)
    for _ in range(5):                              # камешки с бликом
        x, y = r.randrange(T), r.randrange(T)
        s = r.choice((2, 2, 3))
        col = c * r.uniform(1.3, 1.7)
        for dy in range(s):
            for dx in range(s):
                if (dx, dy) != (s - 1, s - 1) or s == 2:
                    px(a, (x + dx) % T, (y + dy) % T, col * (1.15 if dy == 0 else 0.85))
    for _ in range(2):                              # корешки
        x, y = r.randrange(T), r.randrange(T)
        for i in range(6):
            mpx(a, x + i, y + (i // 3), 0.7)
    return a


def rock(seed):
    c = hx("3d3b3a")
    a = canvas(c=c)
    b = blotch(T, T, 4, seed)
    a[..., :3] *= (0.85 + 0.3 * b)[..., None]
    grain(a, 0.2, seed)
    r = random.Random(seed)
    for _ in range(5):                              # слои и трещины
        x, y = r.randrange(T), r.randrange(T)
        L = r.randint(5, 12)
        for i in range(L):
            mpx(a, x + i, y + (1 if i > L // 2 else 0), 0.68)
            mpx(a, x + i, y - 1 + (1 if i > L // 2 else 0), 1.2)
    return a


def sidewalk(seed):
    a = earth(seed)
    slab = hx("7c7b76")
    fill(a, 0, 0, 31, 7, slab)
    grain(a, 0.1, seed + 1, mask=np.pad(np.ones((8, T), bool), ((0, 24), (0, 0))))
    a[0, :, :3] = hx("a2a19b")
    a[1, :, :3] = hx("8e8d87")
    for x in (15,):                                 # шов плитки
        a[1:8, x, :3] = hx("55544f")
        a[1:8, x + 1, :3] = hx("8e8d87")
    a[7, :, :3] = slab * 0.7
    a[8, :, :3] = hx("3e3530")
    a[9, :, :3] = hx("4a4038") * 0.8
    specks(a, 6, (0.78, 0.9), seed, 1, (0, 2, 31, 6))
    mpx(a, 26, 1, 0.6)
    mpx(a, 27, 1, 0.7)
    mpx(a, 27, 2, 0.75)                             # скол
    return a


def grass(seed):
    a = earth(seed)
    g = hx("5d6b45")
    fill(a, 0, 0, 31, 5, g)
    grain(a, 0.16, seed, mask=np.pad(np.ones((6, T), bool), ((0, 26), (0, 0))))
    r = random.Random(seed)
    a[6, :, :3] = g * 0.6
    for x in range(T):                              # травинки над краем — внутри тайла рисуем светлые кончики
        h = r.choice((0, 1, 1, 2, 3))
        for y in range(0, h):
            a[y, x, :3] = g * (1.25 + 0.1 * y)
        if r.random() < 0.08:
            a[1, x, :3] = hx("c9b84a")              # одуванчик
    return a


def asphalt(seed):
    c = hx("4b4c4f")
    a = canvas(c=c)
    b = blotch(T, T, 4, seed)
    a[..., :3] *= (0.92 + 0.12 * b)[..., None]
    grain(a, 0.16, seed)
    specks(a, 40, (1.15, 1.35), seed, 1)            # щебень
    specks(a, 20, (0.7, 0.85), seed + 1, 1)
    a[0, :, :3] = c * 1.3
    a[1, :, :3] = c * 1.08
    r = random.Random(seed)                          # трещина
    x, y = 6, 4
    for i in range(14):
        mpx(a, x, y, 0.6)
        x += 1
        y += r.choice((0, 0, 1, -1)) if 3 < y < 28 else 0
    return a


def gravel(seed):
    c = hx("6d6a63")
    a = canvas(c=c * 0.75)
    r = random.Random(seed)
    for _ in range(60):
        x, y = r.randrange(T), r.randrange(T)
        col = c * r.uniform(0.8, 1.3)
        for dy in range(2):
            for dx in range(2):
                px(a, (x + dx) % T, (y + dy) % T, col * (1.15 if dy == 0 and dx == 0 else (0.75 if dy == 1 and dx == 1 else 1)))
    a[0, :, :3] = hx("8c887e")
    return a


def slab(top, top2, kind, seed):
    cd = hx("5e5f5d")
    a = canvas(c=cd)
    grain(a, 0.1, seed)
    specks(a, 8, (0.8, 0.9), seed, 1, (0, 8, 31, 30))
    fill(a, 0, 0, 31, 5, top)
    a[0, :, :3] = top * 1.2
    if kind == "parquet":                           # ёлочка
        for x in range(0, T):
            for y in range(1, 6):
                if (x + (y if (x // 4) % 2 else -y)) % 8 == 0:
                    a[y, x, :3] = top2
        for x in range(0, T, 4):
            a[1:6, x, :3] *= 0.9
    elif kind == "tile":
        for x in range(0, T, 10):
            a[0:6, x, :3] = top2
    elif kind == "lino":
        b = blotch(T, 6, 4, seed)
        a[0:6, :, :3] *= (0.92 + 0.12 * b)[..., None]
    elif kind == "office":
        specks(a, 20, (0.85, 1.15), seed, 1, (0, 1, 31, 5))
    a[6, :, :3] = top2
    a[7, :, :3] = top2 * 0.8                         # плинтус-тень
    for x in (6, 16, 26):                            # арматура в разрезе
        fill(a, x, 18, x + 1, 19, hx("3b3c3b"))
        a[18, x, :3] = hx("5a5550")
    a[30, :, :3] = cd * 0.8
    a[31, :, :3] = cd * 0.7
    return a


# ---------------- подмена ----------------

FAC = {
    "panel": hx("9b9a92"), "brick": hx("8a4a3a"), "sbrick": hx("a9a395"),
    "stucco": hx("b3a27a"), "granite": hx("5d5a58"), "conc": hx("8a8a86"),
}
CURT = {"panel": hx("b8a888"), "brick": hx("a8987a"), "sbrick": hx("9aa0a8"), "conc": hx("b0a090")}


def wall_of(key, seed):
    c = FAC[key]
    if key == "brick":
        return wall_brick(c * 0.95, hx("8a8378") * 0.8, seed)
    if key == "sbrick":
        return wall_brick(c, hx("8f8a80"), seed)
    if key == "panel":
        return wall_panel(c, seed)
    if key == "conc":
        return wall_panel(c, seed, boards=True)
    if key == "stucco":
        return wall_stucco(c, seed)
    return wall_granite(c, seed)


def replace(tiles):
    """tiles: список (имя, картинка 2×) из gen_tiles; подменяет по именам."""
    new = {}
    for key, c in FAC.items():
        w = wall_of(key, 11)
        new["f_" + key] = w
        new["f_%s_cornice" % key] = cornice(wall_of(key, 11), c)
        new["f_%s_belt" % key] = belt(wall_of(key, 11), c)
        new["f_%s_base" % key] = plinth(c, 13)
        if key == "stucco":
            win = window_stucco(w, c, 3)
        elif key == "granite":
            win = window_granite(w, c, 3)
        else:
            frame = c * 0.5 if key != "sbrick" else hx("d8d4c8")
            if key == "panel":
                frame = hx("dcd8cc")
            win = window_std(w, c, frame, 3, CURT[key])
        for i, (ox, oy) in enumerate(((0, 0), (32, 0), (0, 32), (32, 32))):
            new["f_%s_win%d" % (key, i)] = win[oy:oy + 32, ox:ox + 32].copy()
    # внутренние стены в разрезе — тот же материал
    new["wall_brick"] = wall_brick(hx("8a4a3a") * 0.8, hx("6a6258") * 0.8, 21)
    new["wall_sbrick"] = wall_brick(hx("a9a395") * 0.8, hx("77736a"), 22)
    new["wall_panel"] = wall_panel(hx("9b9a92") * 0.8, 23)
    new["wall_conc"] = wall_panel(hx("8a8a86") * 0.8, 24, boards=True)
    new["wall_stucco"] = wall_stucco(hx("b3a27a") * 0.8, 25)
    new["wall_granite"] = wall_granite(hx("5d5a58") * 0.8, 26)
    new["earth"] = earth(1)
    new["rock"] = rock(2)
    new["sidewalk"] = sidewalk(3)
    new["grass"] = grass(4)
    new["asphalt"] = asphalt(5)
    new["gravel"] = gravel(6)
    for nm, top, top2, kind in (("slab_concrete", hx("8a8a86"), hx("5e5f5d"), "conc"),
                                 ("slab_parquet", hx("8a5f3a"), hx("6b4628"), "parquet"),
                                 ("slab_lino", hx("7a6a52"), hx("5f5141"), "lino"),
                                 ("slab_tile", hx("a8a49a"), hx("7d7a72"), "tile"),
                                 ("slab_office", hx("556066"), hx("434b50"), "office")):
        new[nm] = slab(top, top2, kind, len(nm))
    out = []
    for nm, im in tiles:
        if nm in new:
            out.append((nm, to_img(new[nm])))
        else:
            out.append((nm, im))
    return out, set(new)
