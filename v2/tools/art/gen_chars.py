"""Листы фигур людей: каждый слой одежды — отдельная полоса кадров 48x48 в материальной кодировке.

Все слои рисуются по одному скелету кадра, поэтому совпадают. Игра собирает человека из слоёв
и красит его шейдером палитры. Запуск: python3 gen_chars.py <папка assets>
"""
import sys, os, math
from PIL import Image, ImageDraw
from common import *

C = 48            # размер кадра
GROUND = 46       # нижний ряд подошвы

# ---------------- скелеты ----------------

def leg(hip, a, b, thigh=9, shin=10):
    ar = math.radians(a)
    knee = (hip[0] + thigh * math.sin(ar), hip[1] + thigh * math.cos(ar))
    sr = math.radians(a - b)
    foot = (knee[0] + shin * math.sin(sr), knee[1] + shin * math.cos(sr))
    return knee, foot


def arm(sh, a, b, up=7, fo=7):
    ar = math.radians(a)
    el = (sh[0] + up * math.sin(ar), sh[1] + up * math.cos(ar))
    fr = math.radians(a + b)
    hand = (el[0] + fo * math.sin(fr), el[1] + fo * math.cos(fr))
    return el, hand


def pose(hip, sh, head, lf, lb, af, ab, hd=1, ground=True, extra=None):
    """lf/lb: (угол бедра, изгиб колена); af/ab: (угол плеча, изгиб локтя)."""
    kf, ff = leg(hip, *lf)
    kb, fb = leg(hip, *lb)
    ef, hf = arm(sh, *af)
    eb, hb = arm(sh, *ab)
    p = {"hip": hip, "sh": sh, "head": head, "kf": kf, "ff": ff, "kb": kb, "fb": fb,
         "ef": ef, "hf": hf, "eb": eb, "hb": hb, "hd": hd}
    if extra:
        p.update(extra)
    if ground:
        low = max(ff[1], fb[1])
        dy = GROUND - low
        p = shift(p, 0, dy)
    return p


def shift(p, dx, dy):
    q = {}
    for k, v in p.items():
        if isinstance(v, tuple) and len(v) == 2:
            q[k] = (v[0] + dx, v[1] + dy)
        else:
            q[k] = v
    return q


def explicit(**kw):
    p = dict(kw)
    p.setdefault("hd", 1)
    return p


def stand(hip=(23, 27), lean=0, headf=(1, -7), lf=(4, 0), lb=(-4, 0), af=(6, -8), ab=(-6, 8), hd=1, ground=True):
    sh = (hip[0] + lean, hip[1] - 13)
    head = (sh[0] + headf[0], sh[1] + headf[1])
    return pose(hip, sh, head, lf, lb, af, ab, hd, ground)


FRAMES = []          # (имя, поза или None)
NAMES = {}


def add(name, p):
    NAMES.setdefault(name, len(FRAMES))
    FRAMES.append((name, p))


# 0-1 стоит
add("idle", stand())
p = stand(); p = dict(p); p["sh"] = (p["sh"][0], p["sh"][1] + 1); p["head"] = (p["head"][0], p["head"][1] + 1)
p["ef"] = (p["ef"][0], p["ef"][1] + 1); p["hf"] = (p["hf"][0], p["hf"][1] + 1); p["eb"] = (p["eb"][0], p["eb"][1] + 1); p["hb"] = (p["hb"][0], p["hb"][1] + 1)
add("idle", p)

# 2-9 ходьба
for i in range(8):
    t = i / 8.0 * 2 * math.pi
    s, c = math.sin(t), math.cos(t)
    lf = (26 * s, 8 + 34 * max(0.0, c))
    lb = (-26 * s, 8 + 34 * max(0.0, -c))
    af = (-22 * s, -12 - 8 * max(0.0, -s))
    ab = (22 * s, -12 - 8 * max(0.0, s))
    add("walk", stand(lf=lf, lb=lb, af=af, ab=ab, lean=1))

