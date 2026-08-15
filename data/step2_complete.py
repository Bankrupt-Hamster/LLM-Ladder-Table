#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
*2 补全脚本：原始数据.csv -> 数据源.csv
1) 单值化：HLE=工具/纯思考取最大；AA=改良分首个数值（去*）；DeepSWE=1.1 侧（无则 1.0 侧）；致知=首个数值
2) 个人评分解析：±5 类格式（"+3"->3, "-2"->-2, "0"->0，空->0）；"±5" 视为 0 并警告
3) 串行 kNN + 线性插值补全缺失分数（先补最完整的扩充池，k=5 共享列加权欧氏距离，1/距离加权）
4) 加权和 C = 0.40×DeepSWE + 0.30×致知 + 0.15×AA + 0.15×HLE
5) 最终分数 = 60×(C/C基准)^k + 个人评分（基准=Claude Opus 4.6 的加权和，k=1.0，不截断）
6) 无任何真实数据的模型：四榜留空、加权和=0、最终分数=个人评分
"""
import csv, math, os, re

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "原始数据.csv")
OUT = os.path.join(BASE, "数据源.csv")

F_W = {"DeepSWE": 0.40, "致知": 0.30, "AA": 0.15, "HLE": 0.15}
F_BASE = ("Anthropic", "Claude Opus 4.6")
F_K = 1.0
K_NN = 5
COLS = ["HLE", "AA", "DeepSWE", "致知"]

def first_num(s):
    m = re.search(r'-?\d+(?:\.\d+)?', s or "")
    return float(m.group()) if m else None

def hle_val(s):
    nums = re.findall(r'-?\d+(?:\.\d+)?', s or "")
    return max(float(x) for x in nums) if nums else None

def ds_val(s):
    nums = re.findall(r'-?\d+(?:\.\d+)?', s or "")
    return float(nums[0]) if nums else None

def personal_val(s):
    s = (s or "").strip()
    if not s:
        return 0.0
    m = re.match(r'^([+-])\s*(\d+(?:\.\d+)?)$', s)
    if m:
        return float(m.group(1) + m.group(2))
    m2 = re.match(r'^(\d+(?:\.\d+)?)$', s)
    if m2:
        return float(m2.group(1))
    print(f"  ⚠️ 个人评分无法解析（按 0 处理）: {s!r}")
    return 0.0

raw = list(csv.DictReader(open(SRC, encoding="utf-8-sig")))
rows = []
for r in raw:
    rows.append({
        "公司": (r.get("公司") or "").strip(), "模型": (r.get("模型名") or r.get("模型") or "").strip(),
        "日期": (r.get("发布日期") or "").strip(),
        "HLE": hle_val(r.get("HLE分数")), "AA": first_num(r.get("AA分数")),
        "DeepSWE": ds_val(r.get("DeepSWE分数")), "致知": first_num(r.get("致知分数")),
        "个人评分": personal_val(r.get("个人评分")),
    })
rows = [r for r in rows if r["模型"]]

def avail(r):
    return [c for c in COLS if r[c] is not None]

def dist(a, b, keys):
    return math.sqrt(sum((a[k] - b[k]) ** 2 for k in keys) / len(keys)) if keys else float("inf")

real_n = {id(r): len(avail(r)) for r in rows}
pool = [r for r in rows if len(avail(r)) == len(COLS)]
rest = [r for r in rows if r not in pool]
imputed = []
for r in sorted(rest, key=lambda r: -len(avail(r))):
    if not avail(r):
        continue   # 无任何真实数据，无法补全
    have = avail(r)
    for c in [c for c in COLS if r[c] is None]:
        nbs = []
        for p in pool:
            shared = [k for k in have if p[k] is not None]
            if not shared or p[c] is None:
                continue
            nbs.append((dist(r, p, shared), p[c]))
        if not nbs:
            continue
        nbs.sort(key=lambda x: x[0])
        nbs = nbs[:K_NN]
        wts = [1 / (d + 1e-9) for d, _ in nbs]
        r[c] = sum(w * v for w, (d, v) in zip(wts, nbs)) / sum(wts)
        imputed.append((r["公司"], r["模型"], c))
    pool.append(r)

base_row = next((r for r in rows if (r["公司"], r["模型"]) == F_BASE), None)
if base_row is None or len(avail(base_row)) < 4:
    raise SystemExit("基准模型 %s 数据不足" % (F_BASE,))
comp_base = sum(F_W[c] * base_row[c] for c in COLS)

im_keys = {(m[0], m[1], m[2]) for m in imputed}
with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["公司", "模型", "发布日期", "HLE", "AA", "DeepSWE", "致知",
                "加权和", "最终分数", "个人评分", "完整度",
                "HLE补全", "AA补全", "DeepSWE补全", "致知补全"])
    for r in rows:
        n0 = real_n[id(r)]
        comp = sum(F_W[c] * (r[c] or 0.0) for c in COLS)
        final = 60.0 * (comp / comp_base) ** F_K + r["个人评分"]
        vals = ["" if r[c] is None else f"{r[c]:.1f}" for c in COLS]
        star = ["*" if (r["公司"], r["模型"], c) in im_keys else "" for c in COLS]
        im = [int((r["公司"], r["模型"], c) in im_keys) for c in COLS]
        w.writerow([r["公司"], r["模型"], r["日期"],
                    star[0] + vals[0], star[1] + vals[1], star[2] + vals[2], star[3] + vals[3],
                    f"{comp:.1f}", f"{final:.1f}", f"{r['个人评分']:.1f}", f"{n0}/4"] + im)
print(f"写出: {OUT}")
print(f"基准 {F_BASE} 加权和 = {comp_base:.2f}（=60 分）；k={F_K}")
print(f"模型 {len(rows)} 个；补全 {len(imputed)} 处；无数据模型 {sum(1 for r in rows if not avail(r))} 个")
