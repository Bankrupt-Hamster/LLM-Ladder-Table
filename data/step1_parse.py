#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
*1 解析脚本：原始数据.md -> 原始数据.csv
- 原始数据.md 为纯表格（无 # / > / 备注），手动维护：增删行、填分数，新增模型可留空
- 个人评分列保留原始文本（如 "+3"、"-2"、"±5" 范围、空），由 step2 解析
"""
import csv, os, re

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "原始数据.md")
OUT = os.path.join(BASE, "原始数据.csv")

lines = open(SRC, encoding="utf-8").read().split("\n")
# 表头 = 含 公司 与 模型名 的 | 行
hidx = next(i for i, ln in enumerate(lines) if ln.startswith("|") and "公司" in ln and "模型名" in ln)
hdr = [c.strip() for c in lines[hidx].strip().strip("|").split("|")]
body = []
i = hidx + 1
while i < len(lines) and lines[i].startswith("|"):
    cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
    is_sep = len(cells) == len(hdr) and all(set(c.replace("-", "").replace(" ", "")) == set() for c in cells)
    if len(cells) == len(hdr) and not is_sep:
        body.append(cells)
    i += 1

with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(hdr)
    w.writerows(body)
print(f"写出: {OUT}（表头 {hdr}，数据 {len(body)} 行）")
