from __future__ import annotations

import argparse

from pytrends.request import TrendReq

from common import PROJECT_ROOT, RAW_DIR, START_DATE, END_DATE, ensure_dirs, load_env, read_csv, requests_verify, write_csv


FIELDNAMES = ["event_id", "date", "query", "google_trends_score"]


def resolve_path(value: str):
    from pathlib import Path

    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect Google Trends scores with PyTrends.")
    parser.add_argument("--keywords", default=str(PROJECT_ROOT / "config" / "keywords.csv"))
    parser.add_argument("--output", default=str(RAW_DIR / "google_trends.csv"))
    parser.add_argument("--geo", default="")
    args = parser.parse_args()

    load_env()
    ensure_dirs()
    pytrends = TrendReq(hl="en-US", tz=480, requests_args={"verify": requests_verify()})
    timeframe = f"{START_DATE.isoformat()} {END_DATE.isoformat()}"
    rows = []

    for item in read_csv(resolve_path(args.keywords)):
        query = item.get("google_trends_query") or item.get("keyword_en")
        if not query:
            continue
        pytrends.build_payload([query], timeframe=timeframe, geo=args.geo)
        df = pytrends.interest_over_time()
        if df.empty:
            continue
        for idx, record in df.iterrows():
            rows.append(
                {
                    "event_id": item["event_id"],
                    "date": idx.date().isoformat(),
                    "query": query,
                    "google_trends_score": int(record.get(query, 0)),
                }
            )

    write_csv(resolve_path(args.output), rows, FIELDNAMES)
    print(f"Wrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
