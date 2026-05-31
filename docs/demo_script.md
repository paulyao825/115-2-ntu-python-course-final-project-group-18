# 3 分鐘 Demo 影片腳本

不是逐字稿，只列關鍵點。每段配合投影片講。

---

## 開場（15 秒）

- 「K-pop 偶像的事件對所屬經紀公司的股價有多大影響？」
- 「**comeback** 帶來幾趴正報酬？**PR 危機**平均跌多少？**軍隊入伍**對股價衝擊有多深？」
- 這就是我們研究想回答的問題

---

## 研究設計（30 秒）

- **Y 變數**：4 家經紀公司的 abnormal return（HYBE、SM、JYP、YG）
- **核心 X 變數**：**事件類型 dummies** — comeback、PR_crisis、軍隊、合約、演唱會、活動、戀愛
- 跑出每個事件類型平均對股價的 γ 係數
- 控制變數：媒體關注度、團體人氣、公司規模
- 165 個事件 × 11 個團體 × 5 年資料

---

## 資料收集（45 秒）

- **股價**：Yahoo Finance 抓 4 家公司 daily OHLCV
- **媒體關注**：4 個獨立 daily 訊號互補
  - Naver News（韓國媒體報導量）
  - Naver Blog（韓國粉絲討論量）
  - Naver DataLab（韓國搜尋指數，**自己接的 API**）
  - Google Trends（國際視角）
- **控制變數**：團體 YouTube/Instagram/Spotify 人氣、公司市值
- **事件**：手動策展 165 個 K-pop 重大事件

---

## 技術挑戰 + 解決（45 秒）

挑 2-3 個講：

1. **Naver Blog 日期解析 bug**：API 用 postdate 不是 pubDate，修完 blog 訊號從 2.4% → 32% non-zero coverage
2. **Naver 分頁**：加 pagination 從每事件 100 篇 → 1000 篇，資料量 **12 倍**（11,796 → 141,917 列）
3. **Google Trends rate limit**：寫**可中斷續跑** script + VPN 輪替 30 個地區，抓到 53 個事件 daily 資料
4. **Naver DataLab 整合**：第一次自己接這個 API，解決「文章發佈量」vs「搜尋熱度」的差別

---

## 回歸模型（30 秒）

投影片放公式：

```
AR[i,t] = α + Σ γ_k · D_category[i,k]
        + β · media_attention[i,t]
        + 控制變數 + ε
```

- **γ_k 是核心結果** — 告訴大家哪類事件對股價影響最大、是正是負
- 不用主觀 sentiment / severity 標註
- 改用 `event_category` 客觀分類 → **讓市場資料告訴我們**哪類事件正/負面

---

## 限制 + 貢獻（20 秒）

**限制**：
- Naver Search API 對舊事件索引覆蓋率較低
- YouTube 只有累計快照，當 group-level control 用

**貢獻**：
- 第一份系統性追蹤 K-pop 事件 × 韓股關聯的 panel data
- 多訊號 attention proxy 比單看 Google Trends 完整
- 可重現（scripts 全部 open，含 `docs/` 五份文件）

---

## 結尾（15 秒）

- 「希望這份資料能幫助理解韓國娛樂產業的市場反應機制」
- 「Repo 上有完整 docs 跟程式碼，歡迎參考」

---

## 時間分配

| 段落 | 時間 | 累計 |
|---|---|---|
| 開場 | 0:15 | 0:15 |
| 研究設計 | 0:30 | 0:45 |
| 資料收集 | 0:45 | 1:30 |
| 技術挑戰 | 0:45 | 2:15 |
| 回歸模型 | 0:30 | 2:45 |
| 限制 + 貢獻 + 結尾 | 0:35 | 3:20 |

⚠️ 稍微超過 3 分鐘，可以從「技術挑戰」挑 2 個講（不要 4 個），就能壓到 3 分內。
