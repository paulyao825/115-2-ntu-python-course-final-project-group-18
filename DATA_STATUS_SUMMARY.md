# 資料狀態摘要

最後更新：2026-05-23

## 一、目前事件清單狀態

事件清單已重新平衡，不再以 comeback/new songs 為主。現在所有事件都只使用原本研究設計中的六大分類：

```text
事件清單：75 筆
Crawler keyword：75 筆
女團數：5 組
每團事件數：15 筆
日期範圍：2021-03-12 至 2025-12-19
complete：65 筆
needs_review：10 筆
```

各團事件數：

```text
group
BLACKPINK      15
LE SSERAFIM    15
NewJeans       15
TWICE          15
aespa          15
```

分類分布：

```text
event_category
comeback           21
PR_crisis          20
contract_member     9
concert             9
activity            8
dating              8
```

## 二、這次重配原因

上一版 75 筆事件太集中在 comeback/new songs，會讓後續分析變成「發歌效應」而不是多因素事件研究。這次已補進較多戀愛、爭議、公關、合約與演唱會事件，例如：

- aespa Winter 和 BTS Jungkook 未確認戀愛傳聞
- aespa Winter 和 ENHYPEN Jungwon 戀愛傳聞遭否認
- aespa Karina 戀愛公開、道歉、分手
- BLACKPINK Jennie 室內電子菸事件
- BLACKPINK Jennie 和 BTS V 戀愛傳聞
- NewJeans/HYBE/ADOR 合約與經營權爭議
- NewJeans Hanni 國會職場霸凌證詞
- LE SSERAFIM Garam 校園霸凌爭議與退團
- LE SSERAFIM Coachella 唱功爭議
- TWICE Chaeyoung/Zion.T 確認戀愛
- TWICE Chaeyoung 爭議服裝道歉

注意：未確認戀愛傳聞一律寫成 rumor，不寫成 confirmed。資料狀態若證據較弱，標記為 `needs_review`。

## 三、目前 raw/final 資料狀態

目前本機 raw/final CSV 是「事件重配前」跑出來的結果。因為這次更換了多個 event_id 與 keyword，所以 raw/final 需要重新跑一次，才會完全對上新版 75 筆事件。

目前本機仍可看到的舊輸出規模：

```text
Naver raw：10654
Google Trends raw：6026
YouTube raw：125
Daily traffic：1185
Validation report：10
```

重要判讀：

- `data/templates/events_master.csv` 和 `config/keywords.csv` 已是新版平衡事件清單。
- `data/raw/*.csv` 與 `data/final/*.csv` 目前不要當作新版最終資料。
- 重新跑完爬蟲後，再更新 Naver raw、Google Trends raw、YouTube raw、Daily traffic 與 validation 數量。
- YouTube API 可能遇到 quota exceeded，需要等 quota 重置後再跑。

## 四、下一步：用新版事件清單重跑

請在專案根目錄跑：

```powershell
.\.venv\Scripts\python.exe scripts\collect_naver.py
.\.venv\Scripts\python.exe scripts\collect_google_trends.py
.\.venv\Scripts\python.exe scripts\collect_youtube.py
.\.venv\Scripts\python.exe scripts\build_daily_traffic.py
.\.venv\Scripts\python.exe scripts\validate_dataset.py
```

如果 YouTube 顯示 quota exceeded，先跳過 YouTube，至少跑：

```powershell
.\.venv\Scripts\python.exe scripts\collect_naver.py
.\.venv\Scripts\python.exe scripts\collect_google_trends.py
.\.venv\Scripts\python.exe scripts\build_daily_traffic.py
.\.venv\Scripts\python.exe scripts\validate_dataset.py
```

## 五、事件清單摘要

### TWICE