# 10-15 бег
for i in range(6):
    t = i / 6.0 * 2 * math.pi
    s, c = math.sin(t), math.cos(t)
    lf = (42 * s + 6, 20 + 70 * max(0.0, c))
    lb = (-42 * s + 6, 20 + 70 * max(0.0, -c))
    af = (-40 * s + 10, -85)
    ab = (40 * s + 10, -85)
    add("run", stand(lf=lf, lb=lb, af=af, ab=ab, lean=3, headf=(2, -7)))

# 16 прыжок, 17 падение
add("jump", stand(lf=(55, 85), lb=(15, 70), af=(150, 20), ab=(120, 30), lean=2))
add("fall", stand(lf=(18, 25), lb=(-14, 10), af=(140, -20), ab=(-140, 20), lean=0))

# 18-19 лестница (лицом к лестнице, руки вверх)
add("climb", stand(lf=(40, 70), lb=(0, 5), af=(165, -10), ab=(150, 5), lean=1, headf=(1, -7)))
add("climb", stand(lf=(0, 5), lb=(40, 70), af=(150, 5), ab=(165, -10), lean=1, headf=(1, -7)))

# 20 присел, 21-24 крадётся
add("crouch", stand(hip=(22, 34), lean=4, lf=(70, 110), lb=(30, 100), af=(25, -30), ab=(-5, -20), headf=(2, -6)))
for i in range(4):
    t = i / 4.0 * 2 * math.pi
    s, c = math.sin(t), math.cos(t)
    add("sneak", stand(hip=(22, 33), lean=4, lf=(60 + 18 * s, 95 + 15 * c), lb=(40 - 18 * s, 95 - 15 * c),
                       af=(20 + 15 * s, -40), ab=(10 - 15 * s, -40), headf=(2, -6)))

# 25 сидит на стуле
add("sit", explicit(hip=(21, 33), sh=(20, 20), head=(21, 13), kf=(30, 33), ff=(31, 45), kb=(29, 34), fb=(29, 45),
                    ef=(23, 27), hf=(29, 30), eb=(21, 27), hb=(27, 31)))

# 26 лежит (особый: поворот стоячей позы)
add("lie", "LIE")

# 27 оглушён, сидит у стены
add("slump", explicit(hip=(19, 43), sh=(18, 30), head=(21, 25), kf=(28, 43), ff=(37, 44), kb=(27, 42), fb=(36, 43),
                      ef=(21, 37), hf=(25, 43), eb=(17, 37), hb=(20, 43)))

# 28 несёт тело (руки вверх к плечу)
add("carry", stand(af=(160, -60), ab=(150, -40), lean=0))

# 29-30 душит (руки вперёд на высоте шеи)
add("strangle", stand(af=(95, -20), ab=(85, -10), lean=3, lf=(10, 5), lb=(-20, 0)))
add("strangle", stand(af=(100, -30), ab=(90, -20), lean=4, lf=(10, 5), lb=(-22, 0)))

# 31 толкает
add("push", stand(af=(85, 5), ab=(80, 10), lean=5, lf=(20, 10), lb=(-30, 0), headf=(2, -7)))

# 32 телефон у уха, 33 курит, 34 говорит, 35 тянется
add("phone", stand(af=(150, 160), ab=(-6, 8)))
add("smoke", stand(af=(130, 120)))
add("talk", stand(af=(75, 60)))
add("reach", stand(af=(85, 0), lean=1))

# 36 оглядывается назад
add("look", stand(hd=-1))

# 37 падает на колени (переход к лежанию)
add("kneel", stand(hip=(22, 36), lean=2, lf=(85, 100), lb=(40, 130), af=(30, -10), ab=(10, -10), headf=(2, -6)))

# 38 жертва (руки к шее, голова назад)
add("choke", stand(af=(160, 150), ab=(150, 160), lean=-2, headf=(0, -7)))

