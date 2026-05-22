# K-pop Event Data Collection Project

本資料夾是第18組期末專案的「事件資料蒐集」工作區。

研究主題：

```text
K-pop 偶像事件、社群熱度與娛樂公司股價波動之關聯性分析
```

本版本的研究時間範圍固定為：

```text
2021-01-01 至 2026-01-01
```

## 主要內容

- `DATA_COLLECTION_STANDARD.md`：給教授與組員看的資料蒐集計畫書／標準。
- `config/`：研究對象、事件分類、關鍵字設定。
- `data/templates/`：Google Sheet / CSV 欄位模板。
- `scripts/`：Python crawler 與資料驗證腳本。
- `.env.example`：API key 範本，實際使用時複製成 `.env`。

## 建議執行順序

1. 複製 `.env.example` 成 `.env`，填入 API key。
2. 在 `config/keywords.csv` 補齊各事件關鍵字。
3. 在 `data/templates/events_master.csv` 補人工確認的事件清單。
4. 執行 crawler 收集新聞、Google Trends、YouTube、股價資料。
5. 執行 `scripts/build_daily_traffic.py` 建立每日事件流量資料。
6. 執行 `scripts/validate_dataset.py` 檢查資料品質。
7. 將 CSV 匯入 Google Sheet 給組員共同編輯。

## Python 環境

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

如果 PowerShell 執行政策阻擋啟動虛擬環境，可改用 CMD 或調整本機執行政策。

