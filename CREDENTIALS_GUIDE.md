# API Credentials 取得教學

本專案只需要三個 credential：

```text
NAVER_CLIENT_ID
NAVER_CLIENT_SECRET
YOUTUBE_API_KEY
```

不要把 `.env` 推上 GitHub。`.env` 已被 `.gitignore` 排除。

## 一、Naver API

1. 打開 Naver Developers：

```text
https://developers.naver.com/
```

2. 用 Naver 帳號登入。
3. 進入 `Application` 或 `내 애플리케이션`。
4. 建立新應用程式。
5. 應用程式名稱可填：

```text
kpop-event-crawler
```

6. API 權限選擇（兩個都要勾）：

```text
검색 Search API
데이터랩 (검색어트렌드) DataLab Search Trends
```

注意：同一組 Client ID/Secret 同時用於兩個 endpoint，不用申請兩個 app。

7. 環境可選：

```text
WEB
```

8. 網址可先填 GitHub repo：

```text
https://github.com/paulyao825/115-2-_- 
```

9. 建立後複製：

```text
Client ID
Client Secret
```

10. 貼到 `.env`：

```text
NAVER_CLIENT_ID=你的ClientID
NAVER_CLIENT_SECRET=你的ClientSecret
```

## 二、YouTube Data API

1. 打開 Google Cloud Console：

```text
https://console.cloud.google.com/
```

2. 登入 Google 帳號。
3. 建立新專案，名稱可填：

```text
kpop-event-crawler
```

4. 進入 `APIs & Services`。
5. 點 `Library`。
6. 搜尋：

```text
YouTube Data API v3
```

7. 點進去後按 `Enable`。
8. 到 `Credentials`。
9. 點 `Create Credentials`。
10. 選 `API key`。
11. 複製產生的 API key。
12. 貼到 `.env`：

```text
YOUTUBE_API_KEY=你的YouTubeAPIKey
```

## 三、建立本機 `.env`

Mac/Linux：

```bash
cp .env.example .env
open -e .env    # Mac 預設文字編輯器
```

Windows：

```powershell
copy .env.example .env
notepad .env
```

最後 `.env` 應該長這樣：

```text
NAVER_CLIENT_ID=你的NaverClientID
NAVER_CLIENT_SECRET=你的NaverClientSecret
YOUTUBE_API_KEY=你的YouTubeAPIKey
```

## 四、測試順序

Mac/Linux：

```bash
python scripts/collect_naver.py
python scripts/collect_naver_datalab.py
python scripts/collect_google_trends.py
python scripts/collect_youtube.py
```

Windows：

```powershell
.\.venv\Scripts\python.exe scripts\collect_naver.py
.\.venv\Scripts\python.exe scripts\collect_naver_datalab.py
.\.venv\Scripts\python.exe scripts\collect_google_trends.py
.\.venv\Scripts\python.exe scripts\collect_youtube.py
```

## 五、為什麼我不直接幫你建立 credential

API key 會綁定你的個人帳號、使用條款、配額與可能的帳單設定。這類 credential 應該由你本人登入官方網站建立，不建議交給別人或讓自動化工具代辦。

我可以協助你一步一步看畫面，但不要把完整 API key 貼到聊天或 GitHub。
