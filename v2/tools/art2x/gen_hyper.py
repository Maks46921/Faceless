"""Графика гиперплотного города (2.3), сразу в двойной плотности: ретро-футуризм без неона.

Дорисовывает к готовому атласу и предметам (assets/ после gen_tiles, gen_props, post2x):
тайлы галерей-улиц и секционных поясов фасада, двери экспресса и грузового лифта, доску почёта,
мусоропровод, эмалевые вывески с лампочками по краю, мозаику на торце, кабели, бельё.
Повторный запуск заменяет свои тайлы и предметы, остальное не трогает.

Запуск из tools/art2x: python3 gen_hyper.py ../../assets
"""
import os
import sys
import random

import numpy as np
from PIL import Image

from common import *
import k2
import gen_props as G
import post2x

HERE = os.path.dirname(os.path.abspath(__file__))
G.FONTS = os.path.join(HERE, "..", "..", "fonts")
rnd = random.Random(23)
D, outline, pixel_text = G.D, G.outline, G.pixel_text

CREAM = hexc("e6dcc2")
ENAMEL_R = hexc("a8322a")
ENAMEL_T = hexc("2f6b6a")
ENAMEL_B = hexc("2c4a6e")
BRASS = hexc("b8923e")
BRASS_D = hexc("7c6128")
STEEL = hexc("7b8287")
STEEL_D = hexc("4a5055")
BULB = hexc("f3e2a6")
YEL = hexc("d9b640")
INK = hexc("1c1b1a")

PROPS = []          # (имя, кадры)
TILES = []          # (имя, картинка 32×32)


def prop(nm, frames):
    PROPS.append((nm, frames))


def tile(nm, im):
    TILES.append((nm, im))


# ---------------- тайлы ----------------

def tiles():
    # пол галереи: терраццо с крошкой, кромка сверху
    im = new(16, 16); d = D(im)
    d.rectangle([0, 0, 15, 15], fill=hexc("8d8a80"))
    for _ in range(40):
        x, y = rnd.randrange(16), rnd.randrange(3, 16)
        d.point((x, y), fill=rnd.choice((hexc("b9b3a3"), hexc("6e6a62"), hexc("a3865a"))))
    d.rectangle([0, 0, 15, 2], fill=hexc("b2ad9f")); d.line([(0, 3), (15, 3)], fill=hexc("5d5a53"))
    d.rectangle([0, 12, 15, 15], fill=hexc("57544d"))
    tile("gallery_floor", im)
    # козырёк галереи: плита с заклёпками, снизу тёмная
    im = new(16, 16); d = D(im)
    d.rectangle([0, 0, 15, 15], fill=hexc("6b6f70"))
    d.rectangle([0, 0, 15, 3], fill=hexc("8c9192")); d.rectangle([0, 11, 15, 15], fill=hexc("3e4244"))
    for x in (3, 11):
        d.point((x, 7), fill=hexc("a7adae"))
    tile("gallery_roof", im)
    # стекло галереи: рама, импост, отблеск
    im = new(16, 16); d = D(im)
    d.rectangle([0, 0, 15, 15], fill=(58, 82, 96, 120))
    d.rectangle([0, 0, 1, 15], fill=STEEL_D); d.rectangle([14, 0, 15, 15], fill=STEEL_D)
    d.line([(0, 8), (15, 8)], fill=STEEL)
    d.line([(4, 2), (8, 6)], fill=(200, 220, 230, 90)); d.line([(5, 10), (8, 13)], fill=(200, 220, 230, 70))
    tile("gallery_glass", im)
    # нижний ряд: крашеный металлический парапет с полосой
    im = new(16, 16); d = D(im)
    d.rectangle([0, 0, 15, 15], fill=hexc("4d6a68"))
    d.rectangle([0, 0, 15, 1], fill=hexc("6f8e8b")); d.rectangle([0, 6, 15, 7], fill=CREAM)
    d.rectangle([0, 14, 15, 15], fill=hexc("2f403f"))
    for x in (2, 13):
        d.point((x, 11), fill=hexc("9db3b0"))
    tile("gallery_wall", im)
    # технический этаж мегакорпуса: пояс с жалюзи (вместо обычного пояса на узлах)
    for nm, base in (("f_sec_belt", hexc("6c6e6a")), ("f_sec_louver", hexc("5a5d5a"))):
        im = new(16, 16); d = D(im)
        d.rectangle([0, 0, 15, 15], fill=base)
        if nm == "f_sec_belt":
            d.rectangle([0, 0, 15, 2], fill=hexc("8f918b")); d.rectangle([0, 13, 15, 15], fill=hexc("44463f"))
            d.rectangle([0, 6, 15, 8], fill=ENAMEL_T)
        else:
            for y in range(1, 15, 3):
                d.line([(0, y), (15, y)], fill=hexc("3b3d3a")); d.line([(0, y + 1), (15, y + 1)], fill=hexc("7d807a"))
        tile(nm, im)