# 39 испуг (руки перед лицом)
add("cower", stand(hip=(22, 30), lean=-1, lf=(25, 40), lb=(-10, 30), af=(140, 80), ab=(120, 90)))

# 40 шатается (оглушённый)
add("stagger", stand(lean=4, af=(10, 0), ab=(-10, 5), headf=(3, -5), lf=(8, 10), lb=(-10, 5)))

# 41-48 сутулая походка (руки за спиной)
for i in range(8):
    t = i / 8.0 * 2 * math.pi
    s, c = math.sin(t), math.cos(t)
    lf = (18 * s + 4, 14 + 22 * max(0.0, c))
    lb = (-18 * s + 4, 14 + 22 * max(0.0, -c))
    add("walk_hunch", stand(lf=lf, lb=lb, af=(-40, 60), ab=(-35, 55), lean=4, headf=(3, -5)))

# 49-56 хромая походка (правая нога — передняя — почти не гнётся)
for i in range(8):
    t = i / 8.0 * 2 * math.pi
    s, c = math.sin(t), math.cos(t)
    lf = (16 * s, 4)
    lb = (-28 * s, 10 + 40 * max(0.0, -c))
    af = (-14 * s + 4, -10)
    ab = (14 * s, -10)
    p = stand(lf=lf, lb=lb, af=af, ab=ab, lean=1 + (1 if s > 0.3 else 0))
    add("walk_limp", p)

NFR = len(FRAMES)


# ---------------- рисование ----------------

def P(p, k):
    return (round(p[k][0]), round(p[k][1]))


def head_box(p):
    cx, cy = P(p, "head")
    return cx, cy


def hx(p, dx):
    """смещение по x от центра головы с учётом взгляда (hd=-1 зеркалит)."""
    return P(p, "head")[0] + dx * p.get("hd", 1)


def draw_rect_h(d, p, x0, x1, y0, y1, col):
    """прямоугольник в координатах головы (dx от центра, y абсолютные)."""
    a, b = hx(p, x0), hx(p, x1)
    d.rectangle([min(a, b), y0, max(a, b), y1], fill=col)


def layer_body(img, p):
    d = ImageDraw.Draw(img)
    cx, cy = head_box(p)
    sx, sy = P(p, "sh")
    # шея
    d.rectangle([min(cx, sx), cy + 3, max(cx, sx), sy + 1], fill=mat_px(SKIN, MID))
    # голова 7x8
    draw_rect_h(d, p, -3, 3, cy - 4, cy + 3, mat_px(SKIN, BASE))
    draw_rect_h(d, p, -3, -3, cy + 3, cy + 3, (0, 0, 0, 0))
    draw_rect_h(d, p, 3, 3, cy - 4, cy - 4, (0, 0, 0, 0))
    # нос
    draw_rect_h(d, p, 4, 4, cy, cy, mat_px(SKIN, BASE))
    # затылок теневой
    draw_rect_h(d, p, -3, -2, cy - 3, cy + 2, mat_px(SKIN, MID))
    # ухо
    draw_rect_h(d, p, -1, -1, cy, cy + 1, mat_px(SKIN, SH))
    inner_outline(img)
    # глаз (после обводки)
    draw_rect_h(d, p, 2, 2, cy - 1, cy - 1, mat_px(EYE, 0.25))
    # рот
    draw_rect_h(d, p, 2, 3, cy + 2, cy + 2, mat_px(SKIN, SH))


def limb(d, a, b, w, m, s):
    thick_line(d, a, b, w, mat_px(m, s))


