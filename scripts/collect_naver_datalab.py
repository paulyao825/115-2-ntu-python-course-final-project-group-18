from __future__ import annotations

import argparse
import json
import time
from datetime import datetime

import requests
from requests import HTTPError

from common import (
    PROJECT_ROOT,
    RAW_DIR,
    ensure_dirs,
    env_required,
    load_env,
    parse_date,
    read_csv,
    requests_verify,
    write_csv,
)


FIELDNAMES = [
    "event_id",
    "date",
    "keyword",
    "naver_datalab_score",
    "collected_at",
]


DATALAB_URL = "https://openapi.naver.com/v1/datalab/search"


def datalab_request(
    start_date: str,
    end_date: str,
    keyword: str,
    client_id: str,
    client_secret: str,
) -> dict:
    payload = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": "date",
        "keywordGroups": [
            {"groupName": keyword[:80], "keywords": [keyword[:80]]}
        ],
    }

    response = requests.post(
        DATALAB_URL,
        headers={
            "X-Naver-Client-Id": client_id,
            "X-Naver-Client-Secret": client_secret,
            "Content-Type": "application/json",
        },
        data=json.dumps(payload).encode("utf-8"),
        timeout=20,
        verify=requests_verify(),
    )

    try:
        response.raise_for_status()
    except HTTPError as exc:
        if response.status_code == 401:
            raise RuntimeError(
                "Naver DataLab API returned 401 Unauthorized. Check that "
                "the Naver Developers app has '데이터랩 (검색어트렌드)' permission enabled."
            ) from exc
        if response.status_code == 403:
            raise RuntimeError(
                "Naver DataLab API returned 403. The requesting host is not in "
                "the app's allowlist, or the DataLab API is not enabled for "
                "this app."
            ) from exc
        raise

    return response.json()


def resolve_path(value: str):
    from pathlib import Path

    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Collect Naver DataLab daily search index for each event window. "
            "DataLab returns a 0-100 relative index normalised per query, so "
            "scores are comparable within an event but not directly across events."
        )
    )
    parser.add_argument(
        "--events",
        default=str(PROJECT_ROOT / "data" / "templates" / "events_master.csv"),
    )
    parser.add_argument(
        "--keywords",
        default=str(PROJECT_ROOT / "config" / "keywords.csv"),
    )
    parser.add_argument(
        "--output",
        default=str(RAW_DIR / "naver_datalab.csv"),
    )
    parser.add_argument("--sleep", type=float, default=0.3)
    args = parser.parse_args()

    load_env()
    ensure_dirs()

    client_id = env_required("NAVER_CLIENT_ID")
    client_secret = env_required("NAVER_CLIENT_SECRET")

    keywords_by_event: dict[str, dict] = {
        row["event_id"]: row for row in read_csv(resolve_path(args.keywords))
    }

    events = read_csv(resolve_path(args.events))
    rows = []
    collected_at = datetime.now().isoformat(timespec="seconds")

    failures = 0
    for event in events:
        event_id = event.get("event_id")
        if not event_id:
            continue
        kw_item = keywords_by_event.get(event_id)
        if not kw_item:
            continue

        keyword = (
            kw_item.get("naver_query")
            or kw_item.get("keyword_ko")
            or kw_item.get("keyword_en")
        )
        if not keyword:
            continue

        start_str = event.get("start_date")
        end_str = event.get("end_date")
        if not start_str or not end_str:
            continue

        try:
            parse_date(start_str)
            parse_date(end_str)
        except ValueError:
            continue

        try:
            data = datalab_request(
                start_date=start_str,
                end_date=end_str,
                keyword=keyword,
                client_id=client_id,
                client_secret=client_secret,
            )
        except Exception as exc:
            failures += 1
            print(f"  ! {event_id}: {type(exc).__name__}: {exc}")
            time.sleep(args.sleep)
            continue

        for series in data.get("results", []):
            for point in series.get("data", []):
                rows.append(
                    {
                        "event_id": event_id,
                        "date": point.get("period", ""),
                        "keyword": keyword,
                        "naver_datalab_score": point.get("ratio", 0),
                        "collected_at": collected_at,
                    }
                )

        time.sleep(args.sleep)

    write_csv(resolve_path(args.output), rows, FIELDNAMES)
    print(f"Wrote {len(rows)} rows to {args.output}")
    if failures:
        print(f"  ({failures} event(s) failed)")


if __name__ == "__main__":
    main()
