# 回歸分析 Handoff

給負責跑回歸的同事。包含模型、變數、方法論、限制。

---

## 研究問題

K-pop 藝人個別事件對所屬經紀公司股價的影響。

---

## 回歸模型

```
AR[i,t] = α
        + β₁·media_attention[i,t]
        + β₂·(media_attention[i,t] × fanbase_weight[g])
        + Σγ_k·D_category[i,k]
        + δ·market_cap[c]
        + ε[i,t]
```

### 變數定義

| 符號 | 名稱 | 含意 | 來源 |
|---|---|---|---|
| `AR[i,t]` | abnormal return | 事件 i 在第 t 天的超額報酬 = 實際報酬 − market model 預期報酬 | `data/final/stock_daily.csv`（**還沒抓**，跑 `scripts/collect_stock.py`） |
| `media_attention[i,t]` | 每日關注度 | 4 個 daily 訊號（建議用 `traffic_total_raw` 或自己組合） | `data/final/traffic_daily.csv` 的 `naver_news_count`、`naver_blog_count`、`naver_datalab_score`、`google_trends_score` |
| `fanbase_weight[g]` | 團體人氣 | 該團體粉絲基礎 z-score 平均 | `data/weights/group_weights.csv` 的 `fanbase_weight` |
| `D_category[i,k]` | 事件類別 dummy | comeback、PR_crisis、military 等 6 類的 dummy variables | `data/templates/events_master.csv` 的 `event_category` |
| `market_cap[c]` | 公司市值 | 控制公司規模 | `data/weights/company_weights.csv` 的 `market_cap` 或 z-score |

### 關鍵：互動項 β₂ 的意義

β₂ 測試的是「越紅的團體，同樣的媒體關注帶來越大的股價反應」這個假設。如果 β₂ > 0 且顯著，就證明 BTS 一則新聞對 HYBE 股價的衝擊 > LE SSERAFIM 同類新聞對 HYBE 的衝擊。**這是這個研究的核心 hypothesis**。

---

## 方法論說明

1. **Event study 框架**：用 market model 估事件前 estimation window 的 α、β，預測事件 window 內的 expected return，AR = 實際 − 預期。
2. **Y 是 daily AR**，不是 raw stock return。
3. **不要用 `sentiment_expected` 或 `severity_score` 當 X**：這些是組員主觀標的，沒明文標準，會被 reviewer 質疑。用 `event_category` dummies 取代——讓市場資料告訴你哪類事件正面/負面，而非反過來。
4. **不要把 YouTube cumulative views 當 daily traffic**：那是「累計到今天」的 snapshot，跟事件當天無關。建議當 group-level control variable 用（或忽略）。
5. **`fanbase_weight` 是 group-level 常數**：每個團體一個固定數字，不隨時間變。所以放在互動項裡才有意義（單獨放只是另一個固定效應）。
6. **`market_cap` 是 company-level 常數**：4 個公司各一個數字，可以當 fixed effect 或單獨控制變數。

---

## 已知資料限制（要在 paper limitations 寫）

| 限制 | 影響 | 處理方式 |
|---|---|---|
| Naver Search API 只回近期索引文章 | 老事件（2021）media count 偏低 | 加 `D_year` dummy 控制年份效應 |
| Google Trends pytrends 53/165 事件有 daily 資料 | 剩餘事件用 weekly forward-fill | 報告寫清楚 |
| YouTube 只有累計快照非當日 daily | 不適合當 daily traffic | 當 group-level control 或忽略 |
| Naver DataLab keyword 太具體 → 14.6% 覆蓋 | 部分事件 DataLab 是 0 | 跟其他訊號做 max() 組合，不要單靠 DataLab |
| 165 事件，11 個團體 → group level n=11 | group fixed effect 自由度低 | 用 random effect 或 cluster SE |
| `fanbase_weight` 是「現在的」快照不是「事件當下」 | 對舊事件可能高估 | 可加 `event_year × fanbase` 互動項當 robustness check |

---

## 還沒抓但你需要的資料

```bash
# 1. 必抓：股價 Y 變數
python scripts/collect_stock.py
# → 產出 data/final/stock_daily.csv

# 2. 可選：YouTube（如果要當 control）
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
#   b) Predict expected return in event window
#   c) AR = actual_return - expected_return

# 4. Merge AR into panel by (ticker, date)

# 5. Run regression
panel['media'] = panel['traffic_total_raw']  # or your own combination

model = smf.ols(
    'AR ~ media + media:fanbase_weight '
    '+ C(event_category) + company_scale_weight',
    data=panel,
).fit(
    cov_type='cluster',
    cov_kwds={'groups': panel['event_id']},
)

print(model.summary())
```
