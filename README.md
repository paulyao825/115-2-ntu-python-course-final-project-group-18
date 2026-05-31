# K-pop Event Data Collection Project

第 18 組期末專案 — K-pop 偶像事件對所屬經紀公司股價的影響分析。

研究問題：

```text
不同類型的 K-pop 藝人事件（comeback、PR 危機、軍隊、合約等），
對所屬經紀公司股價的影響程度
```

研究時間範圍：

```text
2021-01-01 至 2026-01-01
```

## 資料規模

- 165 筆事件
- 11 個團體（BTS、SEVENTEEN、BLACKPINK、NewJeans、LE SSERAFIM、TWICE、aespa、Stray Kids、NCT、EXO、BIGBANG）
- 4 家公司（HYBE、SM、JYP、YG）
- 4 個 daily media attention 訊號（Naver News / Blog / DataLab / Google Trends）
- 4 家公司 5 年 daily 股價

## 主要文件

開分析、寫報告請先看 `docs/` 下：

- `docs/data_audit.md` — 所有資料目前狀態 / 覆蓋率 / 缺什麼
- `docs/regression_handoff.md` — 回歸模型、變數、方法論
- `docs/variable_reference.md` — 所有欄位中文說明
- `docs/variable_reference.csv` — 同上 CSV 版（Excel 開）
- `docs/session_changes.md` — 最近一次大改的紀錄

舊版說明文件（背景知識用）：

- `DATA_COLLECTION_STANDARD.md` — 資料蒐集標準與規範
- `CREDENTIALS_GUIDE.md` — API key 申請教學
- `RUN_CRAWLER_NEXT_STEPS.md` — Crawler 執行步驟

## 主要資料夾

- `config/` — 研究對象、關鍵字設定
- `data/templates/` — 事件 metadata
- `data/raw/` — Crawler 原始輸出（gitignore 部分排除）
- `data/final/` — 主分析 panel（traffic_daily.csv、stock_daily.csv）
- `data/weights/` — 團體與公司控制變數
- `scripts/` — 所有 Python crawler 與 build script
- `.env.example` — API key 範本

## 跑 pipeline

```bash
# 1. 複製 .env.example 為 .env，填入 NAVER_CLIENT_ID / SECRET / YOUTUBE_API_KEY
cp .env.example .env

# 2. 裝套件
pip install -r requirements.txt

# 3. 抓資料
python scripts/collect_stock.py            # 股價
python scripts/collect_naver.py            # Naver News + Blog
python scripts/collect_naver_datalab.py    # Naver 搜尋指數
python scripts/collect_google_trends.py    # Google Trends（可中斷續跑）
python scripts/collect_youtube.py          # YouTube 統計（quota 限制）

# 4. 組 panel + 驗證
python scripts/build_daily_traffic.py
python scripts/validate_dataset.py
```

Google Trends 跑到 429 是正常的（Google rate-limit），切 VPN 後重跑 `collect_google_trends.py` 會自動跳過已完成事件。
