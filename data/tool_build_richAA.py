#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tool_build_richAA.py —— 把原始 AA 数据补全成"丰富 AA 数据集"
================================================================
输入：AA_clean.csv（原始爬取数据，很多模型只测了部分分量，缺失为 --）
处理：串行迭代 kNN 补全（与 fill_aa.py 同法）
  1) 按 reasoning/non-reasoning 分池（名称含 "(Non-reasoning" 归非推理池）
  2) 全分量模型先入池；缺分量的按"缺失数升序"逐个用 kNN 补全：
     在共享分量上加权欧氏距离、1/距离加权取 k=K_NN 个邻居该分量的均值
  3) 补完入池，供后续（缺失更多的）模型使用
输出：AA_rich.csv —— 每个模型的 9 个分量全部填满，另存补全标记与真实覆盖
之后 tool_cal_transformAA.py 基于本文件计算改良 AA。
运行：python tool_build_richAA.py
可修改：K_NN（邻居数）
"""
import csv, math, os, re

K_NN = 5
BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "AA_clean.csv")
OUT = os.path.join(BASE, "AA_rich.csv")

COLS = ["GDPvalAAv2", "Tau3Banking", "TerminalBenchv21", "SciCode", "AA-LCR",
        "AA-OmniscienceAccuracy", "HLE", "GPQADiamond", "CritPt"]

def parse_num(v):
    v = (v or "").strip()
    if v in ("--", "", "N/A", "Pass", "Skip", "Pending", "Failed"):
        return None
    m = re.match(r'^(-?\d+(?:\.\d+)?)\*?$', v.replace("%", "").replace(",", ""))
    return float(m.group(1)) if m else None

rows = list(csv.DictReader(open(SRC, encoding="utf-8-sig")))

def vec(r):
    return {k: parse_num(r.get(k)) for k in COLS}

def is_reasoning(r):
    return "(non-reasoning" not in (r["Model"] or "").lower()

def wavg(d, keys):
    sw = sum(1 for k in keys)
    return sum(d[k] for k in keys) / sw if sw else 0.0

def dist(a, b, keys):
    return math.sqrt(sum((a[k] - b[k]) ** 2 for k in keys) / len(keys)) if keys else float("inf")

def enrich(pool_rows):
    pool = {r["Model"]: (r, vec(r)) for r in pool_rows
            if all(v is not None for v in vec(r).values())}
    full_names = set(pool)
    rest = [r for r in pool_rows if r["Model"] not in full_names]
    imputed = {}
    for r in sorted(rest, key=lambda r: -sum(1 for v in vec(r).values() if v is not None)):
        rv = vec(r)
        have = [k for k in COLS if rv[k] is not None]
        miss = [k for k in COLS if rv[k] is None]
        if not have:
            continue
        filled = dict(rv)
        for k in miss:
            nbs = []
            for _, pv in pool.values():
                shared = [s for s in have if pv[s] is not None]
                if not shared or pv[k] is None:
                    continue
                nbs.append((dist(rv, pv, shared), pv[k]))
            if not nbs:
                continue
            nbs.sort(key=lambda x: x[0])
            nbs = nbs[:K_NN]
            wts = [1 / (d + 1e-9) for d, _ in nbs]
            filled[k] = sum(w * v for w, (d, v) in zip(wts, nbs)) / sum(wts)
            imputed.setdefault(r["Model"], set()).add(k)
        pool[r["Model"]] = (r, filled)
    return pool, imputed

pool_r, imp_r = enrich([r for r in rows if is_reasoning(r)])
pool_n, imp_n = enrich([r for r in rows if not is_reasoning(r)])

with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Model", "Creator"] + COLS + ["真实覆盖", "补全分量"] + [c + "补全" for c in COLS])
    for r in rows:
        name = r["Model"]
        rv = vec(r)
        if name in pool_r:
            filled, imp = pool_r[name][1], imp_r.get(name, set())
        elif name in pool_n:
            filled, imp = pool_n[name][1], imp_n.get(name, set())
        else:
            filled, imp = rv, set()
        real_cov = sum(1 for v in rv.values() if v is not None) / len(COLS)
        w.writerow([name, r.get("Creator", "")] + [("" if filled[k] is None else f"{filled[k]:.2f}") for k in COLS] +
                   [f"{real_cov*100:.0f}%", ",".join(sorted(imp))] +
                   [int(k in imp) for k in COLS])
print(f"写出: {OUT}（{len(rows)} 个模型，串行 kNN 补全完成）")
