"""Ручная перерисовка главных уличных предметов на мелком пикселе (вдвое больше пикселей).

Фонарь, таксофон, киоск, остановка, скамейка, контейнер, тополь и берёза, легковушки,
милиция, скорая, двери подъездов. Координаты здесь — в мелких пикселях.
Вызывается из gen_props.main() после всех предметов: run(G) перезаписывает PNG и
возвращает список имён, которые не надо затенять общим проходом.
"""
import math, random, os
import numpy as np
from PIL import Image, ImageDraw
from detail_tiles import hx, canvas, fill, bar, frame_rect, glass_area, grain, blotch, mpx, px, specks

OUTL = hx("181616")


# ---------------- помощники ----------------

def mask_poly(w, h, pts):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).polygon(pts, fill=255)
    return np.array(m) > 0


def mask_ell(w, h, x0, y0, x1, y1):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).ellipse([x0, y0, x1, y1], fill=255)
    return np.array(m) > 0


def mask_line(w, h, pts, width):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).line(pts, fill=255, width=width, joint="curve")
    return np.array(m) > 0


def paint(a, m, c, alpha=255):
    a[m, :3] = c
    a[m, 3] = alpha


def shade_mask(a, m, hi=1.18, lo=0.72, side=0.86):
    """объём по маске: верх/лево светлее, низ/право темнее"""
    up = np.roll(m, 1, 0); up[0] = False
    dn = np.roll(m, -1, 0); dn[-1] = False
    lf = np.roll(m, 1, 1); lf[:, 0] = False
    rt = np.roll(m, -1, 1); rt[:, -1] = False
    a[m & ~up, :3] *= hi
    a[m & ~dn, :3] *= lo
    a[m & ~lf & up, :3] *= 1.06
    a[m & ~rt & up & dn, :3] *= side


def box(a, x0, y0, x1, y1, c, hi=1.2, lo=0.7):
    fill(a, x0, y0, x1, y1, c)
    a[y0, x0:x1 + 1, :3] = c * hi
    a[y1, x0:x1 + 1, :3] = c * lo
    a[y0 + 1:y1, x0, :3] = c * 1.08
    a[y0 + 1:y1, x1, :3] = c * 0.82


def cyl(a, x0, y0, x1, y1, c, alpha=255):
    """вертикальный цилиндр: блик на трети ширины"""
    w = x1 - x0 + 1
    for i in range(w):
        t = i / max(1, w - 1)
        k = 0.75 + 0.55 * math.exp(-((t - 0.3) / 0.22) ** 2) - 0.15 * t
        a[y0:y1 + 1, x0 + i, :3] = c * k
        a[y0:y1 + 1, x0 + i, 3] = alpha


def outline(a, col=OUTL):
    op = a[..., 3] > 200
    near = np.zeros_like(op)
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        s = np.roll(np.roll(op, dy, 0), dx, 1)
        if dy == 1: s[0] = False
        if dy == -1: s[-1] = False
        if dx == 1: s[:, 0] = False
        if dx == -1: s[:, -1] = False
        near |= s
    m = near & (a[..., 3] == 0)
    a[m, :3] = col
    a[m, 3] = 255


def text(a, G, s, x, y, size, col, center_w=None, thr=100):
    t = np.array(G.pixel_text(s, size, tuple(int(v) for v in col) + (255,), thr=thr), float)
    h, w = t.shape[:2]
    if center_w is not None:
        x = x + (center_w - w) // 2
    m = t[..., 3] > 0
    H, W = a.shape[:2]
    for yy in range(h):
        for xx in range(w):
            if m[yy, xx] and 0 <= y + yy < H and 0 <= x + xx < W:
                a[y + yy, x + xx, :3] = t[yy, xx, :3]
                a[y + yy, x + xx, 3] = 255


