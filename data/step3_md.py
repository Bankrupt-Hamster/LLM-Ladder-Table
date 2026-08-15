#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
*3 生成数据源.md：数据源.csv -> 数据源.md（纯表格，无 # / > / 备注，供可视化）
"""
import csv, os

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "数据源.csv")
OUT = os.path.join(BASE, "数据源.md")

rows = list(csv.DictReader(open(SRC, encoding="utf-8-sig")))
cols = list(rows[0].keys())

def dwidth(s):
    return sum(2 if ord(c) > 0x2E80 else 1 for c in str(s))

hdr = cols
widths = [max(dwidth(c) for c in col) for col in zip(*([hdr] + [list(r.values()) for r in rows]))]
def fmt(cells):
    return "|" + "|".join(" " + str(c) + " " * (w - dwidth(str(c))) + " " for c, w in zip(cells, widths)) + "|"

out = [fmt(hdr), "|" + "|".join(" " + "-" * w + " " for w in widths) + "|"]
for r in rows:
    out.append(fmt(list(r.values())))
open(OUT, "w", encoding="utf-8").write("\n".join(out).rstrip("\n") + "\n")
print(f"写出: {OUT}（{len(rows)} 行）")
