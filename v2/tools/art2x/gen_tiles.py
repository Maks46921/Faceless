"""Атлас тайлов 16x16: земля, перекрытия, стены в разрезе, обои, фасады с окнами.

Выход: assets/tiles.png и assets/tiles.txt (имя столбец строка).
"""
import sys, os, random
from PIL import Image, ImageDraw
from common import *

T = 16
COLS = 16
tiles = []        # (имя, картинка)
rnd = random.Random(7)


def tile():
    return new(T, T)


def add(name, im):
    tiles.append((name, im))


# ---------- палитра ----------
EARTH = hexc("4a3f36")
ROCK = hexc("3d3b3a")
ASPH = hexc("4b4c4f")
CONC = hexc("8a8a86")
CONC_D = hexc("5e5f5d")
BRICK = hexc("8a4a3a")
SBRICK = hexc("a9a395")
PANEL = hexc("9b9a92")
STUCCO = hexc("b3a27a")
GRANITE = hexc("5d5a58")
GLASS = hexc("3a4a58")
TAR = hexc("3a3836")
TIN = hexc("6e7470")
WHITE = hexc("d8d6cc")
GREEN_P = hexc("4f6e5a")
BLUE_P = hexc("4f6478")


# ---------- земля и улица ----------
def ground_tiles():
    im = tile(); noise_fill(im, (0, 0, T, T), EARTH, 0.25, rnd)
    for i in range(5):
        put(im, rnd.randrange(T), rnd.randrange(T), mul(EARTH, 1.4))
    add("earth", im)
    im = tile(); noise_fill(im, (0, 0, T, T), ROCK, 0.3, rnd)
    for i in range(3):
        x, y = rnd.randrange(2, 14), rnd.randrange(2, 14)
        rect(im, (x, y, x + 2, y + 1), mul(ROCK, 1.35))
    add("rock", im)
    # тротуар: плитка сверху, под ней песок
    im = tile(); noise_fill(im, (0, 0, T, T), EARTH, 0.2, rnd)
    rect(im, (0, 0, 15, 3), hexc("7c7b76")); hline(im, 0, 15, 0, hexc("9a9993")); vline(im, 7, 1, 3, hexc("5f5e5a"))
    hline(im, 0, 15, 4, hexc("3e3530"))
    add("sidewalk", im)
    im = tile(); noise_fill(im, (0, 0, T, T), EARTH, 0.2, rnd)
    rect(im, (0, 0, 15, 2), hexc("5d6b45")); hline(im, 0, 15, 0, hexc("72814f"))
    for x in range(0, 16, 3):
        put(im, x, 0 - 0, hexc("819059"))
    add("grass", im)
    im = tile(); noise_fill(im, (0, 0, T, T), ASPH, 0.18, rnd)
    hline(im, 0, 15, 0, mul(ASPH, 1.25))
    add("asphalt", im)
    im = tile(); noise_fill(im, (0, 0, T, T), hexc("6d6a63"), 0.3, rnd)
    hline(im, 0, 15, 0, hexc("8c887e"))
    add("gravel", im)


