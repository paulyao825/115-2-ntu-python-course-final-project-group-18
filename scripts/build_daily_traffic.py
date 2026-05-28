from __future__ import annotations

import argparse
from datetime import timedelta
from pathlib import Path

import pandas as pd

from common import FINAL_DIR, PROJECT_ROOT, ensure_dirs, parse_date


OUTPUT_COLUMNS = [
    "event_id",
    "date",
    "naver_news_count",
    "naver_blog_count",
    "naver_datalab_score",
    "google_trends_score",
    "youtube_views",
    "youtube_comments",
    "youtube_likes",
    "instagram_followers",
    "traffic_total_raw",
    "traffic_total_normalized",
    "data_quality",
]


def read_optional_csv(path: Path) -> pd.DataFrame:
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


def main() -> None:
    parser = argparse.ArgumentParser(description="Build daily event traffic panel.")
    parser.add_argument("--events", default=str(PROJECT_ROOT / "data" / "templates" / "events_master.csv"))
    parser.add_argument("--naver", default=str(PROJECT_ROOT / "data" / "raw" / "naver_results.csv"))
    parser.add_argument("--datalab", default=str(PROJECT_ROOT / "data" / "raw" / "naver_datalab.csv"))
    parser.add_argument("--trends", default=str(PROJECT_ROOT / "data" / "raw" / "google_trends.csv"))
    parser.add_argument("--youtube", default=str(PROJECT_ROOT / "data" / "raw" / "youtube_stats.csv"))
    parser.add_argument(
        "--ig-weights",
        default=str(PROJECT_ROOT / "data" / "weights" / "group_instagram_weights.csv"),
    )
    parser.add_argument("--output", default=str(FINAL_DIR / "traffic_daily.csv"))
    args = parser.parse_args()

    ensure_dirs()
    events = pd.read_csv(args.events)
    rows = []
    for _, event in events.dropna(subset=["event_id", "start_date", "end_date"]).iterrows():
        current = parse_date(str(event["start_date"]))
        end = parse_date(str(event["end_date"]))
        while current <= end:
            rows.append({"event_id": event["event_id"], "date": current.isoformat()})
            current += timedelta(days=1)

    daily = pd.DataFrame(rows)
    if daily.empty:
        daily = pd.DataFrame(columns=OUTPUT_COLUMNS)

    naver = read_optional_csv(Path(args.naver))
    if not naver.empty and "published_date" in naver.columns:
        counts = (
            naver.groupby(["event_id", "published_date", "source_type"])
            .size()
            .unstack(fill_value=0)
            .reset_index()
            .rename(columns={"published_date": "date", "news": "naver_news_count", "blog": "naver_blog_count"})
        )
        daily = daily.merge(counts, on=["event_id", "date"], how="left")

    datalab = read_optional_csv(Path(args.datalab))
    if not datalab.empty and {"event_id", "date", "naver_datalab_score"}.issubset(datalab.columns):
        dl_daily = datalab.groupby(["event_id", "date"], as_index=False)["naver_datalab_score"].max()
        daily = daily.merge(dl_daily, on=["event_id", "date"], how="left")

    trends = read_optional_csv(Path(args.trends))
    if not trends.empty and {"event_id", "date", "google_trends_score"}.issubset(trends.columns):
        trend_daily = (
            trends.groupby(["event_id", "date"], as_index=False)["google_trends_score"].max()
        )
        trend_daily["date"] = pd.to_datetime(trend_daily["date"])
        panel = daily.copy()
        panel["date"] = pd.to_datetime(panel["date"])
        panel = panel.sort_values("date").reset_index(drop=True)
        trend_daily = trend_daily.sort_values("date").reset_index(drop=True)
        daily = pd.merge_asof(
            panel,
            trend_daily,
            by="event_id",
            on="date",
            direction="backward",
            tolerance=pd.Timedelta(days=10),
        )
        daily["date"] = daily["date"].dt.strftime("%Y-%m-%d")

    youtube = read_optional_csv(Path(args.youtube))
    if not youtube.empty:
        youtube_latest = youtube.groupby("event_id", as_index=False)[["youtube_views", "youtube_comments", "youtube_likes"]].max()
        daily = daily.merge(youtube_latest, on="event_id", how="left")

    ig_weights = read_optional_csv(Path(args.ig_weights))
    if not ig_weights.empty and {"group", "instagram_followers"}.issubset(ig_weights.columns):
        ig_lookup = ig_weights.set_index("group")["instagram_followers"].to_dict()
        events_lookup = events.set_index("event_id")["group"].to_dict() if "group" in events.columns else {}
        if events_lookup:
            daily["instagram_followers"] = daily["event_id"].map(events_lookup).map(ig_lookup)

    for col in OUTPUT_COLUMNS:
        if col not in daily.columns:
            daily[col] = ""

    numeric_cols = [
        "naver_news_count",
        "naver_blog_count",
        "naver_datalab_score",
        "google_trends_score",
        "youtube_views",
        "youtube_comments",
        "youtube_likes",
        "instagram_followers",
    ]
    for col in numeric_cols:
        daily[col] = pd.to_numeric(daily[col], errors="coerce").fillna(0)

    traffic_signal_cols = [
        "naver_news_count",
        "naver_blog_count",
        "naver_datalab_score",
        "google_trends_score",
    ]
    daily["traffic_total_raw"] = daily[traffic_signal_cols].sum(axis=1)
    max_value = daily["traffic_total_raw"].max()
    daily["traffic_total_normalized"] = 0 if max_value == 0 else daily["traffic_total_raw"] / max_value
    daily["data_quality"] = daily.apply(lambda row: "missing_traffic" if row["traffic_total_raw"] == 0 else "ok", axis=1)
    daily[OUTPUT_COLUMNS].to_csv(args.output, index=False, encoding="utf-8-sig")
    print(f"Wrote {len(daily)} rows to {args.output}")


if __name__ == "__main__":
    main()

