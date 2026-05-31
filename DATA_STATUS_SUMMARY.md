# 資料狀態摘要

> 本檔已過期。最新資料稽核請看 [`docs/data_audit.md`](docs/data_audit.md)。
>
> 此處保留簡短摘要供快速 reference。

最後更新：2026-05-28

## 目前狀態（一句話版）

165 筆事件、11 個團體、4 家公司、5 年資料，daily media attention 與股價已完成。

## 快速數字

| 項目 | 數量 |
|---|---|
| 事件總數 | 165 |
| 團體數 | 11（含男女團） |
| 公司數 | 4（HYBE、SM、JYP、YG） |
| 時間範圍 | 2021-02-27 ~ 2026-01-01 |
| traffic_daily.csv | 2,470 列 |
| stock_daily.csv | 已抓（4 家 × 5 年） |
| naver_results.csv | 141,917 列 |
| naver_datalab.csv | 已抓 |
| google_trends.csv | 53/165 事件有 daily |

## 資料 coverage

- Naver News non-zero: 28% event-day
- Naver Blog non-zero: 32%
- Naver DataLab non-zero: 14.6%
- Google Trends non-zero: 20.3%
- 至少一個 attention 訊號 non-zero: **61.3%**
- 157/165 事件至少有 1 天有訊號

## 已知問題與後續

- YouTube event-day 資料未抓（API 限制只能拿累計快照，不適合 daily 分析）
- Naver DataLab 覆蓋率偏低（關鍵字太具體可改用短關鍵字）
- 8 個事件完全沒 attention 訊號（多為內部成員事件，正常）

詳細稽核、回歸模型、變數說明請看 `docs/`。
