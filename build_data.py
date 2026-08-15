#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将同目录下的「数据源.csv」解析为一个 JS 数据组件「数据源.js」，
供 index.html 通过 <script src="数据源.js"> 加载（绕开 file:// 下 fetch 的限制）。

用法：
    python build_data.py

改动「数据源.csv」后重新运行一次即可刷新。
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, '数据源.csv')
OUT = os.path.join(HERE, '数据源.js')

if not os.path.exists(SRC):
    raise SystemExit('未找到同目录下的「数据源.csv」，请先放置该文件。')

with open(SRC, 'r', encoding='utf-8-sig') as f:
    csv_text = f.read()

# 用 JSON 序列化，安全转义换行/引号/反斜杠，避免破坏 JS 字符串字面量
payload = json.dumps(csv_text, ensure_ascii=False)

js = (
    '// 本文件由 build_data.py 自动生成，请勿手改；改动「数据源.csv」后重新运行。\n'
    'window.__DATA_CSV = ' + payload + ';\n'
)

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(js)

print('已生成 %s（%d 字符）' % (OUT, len(csv_text)))
