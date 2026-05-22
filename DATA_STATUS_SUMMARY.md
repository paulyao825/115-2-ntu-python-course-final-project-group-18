# 資料狀態摘要

最後更新：2026-05-23

## 一、目前事件清單狀態

目前 repo 內事件清單已擴充為：

```text
事件清單：75 筆
Crawler keyword：75 筆
女團數：5 組
每團事件數：15 筆
日期範圍：2021-03-12 至 2025-07-25
needs_review：5 筆
```

各團事件數：

```text
BLACKPINK      15
LE SSERAFIM    15
NewJeans       15
TWICE          15
aespa          15
```

## 二、目前已抓取資料狀態

目前本機已重跑 75-event run，`traffic_daily.csv` 已包含 75 個 event_id。

目前本機可確認的輸出狀態：

```text
Events master：75 筆
Crawler keywords：75 筆
Naver raw：10654 筆
Google Trends raw：6026 筆
YouTube raw：125 筆
Daily traffic：1185 筆
Validation checks：10 筆
Validation failed checks：0 筆
```

判讀：

```text
Naver 與 daily traffic 已反映 75 筆事件重跑後的規模。
Google Trends raw 仍是 6026 筆，因為 PyTrends 依週/月頻率回傳，列數不會跟事件數線性成長。
YouTube raw 仍是 125 筆，代表目前 YouTube 正式輸出仍接近 25-event run；若要完整 75-event YouTube 資料，需要等 YouTube API quota 重置後重跑 collect_youtube.py。
traffic_daily.csv 已有 75 個 event_id，其中 515 列 data_quality=ok，670 列 data_quality=missing_traffic。
```

目前可用輸出檔：

```text
data/raw/naver_results.csv
data/raw/google_trends.csv
data/raw/youtube_stats.csv
data/final/traffic_daily.csv
data/final/data_quality_report.csv
```

注意：目前部分 raw/final CSV 已被 Git 追蹤，因此 repo 內可能看得到舊版 crawl 結果。`.gitignore` 只能避免新檔案自動加入，不能自動停止追蹤已加入過的檔案。

建議協作方式：

```text
小型摘要、事件清單、關鍵字、程式碼：放 GitHub repo
大型 raw/final CSV：確認後再決定是否提交，或改用壓縮檔／雲端附件交給隊友
```

## 三、目前可分析性

目前輸出檔已可支援 75 筆事件的初步分析，但 YouTube 欄位尚未完整覆蓋 75-event run。

- Google Trends 可作為每日事件熱度主指標。
- YouTube 可作為作品或事件規模輔助指標，但它是累積觀看數，不是每日新增流量。
- Naver raw 可作為新聞來源與媒體覆蓋佐證，但 Naver Search API 回傳不等於完整歷史每日新聞量。
- `traffic_total_raw` 不建議直接作為最終分析主欄位，因為 YouTube 累積觀看數會壓過其他欄位。
- `data_quality=missing_traffic` 的列不應直接用於強結論，可在分析時過濾或另外標記。

建議正式分析欄位：

```text
google_trends_score
youtube_views
event_category
sentiment_expected
severity_score
company
group
start_date
peak_date
end_date
```

## 四、下一步

目前 Naver、Google Trends、daily traffic、validation 已可用。若要補完整 YouTube，請等 YouTube quota 重置後跑：

```powershell
.\.venv\Scripts\python.exe scripts\collect_youtube.py
.\.venv\Scripts\python.exe scripts\build_daily_traffic.py
.\.venv\Scripts\python.exe scripts\validate_dataset.py
```

跑完後建議檢查：

```powershell
.\.venv\Scripts\python.exe -B -c "import pandas as pd, os; files=[('events','data/templates/events_master.csv'),('keywords','config/keywords.csv'),('naver_raw','data/raw/naver_results.csv'),('google_trends_raw','data/raw/google_trends.csv'),('youtube_raw','data/raw/youtube_stats.csv'),('traffic','data/final/traffic_daily.csv'),('validation','data/final/data_quality_report.csv')]; [print(name, len(pd.read_csv(path)) if os.path.exists(path) else 'missing') for name,path in files]"
```

若要重新完整抓取全部資料，可跑：

```powershell
.\.venv\Scripts\python.exe scripts\collect_naver.py
.\.venv\Scripts\python.exe scripts\collect_google_trends.py
.\.venv\Scripts\python.exe scripts\collect_youtube.py
.\.venv\Scripts\python.exe scripts\build_daily_traffic.py
.\.venv\Scripts\python.exe scripts\validate_dataset.py
```

## 五、事件清單摘要

### TWICE

