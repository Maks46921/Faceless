"""Предметы мира: улица, интерьеры, транспорт, животные, дух. Каждый предмет — PNG-полоса кадров.

Выход: assets/props/<имя>.png и assets/props.txt (имя ширина_кадра высота кадров).
Опорная точка в игре — середина нижнего края кадра.
"""
import sys, os, random, math
from PIL import Image, ImageDraw, ImageFont
from common import *

rnd = random.Random(11)
OUT = "../../assets"
LIST = []
FONTS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "fonts")


def save(name, frames):
    w, h = frames[0].size
    strip = new(w * len(frames), h)
    for i, f in enumerate(frames):
        strip.paste(f, (i * w, 0))
    strip.save(os.path.join(OUT, "props", name + ".png"))
    LIST.append((name, w, h, len(frames)))


def D(im):
    return ImageDraw.Draw(im)


def outline(im, col=(24, 22, 22, 255)):
    """внешняя тёмная обводка по альфе (1 px)."""
    w, h = im.size
    src = im.copy().load()
    px = im.load()
    for y in range(h):
        for x in range(w):
            if src[x, y][3] > 0:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and src[nx, ny][3] > 200:
                    px[x, y] = col
                    break


def pixel_text(text, size=9, col=(230, 220, 190, 255), font="PT_Sans-Web-Bold.ttf", thr=110):
    f = ImageFont.truetype(os.path.join(FONTS, font), size)
    bb = f.getbbox(text)
    w, h = bb[2] - bb[0] + 2, bb[3] - bb[1] + 2
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).text((1 - bb[0], 1 - bb[1]), text, font=f, fill=255)
    out = new(w, h)
    px = out.load()
    mp = m.load()
    for y in range(h):
        for x in range(w):
            if mp[x, y] > thr:
                px[x, y] = col
    return out


# ================= улица =================