def layer_legs(img, p, kind):
    d = ImageDraw.Draw(img)
    hip = P(p, "hip")
    for side, s in (("b", SH), ("f", BASE)):
        k, f = P(p, "k" + side), P(p, "f" + side)
        if kind == "pants":
            limb(d, hip, k, 4, BOTTOM, s)
            limb(d, k, f, 3, BOTTOM, s)
        else:
            limb(d, k, f, 2, ACC2, s)
            limb(d, hip, k, 3, ACC2, s)
        # ботинок: носок вперёд по направлению стопы
        fx, fy = f
        d.rectangle([fx - 1, fy - 1, fx + 2, fy], fill=mat_px(SHOES, s * 0.85))
    if kind == "skirt":
        kf, kb = P(p, "kf"), P(p, "kb")
        hy = hip[1]
        hem = max(kf[1], kb[1]) - 1
        d.polygon([(hip[0] - 3, hy - 1), (hip[0] + 3, hy - 1), (max(kf[0], kb[0]) + 3, hem), (min(kf[0], kb[0]) - 3, hem)],
                  fill=mat_px(BOTTOM, BASE))
    inner_outline(img)


def torso_poly(p, wf=3, wb=3, down=0):
    sx, sy = P(p, "sh")
    hx_, hy = P(p, "hip")
    return [(sx - wb, sy), (sx + wf, sy), (hx_ + wf, hy + down), (hx_ - wb, hy + down)]


def layer_torso(img, p, kind):
    d = ImageDraw.Draw(img)
    sx, sy = P(p, "sh")
    hx_, hy = P(p, "hip")
    if kind == "coat":
        kf, kb = P(p, "kf"), P(p, "kb")
        hem = max(kf[1], kb[1]) + 2
        poly = [(sx - 3, sy), (sx + 3, sy), (hx_ + 3, hy), (max(kf[0], kb[0]) + 3, hem), (min(kf[0], kb[0]) - 3, hem), (hx_ - 4, hy)]
        d.polygon(poly, fill=mat_px(TOP, BASE))
        # полы и пояс
        d.line([(hx_ - 3, hy - 1), (hx_ + 3, hy - 1)], fill=mat_px(TOP, MID))
        d.line([(hx_ + 1, hy), (min(kf[0], kb[0]) + 1, hem)], fill=mat_px(TOP, MID))
        d.rectangle([sx - 2, sy - 1, sx + 3, sy], fill=mat_px(TOP, HI))   # воротник
    elif kind == "parka":
        d.polygon([(sx - 4, sy - 1), (sx + 4, sy), (hx_ + 4, hy + 2), (hx_ - 4, hy + 2)], fill=mat_px(TOP, BASE))
        d.line([(sx - 4, sy + 6), (hx_ + 4, sy + 7)], fill=mat_px(TOP, MID))
        d.rectangle([sx - 4, sy - 2, sx - 1, sy], fill=mat_px(ACC, HI))   # мех капюшона
    else:
        down = 2 if kind in ("jacket", "uniform", "apron") else 1
        d.polygon(torso_poly(p, 3, 4, down), fill=mat_px(TOP, BASE))
        d.line([(sx - 3, sy + 1), (hx_ - 3, hy + down - 1)], fill=mat_px(TOP, MID))
        if kind == "shirt":
            d.rectangle([sx, sy - 1, sx + 2, sy], fill=mat_px(WHITE, MID))
        if kind == "jacket":
            d.line([(sx + 2, sy + 1), (sx + 2, sy + 6)], fill=mat_px(TOP2, BASE))
            d.line([(sx + 3, sy + 1), (sx + 3, sy + 5)], fill=mat_px(TOP2, HI))
            d.line([(sx + 1, sy + 1), (sx + 1, sy + 4)], fill=mat_px(TOP, MID))
        if kind == "sweater":
            d.line([(hx_ - 3, hy), (hx_ + 3, hy)], fill=mat_px(TOP, MID))
            d.rectangle([sx - 1, sy - 1, sx + 2, sy], fill=mat_px(TOP, MID))
        if kind == "apron":
            d.polygon([(sx + 1, sy + 4), (sx + 4, sy + 4), (hx_ + 4, hy + 6), (hx_ + 1, hy + 6)], fill=mat_px(TOP2, BASE))
        if kind == "uniform":
            d.line([(hx_ - 3, hy - 1), (hx_ + 3, hy - 1)], fill=mat_px(METAL, MID))
            d.rectangle([sx - 1, sy, sx + 1, sy], fill=mat_px(ACC2, BASE))     # погон
            d.point((sx + 2, sy + 3), fill=mat_px(ACC2, HI))
        if kind == "robe":   # белый халат врача/продавца: до колен
            kf, kb = P(p, "kf"), P(p, "kb")
            hem = max(kf[1], kb[1]) - 1
            d.polygon([(sx - 3, sy), (sx + 3, sy), (hx_ + 3, hy), (max(kf[0], kb[0]) + 2, hem), (min(kf[0], kb[0]) - 2, hem), (hx_ - 3, hy)], fill=mat_px(TOP, BASE))
    inner_outline(img)


