from __future__ import annotations

import argparse
from datetime import datetime

import httplib2
from googleapiclient.discovery import build

from common import PROJECT_ROOT, RAW_DIR, ensure_dirs, env_required, httplib2_options, load_env, read_csv, write_csv
import time


FIELDNAMES = [
    "event_id",
    "query",
    "video_id",
    "title",
    "channel_title",
    "published_at",
    "youtube_views",
    "youtube_likes",
    "youtube_comments",
    "url",
    "collected_at",
]


def resolve_path(value: str):
    from pathlib import Path

    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect YouTube video statistics.")
    parser.add_argument("--keywords", default=str(PROJECT_ROOT / "config" / "keywords.csv"))
    parser.add_argument("--output", default=str(RAW_DIR / "youtube_stats.csv"))
    parser.add_argument("--max-results", type=int, default=5)
    args = parser.parse_args()

    load_env()
    ensure_dirs()
    api_key = env_required("YOUTUBE_API_KEY")
    youtube = build("youtube", "v3", developerKey=api_key, http=httplib2.Http(**httplib2_options()))
    collected_at = datetime.now().isoformat(timespec="seconds")
    rows = []

    for item in read_csv(resolve_path(args.keywords)):
        query = item.get("youtube_query") or item.get("keyword_en")
        if not query:
            continue

        search_response = youtube.search().list(
            q=query,
            part="id,snippet",
            type="video",
            maxResults=args.max_results,
            order="relevance",
            publishedAfter="2021-01-01T00:00:00Z",
            publishedBefore="2026-01-02T00:00:00Z",
        ).execute()
        time.sleep(20)
        video_ids = [entry["id"]["videoId"] for entry in search_response.get("items", [])]
        if not video_ids:
            continue

        stats_response = youtube.videos().list(
            part="snippet,statistics",
            id=",".join(video_ids),
        ).execute()

        for video in stats_response.get("items", []):
            stats = video.get("statistics", {})
            snippet = video.get("snippet", {})
            video_id = video["id"]
            rows.append(
                {
                    "event_id": item["event_id"],
                    "query": query,
                    "video_id": video_id,
                    "title": snippet.get("title", ""),
                    "channel_title": snippet.get("channelTitle", ""),
                    "published_at": snippet.get("publishedAt", ""),
                    "youtube_views": stats.get("viewCount", ""),
                    "youtube_likes": stats.get("likeCount", ""),
                    "youtube_comments": stats.get("commentCount", ""),
                    "url": f"https://www.youtube.com/watch?v={video_id}",
                    "collected_at": collected_at,
                }
            )

    write_csv(resolve_path(args.output), rows, FIELDNAMES)
    print(f"Wrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
