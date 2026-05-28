from __future__ import annotations

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

YOUTUBE_PATH = PROJECT_ROOT / "data" / "weights" / "group_youtube_weights.csv"
INSTAGRAM_PATH = PROJECT_ROOT / "data" / "weights" / "group_instagram_weights.csv"
SPOTIFY_PATH = PROJECT_ROOT / "data" / "weights" / "group_spotify_monthly_listeners.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "weights" / "group_weights.csv"


WEIGHT_COLUMNS = [
    "youtube_channel_subscribers",
    "youtube_channel_views",
    "instagram_followers",
    "spotify_monthly_listeners",
]


def read_weight_csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing input file: {path}")

    return pd.read_csv(path)


def standardize(series: pd.Series) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce")

    mean = values.mean()
    std = values.std(ddof=0)

    if pd.isna(std) or std == 0:
        return pd.Series([0] * len(values), index=values.index)

    return (values - mean) / std


def main() -> None:
    youtube = read_weight_csv(YOUTUBE_PATH)
    instagram = read_weight_csv(INSTAGRAM_PATH)
    spotify = read_weight_csv(SPOTIFY_PATH)

    youtube_keep = youtube[
        [
            "company",
            "group",
            "youtube_channel_subscribers",
            "youtube_channel_views",
            "youtube_channel_videos",
        ]
    ].copy()

    instagram_keep = instagram[
        [
            "company",
            "group",
            "instagram_followers",
            "instagram_url",
        ]
    ].copy()

    spotify_keep = spotify[
        [
            "company",
            "group",
            "spotify_monthly_listeners",
            "spotify_url",
        ]
    ].copy()

    merged = youtube_keep.merge(
        instagram_keep,
        on=["company", "group"],
        how="outer",
    ).merge(
        spotify_keep,
        on=["company", "group"],
        how="outer",
    )

    for column in WEIGHT_COLUMNS:
        merged[column] = pd.to_numeric(merged[column], errors="coerce")
        merged[f"{column}_z"] = standardize(merged[column])

    z_columns = [f"{column}_z" for column in WEIGHT_COLUMNS]

    merged["fanbase_weight"] = merged[z_columns].mean(axis=1, skipna=True)

    merged["weight_method"] = (
        "fanbase_weight is the average z-score of YouTube subscribers, "
        "YouTube views, Instagram followers, and Spotify monthly listeners."
    )

    output_columns = [
        "company",
        "group",
        "youtube_channel_subscribers",
        "youtube_channel_views",
        "youtube_channel_videos",
        "instagram_followers",
        "instagram_url",
        "spotify_monthly_listeners",
        "spotify_url",
        "youtube_channel_subscribers_z",
        "youtube_channel_views_z",
        "instagram_followers_z",
        "spotify_monthly_listeners_z",
        "fanbase_weight",
        "weight_method",
    ]

    merged = merged[output_columns].sort_values(["company", "group"])

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(OUTPUT_PATH, index=False, encoding="utf-8-sig")

    print(f"Wrote {len(merged)} rows to {OUTPUT_PATH}")
    print(merged[["company", "group", "fanbase_weight"]].to_string(index=False))


if __name__ == "__main__":
    main()