# ---------- конструкции в разрезе ----------
def structure_tiles():
    # перекрытие: бетон с арматурой, сверху покрытие
    for nm, top, top2 in (("slab_concrete", CONC, CONC_D), ("slab_parquet", hexc("8a5f3a"), hexc("6b4628")),
                          ("slab_lino", hexc("7a6a52"), hexc("5f5141")), ("slab_tile", hexc("a8a49a"), hexc("7d7a72")),
                          ("slab_office", hexc("556066"), hexc("434b50"))):
        im = tile(); noise_fill(im, (0, 0, T, T), CONC_D, 0.12, rnd)
        rect(im, (0, 0, 15, 2), top)
        if nm == "slab_parquet":
            for x in range(0, 16, 4):
                vline(im, x, 0, 2, top2)
        if nm == "slab_tile":
            for x in range(0, 16, 5):
                vline(im, x, 0, 2, top2)
        hline(im, 0, 15, 3, top2)
        for x in (3, 8, 13):
            put(im, x, 9, hexc("3b3c3b"))
        hline(im, 0, 15, 15, mul(CONC_D, 0.8))
        add(nm, im)
    # стена в разрезе (перегородка): штукатурка + кирпич внутри
    im = tile(); noise_fill(im, (0, 0, T, T), hexc("6b6660"), 0.15, rnd)
    vline(im, 0, 0, 15, hexc("8d8880")); vline(im, 15, 0, 15, hexc("8d8880"))
    for y in range(2, 16, 4):
        hline(im, 2, 13, y, hexc("524e49"))
    add("cutwall", im)
    # внешние стены в разрезе
    for nm, c in (("wall_brick", BRICK), ("wall_sbrick", SBRICK), ("wall_panel", PANEL), ("wall_stucco", STUCCO),
                  ("wall_granite", GRANITE), ("wall_conc", CONC)):
        im = tile(); noise_fill(im, (0, 0, T, T), mul(c, 0.8), 0.15, rnd)
        if "brick" in nm:
            for y in range(0, 16, 4):
                hline(im, 0, 15, y, mul(c, 0.55))
                off = 0 if (y // 4) % 2 == 0 else 4
                for x in range(off, 16, 8):
                    vline(im, x, y, y + 3, mul(c, 0.55))
        elif nm == "wall_panel":
            hline(im, 0, 15, 15, mul(c, 0.6))
            vline(im, 15, 0, 15, mul(c, 0.6))
        add(nm, im)
    # крыша: рубероид с гравием и жесть
    im = tile(); noise_fill(im, (0, 0, T, T), CONC_D, 0.12, rnd)
    rect(im, (0, 0, 15, 4), TAR)
    for i in range(8):
        put(im, rnd.randrange(T), rnd.randrange(0, 3), hexc("5a5652"))
    hline(im, 0, 15, 5, hexc("2b2927"))
    add("roof_tar", im)
    im = tile(); noise_fill(im, (0, 0, T, T), CONC_D, 0.12, rnd)
    rect(im, (0, 0, 15, 3), TIN)
    for x in range(0, 16, 4):
        vline(im, x, 0, 3, mul(TIN, 0.75))
    hline(im, 0, 15, 0, mul(TIN, 1.25))
    add("roof_tin", im)
    # парапет
    im = tile(); rect(im, (0, 6, 15, 15), mul(CONC, 0.85)); hline(im, 0, 15, 6, mul(CONC, 1.1)); hline(im, 0, 15, 7, hexc("6c6e6a"))
    add("parapet", im)
    # металлическая площадка пожарной лестницы (полупроход)
    im = tile(); rect(im, (0, 0, 15, 2), hexc("3d3f40"))
    for x in range(0, 16, 3):
        put(im, x, 1, hexc("23252a"))
    vline(im, 0, 3, 15, hexc("35373a")); vline(im, 8, 3, 7, hexc("35373a"))
    add("grate_platform", im)
    # решётка (лаз): видна, людей не пускает, дух проходит
    im = tile()
    for x in range(1, 16, 3):
        vline(im, x, 0, 15, hexc("46484a"))
    hline(im, 0, 15, 0, hexc("5a5c5e")); hline(im, 0, 15, 15, hexc("5a5c5e"))
    add("vent", im)
    # туннель коллектора (кирпич тёмный)
    im = tile(); noise_fill(im, (0, 0, T, T), hexc("4c3a33"), 0.2, rnd)
    for y in range(0, 16, 4):
        hline(im, 0, 15, y, hexc("33261f"))
    add("tunnel_brick", im)
    # путь метро (шпалы)
    im = tile(); noise_fill(im, (0, 0, T, T), hexc("3a3836"), 0.2, rnd)
    rect(im, (0, 0, 15, 2), hexc("4d4b49"))
    for x in (2, 9):
        rect(im, (x, 0, x + 4, 1), hexc("5b4434"))
    hline(im, 0, 15, 0, hexc("8c8f93"))
    add("rail", im)
    # платформа метро: гранит с краем
    im = tile(); noise_fill(im, (0, 0, T, T), hexc("6a6560"), 0.12, rnd)
    rect(im, (0, 0, 15, 2), hexc("b2aca2")); hline(im, 0, 15, 3, hexc("d9b640"))
    add("platform", im)


# ---------- фоновые стены интерьеров ----------
def back_tiles():
    def wp(name, base, motif):
        for low in (False, True):
            im = tile(); noise_fill(im, (0, 0, T, T), base, 0.05, rnd)
            motif(im, base)
            if low:
                rect(im, (0, 12, 15, 15), hexc("5b4532")); hline(im, 0, 15, 12, hexc("7a5d43"))
            add(name + ("_low" if low else ""), im)

    def flowers(im, b):
        for (x, y) in ((3, 3), (11, 9)):
            c = mul(b, 0.72)
            put(im, x, y, c); put(im, x + 1, y, c); put(im, x, y + 1, c); put(im, x - 1, y, c); put(im, x, y - 1, c)
            put(im, x, y, mul(b, 1.15))

    def stripes(im, b):
        for x in (0, 1, 8, 9):
            vline(im, x, 0, 15, mul(b, 0.85))

    def rhomb(im, b):
        c = mul(b, 0.8)
        for i in range(8):
            put(im, 8 + i, i, c); put(im, 8 - i, i, c); put(im, i, 8 + i, c); put(im, 15 - i, 8 + i, c)

    def plain(im, b):
        pass

    wp("wp_flower", hexc("a39a78"), flowers)
    wp("wp_stripe", hexc("7f8a7a"), stripes)
    wp("wp_rhomb", hexc("8d7a73"), rhomb)
    wp("wp_blue", hexc("6f7c8c"), flowers)
    wp("wp_plain", hexc("9a9486"), plain)
    # кухонная плитка
    im = tile(); rect(im, (0, 0, 15, 15), hexc("b7bcb6"))
    for v in range(0, 16, 5):
        hline(im, 0, 15, v, hexc("8e938d")); vline(im, v, 0, 15, hexc("8e938d"))
    add("kitchen", im)
    # подъезд: низ зелёный, полоса, верх побелка
    im = tile(); noise_fill(im, (0, 0, T, T), GREEN_P, 0.08, rnd); add("pod_low", im)
    im = tile(); noise_fill(im, (0, 0, T, T), hexc("c4c2b6"), 0.06, rnd); rect(im, (0, 9, 15, 15), GREEN_P); hline(im, 0, 15, 8, hexc("2f4436"))
    for i in range(3):
        put(im, rnd.randrange(T), rnd.randrange(0, 8), hexc("7d7a70"))
    add("pod_mid", im)
    im = tile(); noise_fill(im, (0, 0, T, T), hexc("c4c2b6"), 0.06, rnd)
    if True:
        for i in range(2):
            put(im, rnd.randrange(T), rnd.randrange(T), hexc("a19f94"))
    add("pod_high", im)
    # офис
    im = tile(); noise_fill(im, (0, 0, T, T), hexc("8f979a"), 0.04, rnd); add("office", im)
    im = tile(); noise_fill(im, (0, 0, T, T), hexc("8f979a"), 0.04, rnd); rect(im, (0, 13, 15, 15), hexc("4b5256")); add("office_low", im)
    # подвал
    im = tile(); noise_fill(im, (0, 0, T, T), hexc("5b5a55"), 0.2, rnd)
    hline(im, 0, 15, 15, hexc("44433f"))
    add("basement", im)
    # магазин / кафе: светлая плитка
    im = tile(); noise_fill(im, (0, 0, T, T), hexc("a7a493"), 0.05, rnd)
    for v in (0, 8):
        hline(im, 0, 15, v, hexc("8c897a")); vline(im, v, 0, 15, hexc("8c897a"))
    add("shop", im)
    im = tile(); noise_fill(im, (0, 0, T, T), hexc("7d5b44"), 0.08, rnd)
    for v in range(0, 16, 4):
        vline(im, v, 0, 15, hexc("684a36"))
    add("cafe", im)
    # метро: мрамор
    im = tile(); noise_fill(im, (0, 0, T, T), hexc("b9b2a5"), 0.06, rnd)
    for i in range(4):
        x = rnd.randrange(T)
        put(im, x, rnd.randrange(T), hexc("958d80"))
    add("marble", im)
    im = tile(); noise_fill(im, (0, 0, T, T), hexc("4a3c34"), 0.1, rnd)
    for y in range(0, 16, 4):
        hline(im, 0, 15, y, hexc("3a2f29"))
    add("tunnel_back", im)
    # фон двора/переулка: дальний забор и стены
    im = tile(); noise_fill(im, (0, 0, T, T), hexc("5a5752"), 0.1, rnd)
    for y in range(0, 16, 4):
        hline(im, 0, 15, y, hexc("4a4743"))
    add("lane_back", im)


# ---------- фасады ----------
FAC = {
    "panel": (PANEL, "panel"),
    "brick": (BRICK, "brick"),
    "sbrick": (SBRICK, "brick"),
    "stucco": (STUCCO, "stucco"),
    "granite": (GRANITE, "granite"),
    "conc": (CONC, "panel"),
}


def facade_wall(c, kind, rowphase=0):
    im = tile(); noise_fill(im, (0, 0, T, T), c, 0.07, rnd)
    if kind == "brick":
        for y in range(rowphase % 4, 16, 4):
            hline(im, 0, 15, y, mul(c, 0.7))
            off = 0 if (y // 4) % 2 == 0 else 4
            for x in range(off, 16, 8):
                vline(im, x, y, min(15, y + 3), mul(c, 0.7))
    elif kind == "panel":
        hline(im, 0, 15, 15, mul(c, 0.72)); vline(im, 15, 0, 15, mul(c, 0.72))
        for i in range(3):
            put(im, rnd.randrange(T), rnd.randrange(T), mul(c, 0.85))
    elif kind == "stucco":
        for i in range(6):
            put(im, rnd.randrange(T), rnd.randrange(T), mul(c, 0.9))
    elif kind == "granite":
        for i in range(10):
            put(im, rnd.randrange(T), rnd.randrange(T), mul(c, 1.25 if i % 2 else 0.8))
        hline(im, 0, 15, 15, mul(c, 0.7))
    return im


def glass(im, box, alpha=120):
    x0, y0, x1, y1 = box
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            t = (x - x0 + (y - y0)) % 11
            hi = 1.3 if t in (0, 1) else 1.0
            im.putpixel((x, y), mul(GLASS, hi, alpha))


def facade_tiles():
    for key, (c, kind) in FAC.items():
        add("f_%s" % key, facade_wall(c, kind))
        # карниз (верх здания)
        im = facade_wall(c, kind); rect(im, (0, 10, 15, 15), mul(c, 0.7)); hline(im, 0, 15, 10, mul(c, 1.2)); add("f_%s_cornice" % key, im)
        # межэтажный пояс
        im = facade_wall(c, kind); hline(im, 0, 15, 13, mul(c, 0.75)); hline(im, 0, 15, 14, mul(c, 1.12)); add("f_%s_belt" % key, im)
        # цоколь
        im = tile(); noise_fill(im, (0, 0, T, T), mul(c, 0.62), 0.1, rnd); hline(im, 0, 15, 0, mul(c, 0.9)); add("f_%s_base" % key, im)
        # окно 2x2 тайла: tl tr bl br. Рама, стекло полупрозрачное, подоконник
        frame = mul(c, 0.5) if kind != "granite" else hexc("2e2c2b")
        if kind == "stucco":
            frame = hexc("e2dccb")
        win = new(32, 32)
        win.paste(facade_wall(c, kind), (0, 0)); win.paste(facade_wall(c, kind), (16, 0))
        win.paste(facade_wall(c, kind), (0, 16)); win.paste(facade_wall(c, kind), (16, 16))
        d = ImageDraw.Draw(win)
        if kind == "stucco":   # арочное окно сталинки с наличником
            d.rectangle([4, 3, 27, 29], fill=frame)
            d.ellipse([4, 0, 27, 12], fill=frame)
            win2 = win.copy()
            glass(win, (6, 5, 25, 27))
            for y in range(2, 6):
                for x in range(6, 26):
                    if (x - 15.5) ** 2 / 100 + (y - 6) ** 2 / 16 < 1:
                        win.putpixel((x, y), mul(GLASS, 1.1, 120))
            d.line([(15, 4), (15, 27)], fill=frame); d.line([(6, 13), (25, 13)], fill=frame)
            d.rectangle([3, 28, 28, 30], fill=mul(c, 1.15))
        elif kind == "granite":
            d.rectangle([1, 1, 30, 30], fill=frame)
            glass(win, (2, 2, 29, 29), 105)
            d.line([(15, 2), (15, 29)], fill=frame)
        else:
            d.rectangle([5, 4, 26, 27], fill=frame)
            glass(win, (6, 5, 25, 26))
            d.line([(15, 5), (15, 26)], fill=frame); d.line([(6, 12), (15, 12)], fill=frame)
            d.rectangle([4, 27, 27, 28], fill=mul(c, 1.2)); d.line([(4, 29), (27, 29)], fill=mul(c, 0.55))
        for i, (ox, oy) in enumerate(((0, 0), (16, 0), (0, 16), (16, 16))):
            add("f_%s_win%d" % (key, i), win.crop((ox, oy, ox + 16, oy + 16)))
    # витрина магазина 1 тайл (повторяется), верх и низ
    im = tile(); rect(im, (0, 0, 15, 15), hexc("2e2c2b")); glass(im, (1, 1, 14, 14), 95); add("shopwin", im)
    im = tile(); rect(im, (0, 0, 15, 15), hexc("2e2c2b")); glass(im, (1, 4, 14, 15), 95); hline(im, 0, 15, 2, hexc("494642")); add("shopwin_top", im)
    im = tile(); rect(im, (0, 0, 15, 15), hexc("3b3936")); glass(im, (1, 0, 14, 9), 95); hline(im, 0, 15, 11, hexc("57534d")); add("shopwin_bot", im)


def tiles_v21():
    """2.1: новые обои, ванная, вентшахта, лифт, нижний коллектор, вода, мостик между домами."""
    r2 = random.Random(21)

    def wp(name, base, motif):
        for low in (False, True):
            im = tile(); noise_fill(im, (0, 0, T, T), base, 0.05, r2)
            motif(im, base)
            if low:
                rect(im, (0, 12, 15, 15), hexc("5b4532")); hline(im, 0, 15, 12, hexc("7a5d43"))
            add(name + ("_low" if low else ""), im)

    def check(im, b):
        for y in range(16):
            for x in range(16):
                if (x // 4 + y // 4) % 2 == 0:
                    im.putpixel((x, y), mul(b, 0.9))

    def damask(im, b):
        c = mul(b, 1.25)
        for (x, y) in ((4, 4), (12, 12)):
            put(im, x, y - 2, c); put(im, x - 1, y - 1, c); put(im, x + 1, y - 1, c); put(im, x - 2, y, c); put(im, x + 2, y, c)
            put(im, x - 1, y + 1, c); put(im, x + 1, y + 1, c); put(im, x, y + 2, c); put(im, x, y, c)

    def ochre(im, b):
        for x in (3, 4, 11, 12):
            vline(im, x, 0, 15, mul(b, 1.12))
        for y in (2, 10):
            put(im, 7, y, mul(b, 0.75)); put(im, 15, y + 4, mul(b, 0.75))

    def kids(im, b):
        for (x, y, c) in ((3, 3, hexc("c94a3a")), (11, 6, hexc("3d6a9a")), (6, 11, hexc("d9b640")), (13, 13, hexc("4a8a4a"))):
            put(im, x, y, c); put(im, x + 1, y, c); put(im, x, y + 1, c); put(im, x + 1, y + 1, c)

    def dots(im, b):
        for y in range(1, 16, 4):
            for x in range(1 + (y // 4 % 2) * 2, 16, 4):
                put(im, x, y, mul(b, 0.78))

    wp("wp_green", hexc("6f8a6a"), dots)
    wp("wp_check", hexc("a08a6a"), check)
    wp("wp_damask", hexc("7a3a36"), damask)
    wp("wp_ochre", hexc("b0904a"), ochre)
    wp("wp_kids", hexc("c8c0a8"), kids)
    # ванная: голубая плитка
    im = tile(); rect(im, (0, 0, 15, 15), hexc("8fb0bc"))
    for v in range(0, 16, 4):
        hline(im, 0, 15, v, hexc("6f909c")); vline(im, v, 0, 15, hexc("6f909c"))
    add("bath", im)
    # прихожая: деревянная панель снизу, обои сверху
    im = tile(); noise_fill(im, (0, 0, T, T), hexc("8a7a5a"), 0.06, r2); add("hall", im)
    im = tile(); noise_fill(im, (0, 0, T, T), hexc("6b4e33"), 0.08, r2)
    for x in range(0, 16, 5):
        vline(im, x, 0, 15, hexc("503a26"))
    hline(im, 0, 15, 0, hexc("8a6a46")); add("hall_low", im)
    # вентшахта: короб за стеной
    im = tile(); noise_fill(im, (0, 0, T, T), hexc("4a5054"), 0.1, r2)
    vline(im, 2, 0, 15, hexc("6a7074")); vline(im, 13, 0, 15, hexc("343a3e"))
    for y in (3, 11):
        hline(im, 3, 12, y, hexc("3a4044"))
    add("duct_back", im)
    # шахта лифта: тёмная, тросы
    im = tile(); noise_fill(im, (0, 0, T, T), hexc("2e3032"), 0.12, r2)
    vline(im, 5, 0, 15, hexc("5a5c5e")); vline(im, 10, 0, 15, hexc("5a5c5e"))
    vline(im, 0, 0, 15, hexc("3e4042")); vline(im, 15, 0, 15, hexc("3e4042"))
    add("lift_shaft", im)
    # нижний коллектор: бетон с потёками
    im = tile(); noise_fill(im, (0, 0, T, T), hexc("4e504c"), 0.18, r2)
    for i in range(3):
        x = r2.randrange(T)
        vline(im, x, r2.randrange(4), r2.randrange(8, 16), hexc("3a3e38"))
    hline(im, 0, 15, 15, hexc("3e403c"))
    add("tunnel_conc", im)
    im = tile(); noise_fill(im, (0, 0, T, T), hexc("3e403c"), 0.15, r2)
    for y in range(0, 16, 4):
        hline(im, 0, 15, y, hexc("33352f"))
    for i in range(4):
        put(im, r2.randrange(T), r2.randrange(T), hexc("4a5a3a"))
    add("tunnel_conc_back", im)
    # мокрый кирпич верхнего коллектора (мох и потёки)
    im = tile(); noise_fill(im, (0, 0, T, T), hexc("4a3a33"), 0.2, r2)
    for y in range(0, 16, 4):
        hline(im, 0, 15, y, hexc("33261f"))
    for i in range(5):
        put(im, r2.randrange(T), r2.randrange(8, 16), hexc("4a5a34"))
    vline(im, 9, 4, 13, hexc("3a4a44"))
    add("tunnel_wet", im)
    # вода в канале (полупрозрачная)
    im = tile()
    for y in range(16):
        for x in range(16):
            a = 150 if y > 1 else 200
            c = hexc("2e4a50") if y > 1 else hexc("5a8088")
            if y == 0 and (x // 3) % 2 == 0:
                c = hexc("7aa0a8")
            im.putpixel((x, y), (c[0], c[1], c[2], a))
    add("water", im)
    # мостик между домами: пол, остеклённая стена, крыша
    im = tile(); rect(im, (0, 0, 15, 3), hexc("6a6e70")); rect(im, (0, 4, 15, 15), hexc("4a4e50"))
    for x in range(0, 16, 4):
        vline(im, x, 4, 15, hexc("3a3e40"))
    hline(im, 0, 15, 0, hexc("8a8e90"))
    add("bridge_floor", im)
    im = tile(); rect(im, (0, 0, 15, 15), hexc("3a4652"))
    glass(im, (1, 1, 14, 14), 140)
    vline(im, 0, 0, 15, hexc("4a4e50")); hline(im, 0, 15, 15, hexc("4a4e50"))
    add("bridge_glass", im)
    im = tile(); rect(im, (0, 8, 15, 15), hexc("5a5e60")); hline(im, 0, 15, 8, hexc("7a7e80")); hline(im, 0, 15, 15, hexc("3a3e40"))
    add("bridge_roof", im)
    im = tile(); noise_fill(im, (0, 0, T, T), hexc("6a6e70"), 0.06, r2); hline(im, 0, 15, 15, hexc("4a4e50"))
    add("bridge_wall", im)


def main(out):
    global tiles
    ground_tiles(); structure_tiles(); back_tiles(); facade_tiles(); tiles_v21()
    import detail_tiles
    tiles, DETAILED = detail_tiles.replace(tiles)
    with open(os.path.join(out, "tiles_detailed.txt"), "w") as f:
        f.write("\n".join(sorted(DETAILED)) + "\n")
    rows = (len(tiles) + COLS - 1) // COLS
    atlas = new(COLS * T, rows * T)
    with open(os.path.join(out, "tiles.txt"), "w") as f:
        for i, (nm, im) in enumerate(tiles):
            cx, cy = i % COLS, i // COLS
            atlas.paste(im, (cx * T, cy * T))
            f.write("%s %d %d\n" % (nm, cx, cy))
    atlas.save(os.path.join(out, "tiles.png"))
    print("tiles", len(tiles))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "../../assets")
