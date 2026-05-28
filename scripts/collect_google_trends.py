from __future__ import annotations

import argparse
import csv
import time
from pathlib import Path

from pytrends.exceptions import TooManyRequestsError
from pytrends.request import TrendReq

from common import PROJECT_ROOT, RAW_DIR, ensure_dirs, load_env, read_csv, requests_verify


FIELDNAMES = ["event_id", "date", "query", "google_trends_score"]


def resolve_path(value: str):
    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def load_done_events(path: Path) -> set[str]:
    if not path.exists():
        return set()
    done = set()
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            event_id = row.get("event_id")
            if event_id:
                done.add(event_id)
    return done


def ensure_output_header(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        with path.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()


def append_rows(path: Path, rows: list[dict]) -> None:
    with path.open("a", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Collect Google Trends daily scores per event window. Writes "
            "incrementally and resumes by skipping event_ids already present "
            "in the output file. Recommended workflow when Google rate-limits: "
            "rotate VPN location and re-run; finished events are skipped."
        )
    )
    parser.add_argument("--keywords", default=str(PROJECT_ROOT / "config" / "keywords.csv"))
    parser.add_argument(
        "--events",
        default=str(PROJECT_ROOT / "data" / "templates" / "events_master.csv"),
    )
    parser.add_argument("--output", default=str(RAW_DIR / "google_trends.csv"))
    parser.add_argument("--geo", default="")
    parser.add_argument("--sleep", type=float, default=2.0)
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Discard existing output and start fresh.",
    )
    args = parser.parse_args()

    load_env()
    ensure_dirs()
    pytrends = TrendReq(hl="en-US", tz=480, requests_args={"verify": requests_verify()})

    output_path = resolve_path(args.output)

    if args.reset and output_path.exists():
        output_path.unlink()

    done_events = load_done_events(output_path)
    ensure_output_header(output_path)

    events_by_id = {row["event_id"]: row for row in read_csv(resolve_path(args.events))}

    total = 0
    skipped = 0
    appended_rows = 0
    rate_limited = False

    for item in read_csv(resolve_path(args.keywords)):
        event_id = item.get("event_id")
        if not event_id:
            continue

        total += 1

        if event_id in done_events:
            skipped += 1
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
        except TooManyRequestsError:
            print(f"  ! {event_id}: 429 rate limit hit, stopping. Switch VPN and re-run to resume.")
            rate_limited = True
            break
        except Exception as exc:
            print(f"  ! {event_id}: {type(exc).__name__}: {exc}")
            time.sleep(args.sleep)
            continue

        if df.empty:
            time.sleep(args.sleep)
            continue

        rows = [
            {
                "event_id": event_id,
                "date": idx.date().isoformat(),
                "query": query,
                "google_trends_score": int(record.get(query, 0)),
            }
            for idx, record in df.iterrows()
        ]

        if rows:
            append_rows(output_path, rows)
            appended_rows += len(rows)
            done_events.add(event_id)
            print(f"  + {event_id}: {len(rows)} rows (total events done: {len(done_events)})")

        time.sleep(args.sleep)

    print()
    print(f"Output: {output_path}")
    print(f"Events skipped (already done): {skipped}/{total}")
    print(f"Events newly collected this run: {appended_rows} rows added")
    print(f"Total events done so far: {len(done_events)}/{total}")
    if rate_limited:
        print()
        print("To continue: switch VPN to a different location, then re-run the same command.")
        print("Already-collected events will be skipped automatically.")


if __name__ == "__main__":
    main()