def layer_arm(img, p, side):
    d = ImageDraw.Draw(img)
    sh = P(p, "sh")
    e, h = P(p, "e" + side), P(p, "h" + side)
    s = BASE if side == "f" else SH
    limb(d, sh, e, 3, TOP, s)
    limb(d, e, h, 3, TOP, s)
    inner_outline(img)
    d.rectangle([h[0] - 1, h[1] - 1, h[0], h[1]], fill=mat_px(SKIN, s))


def layer_hair(img, p, kind):
    d = ImageDraw.Draw(img)
    cx, cy = head_box(p)
    c = mat_px(HAIR, BASE)
    cm = mat_px(HAIR, MID)
    if kind == "short":
        draw_rect_h(d, p, -3, 3, cy - 5, cy - 3, c)
        draw_rect_h(d, p, -3, -2, cy - 3, cy + 1, cm)
        draw_rect_h(d, p, 3, 3, cy - 5, cy - 5, (0, 0, 0, 0))
    elif kind == "bob":
        draw_rect_h(d, p, -4, 3, cy - 5, cy - 3, c)
        draw_rect_h(d, p, -4, -1, cy - 3, cy + 4, cm)
        draw_rect_h(d, p, 3, 4, cy - 4, cy - 2, c)
    elif kind == "long":
        draw_rect_h(d, p, -4, 3, cy - 5, cy - 3, c)
        draw_rect_h(d, p, -4, -1, cy - 3, cy + 9, cm)
        draw_rect_h(d, p, 3, 4, cy - 4, cy - 3, c)
    elif kind == "bun":
        draw_rect_h(d, p, -3, 3, cy - 5, cy - 3, c)
        draw_rect_h(d, p, -3, -2, cy - 3, cy + 1, cm)
        draw_rect_h(d, p, -6, -4, cy - 6, cy - 3, c)
    elif kind == "pony":
        draw_rect_h(d, p, -3, 3, cy - 5, cy - 3, c)
        draw_rect_h(d, p, -3, -2, cy - 3, cy, cm)
        draw_rect_h(d, p, -5, -4, cy - 3, cy + 4, cm)
    elif kind == "bald":
        draw_rect_h(d, p, -3, -2, cy - 1, cy + 1, cm)
    elif kind == "curly":
        draw_rect_h(d, p, -4, 3, cy - 6, cy - 2, c)
        draw_rect_h(d, p, -4, -2, cy - 2, cy + 2, cm)
        for dx in (-3, -1, 1):
            draw_rect_h(d, p, dx, dx, cy - 6, cy - 6, (0, 0, 0, 0))
    inner_outline(img)


