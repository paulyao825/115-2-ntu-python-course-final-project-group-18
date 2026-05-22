# 開始執行 Crawler 的下一步

## 1. 建立 Python 環境

在專案資料夾執行：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

如果 PowerShell 不允許啟動 `.venv`，可改用：

```powershell
cmd /c .venv\Scripts\activate.bat
```

## 2. 建立 `.env`

複製 `.env.example` 成 `.env`，並填入：

```text
NAVER_CLIENT_ID=
NAVER_CLIENT_SECRET=
YOUTUBE_API_KEY=
```

目前最重要的是：

- `NAVER_CLIENT_ID`
- `NAVER_CLIENT_SECRET`
- `YOUTUBE_API_KEY`
 
目前已改用 GitHub repo 和 CSV 協作，不需要 `GOOGLE_SHEET_ID`。

## 3. 檢查已建立的女團事件清單

先不要直接大量爬。請先在：

```text
data/templates/events_master.csv
```

目前已先整理五個女團各 5 筆事件：

```text
TWICE
aespa
BLACKPINK
NewJeans
LE SSERAFIM
```

請檢查每筆事件的：

```text
event_id
company
ticker
group
event_category
event_title_en
event_title_zh
event_title_ko
start_date
peak_date
end_date
sentiment_expected
severity_score
source_level
official_source_url 或 naver_source_url
collector
status
```

日期範圍必須在：

```text
2021-01-01 至 2026-01-01
```

## 4. 補 crawler 關鍵字

更新：

```text
config/keywords.csv
```

目前裡面的資料已改成事件級關鍵字。每個實際事件都有自己的 `event_id` 和查詢字。

建議每個事件至少有：

```text
keyword_ko
keyword_en
naver_query
google_trends_query
youtube_query
```

Naver 建議優先用韓文關鍵字。

## 5. 執行 crawler

先跑 Naver：

```powershell
python scripts\collect_naver.py
```

再跑 Google Trends：

```powershell
python scripts\collect_google_trends.py
```

再跑 YouTube：

```powershell
python scripts\collect_youtube.py
```

股價資料由其他組員負責，你不需要跑 `collect_stock.py`。

## 6. 建立每日流量資料

```powershell
python scripts\build_daily_traffic.py
```

輸出會在：

```text
data/final/traffic_daily.csv
```

## 7. 檢查資料品質

```powershell
python scripts\validate_dataset.py
```

輸出會在：

```text
data/final/data_quality_report.csv
```

如果有 failed checks，先修 `events_master.csv` 或 `keywords.csv`，再重新跑。

## 8. 用 GitHub 協作

跑完 crawler 後，請檢查 `data/raw/` 與 `data/final/` 的輸出，再視需要提交到 GitHub。
目前 `.gitignore` 預設不提交 raw/final 輸出，避免把大量或未清理資料直接推上去。

## 9. 注意事項

- Google Trends 是 0 到 100 的相對熱度，不是真實搜尋量。
- YouTube API 抓到的是查詢當下累積數，不是每日新增數。
- Instagram、Weverse、Bubble 歷史資料通常不完整，只能當 fanbase proxy。
- 不確定事件請標記 `needs_review`，不要標記 `complete`。
- 每個事件至少要有一個官方或 Naver 來源。
