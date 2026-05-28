from __future__ import annotations

import argparse
import time
from datetime import datetime
from email.utils import parsedate_to_datetime

import requests
from requests import HTTPError

from common import (
    END_DATE,
    PROJECT_ROOT,
    RAW_DIR,
    START_DATE,
    ensure_dirs,
    env_required,
    load_env,
    read_csv,
    requests_verify,
    write_csv,
)


FIELDNAMES = [
    "event_id",
    "query",
    "source_type",
    "platform",
    "title",
    "url",
    "published_date",
    "description",
    "collected_at",
]


def clean_html(text: str) -> str:
    return (
        text.replace("<b>", "")
        .replace("</b>", "")
        .replace("&quot;", '"')
        .replace("&amp;", "&")
        .replace("&lt;", "<")
        .replace("&gt;", ">")
    )


def parse_pubdate(value: str) -> str:
    """Parse Naver News pubDate into YYYY-MM-DD."""
    try:
        return parsedate_to_datetime(value).date().isoformat()
    except Exception:
        return ""


def parse_blog_postdate(value: str) -> str:
    """Parse Naver Blog postdate format YYYYMMDD into YYYY-MM-DD."""
    value = str(value).strip()

    if len(value) == 8 and value.isdigit():
        return f"{value[:4]}-{value[4:6]}-{value[6:8]}"

    return ""


def naver_search(
    query: str,
    search_type: str,
    client_id: str,
    client_secret: str,
    display: int,
    start: int = 1,
) -> list[dict]:
    url = f"https://openapi.naver.com/v1/search/{search_type}.json"
    headers = {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret,
    }
    params = {
        "query": query,
        "display": display,
        "start": start,
        "sort": "date",
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=20,
        verify=requests_verify(),
    )

    try:
        response.raise_for_status()
    except HTTPError as exc:
        if response.status_code == 401:
            raise RuntimeError(
                "Naver API returned 401 Unauthorized. Check that "
                "NAVER_CLIENT_ID and NAVER_CLIENT_SECRET are copied from "
                "the same Naver Developers app, and that the app has Search "
                "API permission enabled."
            ) from exc
        raise

    return response.json().get("items", [])


def resolve_path(value: str):
    from pathlib import Path

    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Collect Naver news/blog search results."
    )
    parser.add_argument(
        "--keywords",
        default=str(PROJECT_ROOT / "config" / "keywords.csv"),
    )
    parser.add_argument(
        "--output",
        default=str(RAW_DIR / "naver_results.csv"),
    )
    parser.add_argument("--display", type=int, default=100)
    parser.add_argument("--sleep", type=float, default=0.2)
    parser.add_argument(
        "--max-start",
        type=int,
        default=1000,
        help="Highest start offset to paginate to. Naver caps start+display-1 at 1000.",
    )
    args = parser.parse_args()

    load_env()
    ensure_dirs()

    client_id = env_required("NAVER_CLIENT_ID")
    client_secret = env_required("NAVER_CLIENT_SECRET")

    rows = []
    collected_at = datetime.now().isoformat(timespec="seconds")

    for item in read_csv(resolve_path(args.keywords)):
        event_id = item["event_id"]
        query = (
            item.get("naver_query")
            or item.get("keyword_ko")
            or item.get("keyword_en")
        )

        if not query:
            continue

        for search_type, platform in [
            ("news", "Naver News"),
            ("blog", "Naver Blog"),
        ]:
            seen_urls: set[str] = set()
            for start in range(1, args.max_start + 1, args.display):
                if start + args.display - 1 > 1000:
                    break

                results = naver_search(
                    query=query,
                    search_type=search_type,
                    client_id=client_id,
                    client_secret=client_secret,
                    display=args.display,
                    start=start,
                )

                if not results:
                    break

                for result in results:
                    if search_type == "blog":
                        published_date = parse_blog_postdate(
                            result.get("postdate", "")
                        )
                    else:
                        published_date = parse_pubdate(
                            result.get("pubDate", "")
                        )

                    if published_date and not (
                        START_DATE.isoformat()
                        <= published_date
                        <= END_DATE.isoformat()
                    ):
                        continue

                    url_key = result.get("originallink") or result.get("link", "")
                    if url_key and url_key in seen_urls:
                        continue
                    seen_urls.add(url_key)

                    rows.append(
                        {
                            "event_id": event_id,
                            "query": query,
                            "source_type": search_type,
                            "platform": platform,
                            "title": clean_html(result.get("title", "")),
                            "url": url_key,
                            "published_date": published_date,
                            "description": clean_html(
                                result.get("description", "")
                            ),
                            "collected_at": collected_at,
                        }
                    )

                time.sleep(args.sleep)

                if len(results) < args.display:
                    break

    write_csv(resolve_path(args.output), rows, FIELDNAMES)
    print(f"Wrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