| event_id | 分類 | 事件 | 日期 | 情緒 | 狀態 |
|---|---|---|---|---|---|
| TWICE_20210609_ALCOHOL_FREE | comeback | TWICE Alcohol-Free and Taste of Love comeback | 2021-05-31 to 2021-06-18 | positive | complete |
| TWICE_20211001_THE_FEELS | comeback | TWICE releases first English single The Feels | 2021-10-01 to 2021-10-11 | positive | complete |
| TWICE_20211112_FORMULA_OF_LOVE | comeback | TWICE releases Formula of Love and Scientist | 2021-11-12 to 2021-11-25 | positive | complete |
| TWICE_20220624_NAYEON_POP | activity | Nayeon makes solo debut with Pop | 2022-06-24 to 2022-07-08 | positive | complete |
| TWICE_20220712_CONTRACT_RENEWAL | contract_member | All TWICE members renew contracts with JYP | 2022-07-12 to 2022-07-19 | positive | complete |
| TWICE_20220826_BETWEEN_1_AND_2 | comeback | TWICE releases Between 1 and 2 and Talk That Talk | 2022-08-26 to 2022-09-09 | positive | complete |
| TWICE_20230120_MOONLIGHT_SUNRISE | comeback | TWICE releases English pre-release Moonlight Sunrise | 2023-01-20 to 2023-02-03 | positive | complete |
| TWICE_20230221_READY_TO_BE_TOUR | concert | TWICE announces Ready To Be world tour | 2023-02-21 to 2023-03-03 | positive | complete |
| TWICE_20230310_SET_ME_FREE | comeback | TWICE releases Ready To Be and Set Me Free | 2023-03-10 to 2023-03-24 | positive | complete |
| TWICE_20230726_MISAMO_DEBUT | activity | MISAMO debuts in Japan with Masterpiece | 2023-07-26 to 2023-08-09 | positive | needs_review |
| TWICE_20240202_I_GOT_YOU | comeback | TWICE releases I Got You | 2024-02-02 to 2024-02-16 | positive | complete |
| TWICE_20240223_ONE_SPARK | comeback | TWICE releases One Spark and With YOU-th | 2024-02-23 to 2024-03-08 | positive | complete |
| TWICE_20240303_WITH_YOUTH_BB200 | achievement | TWICE With YOU-th reaches No. 1 on Billboard 200 | 2024-02-23 to 2024-03-09 | positive | complete |
| TWICE_20241206_STRATEGY | comeback | TWICE releases Strategy | 2024-12-06 to 2024-12-20 | positive | complete |
| TWICE_20250711_THIS_IS_FOR | comeback | TWICE releases This Is For | 2025-07-11 to 2025-07-25 | positive | complete |

### aespa

| event_id | 分類 | 事件 | 日期 | 情緒 | 狀態 |
|---|---|---|---|---|---|
| AESPA_20210517_NEXT_LEVEL | comeback | aespa releases Next Level | 2021-05-06 to 2021-05-31 | positive | complete |
| AESPA_20211005_SAVAGE | comeback | aespa releases Savage | 2021-10-05 to 2021-10-19 | positive | complete |
| AESPA_20211211_MAMA_DAESANG | achievement | aespa wins major rookie awards at MAMA | 2021-12-11 to 2021-12-18 | positive | complete |
| AESPA_20220423_COACHELLA | activity | aespa performs at Coachella 2022 | 2022-04-19 to 2022-04-30 | positive | complete |
| AESPA_20220718_GIRLS_BB200_TOP3 | achievement | aespa Girls reaches Top 3 on Billboard 200 | 2022-07-08 to 2022-07-24 | positive | complete |
| AESPA_20230225_SYNKK_HYPER_LINE | concert | aespa starts Synk Hyper Line concert | 2023-02-25 to 2023-03-05 | positive | complete |
| AESPA_20230330_HOLD_ON_TIGHT | activity | aespa releases Hold On Tight for Tetris film | 2023-03-30 to 2023-04-13 | positive | needs_review |
| AESPA_20230508_MY_WORLD_SPICY | comeback | aespa releases My World and Spicy | 2023-05-08 to 2023-05-22 | positive | complete |
| AESPA_20230813_OUTSIDE_LANDS | activity | aespa performs at Outside Lands | 2023-08-11 to 2023-08-20 | positive | needs_review |
| AESPA_20231110_DRAMA | comeback | aespa releases Drama | 2023-11-10 to 2023-11-24 | positive | complete |
| AESPA_20240227_KARINA_DATING_BREAKUP | dating | Karina and Lee Jae-wook dating news and breakup | 2024-02-27 to 2024-04-02 | mixed | complete |
| AESPA_20240513_SUPERNOVA | comeback | aespa releases Supernova | 2024-05-13 to 2024-05-27 | positive | complete |
| AESPA_20240527_ARMAGEDDON | comeback | aespa releases first full album Armageddon | 2024-04-22 to 2024-06-02 | positive | complete |
| AESPA_20241021_WHIPLASH | comeback | aespa releases Whiplash | 2024-10-21 to 2024-11-04 | positive | complete |
| AESPA_20250627_DIRTY_WORK | comeback | aespa releases Dirty Work | 2025-06-27 to 2025-07-11 | positive | complete |