| event_id | 分類 | 事件 | 日期 | 情緒 | 狀態 |
|---|---|---|---|---|---|
| TWICE_20210609_ALCOHOL_FREE | comeback | TWICE Alcohol-Free and Taste of Love comeback | 2021-05-31 to 2021-06-18 | positive | complete |
| TWICE_20210818_JEONGYEON_HIATUS | PR_crisis | Jeongyeon takes hiatus due to panic and anxiety disorder | 2021-08-18 to 2021-09-01 | negative | complete |
| TWICE_20211001_THE_FEELS | comeback | TWICE releases first English single The Feels | 2021-10-01 to 2021-10-11 | positive | complete |
| TWICE_20220624_NAYEON_POP | activity | Nayeon makes solo debut with Pop | 2022-06-24 to 2022-07-08 | positive | complete |
| TWICE_20220712_CONTRACT_RENEWAL | contract_member | All TWICE members renew contracts with JYP | 2022-07-12 to 2022-07-19 | positive | complete |
| TWICE_20230221_READY_TO_BE_TOUR | concert | TWICE announces Ready To Be world tour | 2023-02-21 to 2023-03-03 | positive | complete |
| TWICE_20230310_SET_ME_FREE | comeback | TWICE releases Ready To Be and Set Me Free | 2023-03-10 to 2023-03-24 | positive | complete |
| TWICE_20230321_CHAEYOUNG_SHIRT | PR_crisis | Chaeyoung apologizes for controversial shirt post | 2023-03-21 to 2023-03-29 | negative | needs_review |
| TWICE_20230324_SOFI_SOLDOUT | concert | TWICE becomes first girl group to sell out SoFi Stadium | 2023-03-23 to 2023-03-31 | positive | complete |
| TWICE_20230424_METLIFE_SOLDOUT | concert | TWICE sells out MetLife Stadium concert | 2023-04-24 to 2023-05-01 | positive | complete |
| TWICE_20230726_MISAMO_DEBUT | activity | MISAMO debuts in Japan with Masterpiece | 2023-07-26 to 2023-08-09 | positive | needs_review |
| TWICE_20240223_ONE_SPARK | comeback | TWICE releases One Spark and With YOU-th | 2024-02-23 to 2024-03-08 | positive | complete |
| TWICE_20240325_JIHYO_DATING_RUMOR | dating | Jihyo and Yun Sung-bin dating rumor receives agency response | 2024-03-25 to 2024-04-01 | mixed | complete |
| TWICE_20240405_CHAEYOUNG_ZIONT | dating | Chaeyoung and Zion.T confirmed to be dating | 2024-04-05 to 2024-04-12 | mixed | complete |
| TWICE_20241206_STRATEGY | comeback | TWICE releases Strategy | 2024-12-06 to 2024-12-20 | positive | complete |

### aespa

| event_id | 分類 | 事件 | 日期 | 情緒 | 狀態 |
|---|---|---|---|---|---|
| AESPA_20210517_NEXT_LEVEL | comeback | aespa releases Next Level | 2021-05-06 to 2021-05-31 | positive | complete |
| AESPA_20220423_COACHELLA | activity | aespa performs at Coachella 2022 | 2022-04-19 to 2022-04-30 | positive | complete |
| AESPA_20230225_SYNKK_HYPER_LINE | concert | aespa starts Synk Hyper Line concert | 2023-02-25 to 2023-03-05 | positive | complete |
| AESPA_20230508_MY_WORLD_SPICY | comeback | aespa releases My World and Spicy | 2023-05-08 to 2023-05-22 | positive | complete |
| AESPA_20230607_GISELLE_HEALTH | PR_crisis | Giselle pauses activities for health reasons | 2023-06-07 to 2023-06-21 | negative | complete |
| AESPA_20240227_KARINA_DATING_BREAKUP | dating | Karina and Lee Jae-wook dating news and breakup | 2024-02-27 to 2024-04-02 | mixed | complete |
| AESPA_20240305_KARINA_APOLOGY | PR_crisis | Karina apologizes to fans after dating backlash | 2024-03-05 to 2024-03-19 | negative | complete |
| AESPA_20240402_KARINA_BREAKUP | dating | Karina and Lee Jae-wook confirm breakup | 2024-04-02 to 2024-04-09 | mixed | complete |
| AESPA_20240412_WINTER_SURGERY | PR_crisis | Winter takes break after pneumothorax surgery | 2024-04-12 to 2024-04-26 | negative | complete |
| AESPA_20240527_ARMAGEDDON | comeback | aespa releases first full album Armageddon | 2024-04-22 to 2024-06-02 | positive | complete |
| AESPA_20240513_SUPERNOVA | comeback | aespa releases Supernova | 2024-05-13 to 2024-05-27 | positive | complete |
| AESPA_20241021_WHIPLASH | comeback | aespa releases Whiplash | 2024-10-21 to 2024-11-04 | positive | complete |
| AESPA_20241211_WINTER_JUNGWON | dating | Winter and Jungwon dating rumor denied by agencies | 2024-12-11 to 2024-12-18 | mixed | complete |
| AESPA_20250528_KARINA_JACKET | PR_crisis | Karina deletes Instagram photo amid political jacket controversy | 2025-05-28 to 2025-06-05 | negative | complete |
| AESPA_20251205_WINTER_JUNGKOOK | dating | Winter and Jungkook viral dating rumor spreads online | 2025-12-05 to 2025-12-19 | mixed | needs_review |

