from __future__ import annotations

import argparse
from datetime import datetime

import pandas as pd

from common import FINAL_DIR, PROJECT_ROOT, START_DATE, END_DATE, ensure_dirs


VALID_CATEGORIES = {
    "dating",
    "concert",
    "PR_crisis",
    "activity",
    "contract_member",
    "comeback",
    "military",
    "health_hiatus",
    "legal_dispute",
    "achievement",
    "market_confounder",
}


def add_result(results: list[dict], check_name: str, ok: bool, details: str) -> None:
    results.append(
        {
            "check_name": check_name,
            "status": "pass" if ok else "fail",
            "details": details,
            "checked_at": datetime.now().isoformat(timespec="seconds"),
        }
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate K-pop event dataset.")
    parser.add_argument("--events", default=str(PROJECT_ROOT / "data" / "templates" / "events_master.csv"))
    parser.add_argument("--traffic", default=str(FINAL_DIR / "traffic_daily.csv"))
    parser.add_argument("--output", default=str(FINAL_DIR / "data_quality_report.csv"))
    args = parser.parse_args()

    ensure_dirs()
    results = []
    events = pd.read_csv(args.events)

    add_result(results, "events_not_empty", not events.empty, f"event_rows={len(events)}")
    if not events.empty:
        add_result(results, "event_id_unique", events["event_id"].is_unique, "event_id must be unique")
        required = ["event_id", "company", "ticker", "group", "event_category", "start_date", "end_date", "status"]
        missing_required = [col for col in required if col not in events.columns or events[col].isna().any()]
        add_result(results, "required_fields_present", not missing_required, f"missing_or_blank={missing_required}")

        parsed_start = pd.to_datetime(events["start_date"], errors="coerce")
        parsed_end = pd.to_datetime(events["end_date"], errors="coerce")
        add_result(results, "date_parse_ok", parsed_start.notna().all() and parsed_end.notna().all(), "dates must parse")
        add_result(results, "end_after_start", (parsed_end >= parsed_start).fillna(False).all(), "end_date must be >= start_date")
        add_result(
            results,
            "date_in_scope",
            ((parsed_start.dt.date >= START_DATE) & (parsed_end.dt.date <= END_DATE)).fillna(False).all(),
            f"scope={START_DATE.isoformat()} to {END_DATE.isoformat()}",
        )
        bad_categories = sorted(set(events["event_category"].dropna()) - VALID_CATEGORIES)
        add_result(results, "valid_event_categories", not bad_categories, f"bad_categories={bad_categories}")

        has_source = events.get("official_source_url", pd.Series([""] * len(events))).fillna("").ne("") | events.get(
            "naver_source_url", pd.Series([""] * len(events))
        ).fillna("").ne("")
        add_result(results, "has_primary_source_url", has_source.all(), "each event needs official or Naver source")

    try:
        traffic = pd.read_csv(args.traffic)
        add_result(results, "traffic_file_readable", True, f"traffic_rows={len(traffic)}")
        if not events.empty and not traffic.empty:
            missing_traffic = sorted(set(events["event_id"].dropna()) - set(traffic["event_id"].dropna()))
            add_result(results, "all_events_have_traffic_rows", not missing_traffic, f"missing={missing_traffic[:20]}")
    except FileNotFoundError:
        add_result(results, "traffic_file_readable", False, f"missing file: {args.traffic}")

    pd.DataFrame(results).to_csv(args.output, index=False, encoding="utf-8-sig")
    failed = [row for row in results if row["status"] == "fail"]
    print(f"Wrote validation report to {args.output}")
    print(f"Failed checks: {len(failed)}")
    for row in failed:
        print(f"- {row['check_name']}: {row['details']}")


if __name__ == "__main__":
    main()

