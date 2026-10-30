"""Предметы версии 2.1: обстановка квартир, подземелье, лифт, вентиляция.

Подключается из gen_props.main() последним, чтобы не сдвигать случайные числа старых предметов.
"""
import random
from common import *


def run(G):
    save, D, outline = G.save, G.D, G.outline
    rnd = random.Random(21)

    def s(nm, w, h, fn, ol=True):
        im = new(w, h); fn(D(im), im)
        if ol:
            outline(im)
        save(nm, [im])

    WOOD = hexc("6b4e33"); WOOD_D = hexc("503a26"); WOOD_L = hexc("8a6a46")
    # ---------- квартиры ----------
    def bookshelf(d, im):
        d.rectangle([0, 0, 27, 47], fill=WOOD)
        for i in range(4):
            y = 2 + i * 11
            d.rectangle([2, y, 25, y + 9], fill=hexc("2e2219"))
            x = 3
            while x < 24:
                bw = rnd.choice((1, 2, 2, 3))
                bh = rnd.randrange(6, 10)
                col = rnd.choice((hexc("8a3a2e"), hexc("3d5e78"), hexc("c9b48a"), hexc("5d6b4a"), hexc("6a4a6a"), hexc("b8b2a0")))
                d.rectangle([x, y + 9 - bh + 1, x + bw - 1, y + 9], fill=col)
                x += bw + (1 if rnd.random() < 0.3 else 0)
    s("bookshelf", 28, 48, bookshelf)

    def piano(d, im):
        d.rectangle([0, 2, 35, 29], fill=hexc("2a2220")); d.rectangle([0, 0, 35, 3], fill=hexc("3a302c"))
        d.rectangle([2, 14, 33, 16], fill=hexc("e8e2d2"))
        for x in range(3, 33, 3):
            d.line([(x, 14), (x, 15)], fill=hexc("1a1614"))
        d.rectangle([3, 26, 5, 29], fill=hexc("1a1614")); d.rectangle([30, 26, 32, 29], fill=hexc("1a1614"))
        d.rectangle([12, 4, 23, 10], fill=hexc("e1dccf")); d.line([(13, 6), (22, 6)], fill=hexc("6a6a6a")); d.line([(13, 8), (20, 8)], fill=hexc("6a6a6a"))
    s("piano", 36, 30, piano)

    def wallrug(d, im):
        d.rectangle([0, 0, 43, 27], fill=hexc("7a2a26"))
        d.rectangle([2, 2, 41, 25], outline=hexc("c9a46a"))
        d.rectangle([5, 5, 38, 22], outline=hexc("2e4a5a"))
        for cx in (12, 22, 32):
            d.polygon([(cx, 8), (cx + 5, 14), (cx, 20), (cx - 5, 14)], fill=hexc("c9a46a"))
            d.point((cx, 14), fill=hexc("2e4a5a"))
        for x in range(0, 44, 2):
            d.point((x, 27), fill=hexc("c9a46a"))
    s("wallrug", 44, 28, wallrug, ol=False)

    def clock(d, im):
        d.ellipse([0, 0, 11, 11], fill=hexc("6b4e33")); d.ellipse([1, 1, 10, 10], fill=hexc("e8e2d2"))
        d.line([(5, 5), (5, 2)], fill=hexc("1a1614")); d.line([(5, 5), (8, 6)], fill=hexc("1a1614"))
        d.rectangle([4, 12, 7, 19], fill=hexc("6b4e33")); d.ellipse([3, 16, 8, 21], fill=hexc("c9a43b"))
    s("clock", 12, 22, clock)

    def plant(d, im):
        d.polygon([(4, 18), (13, 18), (12, 25), (5, 25)], fill=hexc("9a5a3a"))
        for (x, y, r) in ((8, 6, 4), (4, 10, 3), (13, 9, 3), (9, 13, 4), (6, 3, 3), (12, 4, 2)):
            d.ellipse([x - r, y - r, x + r, y + r], fill=hexc("3f6a3a"))
            d.point((x - 1, y - 1), fill=hexc("5f8a4a"))
        d.line([(8, 12), (8, 18)], fill=hexc("4a3a26"))
    s("plant", 17, 26, plant)

    def aquarium(d, im):
        d.rectangle([1, 18, 22, 31], fill=WOOD_D); d.rectangle([3, 20, 20, 29], fill=WOOD)
        d.rectangle([0, 2, 23, 17], fill=hexc("2a3a3a"))
        for y in range(4, 17):
            for x in range(2, 22):
                im.putpixel((x, y), mul(hexc("4a8a98"), 0.8 + 0.25 * ((x + y) % 5 == 0)))
        d.rectangle([2, 14, 21, 16], fill=hexc("b8a878"))
        d.point((8, 8), fill=hexc("e08a2a")); d.point((9, 8), fill=hexc("e08a2a"))
        d.point((15, 11), fill=hexc("e0d040")); d.point((16, 11), fill=hexc("e0d040"))
        d.line([(5, 10), (5, 15)], fill=hexc("3f6a3a")); d.line([(18, 9), (18, 15)], fill=hexc("3f6a3a"))
        d.rectangle([0, 0, 23, 2], fill=hexc("3a3d40"))
    s("aquarium", 24, 32, aquarium)

    def sideboard(d, im):
        d.rectangle([0, 0, 39, 43], fill=WOOD)
        d.rectangle([2, 2, 37, 22], fill=hexc("3a3a3a"))
        for x in range(3, 37, 1):
            for y in range(3, 22):
                if (x + y) % 9 == 0:
                    im.putpixel((x, y), hexc("8a98a0"))
        for i in range(5):
            x = 5 + i * 7
            d.ellipse([x, 6, x + 4, 10], fill=hexc("e8e2d2")); d.rectangle([x + 1, 14, x + 3, 19], fill=hexc("c8d8e0"))
        d.line([(20, 2), (20, 22)], fill=WOOD_D)
        d.rectangle([2, 25, 37, 41], fill=WOOD_L); d.line([(20, 25), (20, 41)], fill=WOOD_D)
        d.point((18, 33), fill=hexc("d9c48a")); d.point((22, 33), fill=hexc("d9c48a"))
    s("sideboard", 40, 44, sideboard)

    def dresser(d, im):
        d.rectangle([0, 0, 25, 21], fill=WOOD)
        for i in range(3):
            y = 2 + i * 6
            d.rectangle([2, y, 23, y + 4], fill=WOOD_L); d.rectangle([11, y + 2, 14, y + 2], fill=hexc("d9c48a"))
        d.rectangle([1, 22, 3, 23], fill=WOOD_D); d.rectangle([22, 22, 24, 23], fill=WOOD_D)
    s("dresser", 26, 24, dresser)

    def floorlamp(d, im):
        d.polygon([(1, 10), (12, 10), (10, 0), (3, 0)], fill=hexc("c9a46a"))
        d.line([(6, 10), (6, 37)], fill=hexc("3a3d40")); d.rectangle([2, 37, 10, 39], fill=hexc("3a3d40"))
    s("floorlamp", 13, 40, floorlamp)

    def toilet(d, im):
        d.rectangle([9, 0, 15, 11], fill=hexc("e1dccf")); d.rectangle([0, 9, 13, 12], fill=hexc("e8e4d8"))
        d.polygon([(2, 12), (12, 12), (10, 19), (4, 19)], fill=hexc("e1dccf"))
        d.line([(15, 0), (15, -1)], fill=hexc("8d9496"))
    s("toilet", 16, 20, toilet)

    def washbasin(d, im):
        d.rectangle([2, 0, 13, 12], fill=hexc("9ab0b8")); d.rectangle([3, 1, 12, 11], fill=hexc("c8dce4"))
        d.line([(4, 3), (7, 6)], fill=hexc("e8f4f8"))
        d.rectangle([0, 15, 15, 18], fill=hexc("e8e4d8")); d.rectangle([6, 19, 9, 28], fill=hexc("d8d4c8"))
        d.line([(10, 13), (10, 15)], fill=hexc("8d9496"))
    s("washbasin", 16, 29, washbasin)

    def crib(d, im):
        d.rectangle([0, 0, 2, 21], fill=hexc("d8c8a0")); d.rectangle([29, 0, 31, 21], fill=hexc("d8c8a0"))
        d.rectangle([0, 14, 31, 16], fill=hexc("c8b890"))
        for x in range(4, 29, 3):
            d.line([(x, 3), (x, 14)], fill=hexc("d8c8a0"))
        d.line([(0, 3), (31, 3)], fill=hexc("d8c8a0"))
        d.rectangle([3, 11, 28, 13], fill=hexc("e8d8e8"))
    s("crib", 32, 22, crib)

    def poster(d, im):
        d.rectangle([0, 0, 15, 21], fill=hexc("c8b890"))
        d.rectangle([1, 1, 14, 12], fill=rnd.choice((hexc("a83a2e"), hexc("3a5a8a"), hexc("2e6a4a"))))
        d.ellipse([4, 3, 11, 10], fill=hexc("e8d8b8"))
        d.line([(2, 15), (13, 15)], fill=hexc("3a3030")); d.line([(2, 18), (10, 18)], fill=hexc("3a3030"))
    s("poster", 16, 22, poster)

    def guitar(d, im):
        d.rectangle([5, 0, 6, 14], fill=hexc("3a2a1c")); d.rectangle([4, 0, 7, 2], fill=hexc("2a1e14"))
        d.ellipse([1, 12, 10, 21], fill=hexc("a8682e")); d.ellipse([0, 18, 11, 29], fill=hexc("a8682e"))
        d.ellipse([4, 19, 7, 22], fill=hexc("2a1e14"))
    s("guitar", 12, 30, guitar)

    def radio(d, im):
        d.rounded_rectangle([0, 0, 19, 13], 2, fill=hexc("6b4e33"))
        d.rectangle([2, 2, 11, 11], fill=hexc("c9b48a"))
        for y in range(3, 11, 2):
            d.line([(3, y), (10, y)], fill=hexc("8a7a5a"))
        d.ellipse([13, 3, 17, 7], fill=hexc("2a2a2a")); d.rectangle([13, 9, 17, 10], fill=hexc("e8d080"))
    s("radio", 20, 14, radio)

    def sewing(d, im):
        d.rectangle([0, 14, 23, 16], fill=WOOD_L); d.rectangle([1, 17, 2, 27], fill=hexc("2a2a2a")); d.rectangle([21, 17, 22, 27], fill=hexc("2a2a2a"))
        d.rectangle([2, 25, 21, 26], fill=hexc("2a2a2a"))
        d.rectangle([3, 4, 19, 7], fill=hexc("1e1e22")); d.rectangle([3, 7, 6, 13], fill=hexc("1e1e22")); d.rectangle([16, 7, 19, 13], fill=hexc("1e1e22"))
        d.line([(5, 5), (17, 5)], fill=hexc("c9a43b"))
    s("sewing", 24, 28, sewing)

    def coatrack(d, im):
        d.line([(7, 2), (7, 41)], fill=hexc("4a3a26")); d.rectangle([3, 41, 11, 43], fill=hexc("4a3a26"))
        d.line([(2, 4), (12, 4)], fill=hexc("4a3a26"))
        d.polygon([(1, 5), (5, 5), (6, 22), (0, 22)], fill=rnd.choice((hexc("3a3a40"), hexc("5a4a3a"))))
        d.polygon([(9, 5), (13, 5), (14, 18), (8, 18)], fill=hexc("6a3a30"))
        d.ellipse([5, 0, 10, 4], fill=hexc("2a2a2a"))
    s("coatrack", 15, 44, coatrack)

    def washer(d, im):
        d.rectangle([0, 0, 17, 23], fill=hexc("d8d4c8")); d.rectangle([0, 0, 17, 3], fill=hexc("b8b4a8"))
        d.ellipse([3, 7, 14, 18], fill=hexc("8a98a0")); d.ellipse([5, 9, 12, 16], fill=hexc("a8c0c8"))
        d.point((14, 1), fill=hexc("c94a3a"))
    s("washer", 18, 24, washer)

    def picture(d, im):
        d.rectangle([0, 0, 19, 14], fill=hexc("a88a4a")); d.rectangle([2, 2, 17, 12], fill=hexc("8ab0c8"))
        d.polygon([(2, 12), (8, 6), (12, 9), (17, 5), (17, 12)], fill=hexc("4a6a3a"))
        d.ellipse([12, 3, 15, 6], fill=hexc("e8d080"))
    s("picture", 20, 15, picture)

    def portrait(d, im):
        d.rectangle([0, 0, 13, 17], fill=hexc("6b4e33")); d.rectangle([2, 2, 11, 15], fill=hexc("c8c0a8"))
        d.ellipse([4, 4, 9, 9], fill=hexc("6a5a4a")); d.rectangle([3, 10, 10, 15], fill=hexc("3a3a40"))
    s("portrait_frame", 14, 18, portrait)

    def calendar(d, im):
        d.rectangle([0, 0, 11, 15], fill=hexc("e8e4d8")); d.rectangle([0, 0, 11, 4], fill=hexc("a83a2e"))
        for y in range(6, 15, 2):
            for x in range(1, 11, 2):
                d.point((x, y), fill=hexc("6a6a6a"))
    s("calendar", 12, 16, calendar)

    def homedesk(d, im):
        d.rectangle([0, 12, 33, 14], fill=WOOD_L); d.rectangle([1, 15, 3, 27], fill=WOOD_D); d.rectangle([22, 15, 32, 27], fill=WOOD)
        d.rectangle([24, 17, 30, 20], outline=WOOD_D); d.rectangle([24, 22, 30, 25], outline=WOOD_D)
        d.line([(4, 11), (4, 3)], fill=hexc("2a5a3a")); d.polygon([(1, 3), (9, 3), (7, 0), (3, 0)], fill=hexc("2a6a3a"))
        d.rectangle([12, 9, 21, 11], fill=hexc("e1dccf")); d.rectangle([14, 7, 17, 9], fill=hexc("3a3d40"))
    s("homedesk", 34, 28, homedesk)

    def horse(d, im):
        d.arc([0, 10, 19, 18], 200, 340, fill=hexc("8a5a2e"), width=2)
        d.rectangle([5, 5, 14, 9], fill=hexc("c94a3a")); d.rectangle([13, 1, 17, 6], fill=hexc("c94a3a"))
        d.line([(6, 9), (4, 13)], fill=hexc("c94a3a")); d.line([(13, 9), (15, 13)], fill=hexc("c94a3a"))
        d.point((16, 2), fill=hexc("1a1a1a"))
    s("toyhorse", 20, 18, horse)

    def bicycle(d, im):
        for cx in (6, 25):
            d.ellipse([cx - 6, 8, cx + 6, 20], outline=hexc("2a2a2a"), width=1)
        d.line([(6, 14), (14, 8), (25, 14)], fill=hexc("3a5a8a")); d.line([(14, 8), (22, 8), (25, 14)], fill=hexc("3a5a8a"))
        d.line([(14, 8), (12, 4)], fill=hexc("2a2a2a")); d.rectangle([10, 3, 14, 4], fill=hexc("2a2a2a"))
        d.line([(22, 8), (23, 3)], fill=hexc("2a2a2a")); d.line([(21, 3), (25, 3)], fill=hexc("2a2a2a"))
    s("bicycle", 32, 21, bicycle)

    def shoes(d, im):
        d.rectangle([0, 6, 23, 7], fill=WOOD_D)
        for x in (1, 7, 13, 18):
            d.rectangle([x, 3, x + 4, 5], fill=rnd.choice((hexc("2a2220"), hexc("5a3a2a"), hexc("6a2a2a"))))
    s("shoerack", 24, 8, shoes, ol=False)

    def mirror(d, im):
        d.ellipse([0, 0, 11, 17], fill=hexc("6b4e33")); d.ellipse([1, 1, 10, 16], fill=hexc("b8ccd4")); d.line([(3, 4), (6, 9)], fill=hexc("e8f4f8"))
    s("mirror", 12, 18, mirror)

    def iron(d, im):
        d.polygon([(0, 8), (30, 8), (27, 11), (0, 11)], fill=hexc("c8c4b8"))
        d.line([(8, 11), (20, 23)], fill=hexc("4a4a4a")); d.line([(20, 11), (8, 23)], fill=hexc("4a4a4a"))
        d.polygon([(18, 4), (26, 4), (26, 7), (16, 7)], fill=hexc("7a8287"))
    s("ironboard", 31, 24, iron)

    def stool(d, im):
        d.rectangle([0, 0, 11, 2], fill=WOOD_L); d.line([(1, 3), (1, 13)], fill=WOOD_D); d.line([(10, 3), (10, 13)], fill=WOOD_D)
    s("stool", 12, 14, stool)

    def gasheater(d, im):
        d.rectangle([0, 0, 13, 19], fill=hexc("e1dccf")); d.rectangle([3, 12, 10, 16], fill=hexc("3a3a3a")); d.point((6, 14), fill=hexc("4a8ae0"))
        d.line([(7, 0), (7, -1)], fill=hexc("8d9496")); d.rectangle([5, 3, 8, 5], fill=hexc("8d9496"))
    s("gasheater", 14, 20, gasheater)

    def fishtank_rods(d, im):
        for i, x in enumerate((2, 5, 8)):
            d.line([(x, 0), (x + 1, 37)], fill=hexc("5a4a2a"))
        d.rectangle([0, 30, 11, 37], fill=hexc("4a5a3a"))
    s("rods", 12, 38, fishtank_rods)

    def chess(d, im):
        d.rectangle([0, 6, 17, 7], fill=WOOD_L); d.line([(2, 8), (2, 15)], fill=WOOD_D); d.line([(15, 8), (15, 15)], fill=WOOD_D)
        for x in range(2, 16, 2):
            d.point((x, 5), fill=hexc("e8e2d2") if x < 9 else hexc("2a2220")); d.point((x, 4), fill=hexc("e8e2d2") if x < 9 else hexc("2a2220"))
    s("chesstable", 18, 16, chess)

    # ---------- лифт, вентиляция, мостик ----------
    fr = []
    for op in range(3):
        im = new(28, 50); d = D(im)
        d.rectangle([0, 0, 27, 49], fill=hexc("4a4e52")); d.rectangle([2, 6, 25, 49], fill=hexc("2a2c2e"))
        gap = (0, 6, 11)[op]
        d.rectangle([2, 6, 13 - gap, 49], fill=hexc("8a8478")); d.rectangle([14 + gap, 6, 25, 49], fill=hexc("8a8478"))
        if op < 2:
            d.line([(13 - gap, 6), (13 - gap, 49)], fill=hexc("5a564e"))
        d.rectangle([9, 1, 18, 4], fill=hexc("1a1a1a")); d.point((13, 2), fill=hexc("e0a030")); d.point((14, 2), fill=hexc("e0a030"))
        outline(im); fr.append(im)
    save("lift_door", fr)
    s("lift_panel", 6, 10, lambda d, im: (d.rectangle([0, 0, 5, 9], fill=hexc("7a7f84")), d.ellipse([1, 1, 4, 4], fill=hexc("e8e2d2")), d.ellipse([1, 5, 4, 8], fill=hexc("e8e2d2"))))
    s("lift_cabin", 26, 46, lambda d, im: (d.rectangle([0, 0, 25, 45], fill=hexc("6a5a46")), d.rectangle([2, 2, 23, 43], fill=hexc("8a7a5e")),
                                           d.rectangle([3, 30, 22, 31], fill=hexc("5a4a3a")), d.line([(13, -6), (13, 0)], fill=hexc("3a3a3a"))))
    s("broken_sign", 22, 10, lambda d, im: (d.rectangle([0, 0, 21, 9], fill=hexc("e8e4d8")), d.rectangle([0, 0, 21, 9], outline=hexc("a83a2e")),
                                            d.line([(3, 3), (18, 3)], fill=hexc("3a3030")), d.line([(3, 6), (14, 6)], fill=hexc("3a3030"))), ol=False)
    s("vent_grille", 14, 8, lambda d, im: (d.rectangle([0, 0, 13, 7], fill=hexc("8a8e90")), [d.line([(2, y), (11, y)], fill=hexc("3a3e40")) for y in (2, 4, 6)]), ol=False)
    s("duct", 16, 16, lambda d, im: (d.rectangle([2, 0, 13, 15], fill=hexc("6a7074")), d.line([(2, 0), (2, 15)], fill=hexc("8a9094")),
                                     d.line([(13, 0), (13, 15)], fill=hexc("4a5054")), d.line([(2, 15), (13, 15)], fill=hexc("4a5054"))), ol=False)
    s("roofvent_big", 20, 22, lambda d, im: (d.rectangle([2, 6, 17, 21], fill=hexc("7a7f84")), d.rectangle([0, 2, 19, 6], fill=hexc("5a5f64")),
                                             [d.line([(4, y), (15, y)], fill=hexc("3a3e40")) for y in (9, 12, 15, 18)]))
    # ---------- подземелье ----------
    fr = []
    for op in (0, 1):
        im = new(16, 48); d = D(im)
        d.rectangle([0, 0, 1, 47], fill=hexc("3a3c3e")); d.rectangle([14, 0, 15, 47], fill=hexc("3a3c3e")); d.rectangle([0, 0, 15, 1], fill=hexc("3a3c3e"))
        if op:
            d.polygon([(2, 2), (7, 5), (7, 47), (2, 47)], fill=hexc("4a4c4e"))
            for y in range(6, 46, 4):
                d.line([(2, y), (7, y)], fill=hexc("2a2c2e"))
        else:
            for x in range(3, 14, 3):
                d.line([(x, 2), (x, 47)], fill=hexc("5a5c5e"))
            for y in (10, 24, 38):
                d.line([(2, y), (13, y)], fill=hexc("5a5c5e"))
            d.rectangle([10, 22, 12, 27], fill=hexc("8a7a3a"))
        fr.append(im)
    save("grate_door", fr)
    s("valve", 14, 14, lambda d, im: (d.ellipse([0, 0, 13, 13], outline=hexc("a83a2e"), width=2), d.line([(7, 0), (7, 13)], fill=hexc("a83a2e")),
                                      d.line([(0, 7), (13, 7)], fill=hexc("a83a2e")), d.ellipse([5, 5, 8, 8], fill=hexc("6a2a20"))), ol=False)
    s("sign_coll", 34, 10, lambda d, im: (d.rectangle([0, 0, 33, 9], fill=hexc("2e5a8a")), d.rectangle([1, 1, 32, 8], outline=hexc("e8e4d8")),
                                          d.line([(4, 4), (22, 4)], fill=hexc("e8e4d8")), d.line([(4, 6), (16, 6)], fill=hexc("e8e4d8")),
                                          d.polygon([(25, 3), (30, 5), (25, 7)], fill=hexc("e8e4d8"))), ol=False)
    s("puddle", 28, 3, lambda d, im: d.ellipse([0, 0, 27, 2], fill=(70, 90, 100, 170)), ol=False)
    s("rubble", 22, 8, lambda d, im: [d.rectangle([x, 8 - h, x + w, 7], fill=c) for (x, w, h, c) in
                                       ((0, 5, 3, hexc("6a6560")), (4, 6, 5, hexc("5a5550")), (9, 4, 7, hexc("7a7570")), (13, 7, 4, hexc("5f5a55")), (18, 3, 2, hexc("6a6560")))])
    s("mattress", 40, 9, lambda d, im: (d.rectangle([0, 3, 39, 8], fill=hexc("6a6a4a")), d.line([(0, 5), (39, 5)], fill=hexc("5a5a3a")),
                                        d.rectangle([2, 0, 12, 4], fill=hexc("5a4a3a")), d.rectangle([20, 1, 34, 3], fill=hexc("4a3a5a"))))
    s("pump", 34, 30, lambda d, im: (d.rectangle([2, 10, 31, 29], fill=hexc("4a6a5a")), d.ellipse([4, 2, 18, 16], fill=hexc("5a7a6a")),
                                     d.rectangle([22, 4, 26, 10], fill=hexc("7a7f84")), d.rectangle([0, 24, 33, 29], fill=hexc("3a3e40")),
                                     d.ellipse([8, 6, 14, 12], fill=hexc("2a3a32"))))
    s("pipes_big", 48, 14, lambda d, im: (d.rectangle([0, 1, 47, 6], fill=hexc("5a4a3a")), d.rectangle([0, 9, 47, 12], fill=hexc("6a7074")),
                                          d.rectangle([14, 0, 17, 7], fill=hexc("4a3a2a")), d.rectangle([38, 8, 40, 13], fill=hexc("4a5054"))), ol=False)
    s("arrow_sign", 14, 8, lambda d, im: (d.rectangle([0, 0, 13, 7], fill=hexc("d8d0b0")), d.polygon([(2, 2), (8, 2), (8, 0), (12, 4), (8, 7), (8, 5), (2, 5)], fill=hexc("a83a2e"))), ol=False)
    s("barrel", 14, 18, lambda d, im: (d.rectangle([0, 0, 13, 17], fill=hexc("3a5a4a")), d.line([(0, 4), (13, 4)], fill=hexc("2a3a32")), d.line([(0, 13), (13, 13)], fill=hexc("2a3a32"))))
    s("bottles", 14, 8, lambda d, im: [d.rectangle([x, 1 + (x % 3), x + 2, 7], fill=hexc("3a6a3a") if x % 2 else hexc("6a5a3a")) for x in range(0, 13, 3)], ol=False)
    s("campfire", 16, 10, lambda d, im: (d.line([(1, 9), (14, 6)], fill=hexc("4a3a26"), width=2), d.line([(1, 6), (14, 9)], fill=hexc("4a3a26"), width=2),
                                        d.polygon([(4, 7), (8, 0), (12, 7)], fill=hexc("e08a2a")), d.polygon([(6, 7), (8, 3), (10, 7)], fill=hexc("f0d050"))), ol=False)
    fr = []
    for i in range(4):
        im = new(16, 26); d = D(im)
        for k in range(3 + i):
            y = 24 - k * 6 - i * 2
            r = 2 + k + i // 2
            a = max(30, 160 - k * 30 - i * 15)
            d.ellipse([8 - r + (k % 2), y - r, 8 + r + (k % 2), y + r], fill=(220, 225, 230, a))
        fr.append(im)
    save("steam", fr)
    fr = []
    for i in range(2):
        im = new(12, 6); d = D(im)
        d.ellipse([2, 1, 9, 5], fill=hexc("4a4038")); d.ellipse([8, 1, 11, 4], fill=hexc("4a4038"))
        d.line([(0, 3 + i), (2, 3)], fill=hexc("6a5a50")); d.point((10, 2), fill=hexc("c94a3a"))
        d.line([(4, 5), (4 + i, 5)], fill=hexc("3a3028")); d.line([(7, 5), (7 - i, 5)], fill=hexc("3a3028"))
        fr.append(im)
    save("rat", fr)
    s("drain_grate", 18, 4, lambda d, im: (d.rectangle([0, 0, 17, 3], fill=hexc("2a2c2e")), [d.line([(x, 0), (x, 3)], fill=hexc("5a5c5e")) for x in range(1, 18, 3)]), ol=False)
    s("ladder_iron", 14, 16, lambda d, im: (d.line([(1, 0), (1, 15)], fill=hexc("5a5c5e")), d.line([(12, 0), (12, 15)], fill=hexc("5a5c5e")),
                                            d.line([(1, 4), (12, 4)], fill=hexc("7a7c7e")), d.line([(1, 12), (12, 12)], fill=hexc("7a7c7e"))), ol=False)
    s("srv_door", 18, 48, lambda d, im: (d.rectangle([0, 0, 17, 47], fill=hexc("3a3c3e")), d.rectangle([2, 2, 15, 47], fill=hexc("6a5a3a")),
                                         d.rectangle([4, 8, 13, 14], fill=hexc("e8e4d8")), d.line([(5, 10), (12, 10)], fill=hexc("a83a2e")), d.line([(5, 12), (10, 12)], fill=hexc("3a3030")),
                                         d.point((13, 28), fill=hexc("c9b48a"))))
