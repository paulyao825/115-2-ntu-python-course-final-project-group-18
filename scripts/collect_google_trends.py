from __future__ import annotations

import argparse
import time

from pytrends.request import TrendReq

from common import PROJECT_ROOT, RAW_DIR, ensure_dirs, load_env, read_csv, requests_verify, write_csv


FIELDNAMES = ["event_id", "date", "query", "google_trends_score"]


def resolve_path(value: str):
    from pathlib import Path

    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Collect Google Trends daily scores per event window with PyTrends. "
            "Each event uses its own start_date..end_date window so PyTrends returns "
            "daily granularity (windows >= 270 days drop to weekly)."
        )
    )
    parser.add_argument("--keywords", default=str(PROJECT_ROOT / "config" / "keywords.csv"))
    parser.add_argument(
        "--events",
        default=str(PROJECT_ROOT / "data" / "templates" / "events_master.csv"),
    )
    parser.add_argument("--output", default=str(RAW_DIR / "google_trends.csv"))
    parser.add_argument("--geo", default="")
    parser.add_argument("--sleep", type=float, default=1.0)
    args = parser.parse_args()

    load_env()
    ensure_dirs()
    pytrends = TrendReq(hl="en-US", tz=480, requests_args={"verify": requests_verify()})

    events_by_id = {row["event_id"]: row for row in read_csv(resolve_path(args.events))}
    rows = []
    failures = 0

    for item in read_csv(resolve_path(args.keywords)):
        event_id = item.get("event_id")
        if not event_id:
            continue

        event = events_by_id.get(event_id)
        if not event:
            continue

        start_str = event.get("start_date")
        end_str = event.get("end_date")
        if not start_str or not end_str:
            continue

        query = item.get("google_trends_query") or item.get("keyword_en")
        if not query:
            continue

        timeframe = f"{start_str} {end_str}"

        try:
            pytrends.build_payload([query], timeframe=timeframe, geo=args.geo)
            df = pytrends.interest_over_time()
        except Exception as exc:
            failures += 1
            print(f"  ! {event_id}: {type(exc).__name__}: {exc}")
            time.sleep(args.sleep)
            continue

        if df.empty:
            time.sleep(args.sleep)
            continue

        for idx, record in df.iterrows():
            rows.append(
                {
                    "event_id": event_id,
                    "date": idx.date().isoformat(),
                    "query": query,
                    "google_trends_score": int(record.get(query, 0)),
                }
            )

        time.sleep(args.sleep)

    write_csv(resolve_path(args.output), rows, FIELDNAMES)
    print(f"Wrote {len(rows)} rows to {args.output}")
    if failures:
        print(f"  ({failures} event(s) failed)")


if __name__ == "__main__":
    main()