FONT3 = {"Т": ["###", ".#.", ".#.", ".#.", ".#."], "А": [".#.", "#.#", "###", "#.#", "#.#"],
         "К": ["#.#", "##.", "#..", "##.", "#.#"], "С": [".##", "#..", "#..", "#..", ".##"],
         "О": [".#.", "#.#", "#.#", "#.#", ".#."], "Ф": [".#.", "###", "###", ".#.", ".#."],
         "Н": ["#.#", "#.#", "###", "#.#", "#.#"]}


def tiny(a, s, x, y, col):
    """мелкий шрифт 3×5 для табличек"""
    for ch in s:
        for j, row in enumerate(FONT3[ch]):
            for i, c in enumerate(row):
                if c == "#":
                    px(a, x + i, y + j, col)
        x += 4


def img(a):
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8), "RGBA")


def save_frames(G, name, frames):
    w, h = frames[0].shape[1], frames[0].shape[0]
    strip = Image.new("RGBA", (w * len(frames), h), (0, 0, 0, 0))
    for i, f in enumerate(frames):
        strip.paste(img(f), (i * w, 0))
    strip.save(os.path.join(G.OUT, "props", name + ".png"))


# ---------------- фонарь ----------------

def lamp(G):
    out = []
    pole = hx("3a3d40")
    for on in (0, 1):
        a = canvas(48, 144)
        # основание-тумба с болтами
        box(a, 18, 128, 29, 143, hx("2c2e30"))
        fill(a, 17, 127, 30, 128, hx("3e4144"))
        for x in (19, 28):
            px(a, x, 140, hx("5a5d60"))
        # ствол, сужается кверху
        for y in range(20, 128):
            t = (y - 20) / 108
            hw = 1.5 + 1.5 * t
            x0, x1 = int(round(23.5 - hw)), int(round(23.5 + hw))
            cyl(a, x0, y, x1, y, pole)
        for y in (60, 100):                         # кольца-стыки
            fill(a, 21, y, 26, y + 1, pole * 0.9)
            a[y, 21:27, :3] = pole * 1.3
        box(a, 23, 112, 25, 120, pole * 0.85)       # лючок
        # объявление на столбе
        fill(a, 20, 84, 27, 94, hx("d8d2c0"))
        for y in (86, 88, 90):
            a[y, 21:26, :3] = hx("8a8478")
        a[94, 20:28, :3] = hx("b8b2a0")
        # выгнутый кронштейн
        pts = [(24 + 15 * math.sin(t * math.pi / 2), 22 - 12 * math.sin(t * math.pi / 2) ** 0.7) for t in np.linspace(0, 1, 12)]
        m = mask_line(48, 144, pts, 3)
        paint(a, m, pole)
        shade_mask(a, m)
        # голова светильника
        hm = mask_poly(48, 144, [(30, 10), (44, 8), (47, 11), (45, 15), (31, 15)])
        paint(a, hm, hx("2f3133"))
        shade_mask(a, hm, 1.35, 0.7)
        gm = mask_poly(48, 144, [(32, 15), (45, 15), (44, 17), (33, 17)])
        paint(a, gm, hx("f4dc9a") if on else hx("6d6a5f"))
        if on:
            a[16, 34:44, :3] = hx("fff4d0")
            for y in range(18, 24):                 # ореол
                w = (y - 17)
                for x in range(38 - w * 2, 40 + w * 2):
                    if 0 <= x < 48 and a[y, x, 3] == 0:
                        a[y, x, :3] = hx("f4dc9a")
                        a[y, x, 3] = max(0, 70 - (y - 18) * 12)
        else:
            a[16, 34:44, :3] = hx("8a867a")
        out.append(a)
    for a in out:
        outline(a)
    save_frames(G, "lamp", out)


# ---------------- таксофон ----------------

