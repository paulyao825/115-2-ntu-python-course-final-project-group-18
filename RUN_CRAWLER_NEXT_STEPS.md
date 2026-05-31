# 開始執行 Crawler 的步驟

## 1. 建立 Python 環境

在專案資料夾執行（Mac/Linux）：

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

如果不想用 venv，可直接用系統 Python。

## 2. 建立 `.env`

複製 `.env.example` 成 `.env`，並填入：

```text
NAVER_CLIENT_ID=
NAVER_CLIENT_SECRET=
YOUTUBE_API_KEY=
```

`CRAWLER_INSECURE_SSL_VERIFY` 預設 false。如果遇到 SSL 憑證驗證錯誤，可改 true（不影響資料正確性）。

## 3. 檢查事件清單

事件已收錄 165 筆，11 個團體各 15 筆：

```text
HYBE：BTS, SEVENTEEN, NewJeans, LE SSERAFIM
SM：aespa, NCT, EXO
JYP：TWICE, Stray Kids
YG：BLACKPINK, BIGBANG
```

檔案位置：

```text
data/templates/events_master.csv    # 事件 metadata
config/keywords.csv                  # crawler 查詢關鍵字
```

詳細欄位說明請看 `docs/variable_reference.md`。

## 4. 執行 crawler

依序執行（Mac/Linux）：

```bash
# 韓國新聞與部落格（最久，5-10 分鐘）
python scripts/collect_naver.py

# 韓國搜尋指數（1-2 分鐘）
python scripts/collect_naver_datalab.py

# Google Trends（會撞 rate limit，需 VPN 輪替）
python scripts/collect_google_trends.py

# YouTube（可能 quota exceeded）
python scripts/collect_youtube.py

# 股價
python scripts/collect_stock.py
```

Windows 請把 `python` 改成 `.\.venv\Scripts\python.exe`。

## 5. Google Trends 的 rate limit 處理

`collect_google_trends.py` 已改為**可中斷續跑**：

- 跑到 429 會自動停下並提示
- 切換 VPN 到新地區（建議歐洲或日本 IP）
- 重跑相同指令，會自動跳過已完成事件
- 不同 VPN 地區可以解鎖不同事件（Google 看 IP 地理位置）

如果 quota 用光：

```bash
python scripts/collect_google_trends.py --reset   # 清空重來
python scripts/collect_google_trends.py            # 續跑
```

## 6. 建立每日流量 panel

```bash
python scripts/build_daily_traffic.py
```

輸出：

```text
data/final/traffic_daily.csv
```

包含 4 個 daily attention 訊號 + IG 追蹤數 + 總流量分數。

## 7. 檢查資料品質

```bash
python scripts/validate_dataset.py
```

輸出：

```text
data/final/data_quality_report.csv
```

跑完應顯示 `Failed checks: 0`。

## 8. 用 GitHub 協作

`.gitignore` 預設排除 `data/raw/` 與 `data/final/`，避免大量資料推上去。

如果要 push 資料給組員（例如 final panel），手動 `git add -f`：

```bash
git add -f data/final/traffic_daily.csv data/final/stock_daily.csv
git commit -m "update final panel"
git push origin main
```

## 9. 注意事項

- Naver Search API 一天 25,000 次免費額度，分頁版會用 ~3,300 次
- Naver DataLab API 一天 1,000 次免費額度
- Google Trends 沒明確額度，但 pytrends 一直被 Google 限制
- YouTube Data API v3 每天 10,000 units 免費（一次 search 約 100 units，可能不夠跑全部）
- Naver DataLab 回傳的是 0-100 相對熱度，事件內可比、跨事件不可比
- YouTube 抓的是累計值，不適合當 daily traffic
- 不確定事件請標記 `needs_review`，不要標記 `complete`
