#!/usr/bin/env python3
"""Синтезированная музыка «Без лица»: фон по времени суток и тревога.

Всё строится из синусов и шума (numpy), без сэмплов. Петли бесшовные: реверберация
считается круговой свёрткой, поэтому хвост последней ноты уходит в начало петли.
Выход: assets/music/*.ogg (через ffmpeg, libvorbis).

    python3 tools/audio/gen_music.py
"""
import os
import subprocess
import sys
import wave

import numpy as np

SR = 32000
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "assets", "music")
rng = np.random.default_rng(1979)

NOTE = {"C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "G#": 8,
        "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11}


def hz(midi):
    return 440.0 * 2.0 ** ((midi - 69) / 12.0)


def m(name, octave):
    return 12 * (octave + 1) + NOTE[name]


def chord(root, kind, octave=3):
    r = m(root, octave)
    iv = {"maj": [0, 4, 7], "min": [0, 3, 7], "7": [0, 4, 7, 10], "m7": [0, 3, 7, 10], "dim": [0, 3, 6], "maj7": [0, 4, 7, 11]}[kind]
    return [r + i for i in iv]


# ---------------- инструменты ----------------

def env_adsr(n, a, d, s, r, sustain_len):
    t = np.arange(n) / SR
    e = np.zeros(n)
    a_n, d_n = int(a * SR), int(d * SR)
    sl = int(sustain_len * SR)
    e[:a_n] = np.linspace(0, 1, a_n, endpoint=False) if a_n else 0
    e[a_n:a_n + d_n] = np.linspace(1, s, d_n, endpoint=False)[: max(0, min(d_n, n - a_n))]
    e[a_n + d_n:sl] = s
    rel = n - sl
    if rel > 0:
        e[sl:] = s * np.exp(-np.arange(rel) / (r * SR) * 5.0)
    return e


def piano(f, dur, vel=0.6):
    n = int((dur + 2.5) * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for k, amp in enumerate([1.0, 0.45, 0.25, 0.12, 0.07, 0.04], start=1):
        fk = f * k * (1 + 0.0004 * k * k)
        dec = 1.2 + 2.2 * k + f / 300.0
        out += amp * np.sin(2 * np.pi * fk * t) * np.exp(-t * dec)
    hammer = np.exp(-t * 60) * rng.normal(0, 0.05, n)
    out = out + hammer
    out *= np.minimum(1.0, t / 0.004)
    # глушение после отпускания
    off = int(dur * SR)
    if off < n:
        out[off:] *= np.exp(-np.arange(n - off) / (0.25 * SR) * 3)
    return out * vel * 0.35


def vibes(f, dur, vel=0.5):
    n = int((dur + 2.0) * SR)
    t = np.arange(n) / SR
    trem = 1 + 0.25 * np.sin(2 * np.pi * 5.2 * t)
    out = (np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t * 6)) * np.exp(-t * 1.6) * trem
    out *= np.minimum(1.0, t / 0.003)
    return out * vel * 0.3


def accordion(f, dur, vel=0.5):
    n = int((dur + 0.3) * SR)
    t = np.arange(n) / SR
    vib = 1 + 0.003 * np.sin(2 * np.pi * 5.5 * t)
    ph = 2 * np.pi * f * np.cumsum(vib) / SR
    ph2 = 2 * np.pi * f * 1.004 * np.cumsum(vib) / SR
    sq = lambda p: np.tanh(3 * np.sin(p)) * 0.6 + 0.25 * np.sin(2 * p) + 0.15 * np.sin(3 * p)
    out = sq(ph) + sq(ph2)
    return out * env_adsr(n, 0.03, 0.1, 0.8, 0.12, dur) * vel * 0.18


def pad(freqs, dur, vel=0.4):
    n = int((dur + 1.5) * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for f in freqs:
        for det in (-0.006, 0.0, 0.007):
            ff = f * (1 + det)
            # мягкая пила: несколько гармоник
            for k in range(1, 7):
                out += np.sin(2 * np.pi * ff * k * t + rng.uniform(0, 6.28)) / (k * 1.6)
    out *= env_adsr(n, 1.2, 0.5, 0.8, 1.2, dur)
    return out * vel * 0.03


def bell(f, dur, vel=0.5):
    n = int((dur + 4.0) * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for ratio, amp, dec in [(1.0, 1.0, 0.8), (2.76, 0.5, 1.4), (5.4, 0.25, 2.5), (8.93, 0.12, 4.0)]:
        out += amp * np.sin(2 * np.pi * f * ratio * t) * np.exp(-t * dec)
    out *= np.minimum(1.0, t / 0.002)
    return out * vel * 0.22


def bass(f, dur, vel=0.6):
    n = int((dur + 0.4) * SR)
    t = np.arange(n) / SR
    out = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t) * np.exp(-t * 4)
    return out * env_adsr(n, 0.01, 0.2, 0.6, 0.15, dur) * vel * 0.35


def strings(freqs, dur, vel=0.4, trem=0.0):
    n = int((dur + 0.8) * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for f in freqs:
        for det in (-0.004, 0.003):
            vib = 1 + 0.004 * np.sin(2 * np.pi * 5.0 * t + rng.uniform(0, 6))
            ph = 2 * np.pi * f * (1 + det) * np.cumsum(vib) / SR
            for k in range(1, 8):
                out += np.sin(k * ph) / k
    if trem:
        out *= 0.6 + 0.4 * np.abs(np.sin(2 * np.pi * trem * t))
    return out * env_adsr(n, 0.25, 0.3, 0.85, 0.4, dur) * vel * 0.025


# ---------------- обработка ----------------

def place(buf, sig, at):
    """Кладёт звук в петлю по кругу (хвост уходит в начало)."""
    i = int(at * SR) % len(buf)
    n = len(sig)
    end = i + n
    if end <= len(buf):
        buf[i:end] += sig
    else:
        k = len(buf) - i
        buf[i:] += sig[:k]
        rest = sig[k:]
        while len(rest):
            take = min(len(rest), len(buf))
            buf[:take] += rest[:take]
            rest = rest[take:]


def fft_filter(x, lo=None, hi=None, tilt=0.0):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    g = np.ones_like(f)
    if hi:
        g *= 1 / np.sqrt(1 + (f / hi) ** 4)
    if lo:
        g *= 1 / np.sqrt(1 + (lo / np.maximum(f, 1)) ** 4)
    if tilt:
        g *= (np.maximum(f, 50) / 1000.0) ** tilt
    return np.fft.irfft(X * g, n=len(x))


def reverb(x, seconds=2.2, mix=0.3, bright=4000):
    """Круговая свёртка с затухающим шумом: петля остаётся бесшовной."""
    n = len(x)
    ir_n = int(seconds * SR)
    ir = rng.normal(0, 1, ir_n) * np.exp(-np.arange(ir_n) / SR * (6.9 / seconds))
    ir = fft_filter(ir, hi=bright)
    ir /= np.sqrt(np.sum(ir ** 2)) + 1e-9
    h = np.zeros(n)
    h[: min(n, ir_n)] = ir[: min(n, ir_n)]
    wet = np.fft.irfft(np.fft.rfft(x) * np.fft.rfft(h), n=n)
    return x * (1 - mix) + wet * mix * 1.4


def normalize(x, peak=0.6):
    return x / (np.max(np.abs(x)) + 1e-9) * peak


def save(name, x):
    os.makedirs(OUT, exist_ok=True)
    x = normalize(x)
    # мягкий переход в стык: петля без щелчка
    wav = os.path.join(OUT, name + ".wav")
    with wave.open(wav, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32000).astype("<i2").tobytes())
    ogg = os.path.join(OUT, name + ".ogg")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-c:a", "libvorbis", "-q:a", "3", ogg], check=True)
    os.remove(wav)
    print(name, "%.1f s" % (len(x) / SR))


def melody_line(chords, beats_per_chord, beat, start, octave=5, density=0.6, scale=None, rest_p=0.25, seed=0):
    """Мелодия по аккордам: сильные доли — звуки аккорда, между ними — шаг по гамме."""
    r = np.random.default_rng(seed)
    notes = []
    prev = None
    t = start
    for ch in chords:
        tones = [x % 12 for x in ch]
        for b in range(beats_per_chord):
            if r.random() < rest_p and b != 0:
                t += beat
                continue
            if b == 0 or prev is None or r.random() < 0.5:
                pc = tones[r.integers(len(tones))]
            else:
                step = r.choice([-2, -1, 1, 2])
                cand = prev + step
                pcs = scale if scale else tones
                while cand % 12 not in pcs:
                    cand += 1 if step > 0 else -1
                pc = cand % 12
            base = 12 * (octave + 1)
            note = base + pc
            if prev is not None:
                while note - prev > 6:
                    note -= 12
                while prev - note > 6:
                    note += 12
            prev = note
            ln = beat * (2 if r.random() < 0.3 else 1)
            if r.random() < density:
                notes.append((t, note, ln))
            t += beat
    return notes


# ---------------- пьесы ----------------

def morning():
    """Утро: вальс по радио из окна — аккордеон, «умпа-па», узкая полоса и треск."""
    bpm = 104
    beat = 60 / bpm
    prog = [("C", "maj"), ("A", "min"), ("F", "maj"), ("G", "7"), ("C", "maj"), ("E", "min"), ("F", "maj"), ("G", "7"),
            ("A", "min"), ("E", "min"), ("F", "maj"), ("C", "maj"), ("D", "min"), ("G", "7"), ("C", "maj"), ("G", "7")]
    bars = len(prog)
    buf = np.zeros(int(bars * 3 * beat * SR))
    for i, (r, k) in enumerate(prog):
        t0 = i * 3 * beat
        ch = chord(r, k, 3)
        place(buf, bass(hz(ch[0] - 12), beat * 0.8, 0.7), t0)
        for b in (1, 2):
            for nn in ch[1:]:
                place(buf, accordion(hz(nn), beat * 0.45, 0.35), t0 + b * beat)
    major = [0, 2, 4, 5, 7, 9, 11]
    for (t, nn, ln) in melody_line([chord(r, k, 3) for r, k in prog], 3, beat, 0.0, 5, 0.85, major, 0.15, seed=11):
        place(buf, accordion(hz(nn), ln * 0.9, 0.55), t)
    x = fft_filter(buf, lo=350, hi=2600)
    x = reverb(x, 1.2, 0.25, 3000)
    t = np.arange(len(x)) / SR
    x *= 1 + 0.05 * np.sin(2 * np.pi * 0.3 * t)
    crackle = (rng.random(len(x)) < 0.0007) * rng.normal(0, 0.25, len(x))
    hiss = fft_filter(rng.normal(0, 0.012, len(x)), lo=2000, hi=7000)
    return normalize(x, 0.5) + crackle * 0.4 + hiss


def day():
    """День: редкий вибрафон по аккордам и тихий пэд."""
    bpm = 72
    beat = 60 / bpm
    prog = [("A", "m7"), ("F", "maj7"), ("C", "maj"), ("G", "maj"), ("A", "m7"), ("F", "maj7"), ("D", "min"), ("E", "7")]
    bars = len(prog) * 2
    buf = np.zeros(int(bars * 4 * beat * SR))
    for i in range(bars):
        r, k = prog[i % len(prog)]
        t0 = i * 4 * beat
        ch = chord(r, k, 3)
        if i % 2 == 0:
            place(buf, pad([hz(n) for n in ch], 8 * beat * 0.95, 0.5), t0)
            place(buf, bass(hz(ch[0] - 12), 3 * beat, 0.5), t0)
        arp = [ch[0] + 12, ch[1] + 12, ch[2] + 12, ch[-1] + 24]
        for j in range(4):
            if rng.random() < 0.7:
                place(buf, vibes(hz(arp[(j + i) % len(arp)]), beat * 1.5, 0.35 + 0.15 * rng.random()), t0 + j * beat + rng.uniform(0, 0.02))
    minor = [9, 11, 0, 2, 4, 5, 7]
    for (t, nn, ln) in melody_line([chord(r, k, 3) for r, k in prog] * 2, 4, beat, 0.0, 5, 0.45, minor, 0.45, seed=5):
        place(buf, vibes(hz(nn), ln, 0.45), t)
    return reverb(buf, 2.8, 0.4, 5000)


def evening():
    """Вечер: пианино за стеной — ломаные аккорды и простая мелодия."""
    bpm = 62
    beat = 60 / bpm
    prog = [("D", "min"), ("Bb", "maj"), ("F", "maj"), ("A", "7"), ("D", "min"), ("G", "min"), ("A", "7"), ("D", "min")]
    bars = len(prog) * 2
    buf = np.zeros(int(bars * 4 * beat * SR))
    for i in range(bars):
        r, k = prog[i % len(prog)]
        t0 = i * 4 * beat
        ch = chord(r, k, 3)
        place(buf, piano(hz(ch[0] - 12), 3.5 * beat, 0.55), t0)
        pattern = [ch[0], ch[1] + 0, ch[2], ch[1] + 12 if len(ch) < 4 else ch[3], ch[2] + 12, ch[2], ch[1], ch[2]]
        for j, nn in enumerate(pattern):
            place(buf, piano(hz(nn), beat * 0.9, 0.28 + 0.06 * rng.random()), t0 + j * beat / 2 + rng.uniform(0, 0.015))
    harm_minor = [2, 4, 5, 7, 9, 10, 1]
    for (t, nn, ln) in melody_line([chord(r, k, 3) for r, k in prog] * 2, 4, beat, 0.0, 5, 0.7, harm_minor, 0.3, seed=21):
        place(buf, piano(hz(nn), ln, 0.5), t + rng.uniform(0, 0.02))
    x = fft_filter(buf, hi=4200)  # пианино за стеной
    return reverb(x, 2.4, 0.35, 3500)


def night():
    """Ночь: гул города, низкий дрон и редкие колокольчики."""
    dur = 48.0
    n = int(dur * SR)
    t = np.arange(n) / SR
    base = hz(m("D", 2))
    x = np.zeros(n)
    for f, a in [(base, 1.0), (base * 1.5, 0.5), (base * 2.003, 0.35), (base * 0.5, 0.6)]:
        # целое число периодов огибающей на длину петли
        lfo = 0.7 + 0.3 * np.sin(2 * np.pi * (2 / dur) * t + rng.uniform(0, 6))
        x += a * np.sin(2 * np.pi * round(f * dur) / dur * t) * lfo
    x *= 0.12
    hum = fft_filter(rng.normal(0, 1, n), lo=40, hi=300) * 0.05
    x += hum
    pent = [m("D", 5), m("F", 5), m("G", 5), m("A", 5), m("C", 6), m("D", 6)]
    tt = 1.0
    while tt < dur - 1:
        place(x, bell(hz(pent[rng.integers(len(pent))]), 0.5, 0.25 + 0.2 * rng.random()), tt)
        tt += rng.uniform(3.0, 7.5)
    return reverb(x, 3.5, 0.45, 2500)


def tension():
    """Тревога: свидетель, звонок, милиция — низкая пульсация и тремоло струнных."""
    bpm = 116
    beat = 60 / bpm
    bars = 8
    buf = np.zeros(int(bars * 4 * beat * SR))
    lo = [m("D", 2), m("Eb", 2)]
    for i in range(bars * 8):
        f = hz(lo[(i // 8) % 2] if i % 8 < 6 else lo[(i // 8 + 1) % 2])
        place(buf, bass(f, beat * 0.35, 0.8 if i % 4 == 0 else 0.55), i * beat / 2)
    clusters = [[m("D", 4), m("Eb", 4), m("A", 4)], [m("D", 4), m("F", 4), m("Ab", 4)],
                [m("C#", 4), m("D", 4), m("G#", 4)], [m("D", 4), m("Eb", 4), m("Bb", 4)]]
    for i in range(bars // 2):
        place(buf, strings([hz(n) for n in clusters[i % 4]], 8 * beat * 0.98, 0.5, trem=7.0), i * 8 * beat)
    for i in range(bars):
        if i % 2 == 1:
            place(buf, bell(hz(m("A", 5)), 0.3, 0.15), i * 4 * beat + 3.5 * beat)
    return reverb(buf, 1.6, 0.25, 5000)


def main():
    for name, fn in [("morning", morning), ("day", day), ("evening", evening), ("night", night), ("tension", tension)]:
        save(name, fn())


if __name__ == "__main__":
    sys.exit(main())
