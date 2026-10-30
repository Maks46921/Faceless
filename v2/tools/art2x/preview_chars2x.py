"""Превью людей 2x: собирает несколько человек из слоёв и красит палитрой. python3 preview_chars2x.py <assets> <out.png>"""
import sys, os, random
import numpy as np
from PIL import Image

S = 108
SW = 84
PAL = [(0.86, 0.69, 0.58), (0.2, 0.15, 0.12), (0.3, 0.32, 0.38), (0.2, 0.2, 0.24), (0.12, 0.1, 0.09), (0.25, 0.22, 0.2),
       (0.5, 0.2, 0.18), (0.1, 0.1, 0.1), (0.95, 0.94, 0.9), (0.6, 0.6, 0.62), (0.8, 0.78, 0.72), (0.3, 0.25, 0.3)]


def colorize(im, pal):
    a = np.array(im).astype(float)
    m = np.clip((a[..., 0] // 16).astype(int), 0, 11)
    s = a[..., 1] / 255.0 * 1.25
    p = np.array(pal)[m]
    rgb = np.clip(p * s[..., None] * 255, 0, 255)
    out = np.zeros_like(a)
    out[..., :3] = rgb
    out[..., 3] = a[..., 3]
    return Image.fromarray(out.astype(np.uint8), "RGBA")


def person(assets, build, layers, pal, frame):
    img = Image.new("RGBA", (SW, S), (0, 0, 0, 0))
    for ln in layers:
        p = os.path.join(assets, "fig2", build, ln + ".png")
        if not os.path.exists(p):
            print("no", ln)
            continue
        sh = Image.open(p)
        fr = sh.crop((frame * SW, 0, frame * SW + SW, S))
        img.alpha_composite(colorize(fr, pal))
    return img


PEOPLE = [
    ("m", ["armb", "legs_pants", "shoes_low", "body", "torso_coat", "scarf", "hair_short", "hat_fedora", "armf", "item_briefcase"]),
    ("s", ["armb", "legs_skirt", "shoes_boots", "body", "torso_fur", "hair_bob", "hat_beret", "armf", "item_bag"]),
    ("t", ["armb", "legs_jeans", "shoes_low", "body", "torso_tracksuit", "hair_crop", "armf"]),
    ("h", ["armb_puffy", "legs_pants", "shoes_boots", "body", "torso_parka", "beard_full", "hat_ushanka", "armf_puffy"]),
    ("k", ["armb", "legs_pants", "shoes_low", "body", "wrinkles", "torso_suit", "hair_receding", "beard_mustache", "glasses", "armf", "item_paper"]),
    ("m", ["armb", "legs_skirt", "shoes_low", "body", "wrinkles", "torso_cardigan", "hair_perm", "glasses", "armf", "item_stringbag"]),
    ("s", ["armb", "legs_skirt", "shoes_low", "body", "torso_dress", "hair_braid", "armf"]),
    ("t", ["armb", "legs_pants", "shoes_boots", "body", "torso_uniform", "hair_short", "hat_police", "armf"]),
]
if __name__ == "__main__":
    assets, out = sys.argv[1], sys.argv[2]
    frames = [0, 2, 4, 6, 10, 25, 26, 33]
    rnd = random.Random(3)
    sheet = Image.new("RGBA", (SW * len(PEOPLE), S * len(frames)), (60, 62, 66, 255))
    for i, (b, ls) in enumerate(PEOPLE):
        pal = list(PAL)
        pal[2] = (rnd.random() * 0.5 + 0.15, rnd.random() * 0.5 + 0.15, rnd.random() * 0.5 + 0.15)
        pal[1] = [(0.15, 0.1, 0.08), (0.5, 0.35, 0.2), (0.6, 0.6, 0.58), (0.45, 0.2, 0.1)][i % 4]
        for j, fr in enumerate(frames):
            sheet.alpha_composite(person(assets, b, ls, pal, fr), (i * SW, j * S))
    sheet = sheet.resize((sheet.width * 2, sheet.height * 2), Image.NEAREST)
    sheet.save(out)