def street():
    # фонарь: столб 4 м, кадры выкл/вкл
    fr = []
    for on in (0, 1):
        im = new(24, 72); d = D(im)
        d.rectangle([11, 10, 12, 71], fill=hexc("3a3d40")); d.rectangle([10, 66, 13, 71], fill=hexc("2c2e30"))
        d.line([(12, 10), (19, 6)], fill=hexc("3a3d40"), width=2)
        d.rectangle([15, 5, 22, 8], fill=hexc("2f3133"))
        d.rectangle([16, 8, 21, 9], fill=hexc("f4dc9a") if on else hexc("6d6a5f"))
        fr.append(im)
    save("lamp", fr)
    # стенная лампа
    fr = []
    for on in (0, 1):
        im = new(10, 10); d = D(im)
        d.rectangle([0, 2, 2, 6], fill=hexc("2f3133")); d.rectangle([2, 3, 8, 5], fill=hexc("2f3133"))
        d.rectangle([4, 6, 8, 8], fill=hexc("f4dc9a") if on else hexc("6d6a5f"))
        fr.append(im)
    save("walllamp", fr)
    # таксофон (будка-полузакрытая): кадры обычный / звонит (трубка дрожит)
    fr = []
    for ring in (0, 1, 2):
        im = new(22, 46); d = D(im)
        d.rectangle([1, 2, 20, 45], fill=hexc("8c2f2a")); d.rectangle([1, 2, 20, 6], fill=hexc("6e2420"))
        d.rectangle([3, 8, 18, 40], fill=hexc("3b4752"))
        for y in range(10, 40, 2):
            d.line([(4, y), (17, y)], fill=hexc("43505b"))
        d.rectangle([8, 16, 15, 30], fill=hexc("5b5f61")); d.rectangle([9, 20, 14, 26], fill=hexc("2a2c2d"))
        off = (0, -1, 1)[ring]
        d.rectangle([7 + off, 14, 9 + off, 22], fill=hexc("1c1d1e"))
        t = pixel_text("ТАКСОФОН", 7, hexc("e9e2cf"), thr=90)
        im.paste(t, (max(0, (22 - t.size[0]) // 2), 0), t) if t.size[0] <= 22 else None
        outline(im)
        fr.append(im)
    save("payphone", fr)
    # киоск «Печать»
    im = new(48, 50); d = D(im)
    d.rectangle([2, 10, 45, 49], fill=hexc("5e7a8a")); d.rectangle([0, 6, 47, 12], fill=hexc("3f5563"))
    d.rectangle([5, 16, 42, 34], fill=hexc("2d3a42"))
    for i in range(6):
        x = 7 + i * 6
        d.rectangle([x, 20, x + 4, 32], fill=(hexc("cfc8b2"), hexc("a7442f"), hexc("d9b640"), hexc("b8b2a0"), hexc("6e8aa0"), hexc("cfc8b2"))[i])
    d.rectangle([4, 35, 43, 37], fill=hexc("2a3338"))
    t = pixel_text("ПЕЧАТЬ", 8, hexc("ece4cc"))
    im.paste(t, ((48 - t.size[0]) // 2, 3), t)
    outline(im); save("kiosk", [im])
    # остановка
    im = new(64, 48); d = D(im)
    d.rectangle([2, 4, 61, 7], fill=hexc("4c5560")); d.rectangle([3, 7, 4, 47], fill=hexc("3a3f44")); d.rectangle([58, 7, 59, 47], fill=hexc("3a3f44"))
    for x in range(6, 57):
        for y in range(9, 40):
            im.putpixel((x, y), (120, 140, 150, 70))
    d.rectangle([10, 34, 50, 36], fill=hexc("5a4836")); d.rectangle([12, 37, 13, 42], fill=hexc("3a3f44")); d.rectangle([47, 37, 48, 42], fill=hexc("3a3f44"))
    d.rectangle([52, 0, 60, 8], fill=hexc("e5dfcc")); d.text((54, 0), "A", fill=hexc("2a5a8a"))
    save("busstop", [im])
    # скамейка
    im = new(32, 14); d = D(im)
    d.rectangle([1, 6, 30, 7], fill=hexc("6b4e33")); d.rectangle([1, 1, 30, 3], fill=hexc("6b4e33"))
    d.rectangle([3, 8, 4, 13], fill=hexc("2b2b2b")); d.rectangle([27, 8, 28, 13], fill=hexc("2b2b2b")); d.rectangle([3, 3, 4, 6], fill=hexc("2b2b2b"))
    outline(im); save("bench", [im])
    # мусорный контейнер (можно спрятать тело): закрыт/открыт
    fr = []
    for op in (0, 1):
        im = new(36, 30); d = D(im)
        d.rectangle([2, 8, 33, 27], fill=hexc("3f5a46")); d.line([(2, 14), (33, 14)], fill=hexc("2f4636"))
        d.rectangle([6, 17, 29, 19], fill=hexc("c9a43b"))
        d.rectangle([4, 27, 7, 29], fill=hexc("1d1d1d")); d.rectangle([28, 27, 31, 29], fill=hexc("1d1d1d"))
        if op:
            d.polygon([(2, 8), (33, 8), (36, 0), (5, 0)], fill=hexc("2f4636"))
        else:
            d.rectangle([1, 5, 34, 8], fill=hexc("2f4636"))
        outline(im); fr.append(im)
    save("dumpster", fr)
    # урна (сдвигается)
    im = new(10, 14); d = D(im); d.rectangle([1, 2, 8, 13], fill=hexc("3d4a52")); d.rectangle([0, 1, 9, 2], fill=hexc("2c353b")); outline(im); save("urn", [im])
    # тополь и берёза
    for nm, trunk, leaf in (("tree", hexc("4b4035"), hexc("4d5a3a")), ("birch", hexc("cfcabd"), hexc("6d7a40"))):
        im = new(56, 96); d = D(im)
        d.rectangle([26, 40, 30, 95], fill=trunk)
        if nm == "birch":
            for y in range(44, 95, 7):
                d.line([(26, y), (28, y)], fill=hexc("2b2a28"))
        d.line([(28, 60), (16, 44)], fill=trunk, width=2); d.line([(28, 52), (40, 40)], fill=trunk, width=2)
        for i in range(70):
            a = rnd.random() * 6.283; r = rnd.random() ** 0.6 * 22
            x, y = 28 + math.cos(a) * r * 0.9, 30 + math.sin(a) * r * 1.2
            c = mul(leaf, 0.75 + rnd.random() * 0.5)
            d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=c)
        save(nm, [im])
    # гаражи (ряд)
    im = new(64, 40); d = D(im)
    d.rectangle([0, 6, 63, 39], fill=hexc("6a6c6b")); d.rectangle([0, 4, 63, 7], fill=hexc("4a4c4b"))
    for gx in (3, 34):
        d.rectangle([gx, 12, gx + 26, 39], fill=hexc("5b6b72"))
        d.line([(gx + 13, 12), (gx + 13, 39)], fill=hexc("44525a"))
        d.rectangle([gx + 11, 24, gx + 12, 26], fill=hexc("2a2a2a"))
    save("garages", [im])
    # трансформаторная будка
    im = new(36, 44); d = D(im)
    d.rectangle([1, 4, 34, 43], fill=hexc("9a958a")); d.rectangle([0, 1, 35, 5], fill=hexc("6d6a62"))
    d.rectangle([10, 16, 25, 43], fill=hexc("6e7a6e")); d.polygon([(26, 8), (32, 8), (29, 14)], fill=hexc("d9b640"))
    outline(im); save("transformer", [im])
    # памятник
    im = new(32, 72); d = D(im)
    d.rectangle([4, 50, 27, 71], fill=hexc("6f6c66")); d.rectangle([2, 48, 29, 51], fill=hexc("85827b"))
    d.rectangle([12, 22, 19, 48], fill=hexc("3c4a44")); d.ellipse([12, 13, 19, 21], fill=hexc("3c4a44"))
    d.line([(19, 26), (27, 14)], fill=hexc("3c4a44"), width=3)
    outline(im); save("monument", [im])
    # люк (вид сбоку — кромка) и решётка ливнёвки
    im = new(20, 4); d = D(im); d.rectangle([0, 1, 19, 3], fill=hexc("2c2c2c")); d.line([(1, 1), (18, 1)], fill=hexc("555")); save("manhole", [im])
    # светофор
    fr = []
    for st in range(3):
        im = new(10, 64); d = D(im)
        d.rectangle([4, 20, 5, 63], fill=hexc("2e3134")); d.rectangle([1, 0, 8, 21], fill=hexc("23272a"))
        for i, c in enumerate(("c23a2f", "d9a93a", "4f9a52")):
            on = (2 - st) == i
            d.ellipse([2, 1 + i * 7, 7, 6 + i * 7], fill=hexc(c) if on else mul(hexc(c), 0.3))
        fr.append(im)
    save("trafficlight", fr)
    # гидрант, ограждение, забор
    im = new(8, 14); d = D(im); d.rectangle([2, 2, 5, 13], fill=hexc("8c3a2e")); d.rectangle([1, 4, 6, 5], fill=hexc("6e2c23")); outline(im); save("hydrant", [im])
    im = new(16, 24); d = D(im)
    for x in range(1, 16, 4):
        d.rectangle([x, 2, x + 1, 23], fill=hexc("3d4245"))
    d.line([(0, 4), (15, 4)], fill=hexc("3d4245")); d.line([(0, 18), (15, 18)], fill=hexc("3d4245"))
    save("fence", [im])
    im = new(16, 40); d = D(im)
    d.rectangle([0, 0, 15, 39], fill=hexc("5e5546"))
    for x in range(0, 16, 4):
        d.line([(x, 0), (x, 39)], fill=hexc("4a4337"))
    save("fence_wood", [im])
    # водосточная труба (сегмент 16), лестница (сегмент 16)
    im = new(6, 16); d = D(im); d.rectangle([1, 0, 4, 15], fill=hexc("6f7577")); d.line([(1, 0), (1, 15)], fill=hexc("8d9496")); d.rectangle([0, 6, 5, 7], fill=hexc("4b5052")); save("pipe", [im])
    im = new(16, 16); d = D(im)
    d.rectangle([1, 0, 2, 15], fill=hexc("3c3f42")); d.rectangle([13, 0, 14, 15], fill=hexc("3c3f42"))
    for y in (3, 9, 15):
        d.line([(2, y), (13, y)], fill=hexc("55595c"))
    save("ladder", [im])
    # балкон с бельём (вариант 2)
    for v in range(2):
        im = new(48, 28); d = D(im)
        d.rectangle([0, 22, 47, 25], fill=hexc("7b7b75"))
        for x in range(1, 48, 4):
            d.line([(x, 12), (x, 22)], fill=hexc("4a4d50"))
        d.line([(0, 12), (47, 12)], fill=hexc("3b3e40"), width=2)
        if v == 1:
            d.line([(2, 2), (45, 2)], fill=hexc("2c2c2c"))
            for i, x in enumerate((6, 16, 27, 36)):
                c = (hexc("c8c3b5"), hexc("7d94a8"), hexc("a76b5c"), hexc("d5d0bf"))[i]
                d.rectangle([x, 3, x + 6, 10 + (i % 2) * 3], fill=c)
        save("balcony%d" % v, [im])
    # козырёк подъезда
    im = new(40, 8); d = D(im); d.rectangle([0, 0, 39, 4], fill=hexc("6d6e6a")); d.line([(0, 0), (39, 0)], fill=hexc("8d8e89")); d.rectangle([2, 4, 3, 7], fill=hexc("4a4b48")); d.rectangle([36, 4, 37, 7], fill=hexc("4a4b48")); save("canopy", [im])
    # горшок с цветком на подоконнике и кирпич (сбрасываются)
    im = new(8, 10); d = D(im); d.polygon([(1, 5), (6, 5), (5, 9), (2, 9)], fill=hexc("9a5034")); d.ellipse([0, 0, 7, 6], fill=hexc("4f6a3a")); d.point((3, 1), fill=hexc("c24a4a")); save("flowerpot", [im])
    # камера наблюдения
    fr = []
    for on in (0, 1):
        im = new(14, 10); d = D(im)
        d.rectangle([0, 0, 2, 5], fill=hexc("3a3d40")); d.polygon([(2, 2), (12, 4), (12, 8), (2, 6)], fill=hexc("c9c6bc"))
        d.point((11, 6), fill=hexc("d63a2f") if on else hexc("4a2a2a"))
        outline(im); fr.append(im)
    save("camera", fr)
    # антенна, вентшахта, будка выхода на крышу
    im = new(20, 28); d = D(im); d.line([(10, 27), (10, 2)], fill=hexc("3a3d40")); d.line([(2, 6), (18, 6)], fill=hexc("3a3d40")); d.line([(4, 12), (16, 12)], fill=hexc("3a3d40")); save("antenna", [im])
    im = new(16, 18); d = D(im); d.rectangle([2, 4, 13, 17], fill=hexc("7a7b77")); d.rectangle([0, 1, 15, 4], fill=hexc("5a5b57")); outline(im); save("vent_roof", [im])
    im = new(32, 40); d = D(im); d.rectangle([1, 6, 30, 39], fill=hexc("8a8880")); d.polygon([(0, 7), (31, 7), (31, 2), (0, 5)], fill=hexc("5a5b57")); d.rectangle([8, 14, 22, 39], fill=hexc("5f5547")); d.point((20, 27), fill=hexc("2a2a2a")); outline(im); save("roofexit", [im])
    # дымящая труба ТЭЦ для дальнего плана рисуется в игре, здесь только вывески
    signs = [("sign_apteka", "АПТЕКА", hexc("52c28c"), hexc("1c2a24")), ("sign_produkty", "ПРОДУКТЫ", hexc("e2c05a"), hexc("2a2418")),
             ("sign_cafe", "КАФЕ «ВСТРЕЧА»", hexc("e58f6a"), hexc("2a1d18")), ("sign_granit", "ГРАНИТ", hexc("d9d4c4"), hexc("2c2b29")),
             ("sign_metro", "М", hexc("e0473a"), hexc("1e1e1e")), ("sign_slava", "СЛАВА ТРУДУ", hexc("c9b48a"), None),
             ("sign_nii", "НИИ «СВЯЗЬ»", hexc("9fc0d8"), hexc("1d252c")), ("sign_school", "ШКОЛА № 7", hexc("d8d2c0"), hexc("323a40")),
             ("sign_univ", "УНИВЕРСАМ", hexc("e2c05a"), hexc("2a2418")), ("sign_hotel", "ГОСТИНИЦА", hexc("d0a0d8"), hexc("221a26")),
             ("sign_dom", "ДОМ БЫТА", hexc("d8d2c0"), hexc("2c2b29")), ("sign_bar", "ПИВО", hexc("e8b34a"), hexc("2a1d10"))]
    for nm, txt, c, bg in signs:
        t = pixel_text(txt, 10 if nm != "sign_metro" else 16, c, thr=100)
        w, h = t.size[0] + 6, t.size[1] + 4
        im = new(w, h)
        if bg:
            D(im).rectangle([0, 0, w - 1, h - 1], fill=bg)
            D(im).rectangle([0, 0, w - 1, h - 1], outline=mul(c, 0.5))
        im.paste(t, (3, 2), t)
        save(nm, [im])
    # граффити
    for nm, txt, c in (("graf_tsoy", "ЦОЙ ЖИВ", hexc("c9c3b5")), ("graf_seen", "ТЫ ЕГО ВИДЕЛ?", hexc("b04a3a"))):
        t = pixel_text(txt, 9, c, font="Caveat.ttf", thr=100)
        save(nm, [t])


# ================= транспорт =================

def car(body, w=64, h=26, kind="car"):
    im = new(w, h); d = D(im)
    if kind == "car":   # «Жигули»: силуэт седана
        d.polygon([(2, 12), (14, 11), (20, 3), (42, 3), (50, 11), (62, 13), (62, 21), (2, 21)], fill=body)
        d.polygon([(22, 5), (31, 5), (31, 11), (17, 11)], fill=hexc("2c3a44")); d.polygon([(33, 5), (41, 5), (47, 11), (33, 11)], fill=hexc("2c3a44"))
        d.line([(2, 15), (62, 15)], fill=mul(body, 0.75))
        d.rectangle([59, 13, 62, 15], fill=hexc("e8e2c8")); d.rectangle([2, 13, 4, 15], fill=hexc("a5322a"))
    elif kind == "police":
        d.polygon([(2, 12), (14, 11), (20, 3), (42, 3), (50, 11), (62, 13), (62, 21), (2, 21)], fill=hexc("d9d7cf"))
        d.rectangle([2, 14, 62, 16], fill=hexc("2e4f8a"))
        d.polygon([(22, 5), (31, 5), (31, 11), (17, 11)], fill=hexc("2c3a44")); d.polygon([(33, 5), (41, 5), (47, 11), (33, 11)], fill=hexc("2c3a44"))
        d.rectangle([28, 0, 35, 2], fill=hexc("3a6ad0"))
        d.rectangle([59, 13, 62, 15], fill=hexc("e8e2c8"))
    elif kind == "ambulance":
        d.polygon([(2, 2), (46, 2), (52, 10), (62, 12), (62, 21), (2, 21)], fill=hexc("e2ded2"))
        d.rectangle([47, 4, 52, 10], fill=hexc("2c3a44")); d.rectangle([2, 13, 62, 14], fill=hexc("b8342b"))
        d.rectangle([18, 6, 24, 8], fill=hexc("b8342b")); d.rectangle([20, 4, 22, 10], fill=hexc("b8342b"))
        d.rectangle([20, 0, 26, 1], fill=hexc("3a6ad0"))
    for wx in (14, 50):
        d.ellipse([wx - 5, h - 11, wx + 5, h - 1], fill=hexc("1d1d1f")); d.ellipse([wx - 2, h - 8, wx + 2, h - 4], fill=hexc("77797b"))
    outline(im)
    return im


def transport():
    for i, c in enumerate(("8a3a2e", "c8c2a8", "3d5e78", "5d6b4a", "2e2e33")):
        save("car%d" % i, [car(hexc(c))])
    save("police_car", [car(None, kind="police")])
    save("ambulance", [car(None, kind="ambulance")])
    # троллейбус
    im = new(160, 56); d = D(im)
    d.rounded_rectangle([2, 12, 157, 50], 6, fill=hexc("c8b46a")); d.rectangle([2, 38, 157, 42], fill=hexc("8a3a2e"))
    for x in range(12, 150, 18):
        d.rectangle([x, 17, x + 13, 32], fill=hexc("2c3a44"))
    d.rectangle([140, 17, 152, 46], fill=hexc("3a4651"))
    d.line([(40, 12), (90, 0)], fill=hexc("2a2a2a"), width=1); d.line([(46, 12), (96, 0)], fill=hexc("2a2a2a"), width=1)
    for wx in (30, 128):
        d.ellipse([wx - 7, 43, wx + 7, 55], fill=hexc("1d1d1f"))
    outline(im); save("trolley", [im])
    # вагон метро
    im = new(192, 48); d = D(im)
    d.rectangle([0, 4, 191, 42], fill=hexc("3d6a8a")); d.rectangle([0, 28, 191, 32], fill=hexc("d9d4c4"))
    for x in range(8, 184, 24):
        d.rectangle([x, 10, x + 14, 24], fill=hexc("e9e0b0"))
    for x in (40, 120):
        d.rectangle([x, 8, x + 16, 42], fill=hexc("2f5672"))
    for wx in (20, 60, 132, 172):
        d.ellipse([wx - 5, 39, wx + 5, 47], fill=hexc("1d1d1f"))
    save("metro_car", [im])


# ================= интерьер =================

def furniture():
    def s(nm, w, h, fn, ol=True):
        im = new(w, h); fn(D(im), im)
        if ol:
            outline(im)
        save(nm, [im])

    s("sofa", 40, 20, lambda d, im: (d.rectangle([1, 6, 38, 17], fill=hexc("6a4a4a")), d.rectangle([1, 1, 38, 8], fill=hexc("5c3e3e")),
                                    d.rectangle([0, 8, 4, 17], fill=hexc("4e3434")), d.rectangle([35, 8, 39, 17], fill=hexc("4e3434")),
                                    d.rectangle([3, 17, 5, 19], fill=hexc("2a2a2a")), d.rectangle([34, 17, 36, 19], fill=hexc("2a2a2a"))))
    s("armchair", 18, 20, lambda d, im: (d.rectangle([1, 1, 6, 17], fill=hexc("5a5f4a")), d.rectangle([1, 9, 16, 15], fill=hexc("6a705a")), d.rectangle([13, 8, 16, 17], fill=hexc("4e523f"))))
    s("table", 32, 16, lambda d, im: (d.rectangle([0, 0, 31, 2], fill=hexc("7a5a3c")), d.rectangle([2, 3, 3, 15], fill=hexc("5e442c")), d.rectangle([28, 3, 29, 15], fill=hexc("5e442c")),
                                     d.rectangle([4, -1, 27, 0], fill=hexc("d6d0c0"))))
    s("chair", 12, 22, lambda d, im: (d.rectangle([1, 0, 2, 21], fill=hexc("5e442c")), d.rectangle([1, 11, 10, 12], fill=hexc("7a5a3c")), d.rectangle([9, 12, 10, 21], fill=hexc("5e442c"))))
    s("stove", 20, 24, lambda d, im: (d.rectangle([0, 2, 19, 23], fill=hexc("d4d1c6")), d.rectangle([2, 10, 17, 20], fill=hexc("3a3a3a")), d.rectangle([0, 0, 19, 2], fill=hexc("b2afa4")),
                                     d.rectangle([4, -1 + 1, 8, 1], fill=hexc("2a2a2a")), d.rectangle([12, 0, 16, 1], fill=hexc("2a2a2a")), [d.point((3 + i * 4, 5), fill=hexc("2a2a2a")) for i in range(4)]))
    s("fridge", 20, 44, lambda d, im: (d.rounded_rectangle([0, 0, 19, 43], 3, fill=hexc("dcd9cf")), d.line([(0, 14), (19, 14)], fill=hexc("a8a59a")), d.rectangle([16, 4, 17, 11], fill=hexc("8d8a80")), d.rectangle([16, 18, 17, 30], fill=hexc("8d8a80"))))
    s("sink", 24, 26, lambda d, im: (d.rectangle([0, 8, 23, 25], fill=hexc("8a7458")), d.rectangle([0, 6, 23, 8], fill=hexc("c9c6bb")), d.line([(14, 0), (14, 6)], fill=hexc("8d9496")), d.line([(14, 0), (18, 0)], fill=hexc("8d9496")),
                                    d.line([(12, 9), (12, 25)], fill=hexc("6e5c45"))))
    s("cabinet", 24, 18, lambda d, im: (d.rectangle([0, 0, 23, 17], fill=hexc("8a7458")), d.line([(12, 0), (12, 17)], fill=hexc("6e5c45")), d.point((10, 9), fill=hexc("d9d4c4")), d.point((14, 9), fill=hexc("d9d4c4"))))
    s("bed", 44, 18, lambda d, im: (d.rectangle([0, 0, 3, 17], fill=hexc("5e442c")), d.rectangle([40, 5, 43, 17], fill=hexc("5e442c")), d.rectangle([3, 7, 40, 13], fill=hexc("c9c3b3")),
                                   d.rectangle([12, 6, 40, 12], fill=hexc("7d6a8a")), d.rectangle([4, 4, 11, 8], fill=hexc("e1dccf"))))
    s("wardrobe", 28, 52, lambda d, im: (d.rectangle([0, 0, 27, 51], fill=hexc("6b4e33")), d.line([(14, 2), (14, 49)], fill=hexc("503a26")), d.rectangle([0, 0, 27, 2], fill=hexc("503a26")),
                                        d.point((12, 26), fill=hexc("c9b48a")), d.point((16, 26), fill=hexc("c9b48a"))))
    fr = []
    for op in (0, 1):
        im = new(28, 52); d = D(im)
        d.rectangle([0, 0, 27, 51], fill=hexc("6b4e33")); d.rectangle([2, 3, 25, 49], fill=hexc("2a2119"))
        if op:
            d.rectangle([0, 0, 4, 51], fill=hexc("7a5a3c"))
        else:
            d.line([(14, 2), (14, 49)], fill=hexc("503a26")); d.rectangle([2, 3, 13, 49], fill=hexc("6b4e33")); d.rectangle([15, 3, 25, 49], fill=hexc("6b4e33")); d.line([(14, 2), (14, 49)], fill=hexc("3c2c1d"))
        outline(im); fr.append(im)
    save("closet", fr)
    s("tv", 20, 30, lambda d, im: (d.rectangle([2, 16, 17, 29], fill=hexc("5e442c")), d.rounded_rectangle([0, 0, 19, 16], 2, fill=hexc("3d3a36")), d.rectangle([3, 3, 14, 13], fill=hexc("6f8a9a")), d.point((17, 5), fill=hexc("c94a3a"))))
    s("shelf", 28, 44, lambda d, im: (d.rectangle([0, 0, 27, 43], fill=hexc("5e442c")), [d.rectangle([2, 2 + i * 10, 25, 10 + i * 10], fill=hexc("3a2a1c")) for i in range(4)],
                                      [d.rectangle([3 + j * 3, 4 + i * 10, 4 + j * 3, 10 + i * 10], fill=(hexc("8a3a2e"), hexc("3d5e78"), hexc("c9b48a"), hexc("5d6b4a"))[(i + j) % 4]) for i in range(4) for j in range(7)]))
    s("carpet", 40, 28, lambda d, im: (d.rectangle([0, 0, 39, 27], fill=hexc("7a2e2a")), d.rectangle([3, 3, 36, 24], outline=hexc("c9a46a")), d.ellipse([12, 6, 27, 21], outline=hexc("c9a46a")),
                                       d.rectangle([17, 11, 22, 16], fill=hexc("2e4a5a"))), ol=False)
    s("radiator", 20, 12, lambda d, im: (d.rectangle([0, 0, 19, 11], fill=hexc("c7c4b8")), [d.line([(x, 0), (x, 11)], fill=hexc("9a978c")) for x in range(2, 20, 3)]))
    s("desk", 36, 30, lambda d, im: (d.rectangle([0, 14, 35, 16], fill=hexc("7a6a5a")), d.rectangle([1, 17, 3, 29], fill=hexc("4a4038")), d.rectangle([24, 17, 34, 29], fill=hexc("5a4e44")),
                                    d.rectangle([8, 1, 22, 12], fill=hexc("c9c3b0")), d.rectangle([10, 3, 20, 10], fill=hexc("3a6a5a")), d.rectangle([13, 12, 17, 13], fill=hexc("a8a290"))))
    s("filing", 16, 34, lambda d, im: (d.rectangle([0, 0, 15, 33], fill=hexc("7a8287")), [d.line([(0, y), (15, y)], fill=hexc("5a6166")) for y in (11, 22)], [d.rectangle([6, y, 9, y + 1], fill=hexc("c9c6bc")) for y in (5, 16, 27)]))
    s("cooler", 12, 36, lambda d, im: (d.rectangle([1, 14, 10, 35], fill=hexc("d9d6cc")), d.rectangle([2, 0, 9, 13], fill=hexc("8fb4cc"))))
    s("turnstile", 20, 26, lambda d, im: (d.rectangle([0, 6, 7, 25], fill=hexc("7a7f84")), d.line([(7, 12), (19, 12)], fill=hexc("b8bcc0"), width=2), d.rectangle([1, 8, 6, 10], fill=hexc("4f9a52"))))
    s("guarddesk", 40, 26, lambda d, im: (d.rectangle([0, 6, 39, 25], fill=hexc("5a4e44")), d.rectangle([0, 4, 39, 6], fill=hexc("7a6a5a")), d.rectangle([24, -2 + 2, 34, 4], fill=hexc("3a3d40"))))
    fr = []
    for st in range(2):
        im = new(44, 30); d = D(im)
        d.rectangle([0, 18, 43, 29], fill=hexc("4a4e52"))
        for i in range(3):
            d.rectangle([2 + i * 14, 2, 13 + i * 14, 15], fill=hexc("2b2e30"))
            c = hexc("6a8f7a") if st == 0 else hexc("8a8a86")
            d.rectangle([4 + i * 14, 4, 11 + i * 14, 13], fill=c)
            if st == 0:
                d.line([(5 + i * 14, 6 + i), (10 + i * 14, 6 + i)], fill=hexc("a8d0b8"))
        outline(im); fr.append(im)
    save("console", fr)
    s("counter", 48, 22, lambda d, im: (d.rectangle([0, 4, 47, 21], fill=hexc("6a4e3a")), d.rectangle([0, 2, 47, 4], fill=hexc("a8a290")), d.line([(0, 12), (47, 12)], fill=hexc("5a3e2a"))))
    s("coffeemachine", 16, 18, lambda d, im: (d.rectangle([0, 0, 15, 17], fill=hexc("8d9496")), d.rectangle([3, 6, 12, 12], fill=hexc("2a2a2a")), d.rectangle([6, 13, 9, 15], fill=hexc("e1dccf")), d.point((12, 2), fill=hexc("c94a3a"))))
    s("cafetable", 20, 20, lambda d, im: (d.ellipse([0, 0, 19, 4], fill=hexc("c9c3b0")), d.rectangle([9, 3, 10, 18], fill=hexc("3a3d40")), d.rectangle([5, 18, 14, 19], fill=hexc("3a3d40")), d.rectangle([12, -2 + 1, 15, 1], fill=hexc("e9e2cf"))))
    s("shopshelf", 36, 44, lambda d, im: (d.rectangle([0, 0, 35, 43], fill=hexc("8a8a86")), [d.rectangle([1, 1 + i * 11, 34, 2 + i * 11], fill=hexc("5a5a56")) for i in range(4)],
                                         [d.rectangle([2 + j * 4, 4 + i * 11, 4 + j * 4, 11 + i * 11], fill=(hexc("c9a43b"), hexc("8a3a2e"), hexc("d9d4c4"), hexc("3d5e78"), hexc("6a8a4a"))[(i * 3 + j) % 5]) for i in range(4) for j in range(8)]))
    s("register", 16, 12, lambda d, im: (d.rectangle([0, 4, 15, 11], fill=hexc("3a3d40")), d.rectangle([2, 0, 13, 4], fill=hexc("5a5e60")), d.rectangle([4, 1, 11, 2], fill=hexc("6aa07a"))))
    s("mailboxes", 28, 16, lambda d, im: (d.rectangle([0, 0, 27, 15], fill=hexc("4a5e6a")), [d.rectangle([2 + i * 6, 2, 6 + i * 6, 6], outline=hexc("2f3d45")) for i in range(4)], [d.rectangle([2 + i * 6, 9, 6 + i * 6, 13], outline=hexc("2f3d45")) for i in range(4)]))
    s("ceilinglamp", 10, 14, lambda d, im: (d.line([(5, 0), (5, 8)], fill=hexc("2a2a2a")), d.pieslice([0, 6, 9, 16], 180, 360, fill=hexc("c9a46a"))), ol=False)
    s("bathtub", 40, 16, lambda d, im: (d.rounded_rectangle([0, 2, 39, 15], 4, fill=hexc("e1dccf")), d.rectangle([3, 2, 36, 5], fill=hexc("bcd0d8"))))
    s("pipes_wall", 32, 16, lambda d, im: (d.rectangle([0, 3, 31, 6], fill=hexc("6a5a4a")), d.rectangle([0, 10, 31, 12], fill=hexc("7a7f84")), d.rectangle([20, 2, 23, 7], fill=hexc("8a3a2e"))), ol=False)
    s("boiler", 24, 36, lambda d, im: (d.rounded_rectangle([0, 0, 23, 35], 6, fill=hexc("7a7f84")), d.rectangle([8, 10, 15, 14], fill=hexc("2a2a2a")), d.ellipse([9, 22, 14, 27], fill=hexc("c94a3a"))))
    s("crate", 16, 14, lambda d, im: (d.rectangle([0, 0, 15, 13], fill=hexc("8a6a42")), d.line([(0, 0), (15, 13)], fill=hexc("6a5032")), d.rectangle([0, 0, 15, 13], outline=hexc("6a5032"))))
    s("bucket", 10, 10, lambda d, im: (d.polygon([(1, 2), (8, 2), (7, 9), (2, 9)], fill=hexc("7a8287")), d.arc([1, -3, 8, 5], 180, 360, fill=hexc("3a3d40"))))
    # щиток: закрыт / дёрнут (рычаг вниз)
    fr = []
    for st in range(2):
        im = new(14, 18); d = D(im)
        d.rectangle([0, 0, 13, 17], fill=hexc("6e7a6e")); d.polygon([(4, 3), (9, 3), (6, 8)], fill=hexc("d9b640"))
        d.rectangle([5, 10, 8, 15], fill=hexc("2a2a2a"))
        d.rectangle([6, 10 if st == 0 else 13, 7, 12 if st == 0 else 15], fill=hexc("c94a3a"))
        outline(im); fr.append(im)
    save("fusebox", fr)
    # ящик с защёлкой: закрыт/открыт
    fr = []
    for st in range(2):
        im = new(18, 12); d = D(im)
        d.rectangle([0, 4, 17, 11], fill=hexc("5a6a5a"))
        if st:
            d.polygon([(0, 4), (17, 4), (14, 0), (3, 0)], fill=hexc("4a5a4a"))
        else:
            d.rectangle([0, 2, 17, 4], fill=hexc("4a5a4a")); d.rectangle([8, 3, 9, 6], fill=hexc("c9b48a"))
        outline(im); fr.append(im)
    save("lockbox", fr)
    # мелкие предметы
    s("key", 8, 4, lambda d, im: (d.ellipse([0, 0, 3, 3], fill=hexc("d9b640")), d.line([(3, 2), (7, 2)], fill=hexc("d9b640")), d.point((6, 3), fill=hexc("d9b640"))), ol=False)
    s("phone_item", 5, 8, lambda d, im: (d.rectangle([0, 0, 4, 7], fill=hexc("2a2c2e")), d.rectangle([1, 1, 3, 4], fill=hexc("6a8f9a"))), ol=False)
    s("clue", 10, 8, lambda d, im: (d.rectangle([0, 1, 9, 7], fill=hexc("e1dccf")), d.line([(2, 3), (7, 3)], fill=hexc("8a8a86")), d.line([(2, 5), (6, 5)], fill=hexc("8a8a86"))), ol=False)
    s("pills", 6, 8, lambda d, im: (d.rectangle([0, 2, 5, 7], fill=hexc("c9a46a")), d.rectangle([1, 0, 4, 2], fill=hexc("e1dccf"))), ol=False)
    s("photo", 10, 12, lambda d, im: (d.rectangle([0, 0, 9, 11], fill=hexc("6b4e33")), d.rectangle([2, 2, 7, 9], fill=hexc("b8b2a0")), d.ellipse([3, 3, 6, 6], fill=hexc("4a4038"))), ol=False)


def doors():
    # дверь квартиры 16x48: закрыта / открыта (вид сбоку: дверь в перегородке)
    fr = []
    for op in (0, 1):
        im = new(16, 48); d = D(im)
        if op:
            d.rectangle([0, 0, 2, 47], fill=hexc("3a2c1e")); d.rectangle([13, 0, 15, 47], fill=hexc("3a2c1e"))
            d.polygon([(2, 1), (8, 6), (8, 47), (2, 47)], fill=hexc("6b4e33"))
        else:
            d.rectangle([0, 0, 15, 47], fill=hexc("3a2c1e")); d.rectangle([2, 1, 13, 47], fill=hexc("6b4e33"))
            d.rectangle([4, 4, 11, 20], outline=hexc("5a4029")); d.rectangle([4, 24, 11, 44], outline=hexc("5a4029"))
            d.point((11, 26), fill=hexc("c9b48a")); d.rectangle([6, 10, 9, 11], fill=hexc("d9d4c4"))
        fr.append(im)
    save("door", fr)
    # железная дверь (служебная, подвал)
    fr = []
    for op in (0, 1):
        im = new(16, 48); d = D(im)
        if op:
            d.rectangle([0, 0, 2, 47], fill=hexc("2a2c2e")); d.rectangle([13, 0, 15, 47], fill=hexc("2a2c2e"))
            d.polygon([(2, 1), (8, 6), (8, 47), (2, 47)], fill=hexc("5a6166"))
        else:
            d.rectangle([0, 0, 15, 47], fill=hexc("2a2c2e")); d.rectangle([2, 1, 13, 47], fill=hexc("5a6166"))
            for y in (8, 24, 40):
                d.line([(3, y), (12, y)], fill=hexc("4a5055"))
            d.point((11, 26), fill=hexc("c9c6bc"))
        fr.append(im)
    save("door_metal", fr)
    # подъездная дверь на фасаде 32x48 и вход в магазин
    for nm, c in (("entrance", hexc("4a3a2c")), ("entrance_metal", hexc("3d4a52")), ("entrance_glass", hexc("2e2c2b"))):
        fr = []
        for op in (0, 1):
            im = new(32, 48); d = D(im)
            d.rectangle([0, 0, 31, 47], fill=hexc("2a2622"))
            if op:
                d.rectangle([3, 3, 28, 47], fill=hexc("151312"))
                d.polygon([(3, 3), (9, 6), (9, 47), (3, 47)], fill=c)
            else:
                d.rectangle([3, 3, 28, 47], fill=c)
                if nm == "entrance_glass":
                    for x in range(4, 28):
                        for y in range(4, 46):
                            im.putpixel((x, y), (58, 74, 88, 150))
                    d.line([(15, 3), (15, 47)], fill=c)
                else:
                    d.rectangle([6, 8, 25, 18], fill=mul(c, 0.8)); d.line([(15, 3), (15, 47)], fill=mul(c, 0.7))
                    d.rectangle([20, 26, 22, 27], fill=hexc("c9c6bc"))
                d.rectangle([26, 20, 28, 26], fill=hexc("3a3d40"))   # домофон
            fr.append(im)
        save(nm, fr)
    # лестничный марш: зигзаг на высоту этажа (80) шириной 64
    im = new(64, 80); d = D(im)
    st = hexc("7a7872"); edge = hexc("5a5852"); rail = hexc("3a3d40")
    # нижний марш: слева направо вверх до середины, площадка справа; верхний: справа налево
    for i in range(8):
        x = 2 + i * 6; y = 79 - i * 5
        d.rectangle([x, y - 5, x + 6, y], fill=st); d.line([(x, y - 5), (x + 6, y - 5)], fill=mul(st, 1.2))
    d.rectangle([50, 36, 63, 40], fill=edge)
    for i in range(8):
        x = 56 - i * 6; y = 39 - i * 5
        d.rectangle([x - 6, y - 5, x, y], fill=mul(st, 0.85)); d.line([(x - 6, y - 5), (x, y - 5)], fill=st)
    d.line([(4, 72), (52, 32)], fill=rail); d.line([(58, 32), (10, -6)], fill=rail)
    for x in range(8, 52, 8):
        d.line([(x, 72 - (x - 4) * 40 // 48), (x, 79 - (x - 4) * 40 // 48 - 4)], fill=rail)
    save("stairs", [im])
    # люк на крышу (в потолке)
    im = new(20, 6); d = D(im); d.rectangle([0, 0, 19, 5], fill=hexc("3a3d40")); d.rectangle([2, 1, 17, 4], fill=hexc("5a6166")); save("hatch", [im])
    # эскалатор метро (наклон)
    im = new(96, 96); d = D(im)
    d.polygon([(0, 95), (16, 95), (95, 16), (95, 0), (80, 0), (0, 80)], fill=hexc("4a4e52"))
    for i in range(0, 96, 6):
        d.line([(i, 95 - i), (i + 12, 95 - i)], fill=hexc("6a6e72"))
    d.line([(0, 72), (88, -16)], fill=hexc("b8a878"), width=2)
    save("escalator", [im])


def animals():
    # собака: 8 кадров 32x24: стоит 0-1, идёт 2-5, бежит 6-9, лает 10-11
    def dog(phase, mode):
        im = new(32, 24); d = D(im)
        body = hexc("5e5040"); dark = hexc("3e352a")
        yb = 12 if mode != "run" else 11
        d.rounded_rectangle([7, yb, 23, yb + 6], 2, fill=body)
        hy = yb - 4 if mode != "bark" else yb - 5
        d.rectangle([21, hy, 27, hy + 5], fill=body); d.rectangle([27, hy + 2, 29, hy + 4], fill=dark)
        d.polygon([(21, hy), (23, hy - 3), (24, hy)], fill=dark)
        if mode == "bark" and phase % 2:
            d.line([(27, hy + 5), (29, hy + 6)], fill=dark)
        d.line([(7, yb + 1), (3, yb - 3 + (phase % 2))], fill=body, width=2)
        legs = {"idle": [0, 0, 0, 0], "walk": [math.sin(phase * 1.57 + k * 1.57) * 3 for k in range(4)],
                "run": [math.sin(phase * 1.57 + k * 3.14) * 5 for k in range(4)], "bark": [0, 0, 0, 0]}[mode]
        for i, lx in enumerate((9, 12, 19, 22)):
            dx = legs[i]
            d.line([(lx, yb + 6), (lx + dx, 23)], fill=dark if i % 2 == 0 else body, width=2)
        outline(im)
        return im
    fr = [dog(0, "idle"), dog(1, "idle")] + [dog(i, "walk") for i in range(4)] + [dog(i, "run") for i in range(4)] + [dog(0, "bark"), dog(1, "bark")]
    save("dog", fr)
    # кошка 4 кадра 20x14
    fr = []
    for i in range(4):
        im = new(20, 14); d = D(im)
        d.rounded_rectangle([4, 5, 14, 9], 2, fill=hexc("3a3532")); d.rectangle([13, 2, 17, 6], fill=hexc("3a3532"))
        d.polygon([(13, 2), (14, 0), (15, 2)], fill=hexc("3a3532")); d.polygon([(16, 2), (17, 0), (17, 2)], fill=hexc("3a3532"))
        d.line([(4, 6), (1, 2 + i % 2)], fill=hexc("3a3532"))
        for j, lx in enumerate((5, 7, 11, 13)):
            d.line([(lx, 9), (lx + (1 if (i + j) % 2 else -1) * (i % 2), 13)], fill=hexc("2a2522"))
        d.point((16, 3), fill=hexc("c9d040"))
        fr.append(im)
    save("cat", fr)
    # голубь 4 кадра (клюёт 0-1, летит 2-3) 12x10
    fr = []
    for i in range(4):
        im = new(12, 10); d = D(im)
        if i < 2:
            d.ellipse([2, 4, 9, 8], fill=hexc("7d8088")); d.rectangle([7 + i, 2 + i * 2, 9 + i, 4 + i * 2], fill=hexc("6a6e78")); d.point((10 + i, 4 + i * 2), fill=hexc("c9a46a"))
            d.line([(5, 8), (5, 9)], fill=hexc("b0605a"))
        else:
            d.ellipse([3, 4, 9, 7], fill=hexc("7d8088"))
            if i == 2:
                d.polygon([(4, 5), (7, 5), (5, 0)], fill=hexc("969aa2"))
            else:
                d.polygon([(4, 6), (7, 6), (5, 9)], fill=hexc("969aa2"))
        fr.append(im)
    save("pigeon", fr)
    fr = []
    for i in range(2):
        im = new(14, 10); d = D(im)
        d.ellipse([3, 4, 10, 7], fill=hexc("1e1e22"))
        d.polygon([(4, 5), (8, 5), (5, 0 if i == 0 else 9)], fill=hexc("2a2a30"))
        d.point((11, 5), fill=hexc("2a2a30"))
        fr.append(im)
    save("crow", fr)


def spirit():
    # дух: сгусток с двумя золотыми глазами, 6 кадров 24x28 (колышется)
    fr = []
    for i in range(6):
        im = new(24, 28)
        px = im.load()
        ph = i / 6.0 * 6.283
        for y in range(28):
            for x in range(24):
                cx = 12 + math.sin(ph + y * 0.35) * (y / 28.0) * 2.5
                ry = (y - 10) / 12.0
                wdt = 7.5 * (1 - max(0, ry) ** 2 * 0.75) if ry > -0.8 else 0
                if y < 4:
                    wdt = 7.5 * math.sqrt(max(0, 1 - ((10 - y) / 7.0) ** 2))
                dx = abs(x - cx)
                if dx < wdt:
                    edge = dx / max(0.1, wdt)
                    a = int(235 * (1 - edge ** 3) * (1 - max(0, (y - 18) / 10.0)))
                    if a > 20:
                        k = 0.6 + 0.4 * (1 - edge)
                        px[x, y] = (int(28 * k), int(30 * k), int(40 * k), a)
        for ex in (9, 15):
            im.putpixel((ex, 9), hexc("d9b640")); im.putpixel((ex, 10), mul(hexc("d9b640"), 0.7))
        fr.append(im)
    save("spirit", fr)
    # клешня: 3 кадра 20x12 (открыта, тянет, схватила)
    fr = []
    for i in range(3):
        im = new(20, 12); d = D(im)
        d.line([(0, 6), (11, 6)], fill=hexc("1a1a22"), width=3)
        op = (4, 2, 0)[i]
        d.line([(11, 6), (18, 6 - op)], fill=hexc("23232c"), width=2)
        d.line([(11, 6), (18, 6 + op)], fill=hexc("23232c"), width=2)
        d.point((18, 6 - op), fill=hexc("d9b640"))
        fr.append(im)
    save("claw", fr)
    # кровь/лужа и след
    im = new(24, 4); d = D(im); d.ellipse([0, 0, 23, 3], fill=(110, 20, 20, 200)); save("blood", [im])


def main(out):
    global OUT
    OUT = out
    os.makedirs(os.path.join(out, "props"), exist_ok=True)
    street(); transport(); furniture(); doors(); animals(); spirit()
    import props_v21
    props_v21.run(sys.modules[__name__])
    with open(os.path.join(out, "props.txt"), "w") as f:
        for nm, w, h, n in LIST:
            f.write("%s %d %d %d\n" % (nm, w, h, n))
    print("props", len(LIST))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "../../assets")