def layer_beard(img, p, kind):
    d = ImageDraw.Draw(img)
    cx, cy = head_box(p)
    if kind == "full":
        draw_rect_h(d, p, -1, 3, cy + 1, cy + 4, mat_px(HAIR, MID))
        draw_rect_h(d, p, 2, 3, cy + 1, cy + 1, mat_px(HAIR, BASE))
    elif kind == "mustache":
        draw_rect_h(d, p, 2, 4, cy + 1, cy + 1, mat_px(HAIR, MID))
    elif kind == "stubble":
        for dx, dy in ((0, 2), (2, 3), (1, 3), (3, 2), (-1, 2)):
            draw_rect_h(d, p, dx, dx, cy + dy, cy + dy, mat_px(HAIR, SH))


def layer_glasses(img, p):
    d = ImageDraw.Draw(img)
    cx, cy = head_box(p)
    draw_rect_h(d, p, -1, 3, cy - 1, cy - 1, mat_px(METAL, 0.35))
    draw_rect_h(d, p, 2, 3, cy - 2, cy, mat_px(METAL, 0.35))
    draw_rect_h(d, p, 2, 2, cy - 1, cy - 1, mat_px(WHITE, 0.7))


def layer_hat(img, p, kind):
    d = ImageDraw.Draw(img)
    cx, cy = head_box(p)
    c, cm, cs = mat_px(HAT, BASE), mat_px(HAT, MID), mat_px(HAT, SH)
    if kind == "fedora":
        draw_rect_h(d, p, -3, 3, cy - 8, cy - 4, c)
        draw_rect_h(d, p, -2, 2, cy - 9, cy - 9, c)
        draw_rect_h(d, p, -5, 5, cy - 4, cy - 4, cm)
        draw_rect_h(d, p, -3, 3, cy - 5, cy - 5, mat_px(ACC2, 0.4))
        draw_rect_h(d, p, 0, 0, cy - 9, cy - 8, (0, 0, 0, 0))
    elif kind == "cap":
        draw_rect_h(d, p, -3, 3, cy - 6, cy - 4, c)
        draw_rect_h(d, p, -2, 2, cy - 7, cy - 7, cm)
        draw_rect_h(d, p, 3, 6, cy - 4, cy - 4, cs)
    elif kind == "beret":
        draw_rect_h(d, p, -4, 3, cy - 6, cy - 4, c)
        draw_rect_h(d, p, -5, -4, cy - 5, cy - 4, cm)
        draw_rect_h(d, p, 0, 0, cy - 7, cy - 7, cm)
    elif kind == "ushanka":
        draw_rect_h(d, p, -4, 4, cy - 8, cy - 4, c)
        draw_rect_h(d, p, -4, -2, cy - 4, cy + 2, cm)
        draw_rect_h(d, p, -4, 4, cy - 4, cy - 4, cm)
    elif kind == "hood":
        draw_rect_h(d, p, -4, 2, cy - 6, cy - 4, c)
        draw_rect_h(d, p, -5, -1, cy - 4, cy + 5, cm)
        draw_rect_h(d, p, 2, 3, cy - 5, cy - 3, c)
    elif kind == "police":
        draw_rect_h(d, p, -3, 4, cy - 8, cy - 5, c)
        draw_rect_h(d, p, -3, 3, cy - 5, cy - 5, mat_px(ACC2, BASE))
        draw_rect_h(d, p, 3, 6, cy - 4, cy - 4, mat_px(METAL, 0.25))
        draw_rect_h(d, p, 2, 2, cy - 7, cy - 7, mat_px(WHITE, HI))
    elif kind == "beanie":
        draw_rect_h(d, p, -3, 3, cy - 7, cy - 3, c)
        draw_rect_h(d, p, -3, 3, cy - 3, cy - 3, cm)
        draw_rect_h(d, p, -1, 0, cy - 8, cy - 8, cm)
    elif kind == "kerchief":
        draw_rect_h(d, p, -4, 3, cy - 6, cy - 3, c)
        draw_rect_h(d, p, -5, -2, cy - 3, cy + 4, cm)
        draw_rect_h(d, p, 1, 3, cy + 4, cy + 5, cm)
    elif kind == "helmet":   # каска (стройка)
        draw_rect_h(d, p, -4, 4, cy - 8, cy - 4, c)
        draw_rect_h(d, p, -5, 5, cy - 4, cy - 4, cm)
    inner_outline(img)