def payphone(G):
    out = []
    red = hx("8c2f2a")
    for ring in (0, 1, 2):
        a = canvas(44, 92)
        # будка: задняя стенка со стеклом в рёбрах, боковые красные стойки, козырёк
        box(a, 2, 12, 41, 90, red)
        fill(a, 6, 16, 37, 82, hx("3b4752"))
        for y in range(18, 82, 3):
            a[y, 7:37, :3] = hx("4a5865")
            a[y + 1, 7:37, :3] = hx("33404a")
        a[16, 6:38, :3] = hx("252d33")
        a[16:83, 6, :3] = hx("2a333a")
        # козырёк с табличкой
        box(a, 0, 2, 43, 13, hx("6e2420"), 1.3, 0.6)
        fill(a, 3, 4, 40, 11, hx("e9e2cf"))
        a[11, 3:41, :3] = hx("b8b2a0")
        tiny(a, "ТАКСОФОН", 6, 5, hx("8c2f2a"))
        # аппарат
        box(a, 14, 30, 31, 62, hx("5b5f61"), 1.3, 0.6)
        fill(a, 16, 33, 29, 36, hx("2a2c2d"))           # табло
        a[34, 17:24, :3] = hx("9ab060")
        # диск номеронабирателя
        dm = mask_ell(44, 92, 17, 40, 28, 51)
        paint(a, dm, hx("c8c4b8"))
        shade_mask(a, dm, 1.1, 0.7)
        for k in range(10):
            ang = -math.pi * 0.25 + k * math.pi * 1.5 / 9
            px(a, int(round(22.5 + 3.8 * math.cos(ang))), int(round(45.5 + 3.8 * math.sin(ang))), hx("3a3c3e"))
        px(a, 22, 45, hx("5b5f61")); px(a, 23, 45, hx("5b5f61"))
        fill(a, 25, 54, 28, 55, hx("1c1d1e"))           # монетоприёмник
        fill(a, 17, 57, 28, 59, hx("44484a"))           # лоток
        # трубка на рычаге
        off = (0, -2, 2)[ring]
        hm = mask_poly(44, 92, [(12 + off, 28), (16 + off, 27), (16 + off, 31), (14 + off, 32), (14 + off, 41),
                                 (16 + off, 42), (16 + off, 46), (12 + off, 45)])
        paint(a, hm, hx("1c1d1e"))
        shade_mask(a, hm, 1.8, 0.8)
        # витой шнур
        for i, y in enumerate(range(47, 62)):
            px(a, 13 + off // 2 + (i % 2), y, hx("26282a"))
        if ring:
            for (x, y) in ((8, 26), (9, 24), (8, 47), (9, 49)):
                px(a, x + off, y, hx("e9e2cf"))
        # ржавчина и царапины
        specks(a, 10, (0.75, 0.9), 3, 1, (3, 64, 40, 89))
        for y in range(64, 74):
            mpx(a, 5, y, 0.85)
        fill(a, 4, 86, 39, 90, red * 0.6)
        out.append(a)
    for a in out:
        outline(a)
    save_frames(G, "payphone", out)


# ---------------- киоск ----------------

def kiosk(G):
    a = canvas(96, 100)
    body = hx("5e7a8a")
    box(a, 4, 20, 91, 99, body)
    for x in range(8, 92, 12):                       # вертикальные панели и заклёпки
        a[24:96, x, :3] = body * 0.85
        a[24:96, x + 1, :3] = body * 1.08
        for y in (26, 60, 94):
            px(a, x + 3, y, body * 1.3)
    # козырёк
    box(a, 0, 12, 95, 24, hx("3f5563"), 1.3, 0.6)
    fill(a, 0, 25, 95, 26, hx("2a3a44"))
    a[27, 4:92, :3] *= 0.75
    fill(a, 10, 0, 85, 12, hx("2f3f49"))
    a[0, 10:86, :3] = hx("4a6070")
    text(a, G, "ПЕЧАТЬ", 10, 0, 8, hx("ece4cc"), center_w=76)
    # витрина
    fill(a, 9, 31, 86, 69, hx("2d3a42"))
    frame_rect(a, 9, 31, 86, 69, hx("263038") * 1.4, 2)
    r = random.Random(4)
    cols = (hx("cfc8b2"), hx("a7442f"), hx("d9b640"), hx("b8b2a0"), hx("6e8aa0"), hx("cfc8b2"))
    for i in range(6):
        x = 13 + i * 12
        c = cols[i]
        box(a, x, 38 + (i % 2) * 2, x + 9, 64, c, 1.1, 0.75)
        fill(a, x + 1, 40 + (i % 2) * 2, x + 8, 42 + (i % 2) * 2, c * 0.55)   # заголовок
        for yy in range(46 + (i % 2) * 2, 62, 2):
            ln = r.randint(4, 7)
            a[yy, x + 1:x + 1 + ln, :3] = c * 0.68
        if i in (1, 4):
            fill(a, x + 2, 48, x + 6, 53, c * 0.45)
    for y in range(33, 68):                          # блики на стекле витрины
        for x in range(11, 85):
            if (x + y) % 29 in (0, 1):
                a[y, x, :3] = a[y, x, :3] * 0.6 + hx("c8d4dc") * 0.4
    # прилавок и окошко
    box(a, 7, 70, 88, 74, hx("2a3338"), 1.4, 0.6)
    fill(a, 60, 76, 80, 90, hx("1e272c"))
    frame_rect(a, 59, 75, 81, 91, body * 0.8, 1)
    fill(a, 62, 78, 72, 88, hx("c8a878") * 0.5)       # силуэт продавщицы в окошке
    fill(a, 64, 79, 69, 83, hx("c8a878") * 0.7)
    # вентиляционная решётка и цоколь
    for y in range(80, 88, 2):
        a[y, 14:30, :3] = body * 0.6
    fill(a, 4, 96, 91, 99, body * 0.5)
    specks(a, 14, (0.8, 0.9), 7, 1, (5, 76, 90, 95))
    outline(a)
    save_frames(G, "kiosk", [a])


# ---------------- остановка ----------------

def busstop(G):
    a = canvas(128, 96)
    post = hx("3a3f44")
    for x in (6, 116):
        cyl(a, x, 14, x + 4, 95, post)
    # стёкла с бликами
    for y in range(18, 80):
        for x in range(12, 115):
            t = (x + y) % 37
            c = hx("7890a0") * (1.4 if t < 3 else 1.0)
            a[y, x, :3] = c
            a[y, x, 3] = 85 if t >= 3 else 120
    for x in (40, 76):
        fill(a, x, 18, x + 1, 79, post)
    fill(a, 12, 50, 114, 51, post)
    # крыша
    box(a, 2, 6, 125, 15, hx("4c5560"), 1.35, 0.6)
    a[16, 4:124, :3] = hx("2a2f34")
    a[16, 4:124, 3] = 255
    # скамья
    box(a, 20, 68, 100, 72, hx("5a4836"))
    for x in range(20, 101, 7):
        a[69:72, x, :3] *= 0.8
    for x in (24, 94):
        fill(a, x, 73, x + 3, 85, post)
    # табличка «А» и расписание
    box(a, 104, 0, 121, 17, hx("e5dfcc"))
    text(a, G, "А", 104, 1, 11, hx("2a5a8a"), center_w=18)
    box(a, 46, 24, 70, 44, hx("d8d2c0"))
    for yy in range(28, 43, 3):
        a[yy, 49:67, :3] = hx("7a7468")
    a[26, 49:67, :3] = hx("2a5a8a")
    outline(a)
    # стёкла без обводки снаружи — убираем обводку у полупрозрачных
    save_frames(G, "busstop", [a])


# ---------------- скамейка ----------------

def bench(G):
    a = canvas(64, 28)
    wood = hx("6b4e33")
    iron = hx("2b2b2b")
    # чугунные ножки-боковины
    for x0 in (6, 54):
        m = mask_poly(64, 28, [(x0, 3), (x0 + 3, 3), (x0 + 3, 14), (x0 + 5, 27), (x0 + 1, 27), (x0, 16)])
        paint(a, m, iron)
        shade_mask(a, m, 1.6, 0.8)
    # рейки сиденья и спинки с текстурой дерева
    for (y0, y1) in ((1, 3), (5, 7), (12, 14), (15, 16)):
        box(a, 2, y0, 61, y1, wood, 1.25, 0.7)
        r = random.Random(y0)
        for _ in range(5):
            x = r.randint(4, 56)
            L = r.randint(4, 9)
            a[(y0 + y1) // 2, x:x + L, :3] *= 0.86
        for x in (8, 56):
            px(a, x, (y0 + y1) // 2, hx("8a8a8a"))
    outline(a)
    save_frames(G, "bench", [a])


# ---------------- контейнер ----------------

def dumpster(G):
    out = []
    g = hx("3f5a46")
    for op in (0, 1):
        a = canvas(72, 60)
        box(a, 4, 16, 67, 54, g)
        a[28, 4:68, :3] = g * 0.7
        a[29, 4:68, :3] = g * 1.15
        for x in range(10, 66, 9):                    # рёбра жёсткости
            a[30:53, x, :3] = g * 1.18
            a[30:53, x + 1, :3] = g * 0.78
        box(a, 12, 34, 59, 39, hx("c9a43b"), 1.2, 0.7)
        for x in range(14, 58, 4):                    # трафарет на полосе
            a[36, x:x + 2, :3] = hx("6a5420")
        for x in (20, 47, 58):                        # ржавые потёки
            for y in range(40, 52):
                mpx(a, x, y, 0.85 if y % 3 else 0.75)
                if y % 4 == 0:
                    a[y, x, :3] = a[y, x, :3] * np.array([1.25, 0.95, 0.7])
        specks(a, 18, (0.75, 0.9), 2, 1, (5, 17, 66, 53))
        for x in (8, 56):                             # колёса
            fill(a, x, 54, x + 7, 55, hx("2a2a2a"))
            wm = mask_ell(72, 60, x, 52, x + 7, 59)
            paint(a, wm, hx("1d1d1d"))
            px(a, x + 3, 55, hx("777777")); px(a, x + 4, 55, hx("777777"))
        if op:
            fill(a, 6, 14, 65, 17, hx("151815"))
            bm = mask_ell(72, 60, 14, 6, 34, 20)       # мешок мусора
            paint(a, bm, hx("2a2c30"))
            shade_mask(a, bm, 1.5, 0.8)
            lm = mask_poly(72, 60, [(4, 16), (67, 16), (71, 0), (9, 0)])
            paint(a, lm, g * 0.75)
            shade_mask(a, lm, 1.3, 0.7)
            for i in range(1, 60, 10):
                a[2:15, 8 + i, :3] *= 0.85
        else:
            box(a, 2, 10, 69, 16, g * 0.75, 1.4, 0.6)
            fill(a, 30, 8, 41, 9, g * 0.6)             # ручка крышки
        out.append(a)
    for a in out:
        outline(a)
    save_frames(G, "dumpster", out)


# ---------------- деревья ----------------

def tree(G, name, trunk, leaf, seed):
    W, H = 112, 192
    a = canvas(W, H)
    r = random.Random(seed)
    # ствол
    for y in range(76, 192):
        t = (y - 76) / 116
        hw = 4 + 3.5 * t
        x0, x1 = int(56 - hw), int(56 + hw)
        cyl(a, x0, y, x1, y, trunk)
    if name == "birch":
        for _ in range(26):                           # чёрные полоски берёзы
            y = r.randint(80, 188)
            x = r.randint(50, 58)
            L = r.randint(2, 6)
            for i in range(L):
                if a[y, x + i, 3]:
                    a[y, x + i, :3] = hx("2b2a28")
    else:
        for y in range(78, 184, 3):                   # трещины коры тополя
            x = r.randint(50, 60)
            for i in range(r.randint(2, 5)):
                if a[y + i, x, 3]:
                    a[y + i, x, :3] *= 0.65
    # корни
    for dx in (-12, 10):
        m = mask_poly(W, H, [(56, 182), (56 + dx, 191), (56 + dx * 0.4, 191)])
        paint(a, m, trunk * 0.9)
    # ветви
    br = [((56, 120), (30, 86)), ((56, 104), (82, 78)), ((40, 96), (24, 66)), ((70, 90), (86, 60)), ((56, 80), (54, 40))]
    for p, q in br:
        m = mask_line(W, H, [p, q], 4)
        paint(a, m, trunk * 0.95)
        shade_mask(a, m)
    # крона: кластеры листьев, каждый с объёмом
    leafm = np.zeros((H, W), bool)
    clusters = []
    for _ in range(26):
        ang = r.random() * 6.283
        rr = r.random() ** 0.6 * 40
        cx, cy = 56 + math.cos(ang) * rr * 0.95, 60 + math.sin(ang) * rr * 1.15
        rad = r.uniform(9, 15)
        clusters.append((cy, cx, rad))
    clusters.sort()
    yy, xx = np.mgrid[0:H, 0:W]
    noise = np.random.default_rng(seed).random((H, W))
    for cy, cx, rad in clusters:
        d = np.hypot((xx - cx) / rad, (yy - cy) / (rad * 0.9))
        m = (d < 1) & (noise < 1.15 - d * 0.6)
        # освещённость кластера: свет сверху слева
        lx = ((cx - xx) + (cy - yy)) / (rad * 2)
        base = leaf * (0.8 + 0.3 * r.random())
        k = 0.85 + 0.45 * np.clip(lx, -0.6, 0.6)
        k = np.where(d > 0.85, k * 0.8, k)
        a[m, :3] = base * k[m][:, None]
        a[m, 3] = 255
        leafm |= m
    # просветы и отдельные листочки по краю
    for _ in range(140):
        cy, cx, rad = r.choice(clusters)
        ang = r.random() * 6.283
        x = int(cx + math.cos(ang) * rad * r.uniform(0.9, 1.25))
        y = int(cy + math.sin(ang) * rad * r.uniform(0.9, 1.2))
        if 0 <= x < W and 0 <= y < H:
            a[y, x, :3] = leaf * r.uniform(0.7, 1.2)
            a[y, x, 3] = 255
    for _ in range(40):
        x, y = r.randrange(20, 92), r.randrange(20, 100)
        if leafm[y, x]:
            a[y, x, :3] *= 1.3
    # без внешней обводки: крона мягкая, как раньше
    save_frames(G, name, [a])


# ---------------- машины ----------------

def car(G, name, body, kind="car"):
    W, H = 128, 52
    a = canvas(W, H)
    if kind == "ambulance":
        shape = [(4, 4), (92, 4), (104, 20), (124, 24), (125, 42), (4, 42)]
    else:
        shape = [(4, 24), (28, 21), (40, 6), (84, 6), (100, 21), (124, 25), (125, 42), (4, 42)]
    m = mask_poly(W, H, shape)
    yy, xx = np.mgrid[0:H, 0:W]
    # кузов: верх светлее, к порогу темнее, линия бокового «плеча»
    k = 1.15 - 0.4 * np.clip((yy - 6) / 36, 0, 1)
    a[m, :3] = body * k[m][:, None]
    a[m, 3] = 255
    shade_mask(a, m, 1.3, 0.6)
    shoulder = 29
    a[shoulder, 5:124, :3] = body * 1.35
    a[shoulder + 1, 5:124, :3] = body * 0.78
    if kind != "ambulance":
        # окна с переплётами и отражением
        for poly in ([(44, 10), (62, 10), (62, 22), (34, 22)], [(66, 10), (82, 10), (94, 22), (66, 22)]):
            wm = mask_poly(W, H, poly)
            t = np.clip((yy - 10) / 12, 0, 1)
            g = hx("2c3a44")[None, :] * (1.35 - 0.5 * t[wm])[:, None]
            a[wm, :3] = g
            refl = wm & (((xx + yy) % 19) < 3)
            a[refl, :3] *= 1.5
        fill(a, 62, 9, 65, 23, body * 0.7)            # стойка
        a[23, 34:96, :3] = hx("8a8e90")                 # молдинг стекла
        # двери, ручки, зеркало
        for x in (64,):
            a[24:41, x, :3] = body * 0.6
        a[24:41, 96, :3] = body * 0.6
        a[24:41, 33, :3] = body * 0.6
        fill(a, 54, 27, 58, 27, hx("b8bcc0"))
        fill(a, 86, 27, 90, 27, hx("b8bcc0"))
        fill(a, 96, 18, 99, 21, body * 0.8)
    # хромированные бамперы и фары
    box(a, 2, 33, 10, 36, hx("b8bcc0"), 1.3, 0.6)
    box(a, 118, 33, 126, 36, hx("b8bcc0"), 1.3, 0.6)
    fill(a, 121, 27, 125, 31, hx("e8e2c8"))
    a[27, 121:126, :3] = hx("fffbe8")
    fill(a, 4, 27, 7, 31, hx("a5322a"))
    a[28, 4:8, :3] = hx("d0483a")
    fill(a, 108, 35, 116, 38, hx("e8e4d8"))           # номер
    a[36, 109:116, :3] = hx("2a2a2a")
    # колёса: шина с протектором, колпак с отверстиями, тёмная арка
    for wx in (28, 100):
        am = mask_ell(W, H, wx - 13, 26, wx + 13, 52) & m
        a[am, :3] *= 0.45
        tm = mask_ell(W, H, wx - 10, 30, wx + 10, 50)
        paint(a, tm, hx("1d1d1f"))
        for ang in np.linspace(0, 6.283, 18, endpoint=False):
            px(a, int(round(wx + 9.4 * math.cos(ang))), int(round(40 + 9.4 * math.sin(ang))), hx("2e2e31"))
        hm = mask_ell(W, H, wx - 5, 35, wx + 5, 45)
        paint(a, hm, hx("8a8c8e"))
        shade_mask(a, hm, 1.4, 0.6)
        for ang in (0.8, 2.4, 3.9, 5.5):
            px(a, int(round(wx + 3 * math.cos(ang))), int(round(40 + 3 * math.sin(ang))), hx("3a3c3e"))
        px(a, wx, 40, hx("c8cacc"))
    if kind == "police":
        fill(a, 5, 30, 123, 34, hx("2e4f8a"))
        a[30, 5:124, :3] = hx("4a6aa8")
        text(a, G, "МИЛИЦИЯ", 34, 30, 5, hx("e9e6dc"), thr=60)
        box(a, 54, 0, 70, 5, hx("3a6ad0"), 1.4, 0.6)
        fill(a, 55, 1, 59, 3, hx("8ab0ff"))
    if kind == "ambulance":
        wm = mask_poly(W, H, [(94, 8), (103, 20), (94, 20)])
        paint(a, wm, hx("2c3a44"))
        a[wm & (((xx + yy) % 13) < 2), :3] = hx("5a6c78")
        for x0 in (12, 40, 64):
            fill(a, x0, 9, x0 + 18, 19, hx("2c3a44"))
            frame_rect(a, x0, 9, x0 + 18, 19, hx("b8b2a0"), 1)
            fill(a, x0 + 1, 10, x0 + 17, 18, hx("d8d4c8") * 0.9)   # матовое стекло
        fill(a, 4, 26, 124, 28, hx("b8342b"))
        fill(a, 42, 30, 54, 33, hx("b8342b"))
        fill(a, 46, 26, 50, 37, hx("b8342b"))
        box(a, 40, 0, 52, 3, hx("3a6ad0"), 1.4, 0.6)
        a[24:41, 88, :3] = body * 0.6
    outline(a)
    save_frames(G, name, [a])


# ---------------- двери подъездов ----------------

def entrances(G):
    for nm, c in (("entrance", hx("4a3a2c")), ("entrance_metal", hx("3d4a52")), ("entrance_glass", hx("2e2c2b"))):
        out = []
        for op in (0, 1):
            a = canvas(64, 96)
            fill(a, 0, 0, 63, 95, hx("2a2622"))
            frame_rect(a, 0, 0, 63, 95, hx("2a2622") * 1.5, 2)
            fill(a, 4, 4, 59, 6, hx("1a1714"))           # тень откоса
            if op:
                fill(a, 6, 6, 57, 95, hx("151312"))
                # лестница в глубине подъезда
                for i in range(6):
                    fill(a, 14 + i * 7, 88 - i * 8, 57, 95 - i * 8, hx("2a2624") * (1 + i * 0.06))
                    a[88 - i * 8, 14 + i * 7:58, :3] = hx("3e3a36")
                lm = mask_poly(64, 96, [(6, 6), (18, 12), (18, 95), (6, 95)])
                paint(a, lm, c)
                shade_mask(a, lm, 1.3, 0.7)
            else:
                for x0 in (6, 33):
                    box(a, x0, 6, x0 + 24, 95, c, 1.25, 0.7)
                    if nm == "entrance_glass":
                        glass_area(a, x0 + 3, 9, x0 + 21, 90, 150)
                    elif nm == "entrance_metal":
                        for y in range(10, 94, 10):
                            px(a, x0 + 2, y, c * 1.5); px(a, x0 + 22, y, c * 1.5)
                        box(a, x0 + 4, 14, x0 + 20, 40, c * 0.88)
                        box(a, x0 + 4, 50, x0 + 20, 88, c * 0.88)
                    else:
                        box(a, x0 + 4, 12, x0 + 20, 36, c * 0.85)     # филёнки
                        box(a, x0 + 4, 44, x0 + 20, 88, c * 0.85)
                        r = random.Random(x0)
                        for _ in range(6):
                            x = r.randint(x0 + 5, x0 + 19)
                            a[46:87, x, :3] *= 0.92
                fill(a, 31, 6, 32, 95, c * 0.55)
                fill(a, 27, 50, 29, 58, hx("b8b4a8"))       # ручки
                fill(a, 36, 50, 38, 58, hx("b8b4a8"))
                a[50, 27:30, :3] = hx("e0dcd0")
            # домофон и номер подъезда
            box(a, 54, 38, 60, 54, hx("3a3d40"), 1.4, 0.6)
            for y in range(41, 52, 3):
                px(a, 56, y, hx("8a8e90")); px(a, 58, y, hx("8a8e90"))
            box(a, 26, 0, 37, 4, hx("2a5a8a"), 1.3, 0.7)
            px(a, 31, 2, hx("e8e4d8")); px(a, 32, 2, hx("e8e4d8"))
            out.append(a)
        save_frames(G, nm, out)


def run(G):
    lamp(G)
    payphone(G)
    kiosk(G)
    busstop(G)
    bench(G)
    dumpster(G)
    tree(G, "tree", hx("4b4035"), hx("4d5a3a"), 1)
    tree(G, "birch", hx("cfcabd"), hx("6d7a40"), 2)
    for i, c in enumerate(("8a3a2e", "c8c2a8", "3d5e78", "5d6b4a", "2e2e33")):
        car(G, "car%d" % i, hx(c))
    car(G, "police_car", hx("d9d7cf"), "police")
    car(G, "ambulance", hx("e2ded2"), "ambulance")
    entrances(G)
    return ["lamp", "payphone", "kiosk", "busstop", "bench", "dumpster", "tree", "birch",
            "car0", "car1", "car2", "car3", "car4", "police_car", "ambulance", "entrance", "entrance_metal", "entrance_glass"]