### BLACKPINK

| event_id | 分類 | 事件 | 日期 | 情緒 | 狀態 |
|---|---|---|---|---|---|
| BLACKPINK_20210312_ROSE_ON_THE_GROUND | activity | Rose makes solo debut with On The Ground | 2021-03-12 to 2021-03-26 | positive | complete |
| BLACKPINK_20210910_LISA_LALISA | activity | Lisa makes solo debut with Lalisa | 2021-09-10 to 2021-09-24 | positive | complete |
| BLACKPINK_20220523_JENNIE_V_RUMOR | dating | Jennie and BTS V dating rumor begins with viral Jeju photo | 2022-05-23 to 2022-06-06 | mixed | complete |
| BLACKPINK_20220808_BORN_PINK_TOUR_ANNOUNCE | concert | BLACKPINK announces Born Pink world tour | 2022-08-08 to 2022-08-22 | positive | complete |
| BLACKPINK_20220819_PINK_VENOM | comeback | BLACKPINK releases Pink Venom | 2022-08-19 to 2022-08-26 | positive | complete |
| BLACKPINK_20220916_BORN_PINK | comeback | BLACKPINK releases Born Pink | 2022-09-16 to 2022-09-25 | positive | complete |
| BLACKPINK_20230110_COACHELLA_HEADLINER | concert | BLACKPINK announced as Coachella 2023 headliner | 2023-01-10 to 2023-04-22 | positive | complete |
| BLACKPINK_20230331_JISOO_FLOWER | activity | Jisoo makes solo debut with Flower | 2023-03-31 to 2023-04-14 | positive | complete |
| BLACKPINK_20230604_THE_IDOL | PR_crisis | Jennie's The Idol debut draws controversy | 2023-06-04 to 2023-06-18 | mixed | needs_review |
| BLACKPINK_20230917_BORN_PINK_FINALE | concert | BLACKPINK ends Born Pink world tour in Seoul | 2023-09-16 to 2023-09-24 | positive | complete |
| BLACKPINK_20230928_LISA_CRAZY_HORSE | PR_crisis | Lisa's Crazy Horse Paris performances spark controversy | 2023-09-28 to 2023-10-12 | mixed | needs_review |
| BLACKPINK_20231206_GROUP_CONTRACT_RENEWAL | contract_member | BLACKPINK renews group contract with YG | 2023-12-06 to 2023-12-13 | positive | complete |
| BLACKPINK_20231229_INDIVIDUAL_CONTRACTS | contract_member | BLACKPINK members do not renew individual contracts with YG | 2023-12-29 to 2024-01-05 | mixed | needs_review |
| BLACKPINK_20240709_JENNIE_VAPING | PR_crisis | Jennie apologizes for indoor vaping incident | 2024-07-08 to 2024-07-16 | negative | complete |
| BLACKPINK_20250219_DEADLINE_TOUR | concert | BLACKPINK announces Deadline world tour | 2025-02-19 to 2025-03-05 | positive | complete |

### NewJeans

