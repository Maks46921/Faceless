"""Рисование в двойной плотности: генераторы пишут координаты в мировых пикселях (как раньше),
а картинка получается вдвое больше. Заливки покрывают ту же площадь, тонкие линии и обводки
становятся вдвое тоньше, кривые и диагонали — вдвое глаже, шум и зерно — на мелком пикселе.

Картинки, созданные через common.new(), помечены атрибутом _k; для них ImageDraw.Draw,
putpixel, paste, crop, copy и load переводят координаты.
"""
from PIL import Image, ImageDraw, ImageFont

K = 2
_Draw = ImageDraw.Draw
_putpixel = Image.Image.putpixel
_paste = Image.Image.paste
_crop = Image.Image.crop
_copy = Image.Image.copy
_load = Image.Image.load


def mark(im):
    im._k = K
    return im


def is_k(im):
    return getattr(im, "_k", 1) == K


def S(v):
    return int(round(v * K))


def box(b):
    if len(b) == 2:
        (x0, y0), (x1, y1) = b
    else:
        x0, y0, x1, y1 = b
    return [S(x0), S(y0), S(x1) + K - 1, S(y1) + K - 1]


def pt(p):
    return (p[0] * K + (K - 1) / 2.0, p[1] * K + (K - 1) / 2.0)


def _pts(xy):
    xy = list(xy)
    if xy and not isinstance(xy[0], (tuple, list)):
        xy = [(xy[i], xy[i + 1]) for i in range(0, len(xy), 2)]
    return xy


class KDraw:
    def __init__(self, im):
        self.d = _Draw(im)
        self.im = im

    def rectangle(self, b, fill=None, outline=None, width=1):
        self.d.rectangle(box(b), fill=fill, outline=outline, width=width)

    def rounded_rectangle(self, b, radius=0, fill=None, outline=None, width=1, **kw):
        self.d.rounded_rectangle(box(b), radius=radius * K, fill=fill, outline=outline, width=width)

    def ellipse(self, b, fill=None, outline=None, width=1):
        self.d.ellipse(box(b), fill=fill, outline=outline, width=width)

    def arc(self, b, start, end, fill=None, width=1):
        self.d.arc(box(b), start, end, fill=fill, width=max(1, width * K - 1))

    def pieslice(self, b, start, end, fill=None, outline=None, width=1):
        self.d.pieslice(box(b), start, end, fill=fill, outline=outline, width=width)

    def chord(self, b, start, end, fill=None, outline=None, width=1):
        self.d.chord(box(b), start, end, fill=fill, outline=outline, width=width)

    def polygon(self, xy, fill=None, outline=None, width=1):
        p = _pts(xy)
        self.d.polygon([pt(q) for q in p], fill=fill, outline=outline)

    def point(self, xy, fill=None):
        for p in _pts(xy):
            self.d.rectangle(box((p[0], p[1], p[0], p[1])), fill=fill)

    def line(self, xy, fill=None, width=1, joint=None):
        p = _pts(xy)
        if len(p) == 1:
            p = p * 2
        for a, b in zip(p[:-1], p[1:]):
            (x0, y0), (x1, y1) = a, b
            if width <= 1:
                if y0 == y1:
                    xa, xb = sorted((x0, x1))
                    self.d.line([(S(xa), S(y0)), (S(xb) + K - 1, S(y0))], fill=fill)
                    continue
                if x0 == x1:
                    ya, yb = sorted((y0, y1))
                    self.d.line([(S(x0), S(ya)), (S(x0), S(yb) + K - 1)], fill=fill)
                    continue
                self.d.line([pt(a), pt(b)], fill=fill, width=1)
            else:
                w = width * K - 1
                self.d.line([pt(a), pt(b)], fill=fill, width=w)
                r = (w - 1) / 2.0
                if width >= 3:
                    for q in (a, b):
                        c = pt(q)
                        self.d.ellipse([c[0] - r, c[1] - r, c[0] + r, c[1] + r], fill=fill)

    def text(self, xy, text, fill=None, font=None, **kw):
        f2 = font
        if font is not None and hasattr(font, "path"):
            f2 = ImageFont.truetype(font.path, font.size * K)
        self.d.text((xy[0] * K, xy[1] * K), text, fill=fill, font=f2, **kw)

    def __getattr__(self, n):
        return getattr(self.d, n)


def Draw(im, mode=None):
    if is_k(im):
        return KDraw(im)
    return _Draw(im, mode) if mode else _Draw(im)


class KPix:
    def __init__(self, im):
        self.p = _load(im)

    def __getitem__(self, xy):
        return self.p[xy[0] * K, xy[1] * K]

    def __setitem__(self, xy, v):
        x, y = xy
        for dy in range(K):
            for dx in range(K):
                self.p[x * K + dx, y * K + dy] = v


def putpixel(self, xy, v):
    if is_k(self):
        x, y = xy
        for dy in range(K):
            for dx in range(K):
                X, Y = x * K + dx, y * K + dy
                if 0 <= X < self.size[0] and 0 <= Y < self.size[1]:
                    _putpixel(self, (X, Y), v)
    else:
        _putpixel(self, xy, v)


def paste(self, im, b=None, mask=None):
    if is_k(self) and b is not None and not isinstance(b, (int, float)) and len(b) in (2, 4) \
            and not isinstance(b[0], (tuple, list)):
        b = tuple(S(v) for v in b)
    _paste(self, im, b, mask)


def crop(self, b=None):
    if is_k(self) and b is not None:
        r = _crop(self, tuple(S(v) for v in b))
        return mark(r)
    return _crop(self, b)


def copy(self):
    r = _copy(self)
    if is_k(self):
        mark(r)
    return r


def load(self):
    if is_k(self) and getattr(self, "_kload", True):
        _load(self)
        return KPix(self)
    return _load(self)


def raw_load(im):
    """Доступ к мелким пикселям (для проходов по всей картинке)."""
    return _load(im)


def install():
    ImageDraw.Draw = Draw
    Image.Image.putpixel = putpixel
    Image.Image.paste = paste
    Image.Image.crop = crop
    Image.Image.copy = copy
