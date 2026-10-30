"""Сводка по playstats.csv (пишется игрой после каждого дела).

    python tools/stats_summary.py "%APPDATA%/Godot/app_userdata/Без лица/playstats.csv"

Печатает по сложностям: сколько дел, доля закрытых, среднее время, на что ушла память,
сколько свидетелей и тревог — по этим цифрам подбираются цены и скорости.
"""
import csv
import sys
from collections import defaultdict


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def main(path):
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter=";"))
    if not rows:
        print("пусто")
        return
    groups = defaultdict(list)
    for r in rows:
        groups[r["difficulty"]].append(r)
        groups["все"].append(r)
    keys = ["real_min", "body_min", "spirit_min", "memory_end", "spent_enter", "spent_enter_fast", "spent_thrown",
            "spent_claws", "thrown", "jumps", "talks", "witnesses", "alarms", "max_susp", "min_density"]
    for g, rs in groups.items():
        n = len(rs)
        ok = sum(1 for r in rs if r["ok"] == "true")
        print(f"== {g}: дел {n}, закрыто {ok} ({100 * ok // n}%)")
        for k in keys:
            print(f"   {k:16} {sum(num(r.get(k)) for r in rs) / n:8.1f}")
        why = defaultdict(int)
        for r in rs:
            if r["ok"] != "true":
                why[r["why"] or "?"] += 1
        for w, c in sorted(why.items(), key=lambda x: -x[1]):
            print(f"   провал: {w} — {c}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "playstats.csv")