| event_id | 分類 | 事件 | 日期 | 情緒 | 狀態 |
|---|---|---|---|---|---|
| NEWJEANS_20220722_ATTENTION_DEBUT | comeback | NewJeans surprise debuts with Attention | 2022-07-22 to 2022-08-01 | positive | complete |
| NEWJEANS_20220801_COOKIE_CONTROVERSY | PR_crisis | NewJeans Cookie lyrics controversy | 2022-08-01 to 2022-08-15 | negative | complete |
| NEWJEANS_20221219_DITTO | comeback | NewJeans releases Ditto | 2022-12-19 to 2023-01-13 | positive | needs_review |
| NEWJEANS_20230106_OMG_MV_CONTROVERSY | PR_crisis | NewJeans OMG music video draws mental illness aesthetic controversy | 2023-01-06 to 2023-01-20 | negative | complete |
| NEWJEANS_20230707_SUPER_SHY | comeback | NewJeans releases Super Shy | 2023-07-07 to 2023-07-21 | positive | complete |
| NEWJEANS_20230721_ETA_IPHONE | activity | NewJeans releases ETA music video filmed with iPhone | 2023-07-21 to 2023-08-04 | positive | complete |
| NEWJEANS_20240411_HYEIN_INJURY | PR_crisis | Hyein halts activities due to foot injury | 2024-04-11 to 2024-04-25 | negative | complete |
| NEWJEANS_20240422_HYBE_ADOR_DISPUTE | contract_member | HYBE and ADOR dispute involving NewJeans begins | 2024-04-22 to 2024-05-31 | negative | complete |
| NEWJEANS_20240524_HOW_SWEET | comeback | NewJeans releases How Sweet | 2024-05-24 to 2024-06-07 | positive | complete |
| NEWJEANS_20241010_HANNI_ASSEMBLY_SUMMONS | PR_crisis | Hanni selected to testify at National Assembly over workplace bullying allegation | 2024-10-10 to 2024-10-15 | negative | complete |
| NEWJEANS_20241015_HANNI_ASSEMBLY | PR_crisis | Hanni testifies at National Assembly | 2024-10-15 to 2024-10-22 | negative | complete |
| NEWJEANS_20241128_CONTRACT_TERMINATION | contract_member | NewJeans announces contract termination with ADOR | 2024-11-28 to 2024-12-05 | negative | complete |
| NEWJEANS_20250207_NJZ_REBRAND | contract_member | NewJeans members announce NJZ rebrand amid ADOR dispute | 2025-02-07 to 2025-02-21 | negative | complete |
| NEWJEANS_20250321_ADOR_INJUNCTION | contract_member | Court accepts ADOR injunction limiting NewJeans independent activity | 2025-03-21 to 2025-03-28 | negative | complete |
| NEWJEANS_20250324_NJZ_HIATUS | contract_member | NJZ announces hiatus amid ADOR contract dispute | 2025-03-24 to 2025-04-07 | negative | complete |

### LE SSERAFIM

| event_id | 分類 | 事件 | 日期 | 情緒 | 狀態 |
|---|---|---|---|---|---|
| LESSERAFIM_20220502_FEARLESS_DEBUT | comeback | LE SSERAFIM debuts with Fearless | 2022-05-02 to 2022-05-09 | positive | complete |
| LESSERAFIM_20220520_GARAM_HIATUS | PR_crisis | Kim Garam goes on hiatus amid school bullying controversy | 2022-05-20 to 2022-06-03 | negative | complete |
| LESSERAFIM_20220720_GARAM_TERMINATION | PR_crisis | Kim Garam leaves LE SSERAFIM after bullying controversy | 2022-07-20 to 2022-07-27 | negative | complete |
| LESSERAFIM_20221017_ANTIFRAGILE | comeback | LE SSERAFIM releases Antifragile | 2022-10-17 to 2022-10-31 | positive | complete |
| LESSERAFIM_20230812_FLAME_RISES | concert | LE SSERAFIM starts Flame Rises tour | 2023-08-12 to 2023-08-26 | positive | complete |
| LESSERAFIM_20231016_CHAEWON_HEALTH | PR_crisis | Kim Chaewon suspends activities for health recovery | 2023-10-16 to 2023-10-26 | negative | complete |
| LESSERAFIM_20240219_EASY_RELEASE | comeback | LE SSERAFIM releases Easy | 2024-02-19 to 2024-03-04 | positive | complete |
| LESSERAFIM_20240219_SMART_MINOR_CONTROVERSY | PR_crisis | Smart choreography receives criticism over minor member concept | 2024-02-19 to 2024-03-04 | negative | needs_review |
| LESSERAFIM_20240403_KAZUHA_DATING | dating | HYBE denies Kazuha and &TEAM K dating rumor | 2024-04-03 to 2024-04-10 | mixed | complete |
| LESSERAFIM_20240413_COACHELLA_CRITICISM | PR_crisis | LE SSERAFIM Coachella performance receives mixed reviews | 2024-04-13 to 2024-04-20 | negative | complete |
| LESSERAFIM_20240717_SOURCE_ADOR_LAWSUIT | contract_member | Source Music sues ADOR CEO over LE SSERAFIM comments | 2024-07-17 to 2024-07-31 | negative | needs_review |
| LESSERAFIM_20240729_DOCUMENTARY | activity | LE SSERAFIM releases Make It Look Easy documentary | 2024-07-29 to 2024-08-12 | mixed | complete |
| LESSERAFIM_20240829_EUNCHAE_APOLOGY | PR_crisis | Eunchae apologizes for student-mocking controversy | 2024-08-29 to 2024-09-05 | negative | needs_review |
| LESSERAFIM_20240830_CRAZY | comeback | LE SSERAFIM releases Crazy | 2024-08-30 to 2024-09-13 | positive | complete |
| LESSERAFIM_20250314_HOT | comeback | LE SSERAFIM releases Hot | 2025-03-14 to 2025-03-28 | positive | complete |