def layer_scarf(img, p):
    d = ImageDraw.Draw(img)
    sx, sy = P(p, "sh")
    d.rectangle([sx - 3, sy - 2, sx + 3, sy + 1], fill=mat_px(ACC, BASE))
    d.rectangle([sx + 2, sy + 1, sx + 3, sy + 6], fill=mat_px(ACC, MID))
    inner_outline(img)


def layer_item(img, p, kind, fname):
    d = ImageDraw.Draw(img)
    hf = P(p, "hf")
    sx, sy = P(p, "sh")
    hip = P(p, "hip")
    if kind == "briefcase":
        if fname in ("climb", "carry", "lie", "slump", "strangle", "push", "choke", "cower", "phone", "smoke", "jump", "fall"):
            return
        x, y = hf
        d.rectangle([x - 3, y + 1, x + 3, y + 6], fill=mat_px(ACC, BASE))
        d.line([(x - 3, y + 3), (x + 3, y + 3)], fill=mat_px(ACC, MID))
        d.rectangle([x - 1, y, x + 1, y], fill=mat_px(METAL, MID))
    elif kind == "umbrella":
        if fname in ("climb", "carry", "lie", "slump", "strangle", "push", "choke", "cower", "phone", "smoke", "jump", "fall"):
            return
        x, y = hf
        thick_line(d, (x, y), (x + 2, y + 12), 2, mat_px(ACC, BASE))
        d.point((x + 2, y + 13), fill=mat_px(METAL, MID))
        d.point((x - 1, y - 1), fill=mat_px(ACC, MID))
    elif kind == "umbrella_open":
        if fname in ("climb", "lie", "slump", "jump", "fall"):
            return
        cx, cy = P(p, "head")
        top = cy - 14
        d.pieslice([cx - 11, top, cx + 11, top + 12], 180, 360, fill=mat_px(ACC, BASE))
        for i in range(-10, 11, 5):
            d.point((cx + i, top + 6), fill=mat_px(ACC, MID))
        d.line([(cx, top + 6), (cx + 1, sy + 4)], fill=mat_px(METAL, 0.5))
    elif kind == "bag":
        if fname in ("lie",):
            return
        d.line([(sx + 1, sy), (hip[0] - 3, hip[1] - 2)], fill=mat_px(ACC, SH))
        d.rectangle([hip[0] - 6, hip[1] - 3, hip[0] - 2, hip[1] + 2], fill=mat_px(ACC, BASE))
    elif kind == "backpack":
        if fname in ("lie",):
            return
        d.rectangle([sx - 7, sy + 1, sx - 3, sy + 10], fill=mat_px(ACC, BASE))
        d.line([(sx - 7, sy + 6), (sx - 3, sy + 6)], fill=mat_px(ACC, MID))
    elif kind == "paper":
        if fname not in ("idle", "sit", "walk"):
            return
        x, y = hf
        d.rectangle([x - 1, y - 4, x + 3, y + 1], fill=mat_px(WHITE, MID))
        d.line([(x, y - 3), (x + 2, y - 3)], fill=mat_px(METAL, 0.4))
    elif kind == "cig":
        if fname != "smoke":
            return
        x, y = hf
        d.line([(x + 1, y - 1), (x + 3, y - 1)], fill=mat_px(WHITE, HI))
        d.point((x + 3, y - 1), fill=mat_px(ACC2, HI))
    elif kind == "phone":
        if fname != "phone":
            return
        x, y = hf
        d.rectangle([x, y - 2, x + 1, y + 1], fill=mat_px(METAL, 0.3))
    elif kind == "cane":
        if fname in ("climb", "lie", "slump", "jump", "fall", "carry", "strangle", "push", "sit", "choke", "cower", "phone", "smoke"):
            return
        x, y = hf
        thick_line(d, (x, y), (x + 3, GROUND), 1, mat_px(ACC, MID))
        d.line([(x - 2, y), (x, y)], fill=mat_px(ACC, MID))
    elif kind == "flashlight":
        if fname in ("lie", "slump", "climb"):
            return
        x, y = hf
        d.rectangle([x - 1, y - 1, x + 3, y], fill=mat_px(METAL, MID))
        d.point((x + 3, y), fill=mat_px(WHITE, HI))
    if kind not in ("cig", "phone", "flashlight", "umbrella_open"):
        inner_outline(img)