# ---------------- предметы ----------------

def bulbs_border(d, x0, y0, x1, y1, step=3):
    for x in range(x0, x1 + 1, step):
        d.point((x, y0), fill=BULB); d.point((x, y1), fill=BULB)
    for y in range(y0 + step, y1, step):
        d.point((x0, y), fill=BULB); d.point((x1, y), fill=BULB)


def enamel(nm, text, w, h, bg, fg=CREAM, size=7, frames=1):
    """эмалевая вывеска: скруглённая, с каймой и лампочками по краю (не неон)."""
    out = []
    for k in range(frames):
        im = new(w, h); d = D(im)
        d.rounded_rectangle([0, 0, w - 1, h - 1], radius=3, fill=hexc("2a2826"))
        d.rounded_rectangle([1, 1, w - 2, h - 2], radius=2, fill=bg)
        d.rounded_rectangle([3, 3, w - 4, h - 4], radius=1, outline=fg)
        bulbs_border(d, 2, 1, w - 3, h - 2)
        t = pixel_text(text[k] if isinstance(text, list) else text, size, fg, thr=100)
        tw, th = G.tsz(t)
        im.paste(t, ((w - tw) // 2, (h - th) // 2), t)
        out.append(im)
    prop(nm, out)


def props():
    # доска почёта: красное полотно, фото в рамках, золотая надпись
    im = new(40, 26); d = D(im)
    d.rectangle([0, 0, 39, 25], fill=hexc("6b4e33"))
    d.rectangle([1, 1, 38, 24], fill=ENAMEL_R)
    t = pixel_text("ДОСКА ПОЧЁТА", 5, YEL, thr=90)
    tw, th = G.tsz(t)
    im.paste(t, ((40 - tw) // 2, 2), t)
    for i in range(6):
        x = 4 + i * 6
        d.rectangle([x, 11, x + 4, 17], fill=hexc("d8d2c0")); d.rectangle([x + 1, 12, x + 3, 16], fill=hexc("6d6a62"))
        d.point((x + 2, 13), fill=hexc("c9b9a0"))
    d.rectangle([4, 20, 35, 21], fill=YEL)
    outline(im); prop("honorboard", [im])

    # дверь экспресса: латунный портал со скруглённым верхом, створки с полосой, табло
    im = new(28, 52); d = D(im)
    d.rounded_rectangle([0, 0, 27, 51], radius=8, fill=BRASS_D)
    d.rounded_rectangle([2, 2, 25, 51], radius=7, fill=BRASS)
    d.rectangle([4, 10, 23, 51], fill=hexc("8b9196"))
    d.line([(13, 10), (13, 51)], fill=hexc("4a5055")); d.line([(14, 10), (14, 51)], fill=hexc("b7bdc1"))
    for y in (24, 25):
        d.line([(4, y), (23, y)], fill=ENAMEL_T)
    d.ellipse([9, 3, 18, 8], fill=hexc("2a2826")); d.point((12, 5), fill=BULB); d.point((15, 5), fill=hexc("6a5a30"))
    outline(im); prop("express_door", [im])
    enamel("express_sign", "ЭКСПРЕСС", 34, 9, ENAMEL_B, size=6)

    # грузовой: стальная решётчатая дверь, жёлто-чёрная кромка, табличка
    im = new(30, 50); d = D(im)
    d.rectangle([0, 0, 29, 49], fill=STEEL_D)
    d.rectangle([2, 4, 27, 49], fill=hexc("5e6468"))
    for x in range(4, 27, 3):
        d.line([(x, 6), (x, 48)], fill=hexc("3a3f42"))
    for y in (16, 30, 44):
        d.line([(3, y), (26, y)], fill=STEEL)
    for x in range(0, 30, 4):
        d.polygon([(x, 0), (x + 2, 0), (x + 4, 3), (x + 2, 3)], fill=YEL)
    d.rectangle([7, 8, 22, 13], fill=CREAM)
    t = pixel_text("ГРУЗОВОЙ", 4, INK, thr=80)
    tw, th = G.tsz(t)
    im.paste(t, ((30 - tw) // 2, 8), t)
    outline(im); prop("freight_door", [im])

    # люк мусоропровода на стене
    im = new(14, 14); d = D(im)
    d.rectangle([0, 0, 13, 13], fill=STEEL_D)
    d.rectangle([1, 1, 12, 12], fill=hexc("6f777b")); d.polygon([(2, 4), (11, 4), (12, 11), (1, 11)], fill=hexc("5a6165"))
    d.rectangle([5, 2, 8, 3], fill=hexc("2a2d2f"))
    outline(im); prop("chute_hatch", [im])

    # бак под мусоропроводом
    im = new(30, 26); d = D(im)
    d.rectangle([1, 6, 28, 25], fill=hexc("4d5a4a")); d.rectangle([0, 3, 29, 7], fill=hexc("3a4438"))
    d.rectangle([12, 0, 17, 3], fill=STEEL_D)
    for x in (4, 25):
        d.rectangle([x, 8, x + 1, 24], fill=hexc("3a4438"))
    d.rectangle([8, 12, 21, 16], fill=CREAM)
    outline(im); prop("chute_bin", [im])

    # перила галереи (растягиваются по ширине): стойки и поручень
    im = new(64, 14); d = D(im)
    d.rectangle([0, 0, 63, 2], fill=hexc("8c9396")); d.line([(0, 0), (63, 0)], fill=hexc("c3c9cb"))
    for x in range(1, 64, 8):
        d.rectangle([x, 3, x + 1, 13], fill=STEEL_D)
    d.line([(0, 8), (63, 8)], fill=STEEL)
    prop("gallery_rail", [im])

    # киоск на галерее: круглый «Соки-воды» с куполом
    im = new(44, 46); d = D(im)
    d.rectangle([3, 16, 40, 45], fill=ENAMEL_T)
    d.pieslice([0, 0, 43, 26], 180, 360, fill=CREAM); d.rectangle([0, 12, 43, 16], fill=hexc("c9bc9a"))
    d.rectangle([6, 20, 37, 32], fill=(70, 96, 108, 255))
    for x in (11, 22, 33):
        d.line([(x, 20), (x, 32)], fill=hexc("2b4a4a"))
    d.rectangle([4, 34, 39, 36], fill=CREAM)
    for x in (9, 16, 23, 30):
        d.rectangle([x, 26, x + 3, 31], fill=hexc("c36a3a"))
    bulbs_border(d, 1, 13, 42, 15, 4)
    t = pixel_text("СОКИ-ВОДЫ", 5, ENAMEL_R, thr=90)
    tw, th = G.tsz(t)
    im.paste(t, ((44 - tw) // 2, 6), t)
    outline(im); prop("kiosk_gal", [im])

    # номер этажа галереи (эмаль), кадры по узлам
    enamel("sign_floor", ["1", "11", "21", "31", "41", "51"], 22, 14, ENAMEL_B, size=8, frames=6)

    # вывески низа: гастроном, ремонт часов, парикмахерская
    enamel("sign_gastronom", "ГАСТРОНОМ", 58, 12, ENAMEL_R, size=7)
    enamel("sign_clockfix", "РЕМОНТ ЧАСОВ", 62, 12, ENAMEL_T, size=6)
    enamel("sign_barber", "ПАРИКМАХЕРСКАЯ", 70, 12, ENAMEL_B, size=6)
    enamel("sign_section", ["СЕКЦИЯ 1", "СЕКЦИЯ 2", "СЕКЦИЯ 3", "СЕКЦИЯ 4", "СЕКЦИЯ 5", "СЕКЦИЯ 6"], 46, 11, hexc("3d3a36"), size=6, frames=6)

    # мозаика на торце: космонавт, ракета и солнце, смальта крупным зерном
    im = new(64, 96); d = D(im)
    d.rectangle([0, 0, 63, 95], fill=hexc("3e5f74"))
    r2 = random.Random(5)
    for _ in range(900):
        x, y = r2.randrange(64), r2.randrange(96)
        d.point((x, y), fill=r2.choice((hexc("3e5f74"), hexc("4a6d83"), hexc("355467"))))
    d.ellipse([38, 6, 58, 26], fill=hexc("d9a441")); d.ellipse([42, 10, 54, 22], fill=hexc("eac46a"))
    d.polygon([(10, 80), (16, 30), (22, 80)], fill=CREAM); d.polygon([(16, 22), (12, 32), (20, 32)], fill=ENAMEL_R)
    d.polygon([(8, 80), (12, 70), (12, 84)], fill=ENAMEL_R); d.polygon([(24, 80), (20, 70), (20, 84)], fill=ENAMEL_R)
    for i in range(4):
        d.ellipse([12 + i, 82 + i * 2, 20 - i, 86 + i * 2], fill=hexc("e7b45a"))
    d.ellipse([34, 40, 50, 56], fill=CREAM); d.ellipse([37, 43, 47, 53], fill=hexc("2c3d4a"))
    d.rectangle([33, 56, 51, 80], fill=CREAM); d.rectangle([28, 58, 33, 74], fill=CREAM); d.rectangle([51, 58, 56, 74], fill=CREAM)
    d.rectangle([35, 80, 41, 92], fill=CREAM); d.rectangle([43, 80, 49, 92], fill=CREAM)
    d.rectangle([38, 62, 46, 66], fill=ENAMEL_R)
    t = pixel_text("МИРУ — МИР", 6, CREAM, thr=90)
    tw, th = G.tsz(t)
    im.paste(t, ((64 - tw) // 2, 2), t)
    d.rectangle([0, 0, 63, 95], outline=hexc("2a2826"))
    prop("mosaic", [im])

    # кабели и трубы по фасаду (вертикальная полоса 16)
    im = new(10, 16); d = D(im)
    d.rectangle([1, 0, 3, 15], fill=hexc("2f3133")); d.rectangle([5, 0, 6, 15], fill=hexc("3d3f42"))
    d.rectangle([8, 0, 9, 15], fill=hexc("5a5048"))
    d.rectangle([0, 6, 9, 7], fill=hexc("6a6e70"))
    prop("cables", [im])

    # бельё на верёвке между окнами (растягивается)
    im = new(48, 16); d = D(im)
    d.line([(0, 2), (24, 5), (47, 2)], fill=hexc("bdb8aa"))
    cols = (hexc("d8d2c0"), hexc("a8322a"), hexc("4f6478"), hexc("e6dcc2"), hexc("6e8b5a"))
    for i, x in enumerate((5, 13, 22, 31, 40)):
        y = 3 + (3 if 10 < x < 38 else 1)
        d.rectangle([x, y, x + 5, y + 7 + (i % 2) * 2], fill=cols[i])
        d.point((x + 1, y), fill=hexc("8a8478")); d.point((x + 4, y), fill=hexc("8a8478"))
    prop("laundry", [im])

    # фонарь галереи: шар на кронштейне
    im = new(14, 14); d = D(im)
    d.rectangle([6, 0, 7, 4], fill=STEEL_D); d.ellipse([2, 4, 11, 13], fill=BULB); d.ellipse([4, 6, 8, 9], fill=hexc("fff6d6"))
    outline(im); prop("gallerylamp", [im])


# ---------------- сборка ----------------

def flat(im):
    """картинка 2× как numpy RGBA (метка k2 не мешает)."""
    return np.array(im.convert("RGBA"))


def main(A):
    tiles(); props()
    # предметы: PNG-полоса кадров, строка в props.txt (мировые размеры)
    lines = [l for l in open(os.path.join(A, "props.txt")).read().splitlines() if l.strip()]
    mine = {nm for nm, _ in PROPS}
    lines = [l for l in lines if l.split()[0] not in mine]
    for nm, frames in PROPS:
        w, h = frames[0].size[0] // k2.K, frames[0].size[1] // k2.K
        strip = Image.new("RGBA", (w * k2.K * len(frames), h * k2.K))
        for i, f in enumerate(frames):
            strip.paste(Image.fromarray(flat(f), "RGBA"), (i * w * k2.K, 0))
        a = post2x.shade(np.array(strip), seed=len(nm))
        Image.fromarray(a, "RGBA").save(os.path.join(A, "props", nm + ".png"))
        lines.append("%s %d %d %d" % (nm, w, h, len(frames)))
    open(os.path.join(A, "props.txt"), "w").write("\n".join(lines) + "\n")
    # тайлы: свои заменяются на месте, новые — в свободные клетки (атлас растёт вниз)
    T2 = 16 * k2.K
    at = Image.open(os.path.join(A, "tiles.png")).convert("RGBA")
    cols = at.size[0] // T2
    pos = {}
    for l in open(os.path.join(A, "tiles.txt")).read().splitlines():
        if l.strip():
            n, cx, cy = l.split()
            pos[n] = (int(cx), int(cy))
    used = set(pos.values())
    for nm, im in TILES:
        if nm not in pos:
            i = 0
            while (i % cols, i // cols) in used:
                i += 1
            pos[nm] = (i % cols, i // cols)
            used.add(pos[nm])
        cx, cy = pos[nm]
        need_h = (cy + 1) * T2
        if need_h > at.size[1]:
            big = Image.new("RGBA", (at.size[0], need_h))
            big.paste(at, (0, 0))
            at = big
        t = post2x.shade(flat(im), wrap=True, seed=cx * 7 + cy, grad=False)
        at.paste(Image.fromarray(t, "RGBA"), (cx * T2, cy * T2))
    at.save(os.path.join(A, "tiles.png"))
    with open(os.path.join(A, "tiles.txt"), "w") as f:
        for n, (cx, cy) in sorted(pos.items(), key=lambda e: (e[1][1], e[1][0])):
            f.write("%s %d %d\n" % (n, cx, cy))
    print("hyper: tiles", len(TILES), "props", len(PROPS))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "..", "assets"))
