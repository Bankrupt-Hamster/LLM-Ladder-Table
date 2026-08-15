#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tool_cal_transformAA.py —— 改良 AA 分数计算工具（未知模型匹配版）
====================================================================
【流程】
  官方爬取 AA 原始数据表（AA_clean.csv）
    → 补全脚本（tool_build_richAA.py）→ 补全的 AA 数据表（AA_rich.csv）
    → 本工具：在顶端定义目标模型的各项分数（已知的填数值，未知的填 None/NULL）
    → 在 AA_rich.csv 中按"已知分量"近似匹配最相近的模型（kNN，加权欧氏距离）
    → 用邻居做线性插值（1/距离加权）拟合出目标模型缺失的各分量
    → 按改良 AA 算法（v4 修正口径）输出改良分数
  之后手动把结果填入 原始数据.md。
  这样面对从未见过的模型，只要知道它几个分量（官网/自己测），也能匹配出完整分数。

【改良 AA 算法（v4 修正口径）】
  原版 AA-Omniscience = 8%×Accuracy + 4%×(1−幻觉率)；改良剔除幻觉率，Omni=12%×Accuracy。
  改良 AA = 0.20×GDPval + 0.14×𝜏³-Banking + 0.16×TB-v2.1 + 0.08×SciCode
           + 0.06×AA-LCR + 0.12×Omni-Accuracy + 0.12×HLE + 0.06×GPQA + 0.06×CritPt

运行：先 python tool_build_richAA.py（生成 AA_rich.csv），再 python tool_cal_transformAA.py
可修改下方变量：MODEL_NAME / MODEL_COMPONENTS / K_NN / PRINT_NEIGHBORS
"""
import csv, math, os

# ================== 可修改变量 ==================
MODEL_NAME = "未知模型（示例）"   # 目标模型名（仅展示用）

# 该模型已知的各分量分数（0-100 制），未知项填 None（NULL）
MODEL_COMPONENTS = {
    "GDPvalAAv2": None,            # GDPval-AA v2
    "Tau3Banking": None,           # 𝜏³-Banking
    "TerminalBenchv21": None,      # Terminal-Bench v2.1
    "SciCode": None,
    "AA-LCR": None,
    "AA-OmniscienceAccuracy": None, # Omniscience 准确率
    "HLE": None,
    "GPQADiamond": None,
    "CritPt": None,
}
K_NN = 5                            # 匹配的最近邻数
PRINT_NEIGHBORS = True              # 打印匹配到的相近模型
# =================================================

# 权重：v4 修正口径
WEIGHTS = {
    "GDPvalAAv2": 0.20, "Tau3Banking": 0.14, "TerminalBenchv21": 0.16,
    "SciCode": 0.08, "AA-LCR": 0.06, "AA-OmniscienceAccuracy": 0.12,
    "HLE": 0.12, "GPQADiamond": 0.06, "CritPt": 0.06,
}

RICH_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "AA_rich.csv")
if not os.path.exists(RICH_CSV):
    print("❌ 未找到 AA_rich.csv，请先运行: python tool_build_richAA.py")
    raise SystemExit(1)

rows = list(csv.DictReader(open(RICH_CSV, encoding="utf-8-sig")))
COLS = list(WEIGHTS.keys())

known = {k: v for k, v in MODEL_COMPONENTS.items() if v is not None}
unknown = [k for k in COLS if k not in known]
if not known:
    print("❌ MODEL_COMPONENTS 至少需要填一项已知分数")
    raise SystemExit(1)

# ---- kNN 匹配：按已知分量（按权重加权）算距离 ----
def wdist(model_row, keys):
    wsum = sum(WEIGHTS[k] for k in keys)
    if wsum == 0:
        return float("inf")
    d2 = sum(WEIGHTS[k] * (float(model_row[k]) - known[k]) ** 2 for k in keys)
    return math.sqrt(d2 / wsum)

nbs = []
for r in rows:
    if all(r[k] for k in known):   # 邻居必须在已知分量上有值
        nbs.append((wdist(r, list(known)), r))
nbs.sort(key=lambda x: x[0])
nbs = nbs[:K_NN]

# ---- 线性插值拟合未知分量（1/距离加权）----
fitted = dict(known)
for k in unknown:
    wts, vals = [], []
    for d, r in nbs:
        if r[k]:
            wts.append(1 / (d + 1e-9))
            vals.append(float(r[k]))
    fitted[k] = sum(w * v for w, v in zip(wts, vals)) / sum(wts) if vals else None

# ---- 改良 AA ----
tot = sum(WEIGHTS[k] * fitted[k] for k in COLS if fitted[k] is not None)
sw = sum(WEIGHTS[k] for k in COLS if fitted[k] is not None)

print(f"\n=== {MODEL_NAME} ===")
print(f"已知分量 {len(known)} 个：{ {k: v for k, v in known.items()} }")
print(f"改良 AA 分数 = {tot/sw:.2f}" if sw else "无有效分量")
if sw < 1.0:
    print(f"⚠️ 有 {len([k for k in COLS if fitted[k] is None])} 个分量无法拟合（无邻居提供）")
print("\n拟合后的完整分量：")
for k in COLS:
    mark = "" if k in known else "（插值*）"
    print(f"    {k:28} {fitted[k]:7.2f} {mark}")
if PRINT_NEIGHBORS:
    print(f"\n匹配到的 {K_NN} 个最相近模型：")
    for d, r in nbs:
        print(f"    {r['Model']!r:40} 距离={d:.3f}")