# ---------------- сборка листов ----------------

LIE_SRC = stand(lf=(2, 0), lb=(-2, 0), af=(3, -2), ab=(-3, 2))
LIE_DY = 17


def render(fn, p, fname):
    """Рисует один кадр слоя. Для лежачего кадра рисует стоячую позу и поворачивает."""
    img = new(C, C)
    if p == "LIE":
        tmp = new(C, C)
        fn(tmp, LIE_SRC, "lie")
        tmp = tmp.transpose(Image.Transpose.ROTATE_90)   # голова влево
        img2 = new(C, C)
        img2.paste(tmp, (1, LIE_DY), tmp)
        return img2
    fn(img, p, fname)
    return img


LAYERS = {
    "body": lambda im, p, f: layer_body(im, p),
    "legs_pants": lambda im, p, f: layer_legs(im, p, "pants"),
    "legs_skirt": lambda im, p, f: layer_legs(im, p, "skirt"),
    "armb": lambda im, p, f: layer_arm(im, p, "b"),
    "armf": lambda im, p, f: layer_arm(im, p, "f"),
    "scarf": lambda im, p, f: layer_scarf(im, p),
    "glasses": lambda im, p, f: layer_glasses(im, p),
}
for k in ("shirt", "jacket", "coat", "sweater", "apron", "uniform", "parka", "robe"):
    LAYERS["torso_" + k] = (lambda kk: (lambda im, p, f: layer_torso(im, p, kk)))(k)
for k in ("short", "bob", "long", "bun", "pony", "bald", "curly"):
    LAYERS["hair_" + k] = (lambda kk: (lambda im, p, f: layer_hair(im, p, kk)))(k)
for k in ("full", "mustache", "stubble"):
    LAYERS["beard_" + k] = (lambda kk: (lambda im, p, f: layer_beard(im, p, kk)))(k)
for k in ("fedora", "cap", "beret", "ushanka", "hood", "police", "beanie", "kerchief", "helmet"):
    LAYERS["hat_" + k] = (lambda kk: (lambda im, p, f: layer_hat(im, p, kk)))(k)
for k in ("briefcase", "umbrella", "umbrella_open", "bag", "backpack", "paper", "cig", "phone", "cane", "flashlight"):
    LAYERS["item_" + k] = (lambda kk: (lambda im, p, f: layer_item(im, p, kk, f)))(k)


def main(out):
    os.makedirs(os.path.join(out, "fig"), exist_ok=True)
    for name, fn in LAYERS.items():
        sheet = new(C * NFR, C)
        for i, (fname, p) in enumerate(FRAMES):
            fr = render(fn, p, fname)
            sheet.paste(fr, (i * C, 0), fr)
        sheet.save(os.path.join(out, "fig", name + ".png"))
    # таблица кадров для игры
    anims = {}
    for i, (fname, p) in enumerate(FRAMES):
        anims.setdefault(fname, []).append(i)
    with open(os.path.join(out, "fig", "frames.txt"), "w") as f:
        for k, v in anims.items():
            f.write("%s %s\n" % (k, ",".join(str(x) for x in v)))
    print("frames", NFR, "layers", len(LAYERS))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "../../assets")