### BLACKPINK

| event_id | 分類 | 事件 | 日期 | 情緒 | 狀態 |
|---|---|---|---|---|---|
| BLACKPINK_20210312_ROSE_ON_THE_GROUND | activity | Rose makes solo debut with On The Ground | 2021-03-12 to 2021-03-26 | positive | complete |
| BLACKPINK_20210804_THE_MOVIE | activity | BLACKPINK releases The Movie | 2021-08-04 to 2021-08-18 | positive | complete |
| BLACKPINK_20210910_LISA_LALISA | activity | Lisa makes solo debut with Lalisa | 2021-09-10 to 2021-09-24 | positive | complete |
| BLACKPINK_20220808_BORN_PINK_TOUR_ANNOUNCE | concert | BLACKPINK announces Born Pink world tour | 2022-08-08 to 2022-08-22 | positive | complete |
| BLACKPINK_20220819_PINK_VENOM | comeback | BLACKPINK releases Pink Venom | 2022-08-19 to 2022-08-26 | positive | complete |
| BLACKPINK_20220916_BORN_PINK | comeback | BLACKPINK releases Born Pink | 2022-09-16 to 2022-09-25 | positive | complete |
| BLACKPINK_20220916_SHUT_DOWN | comeback | BLACKPINK releases Shut Down | 2022-09-16 to 2022-09-30 | positive | complete |
| BLACKPINK_20230110_COACHELLA_HEADLINER | achievement | BLACKPINK announced as Coachella 2023 headliner | 2023-01-10 to 2023-04-22 | positive | complete |
| BLACKPINK_20230331_JISOO_FLOWER | activity | Jisoo makes solo debut with Flower | 2023-03-31 to 2023-04-14 | positive | complete |
| BLACKPINK_20230702_BST_HYDE_PARK | concert | BLACKPINK headlines BST Hyde Park | 2023-07-02 to 2023-07-09 | positive | complete |
| BLACKPINK_20230917_BORN_PINK_FINALE | concert | BLACKPINK ends Born Pink world tour in Seoul | 2023-09-16 to 2023-09-24 | positive | complete |
| BLACKPINK_20231206_GROUP_CONTRACT_RENEWAL | contract_member | BLACKPINK renews group contract with YG | 2023-12-06 to 2023-12-13 | positive | complete |
| BLACKPINK_20231229_INDIVIDUAL_CONTRACTS | contract_member | BLACKPINK members do not renew individual contracts with YG | 2023-12-29 to 2024-01-05 | mixed | needs_review |
| BLACKPINK_20240721_2025_COMEBACK_TOUR_PLAN | contract_member | YG announces BLACKPINK 2025 comeback and tour plan | 2024-07-21 to 2024-08-04 | positive | complete |
| BLACKPINK_20250219_DEADLINE_TOUR | concert | BLACKPINK announces Deadline world tour | 2025-02-19 to 2025-03-05 | positive | complete |

### NewJeans

