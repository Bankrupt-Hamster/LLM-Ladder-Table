# DeepSWE 榜 · 清洗合并表

> 数据源：`DeepSWE 1.0_src.txt`（21 条）、`DeepSWE 1.1_src.txt`（24 条），共 37 个模型。
> 合并列格式：`1.1分数/1.0分数`（Pass@1，%），缺的一边留空（如 `59/`、`/42`）。
> 说明：DeepSWE 1.1 的数据均为新版本（DeepSeek V4 Pro 0813 / V4 Flash 0731）；1.0 的 deepseek-v4-pro=8% 对应 0424 旧版。

| 模型 | 1.1 Pass@1 | 1.0 Pass@1 | 合并 1.1/1.0 |
| --- | --- | --- | --- |
| claude-opus-5 | 74%±4%[max] |  | 74/ |
| gpt-5.6-sol | 73%±3%[max] |  | 73/ |
| claude-fable-5 | 70%±4%[max] |  | 70/ |
| gpt-5.6-terra | 70%±3%[max] |  | 70/ |
| kimi-k3 | 69%±5%[max] |  | 69/ |
| gpt-5.5 | 67%±6%[xhigh] | 70%±3%[xhigh] | 67/70 |
| gpt-5.6-luna | 67%±4%[max] |  | 67/ |
| grok-4.6 | 67%±2%[xhigh] |  | 67/ |
| gemini-3.7-flash | 65%±2%[high] |  | 65/ |
| deepseek-v4-pro | 63%±6%[max] | 8%±3% | 63/8 |
| claude-opus-4.8 | 59%±2%[max] | 58%±2%[max] | 59/58 |
| qwen3.8-max | 57%±3%[xhigh] |  | 57/ |
| muse-spark-1.2 | 55%±2%[xhigh] |  | 55/ |
| claude-opus-4.7 |  | 54%±5%[max] | /54 |
| claude-sonnet-5 | 54%±4%[max] |  | 54/ |
| grok-4.5 | 54%±2%[high] |  | 54/ |
| deepseek-v4-flash | 53%±4%[max] |  | 53/ |
| muse-spark-1.1 | 53%±3%[xhigh] |  | 53/ |
| gpt-5.4 | 52%±2%[xhigh] | 56%±2%[xhigh] | 52/56 |
| gemini-3.6-flash | 47%±4%[high] |  | 47/ |
| glm-5.2 | 44%±2%[max] | 42%±3%[max] | 44/42 |
| gemini-3.5-flash | 36%±4%[high] | 28%±4%[medium] | 36/28 |
| kimi-k2.7-code | 31%±1% |  | 31/ |
| claude-sonnet-4.6 | 30%±4%[high] | 32%±2%[high] | 30/32 |
| claude-opus-4.6 |  | 28%±4%[max] | /28 |
| gpt-5.4-mini |  | 24%±3%[xhigh] | /24 |
| kimi-k2.6 |  | 24%±2% | /24 |
| minimax-m3 |  | 20%±4% | /20 |
| mimo-v2.5-pro |  | 19%±2% | /19 |
| glm-5.1 |  | 18%±1% | /18 |
| qwen3.7-max |  | 18%±1% | /18 |
| grok-build-0.1 |  | 13%±2% | /13 |
| gemini-3.1-pro | 12%±1%[high] | 10%±3% | 12/10 |
| gemini-3-flash |  | 5%±2% | /5 |
| qwen3.6-plus |  | 3%±1% | /3 |
| claude-haiku-4.5 |  | 0%±0% | /0 |
| minimax-m2.7 |  | 0%±0% | /0 |

---

## 备注
- 同一模型两版均有成绩时分数可能不同（题库/配置差异），合并列保留两版数值。
- 无 effort 档的记录（如 1.0 的 deepseek-v4-pro）表示测试时未开启思考档。
