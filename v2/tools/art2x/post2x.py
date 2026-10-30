"""Проход объёма для графики двойной плотности: свет сверху слева.

Для каждой плоской области цвета: светлая кромка сверху/слева, тень снизу/справа,
падающая тень под выступами, лёгкий вертикальный градиент и зерно на мелком пикселе.
Тайлы обрабатываются по одному с заворотом краёв, чтобы стыки не было видно.
Запуск: python3 post2x.py <папка assets 2x>  (перезаписывает tiles.png и props/*.png)
"""
import sys, os
import numpy as np
from PIL import Image

T2 = 32


def lum(a):
    return a[..., 0] * 0.3 + a[..., 1] * 0.59 + a[..., 2] * 0.11


def sh(a, dx, dy, wrap):
    """значение соседа в направлении (dx, dy)"""
    if wrap:
        return np.roll(np.roll(a, -dy, 0), -dx, 1)
    h, w = a.shape[:2]
    out = np.zeros_like(a)
    ys = slice(max(0, dy), h + min(0, dy)); yd = slice(max(0, -dy), h - max(0, dy))
    xs = slice(max(0, dx), w + min(0, dx)); xd = slice(max(0, -dx), w - max(0, dx))
    out[yd, xd] = a[ys, xs]
    return out


def shade(a, wrap=False, seed=0, grad=True, hi=0.10, lo=0.13, ao=0.12, grain=0.035):
    a = a.astype(float)
    rgb = a[..., :3]
    al = a[..., 3] > 0
    L = lum(a)
    body = al & (L > 30)
    def differs(n):
        return np.abs(n[..., :3] - rgb).sum(-1) > 18
    k = np.ones(L.shape)
    up, lf, dn, rt = sh(a, 0, -1, wrap), sh(a, -1, 0, wrap), sh(a, 0, 1, wrap), sh(a, 1, 0, wrap)
    e_hi = body & ((differs(up) | (up[..., 3] == 0)) | (differs(lf) | (lf[..., 3] == 0)))
    e_lo = body & ((differs(dn) | (dn[..., 3] == 0)) | (differs(rt) | (rt[..., 3] == 0))) & ~e_hi
    k[e_hi] *= 1 + hi
    k[e_lo] *= 1 - lo
    # падающая тень: над пикселем (1..3 выше) есть заметно более тёмная или более выступающая область
    for d, w in ((1, 1.0), (2, 0.7), (3, 0.4)):
        u = sh(a, 0, -d, wrap)
        cast = body & (u[..., 3] > 0) & differs(u) & (lum(u) < L - 25) & ~e_lo
        k[cast & ~e_hi] *= 1 - ao * w
    if grad:
        h = a.shape[0]
        ys = np.arange(h)[:, None] / max(1, h - 1)
        k *= 1.05 - 0.10 * ys
    rng = np.random.default_rng(seed)
    k *= 1 + (rng.random(L.shape) - 0.5) * grain
    k[~body] = 1
    out = np.clip(rgb * k[..., None], 0, 255)
    return np.concatenate([out, a[..., 3:]], -1).astype(np.uint8)


def run(A):
    tp = os.path.join(A, "tiles.png")
    at = np.array(Image.open(tp).convert("RGBA"))
    H, W = at.shape[:2]
    skip = set()
    names = {}
    for l in open(os.path.join(A, "tiles.txt")):
        n, cx, cy = l.split()
        names[(int(cx), int(cy))] = n
    dp = os.path.join(A, "tiles_detailed.txt")
    if os.path.exists(dp):
        skip = set(open(dp).read().split())
    for y in range(0, H, T2):
        for x in range(0, W, T2):
            t = at[y:y + T2, x:x + T2]
            if names.get((x // T2, y // T2)) in skip:
                continue
            if t[..., 3].any():
                at[y:y + T2, x:x + T2] = shade(t, wrap=True, seed=x * 7 + y, grad=False)
    Image.fromarray(at, "RGBA").save(tp)
    dp = os.path.join(A, "props_detailed.txt")
    pskip = set(open(dp).read().split()) if os.path.exists(dp) else set()
    for f in sorted(os.listdir(os.path.join(A, "props"))):
        if not f.endswith(".png") or f[:-4] in pskip:
            continue
        p = os.path.join(A, "props", f)
        a = np.array(Image.open(p).convert("RGBA"))
        Image.fromarray(shade(a, seed=len(f)), "RGBA").save(p)


if __name__ == "__main__":
    run(sys.argv[1])