| event_id | 分類 | 事件 | 日期 | 情緒 | 狀態 |
|---|---|---|---|---|---|
| NEWJEANS_20220722_ATTENTION_DEBUT | comeback | NewJeans surprise debuts with Attention | 2022-07-22 to 2022-08-01 | positive | complete |
| NEWJEANS_20220723_HYPE_BOY | comeback | NewJeans releases Hype Boy | 2022-07-23 to 2022-08-06 | positive | complete |
| NEWJEANS_20220801_COOKIE_CONTROVERSY | PR_crisis | NewJeans Cookie lyrics controversy | 2022-08-01 to 2022-08-15 | negative | complete |
| NEWJEANS_20221219_DITTO | comeback | NewJeans releases Ditto | 2022-12-19 to 2023-01-13 | positive | needs_review |
| NEWJEANS_20230102_OMG | comeback | NewJeans releases OMG | 2023-01-02 to 2023-01-16 | positive | complete |
| NEWJEANS_20230707_SUPER_SHY | comeback | NewJeans releases Super Shy | 2023-07-07 to 2023-07-21 | positive | complete |
| NEWJEANS_20230803_GET_UP_BB200_NO1 | achievement | NewJeans Get Up debuts at No. 1 on Billboard 200 | 2023-07-21 to 2023-08-05 | positive | complete |
| NEWJEANS_20230803_LOLLAPALOOZA | activity | NewJeans performs at Lollapalooza | 2023-08-03 to 2023-08-10 | positive | complete |
| NEWJEANS_20231119_BBMAS_PERFORMANCE | achievement | NewJeans performs at Billboard Music Awards | 2023-11-19 to 2023-11-26 | positive | complete |
| NEWJEANS_20240422_HYBE_ADOR_DISPUTE | legal_dispute | HYBE and ADOR dispute involving NewJeans begins | 2024-04-22 to 2024-05-31 | negative | complete |
| NEWJEANS_20240427_BUBBLE_GUM | comeback | NewJeans releases Bubble Gum MV | 2024-04-27 to 2024-05-11 | positive | complete |
| NEWJEANS_20240524_HOW_SWEET | comeback | NewJeans releases How Sweet | 2024-05-24 to 2024-06-07 | positive | complete |
| NEWJEANS_20240621_SUPERNATURAL | comeback | NewJeans releases Supernatural for Japan debut | 2024-06-21 to 2024-07-05 | positive | complete |
| NEWJEANS_20241015_HANNI_ASSEMBLY | PR_crisis | Hanni testifies at National Assembly | 2024-10-15 to 2024-10-22 | negative | complete |
| NEWJEANS_20241128_CONTRACT_TERMINATION | contract_member | NewJeans announces contract termination with ADOR | 2024-11-28 to 2024-12-05 | negative | complete |

### LE SSERAFIM

| event_id | 分類 | 事件 | 日期 | 情緒 | 狀態 |
|---|---|---|---|---|---|
| LESSERAFIM_20220502_FEARLESS_DEBUT | comeback | LE SSERAFIM debuts with Fearless | 2022-05-02 to 2022-05-09 | positive | complete |
| LESSERAFIM_20220720_GARAM_TERMINATION | PR_crisis | Kim Garam leaves LE SSERAFIM after bullying controversy | 2022-07-20 to 2022-07-27 | negative | complete |
| LESSERAFIM_20221017_ANTIFRAGILE | comeback | LE SSERAFIM releases Antifragile | 2022-10-17 to 2022-10-31 | positive | complete |
| LESSERAFIM_20230501_UNFORGIVEN | comeback | LE SSERAFIM releases Unforgiven | 2023-05-01 to 2023-05-15 | positive | complete |
| LESSERAFIM_20230524_EVE_PSYCH_BLUEBEARD | achievement | Eve Psyche and The Bluebeard Wife becomes viral | 2023-05-24 to 2023-06-07 | positive | complete |
| LESSERAFIM_20230812_FLAME_RISES | concert | LE SSERAFIM starts Flame Rises tour | 2023-08-12 to 2023-08-26 | positive | complete |
| LESSERAFIM_20231027_PERFECT_NIGHT | comeback | LE SSERAFIM releases Perfect Night | 2023-10-27 to 2023-11-10 | positive | complete |
| LESSERAFIM_20240219_EASY_RELEASE | comeback | LE SSERAFIM releases Easy | 2024-02-19 to 2024-03-04 | positive | complete |
| LESSERAFIM_20240305_EASY_HOT100 | achievement | LE SSERAFIM enters Billboard Hot 100 with Easy | 2024-02-19 to 2024-03-09 | positive | complete |
| LESSERAFIM_20240305_SMART_VIRAL | achievement | LE SSERAFIM Smart gains viral attention | 2024-03-05 to 2024-03-19 | positive | complete |
| LESSERAFIM_20240413_COACHELLA_CRITICISM | PR_crisis | LE SSERAFIM Coachella performance receives mixed reviews | 2024-04-13 to 2024-04-20 | negative | complete |
| LESSERAFIM_20240729_DOCUMENTARY | activity | LE SSERAFIM releases Make It Look Easy documentary | 2024-07-29 to 2024-08-12 | mixed | complete |
| LESSERAFIM_20240830_CRAZY | comeback | LE SSERAFIM releases Crazy | 2024-08-30 to 2024-09-13 | positive | complete |
| LESSERAFIM_20240911_MTV_VMAS | achievement | LE SSERAFIM performs at MTV VMAs | 2024-09-11 to 2024-09-18 | positive | complete |
| LESSERAFIM_20250314_HOT | comeback | LE SSERAFIM releases Hot | 2025-03-14 to 2025-03-28 | positive | complete |
