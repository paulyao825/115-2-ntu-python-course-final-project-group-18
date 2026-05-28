from __future__ import annotations

import argparse
import csv
import os
from datetime import date
from pathlib import Path

import requests
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = PROJECT_ROOT / "config" / "group_youtube_channels.csv"
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "weights" / "group_youtube_weights.csv"


FIELDNAMES = [
    "company",
    "group",
    "youtube_channel_id",
    "youtube_channel_title",
    "youtube_channel_subscribers",
    "youtube_channel_views",
    "youtube_channel_videos",
    "youtube_url",
    "source_date",
    "notes",
]


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def get_channel_stats(channel_id: str, api_key: str) -> dict:
    response = requests.get(
        "https://www.googleapis.com/youtube/v3/channels",
        params={
            "part": "snippet,statistics",
            "id": channel_id,
            "key": api_key,
        },
        timeout=20,
    )
    response.raise_for_status()

    items = response.json().get("items", [])

    if not items:
        return {}

    channel = items[0]
    snippet = channel.get("snippet", {})
    stats = channel.get("statistics", {})

    return {
        "youtube_channel_title": snippet.get("title", ""),
        "youtube_channel_subscribers": stats.get("subscriberCount", ""),
        "youtube_channel_views": stats.get("viewCount", ""),
        "youtube_channel_videos": stats.get("videoCount", ""),
    }


def collect(input_path: Path, output_path: Path) -> None:
    load_dotenv(PROJECT_ROOT / ".env")

    api_key = os.getenv("YOUTUBE_API_KEY")

    if not api_key:
        raise RuntimeError("Missing YOUTUBE_API_KEY in .env")

    rows = []
    source_date = date.today().isoformat()

    for item in read_csv(input_path):
        channel_id = item.get("youtube_channel_id", "").strip()

        if not channel_id:
            rows.append(
                {
                    "company": item.get("company", ""),
                    "group": item.get("group", ""),
                    "youtube_channel_id": "",
                    "youtube_channel_title": "",
                    "youtube_channel_subscribers": "",
                    "youtube_channel_views": "",
                    "youtube_channel_videos": "",
                    "youtube_url": item.get("youtube_url", ""),
                    "source_date": source_date,
                    "notes": "missing youtube_channel_id",
                }
            )
            continue

        stats = get_channel_stats(channel_id, api_key)

        rows.append(
            {
                "company": item.get("company", ""),
                "group": item.get("group", ""),
                "youtube_channel_id": channel_id,
                "youtube_channel_title": stats.get("youtube_channel_title", ""),
                "youtube_channel_subscribers": stats.get(
                    "youtube_channel_subscribers", ""
                ),
                "youtube_channel_views": stats.get("youtube_channel_views", ""),
                "youtube_channel_videos": stats.get("youtube_channel_videos", ""),
                "youtube_url": item.get("youtube_url", ""),
                "source_date": source_date,
                "notes": item.get("notes", ""),
            }
        )

    write_csv(output_path, rows, FIELDNAMES)
    print(f"Wrote {len(rows)} rows to {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Collect YouTube channel-level popularity weights."
    )
    parser.add_argument("--input", default=str(DEFAULT_INPUT))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()

    collect(Path(args.input), Path(args.output))


if __name__ == "__main__":
    main()