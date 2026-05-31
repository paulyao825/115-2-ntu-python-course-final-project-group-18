# 回歸分析 Handoff

給負責跑回歸的同事。包含模型、變數、方法論、限制。

---

## 研究問題

**不同類型的 K-pop 藝人事件，對所屬經紀公司股價的影響程度**。

具體想回答：comeback、PR_crisis、軍隊、續約、演唱會等事件類型，各自平均造成多少超額報酬？哪些事件正向、哪些負向、影響有多大？

---

## 回歸模型

```
AR[i,t] = α 
        + Σ γ_k · D_category[i,k]
        + β · media_attention[i,t]
        + δ_1 · fanbase_weight[g] 
        + δ_2 · market_cap[c]
        + ε[i,t]
```

### 變數定義

| 符號 | 名稱 | 含意 | 來源 |
|---|---|---|---|
| `AR[i,t]` | abnormal return | 事件 i 在第 t 天的超額報酬 = 實際報酬 − market model 預期報酬 | `data/final/stock_daily.csv` |
| `D_category[i,k]` | **事件類型 dummy** | **核心解釋變數**：comeback、PR_crisis、military、contract_member、concert、activity、dating 等 | `data/templates/events_master.csv` 的 `event_category` |
| `media_attention[i,t]` | 每日關注度 | 控制媒體曝光強度（4 個 daily 訊號加總） | `data/final/traffic_daily.csv` 的 `traffic_total_raw` |
| `fanbase_weight[g]` | 團體人氣 | 控制團體大小差異 | `data/weights/group_weights.csv` |
| `market_cap[c]` | 公司市值 | 控制公司規模 | `data/weights/company_weights.csv` 的 `company_scale_weight` |

### 關鍵：γ_k 係數的意義

每個 `γ_k` 就是該事件類型的**平均股價影響**。例如：
- `γ_PR_crisis = -0.024` → PR 危機平均造成 -2.4% 異常報酬
- `γ_comeback = +0.008` → 回歸平均造成 +0.8% 異常報酬
- `γ_military = -0.005` → 入伍平均造成 -0.5% 異常報酬

**這就是研究主要結果**——告訴大家「哪類事件對股價傷害最大、哪類最有正面效益」。

---

## 進階分析（選做，robustness check）

如果主回歸跑完想做延伸分析，可以加互動項回答「**同類事件，越紅的團是否影響更大**」：

```
AR[i,t] = ... + β₂ · (media[i,t] × fanbase_weight[g]) + ...
```

但這是次要問題，**先把主回歸的 γ_k 結果跑出來再說**。

---

## 方法論說明

1. **Event study 框架**：用 market model 估事件前 estimation window 的 α、β，預測事件 window 內的 expected return，AR = 實際 − 預期。
2. **Y 是 daily AR**，不是 raw stock return。
3. **不要用 `sentiment_expected` 或 `severity_score` 當 X**：這些是主觀標的，沒明文標準。`event_category` 是客觀分類，讓**市場資料告訴你**哪類事件正/負面。
4. **不要把 YouTube cumulative views 當 daily traffic**：那是「累計到今天」的 snapshot，跟事件當天無關。建議當 group-level control variable 用（或忽略）。
5. **`fanbase_weight` 是 group-level 常數**：每個團體一個固定數字，當控制變數即可。
6. **`market_cap` 是 company-level 常數**：4 個公司各一個數字，當控制變數或公司 fixed effect。

---

## 已知資料限制（要在 paper limitations 寫）

| 限制 | 影響 | 處理方式 |
|---|---|---|
| Naver Search API 只回近期索引文章 | 老事件（2021）media count 偏低 | 加 `D_year` dummy 控制年份效應 |
| Google Trends pytrends 53/165 事件有 daily 資料 | 剩餘事件用 weekly forward-fill | 報告寫清楚 |
| YouTube 只有累計快照非當日 daily | 不適合當 daily traffic | 當 group-level control 或忽略 |
| Naver DataLab keyword 太具體 → 14.6% 覆蓋 | 部分事件 DataLab 是 0 | 跟其他訊號做 max() 組合，不要單靠 DataLab |
| 165 事件，11 個團體 → group level n=11 | group fixed effect 自由度低 | 用 random effect 或 cluster SE |
| `fanbase_weight` 是「現在的」快照不是「事件當下」 | 對舊事件可能高估 | 加 robustness check |

---

## 還沒抓但你需要的資料

```bash
# 1. 必抓：市場指數（算 AR 用的 benchmark，KOSPI + KOSDAQ）
#    需自己寫 collect_market_index.py 或加到 collect_stock.py

# 2. 已抓：股價 Y 變數
# data/final/stock_daily.csv 已存在

# 3. 可選：YouTube event-day（如果要當 control）
python scripts/collect_youtube.py
# → 產出 data/raw/youtube_stats.csv，需要 YOUTUBE_API_KEY
```

---

## 建議的程式架構

```python
import pandas as pd
import statsmodels.formula.api as smf

# 1. Load data
events = pd.read_csv('data/templates/events_master.csv')
traffic = pd.read_csv('data/final/traffic_daily.csv')
stock = pd.read_csv('data/final/stock_daily.csv')
group_w = pd.read_csv('data/weights/group_weights.csv')
company_w = pd.read_csv('data/weights/company_weights.csv')

# 2. Build event-day panel
panel = traffic.merge(
    events[['event_id', 'company', 'group', 'event_category', 'ticker']],
    on='event_id',
)
panel = panel.merge(group_w[['group', 'fanbase_weight']], on='group')
panel = panel.merge(
    company_w[['company', 'company_scale_weight']], on='company'
)

# 3. Compute abnormal returns
# For each event:
#   a) Estimate market model in [-120, -10] window
#      R_i = alpha + beta * R_market + e
#   b) Predict expected return in event window
#   c) AR = actual_return - expected_return
# Merge AR into panel by (ticker, date)

# 4. Run main regression: estimate gamma_k for each event type
panel['media'] = panel['traffic_total_raw']

model = smf.ols(
    'AR ~ C(event_category) + media + fanbase_weight + company_scale_weight',
    data=panel,
).fit(
    cov_type='cluster',
    cov_kwds={'groups': panel['event_id']},
)

print(model.summary())
# Look at C(event_category) coefficients — these are your gamma_k
```
