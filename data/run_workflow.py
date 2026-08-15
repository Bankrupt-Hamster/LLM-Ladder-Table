#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_workflow.py —— 胶水脚本：一键执行数据更新工作流
================================================================
流程：
  原始数据.md（手动维护）
    → step1_parse.py    解析为 原始数据.csv
    → step2_complete.py  kNN+线性插值补全 → 数据源.csv
    → step3_md.py       生成 数据源.md
之后可视化直接读 数据源.csv。
用法：python run_workflow.py
"""
import subprocess, sys, os

BASE = os.path.dirname(os.path.abspath(__file__))
STEPS = ["step1_parse.py", "step2_complete.py", "step3_md.py"]

for s in STEPS:
    p = os.path.join(BASE, s)
    print(f"▶ 运行 {s} ...")
    r = subprocess.run([sys.executable, p], cwd=BASE)
    if r.returncode != 0:
        print(f"❌ {s} 失败（exit {r.returncode}），已中止")
        sys.exit(r.returncode)

print("\n✅ 工作流完成：原始数据.md → 原始数据.csv → 数据源.csv → 数据源.md")
print("可视化请读取: 数据源.csv")
