
# event_study_workflow_v2.py
# ------------------------------------------------------------
# K-pop Event Study Workflow - revised final classification
#
# This script does five things:
# 1. Calculates peer-adjusted AR and event-level CAR
# 2. Draws AAR / CAAR plots, including final-model event type CAAR
# 3. Checks correlations between group/company variables and AR/CAR
# 4. Draws correlation heatmap for group/company variables
# 5. Creates revised final event categories and runs OLS regressions
# 6. Centers firm size and group popularity so the intercept represents positive_activity at average controls
# 7. Exports a publication-style model comparison table with the intercept labeled as positive_activity
#
# Final event classification:
# - positive_activity
# - positive_comeback
# - positive_concert
# - positive_resolution
# - negative_PR_crisis
# - negative_contract_crisis
# - dating
# - artist_transition
#
# t = 0 is start_date. If start_date is not a trading day, use the next trading day.
# AR = firm daily return - average return of the other listed K-pop companies.
# ------------------------------------------------------------

import os
import sqlite3
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor
import patsy

warnings.filterwarnings("ignore", category=FutureWarning)

# ==============================
# 0. Settings
# ==============================

DATA_DIR = Path(".")          # Put original files in the same folder as this script
OUTPUT_DIR = Path("outputs")  # All results will be saved here
OUTPUT_DIR.mkdir(exist_ok=True)

EVENT_WINDOW_MIN = -10
EVENT_WINDOW_MAX = 10

# Main event-study windows
WINDOWS = {
    "AR_0": (0, 0),
    "CAR_m1_p1": (-1, 1),
    "CAR_0_p1": (0, 1),
    "CAR_0_p3": (0, 3),
    "CAR_0_p5": (0, 5),
    "CAR_m5_p5": (-5, 5),
    "CAR_m10_p10": (-10, 10),
}

# Use this as the formal main model DV
MAIN_DV = "CAR_m1_p1"

# Robustness windows
ROBUSTNESS_DVS = [
    "AR_0",
    "CAR_m1_p1",
    "CAR_0_p1",
    "CAR_0_p3",
    "CAR_0_p5",
    "CAR_m5_p5",
    "CAR_m10_p10",
]


# ==============================
# 1. Helper functions
# ==============================

def read_data_file(possible_names):
    """
    Read the first file that exists from possible_names.
    Supports csv, xlsx, and xls.
    """
    for name in possible_names:
        path = DATA_DIR / name
        if path.exists():
            if path.suffix.lower() == ".csv":
                return pd.read_csv(path), path
            if path.suffix.lower() in [".xlsx", ".xls"]:
                return pd.read_excel(path), path

    raise FileNotFoundError(
        "None of these files were found: " + ", ".join(possible_names)
    )


def safe_log1p(df, col):
    """
    Create log1p version of a numeric column.
    Non-numeric values are coerced to NaN.
    """
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df[f"log_{col}"] = np.log1p(df[col])
    return df


def recode_event_type_final(row):
    """
    Revised final event classification.

    Logic:
    1. concert and comeback are treated as positive commercial events.
    2. dating is kept as its own category.
    3. activity is positive_activity, except solo_activity_transition, which is artist_transition.
    4. PR_crisis:
       - positive cases are positive_resolution
       - negative or mixed cases are negative_PR_crisis
    5. contract_member:
       - positive cases are positive_resolution
       - negative cases are negative_contract_crisis
       - mixed cases are artist_transition
    """
    sentiment = str(row.get("sentiment_expected", "")).strip()
    category = str(row.get("event_category", "")).strip()
    subtype = str(row.get("event_subtype", "")).strip()

    # Commercial positive events
    if category == "concert":
        return "positive_concert"

    if category == "comeback":
        return "positive_comeback"

    # Dating / private life
    if category == "dating":
        return "dating"

    # Activity
    if category == "activity":
        if subtype == "solo_activity_transition":
            return "artist_transition"
        return "positive_activity"

    # PR / reputation crisis
    if category == "PR_crisis":
        if sentiment == "positive":
            return "positive_resolution"
        return "negative_PR_crisis"

    # Contract / member / artist continuity
    if category == "contract_member":
        if sentiment == "positive":
            return "positive_resolution"
        if sentiment == "negative":
            return "negative_contract_crisis"
        if sentiment == "mixed":
            return "artist_transition"

    return "other"


def calculate_peer_adjusted_ar(stock):
    """
    AR_it = firm daily return - average return of other K-pop companies on the same date.
    """
    stock = stock.copy()
    stock["daily_return"] = pd.to_numeric(stock["daily_return"], errors="coerce")

    stock_for_peer = stock[["date", "company", "daily_return"]].copy()

    peer_rows = []
    for company in stock_for_peer["company"].dropna().unique():
        peer_avg = (
            stock_for_peer[stock_for_peer["company"] != company]
            .groupby("date", as_index=False)["daily_return"]
            .mean()
            .rename(columns={"daily_return": "peer_avg_return"})
        )
        peer_avg["company"] = company
        peer_rows.append(peer_avg)

    peer_avg_df = pd.concat(peer_rows, ignore_index=True)

    stock_ar = stock.merge(peer_avg_df, on=["date", "company"], how="left")
    stock_ar["abnormal_return"] = (
        stock_ar["daily_return"] - stock_ar["peer_avg_return"]
    )

    return stock_ar


def make_event_day_panel(events_df, stock_ar_df, min_day=-10, max_day=10):
    """
    Create event-day panel.

    For each event:
    - t = 0 is start_date
    - If start_date is not a trading day, use the next trading day
    - Keep event days from min_day to max_day
    """
    panels = []

    event_cols = [
        "event_id", "company", "ticker", "group", "member",
        "event_category", "event_subtype", "event_title_en",
        "start_date", "peak_date", "end_date",
        "sentiment_expected", "severity_score", "duration_days",
        "source_level"
    ]

    available_event_cols = [c for c in event_cols if c in events_df.columns]

    for _, ev in events_df.iterrows():
        company = ev["company"]
        event_id = ev["event_id"]
        start_date = ev["start_date"]

        firm_stock = (
            stock_ar_df[stock_ar_df["company"] == company]
            .sort_values("date")
            .reset_index(drop=True)
        )

        possible = firm_stock[firm_stock["date"] >= start_date]
        if possible.empty:
            continue

        event0_date = possible.iloc[0]["date"]
        event0_idx = firm_stock.index[firm_stock["date"] == event0_date][0]

        lo = event0_idx + min_day
        hi = event0_idx + max_day

        if lo < 0 or hi >= len(firm_stock):
            continue

        window_df = firm_stock.iloc[lo:hi + 1].copy()
        window_df["event_id"] = event_id
        window_df["event_day"] = np.arange(min_day, max_day + 1)
        window_df["event0_date"] = event0_date

        for col in available_event_cols:
            if col != "event_id":
                window_df[col] = ev[col]

        panels.append(window_df)

    if len(panels) == 0:
        raise ValueError("No event-day panel rows were created. Check dates and company names.")

    return pd.concat(panels, ignore_index=True)


def calc_car_for_window(panel_df, start, end, name):
    """
    Sum abnormal returns for each event over [start, end].
    """
    out = (
        panel_df[
            (panel_df["event_day"] >= start) &
            (panel_df["event_day"] <= end)
        ]
        .groupby("event_id", as_index=False)["abnormal_return"]
        .sum()
        .rename(columns={"abnormal_return": name})
    )
    return out


def regression_to_dataframe(model, dv_name):
    """
    Convert statsmodels result to a tidy dataframe.
    """
    rows = []
    for term in model.params.index:
        rows.append({
            "DV": dv_name,
            "term": term,
            "coef": model.params[term],
            "std_err": model.bse[term],
            "t_value": model.tvalues[term],
            "p_value": model.pvalues[term],
            "nobs": int(model.nobs),
            "r2": model.rsquared,
            "adj_r2": model.rsquared_adj,
            "model_p_value": model.f_pvalue,
        })
    return pd.DataFrame(rows)


def calculate_vif(formula, data):
    """
    Calculate VIF for design matrix from formula.
    """
    y, X = patsy.dmatrices(formula, data, return_type="dataframe")
    vif_df = pd.DataFrame({
        "variable": X.columns,
        "VIF": [
            variance_inflation_factor(X.values, i)
            for i in range(X.shape[1])
        ]
    })
    return vif_df


# ==============================
# 2. Load data
# ==============================

events, events_path = read_data_file([
    "events_master (1).csv",
    "events_master.csv",
    "events_master.xlsx",
    "events_master (1).xlsx",
])

stock, stock_path = read_data_file([
    "stock_daily.csv",
    "stock_daily.xlsx",
])

traffic, traffic_path = read_data_file([
    "traffic_daily.csv",
    "traffic_daily.xlsx",
])

group_w, group_path = read_data_file([
    "group_weights.csv",
    "group_weights.xlsx",
])

company_w, company_path = read_data_file([
    "company_weights.csv",
    "company_weights.xlsx",
])

print("Loaded files:")
print("events:", events_path)
print("stock:", stock_path)
print("traffic:", traffic_path)
print("group weights:", group_path)
print("company weights:", company_path)

# Parse dates
for col in ["start_date", "peak_date", "end_date"]:
    if col in events.columns:
        events[col] = pd.to_datetime(events[col], errors="coerce")

stock["date"] = pd.to_datetime(stock["date"], errors="coerce")
traffic["date"] = pd.to_datetime(traffic["date"], errors="coerce")

# Basic cleaning
events = events.dropna(subset=["event_id", "company", "start_date"]).copy()
stock = stock.dropna(subset=["date", "company", "daily_return"]).copy()


# ==============================
# 3. Calculate AR and CAR
# ==============================

stock_ar = calculate_peer_adjusted_ar(stock)
stock_ar.to_csv(OUTPUT_DIR / "stock_daily_with_AR.csv", index=False)

event_day_panel = make_event_day_panel(
    events,
    stock_ar,
    min_day=EVENT_WINDOW_MIN,
    max_day=EVENT_WINDOW_MAX
)

# Add final classification to event-day panel
event_day_panel["event_type_final"] = event_day_panel.apply(
    recode_event_type_final,
    axis=1
)

event_day_panel.to_csv(OUTPUT_DIR / "event_day_panel_AR.csv", index=False)

# Event-level data
event_level = events.copy()

event0_dates = (
    event_day_panel[["event_id", "event0_date"]]
    .drop_duplicates()
)
event_level = event_level.merge(event0_dates, on="event_id", how="left")

for name, (s, e) in WINDOWS.items():
    car = calc_car_for_window(event_day_panel, s, e, name)
    event_level = event_level.merge(car, on="event_id", how="left")

# Add final classification
event_level["event_type_final"] = event_level.apply(
    recode_event_type_final,
    axis=1
)


# ==============================
# 4. Merge company and group variables
# ==============================

company_cols = [
    c for c in ["company", "market_cap", "revenue", "company_scale_weight"]
    if c in company_w.columns
]
event_level = event_level.merge(company_w[company_cols], on="company", how="left")

group_cols = [
    c for c in [
        "company", "group",
        "youtube_channel_subscribers",
        "youtube_channel_views",
        "youtube_channel_videos",
        "instagram_followers",
        "spotify_monthly_listeners",
        "fanbase_weight"
    ]
    if c in group_w.columns
]
event_level = event_level.merge(group_w[group_cols], on=["company", "group"], how="left")

for col in [
    "market_cap",
    "revenue",
    "youtube_channel_subscribers",
    "youtube_channel_views",
    "youtube_channel_videos",
    "instagram_followers",
    "spotify_monthly_listeners",
]:
    event_level = safe_log1p(event_level, col)

event_level.to_csv(OUTPUT_DIR / "event_level_CAR_dataset_final.csv", index=False)


# ==============================
# 5. AAR / CAAR plots
# ==============================

aar_caar = (
    event_day_panel
    .groupby("event_day", as_index=False)["abnormal_return"]
    .mean()
    .rename(columns={"abnormal_return": "AAR"})
)
aar_caar["CAAR"] = aar_caar["AAR"].cumsum()
aar_caar.to_csv(OUTPUT_DIR / "AAR_CAAR_table.csv", index=False)

plt.figure(figsize=(8, 5))
plt.plot(aar_caar["event_day"], aar_caar["AAR"], marker="o")
plt.axhline(0, linestyle="--", linewidth=1)
plt.axvline(0, linestyle="--", linewidth=1)
plt.title("Average Abnormal Return around Event Date")
plt.xlabel("Event Day")
plt.ylabel("AAR")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "AAR_plot.png", dpi=300)
plt.close()

plt.figure(figsize=(8, 5))
plt.plot(aar_caar["event_day"], aar_caar["CAAR"], marker="o")
plt.axhline(0, linestyle="--", linewidth=1)
plt.axvline(0, linestyle="--", linewidth=1)
plt.title("Cumulative Average Abnormal Return around Event Date")
plt.xlabel("Event Day")
plt.ylabel("CAAR")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "CAAR_plot.png", dpi=300)
plt.close()


# ==============================
# 6. CAAR plot by original event_category
# ==============================

category_caar = (
    event_day_panel
    .groupby(["event_category", "event_day"], as_index=False)["abnormal_return"]
    .mean()
    .rename(columns={"abnormal_return": "AAR"})
)
category_caar["CAAR"] = category_caar.groupby("event_category")["AAR"].cumsum()
category_caar.to_csv(OUTPUT_DIR / "category_AAR_CAAR_table.csv", index=False)

plt.figure(figsize=(9, 6))
for cat, sub in category_caar.groupby("event_category"):
    plt.plot(sub["event_day"], sub["CAAR"], marker="o", label=cat)

plt.axhline(0, linestyle="--", linewidth=1)
plt.axvline(0, linestyle="--", linewidth=1)
plt.title("CAAR by Original Event Category")
plt.xlabel("Event Day")
plt.ylabel("CAAR")
plt.legend()
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "category_CAAR_plot.png", dpi=300)
plt.close()


# ==============================
# 7. CAAR plot by final event type
# ==============================

final_order = [
    "positive_activity",
    "positive_comeback",
    "positive_concert",
    "positive_resolution",
    "negative_PR_crisis",
    "negative_contract_crisis",
    "dating",
    "artist_transition",
]

panel_final = event_day_panel[
    event_day_panel["event_type_final"].isin(final_order)
].copy()

final_caar = (
    panel_final
    .groupby(["event_type_final", "event_day"], as_index=False)["abnormal_return"]
    .mean()
    .rename(columns={"abnormal_return": "AAR"})
)

final_caar["event_type_final"] = pd.Categorical(
    final_caar["event_type_final"],
    categories=final_order,
    ordered=True
)

final_caar = final_caar.sort_values(["event_type_final", "event_day"])
final_caar["CAAR"] = (
    final_caar
    .groupby("event_type_final", observed=True)["AAR"]
    .cumsum()
)

final_counts = (
    panel_final[["event_id", "event_type_final"]]
    .drop_duplicates()
    .groupby("event_type_final", observed=True)
    .size()
    .reindex(final_order)
)

final_caar.to_csv(OUTPUT_DIR / "CAAR_by_final_event_type.csv", index=False)

plt.figure(figsize=(12, 7))
for event_type in final_order:
    sub = final_caar[final_caar["event_type_final"] == event_type]
    if sub.empty:
        continue
    label = f"{event_type} (N={final_counts.loc[event_type]})"
    plt.plot(sub["event_day"], sub["CAAR"], marker="o", label=label)

plt.axhline(0, linestyle="--", linewidth=1)
plt.axvline(0, linestyle="--", linewidth=1)
plt.title("CAAR by Final Event Type")
plt.xlabel("Event Day")
plt.ylabel("CAAR")
plt.legend(loc="best", fontsize=9)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "CAAR_by_final_event_type.png", dpi=300)
plt.close()


# ==============================
# 8. Correlations: company/group variables with CAR
# ==============================

weight_vars = [
    "market_cap",
    "revenue",
    "company_scale_weight",
    "youtube_channel_subscribers",
    "youtube_channel_views",
    "youtube_channel_videos",
    "instagram_followers",
    "spotify_monthly_listeners",
    "fanbase_weight",
    "log_market_cap",
    "log_revenue",
    "log_youtube_channel_subscribers",
    "log_youtube_channel_views",
    "log_youtube_channel_videos",
    "log_instagram_followers",
    "log_spotify_monthly_listeners",
]

weight_vars = [v for v in weight_vars if v in event_level.columns]
dv_vars = list(WINDOWS.keys())

corr_rows = []
for x in weight_vars:
    for y in dv_vars:
        tmp = event_level[[x, y]].dropna()
        if len(tmp) >= 3:
            corr_rows.append({
                "predictor": x,
                "outcome": y,
                "correlation": tmp[x].corr(tmp[y]),
                "abs_correlation": abs(tmp[x].corr(tmp[y])),
                "N": len(tmp),
            })

corr_with_car = pd.DataFrame(corr_rows)
corr_with_car = corr_with_car.sort_values(
    ["outcome", "abs_correlation"],
    ascending=[True, False]
)
corr_with_car.to_csv(
    OUTPUT_DIR / "weight_variables_correlations_with_CAR.csv",
    index=False
)


# ==============================
# 9. Heatmap: company/group variable correlations
# ==============================

heatmap_vars = [
    "log_market_cap",
    "log_revenue",
    "log_youtube_channel_subscribers",
    "log_youtube_channel_views",
    "log_youtube_channel_videos",
    "log_instagram_followers",
    "log_spotify_monthly_listeners",
]

heatmap_vars = [v for v in heatmap_vars if v in event_level.columns]
corr_matrix = event_level[heatmap_vars].corr()
corr_matrix.to_csv(OUTPUT_DIR / "weight_variables_correlation_matrix.csv")

plt.figure(figsize=(9, 7))
im = plt.imshow(corr_matrix, aspect="auto")
plt.colorbar(im, fraction=0.046, pad=0.04)
plt.xticks(range(len(heatmap_vars)), heatmap_vars, rotation=45, ha="right")
plt.yticks(range(len(heatmap_vars)), heatmap_vars)
plt.title("Correlation Heatmap: Company and Group Variables")

for i in range(len(heatmap_vars)):
    for j in range(len(heatmap_vars)):
        plt.text(
            j, i,
            f"{corr_matrix.iloc[i, j]:.2f}",
            ha="center",
            va="center"
        )

plt.tight_layout()
plt.savefig(OUTPUT_DIR / "weight_variables_correlation_heatmap.png", dpi=300)
plt.close()


# ==============================
# 10. SQL database and summaries
# ==============================

conn = sqlite3.connect(OUTPUT_DIR / "event_study_final.db")

event_level.to_sql("event_level", conn, if_exists="replace", index=False)
event_day_panel.to_sql("event_day_panel", conn, if_exists="replace", index=False)

sql_final_summary = pd.read_sql_query(
    """
    SELECT
        event_type_final,
        COUNT(*) AS n_events,
        AVG(CAR_m1_p1) AS mean_CAR_m1_p1,
        AVG(CAR_0_p3) AS mean_CAR_0_p3,
        AVG(CAR_0_p5) AS mean_CAR_0_p5
    FROM event_level
    GROUP BY event_type_final
    ORDER BY n_events DESC;
    """,
    conn
)
sql_final_summary.to_csv(OUTPUT_DIR / "sql_final_event_type_summary.csv", index=False)

sql_mixed_original = pd.read_sql_query(
    """
    SELECT
        event_id,
        company,
        "group",
        member,
        event_category,
        event_subtype,
        event_title_en,
        sentiment_expected,
        event_type_final
    FROM event_level
    WHERE sentiment_expected = 'mixed'
    ORDER BY event_category, company, "group";
    """,
    conn
)
sql_mixed_original.to_csv(OUTPUT_DIR / "mixed_events_reclassified_list.csv", index=False)

conn.close()


# ==============================
# 11. Descriptive tables
# ==============================

event_type_counts = (
    event_level["event_type_final"]
    .value_counts()
    .rename_axis("event_type_final")
    .reset_index(name="N")
)
event_type_counts.to_csv(OUTPUT_DIR / "event_type_final_counts.csv", index=False)

event_type_descriptives = (
    event_level
    .groupby("event_type_final", as_index=False)
    .agg(
        N=("event_id", "count"),
        mean_AR_0=("AR_0", "mean"),
        mean_CAR_m1_p1=("CAR_m1_p1", "mean"),
        mean_CAR_0_p3=("CAR_0_p3", "mean"),
        mean_CAR_0_p5=("CAR_0_p5", "mean"),
        mean_CAR_m10_p10=("CAR_m10_p10", "mean"),
    )
    .sort_values("N", ascending=False)
)
event_type_descriptives.to_csv(
    OUTPUT_DIR / "event_type_final_descriptives.csv",
    index=False
)

# Event list with final classification
event_list_cols = [
    "event_id", "company", "group", "member",
    "event_title_en", "start_date",
    "sentiment_expected", "event_category", "event_subtype",
    "event_type_final"
]
event_list_cols = [c for c in event_list_cols if c in event_level.columns]

event_level[event_list_cols].to_csv(
    OUTPUT_DIR / "event_list_with_final_classification.csv",
    index=False
)


# ==============================
# 12. Regression models
# ==============================

reg_df = event_level[
    event_level["event_type_final"].isin(final_order)
].copy()

reg_df["event_type_final"] = pd.Categorical(
    reg_df["event_type_final"],
    categories=final_order,
    ordered=False
)

# Center continuous controls.
# After centering, the intercept represents the predicted CAR for the reference group
# positive_activity at average firm size and average group popularity.
reg_df["log_market_cap_c"] = (
    reg_df["log_market_cap"] - reg_df["log_market_cap"].mean()
)

reg_df["log_youtube_channel_subscribers_c"] = (
    reg_df["log_youtube_channel_subscribers"]
    - reg_df["log_youtube_channel_subscribers"].mean()
)

# Main model:
# Reference group = positive_activity, because it is first in final_order.
# Because controls are centered, Intercept = predicted CAR of positive_activity
# at average log_market_cap and average log_youtube_channel_subscribers.
main_formula: str = (
    f"{MAIN_DV} ~ C(event_type_final) "
    "+ log_market_cap_c "
    "+ log_youtube_channel_subscribers_c"
)

main_model = smf.ols(main_formula, data=reg_df).fit(cov_type="HC3")

with open(OUTPUT_DIR / f"regression_main_{MAIN_DV}.txt", "w", encoding="utf-8") as f:
    f.write(main_model.summary().as_text())

main_results_df = regression_to_dataframe(main_model, MAIN_DV)
main_results_df.to_csv(OUTPUT_DIR / f"regression_main_{MAIN_DV}.csv", index=False)

# Robustness across windows with same controls
all_window_results = []
for dv in ROBUSTNESS_DVS:
    formula = (
        f"{dv} ~ C(event_type_final) "
        "+ log_market_cap_c "
        "+ log_youtube_channel_subscribers_c"
    )
    model = smf.ols(formula, data=reg_df).fit(cov_type="HC3")

    with open(OUTPUT_DIR / f"regression_{dv}.txt", "w", encoding="utf-8") as f:
        f.write(model.summary().as_text())

    all_window_results.append(regression_to_dataframe(model, dv))

all_window_results = pd.concat(all_window_results, ignore_index=True)
all_window_results.to_csv(OUTPUT_DIR / "regression_results_all_windows.csv", index=False)


# ==============================
# 12B. Publication-style regression comparison table
# ==============================
# This table is easier to paste into a thesis/paper.
# Coefficients and robust SEs are reported in percentage points.
# The Intercept is labeled as Positive activity because controls are centered.

from collections import OrderedDict

window_labels = OrderedDict({
    "AR_0": "AR[0]",
    "CAR_m1_p1": "CAR[-1,+1]",
    "CAR_0_p1": "CAR[0,+1]",
    "CAR_0_p3": "CAR[0,+3]",
    "CAR_0_p5": "CAR[0,+5]",
    "CAR_m5_p5": "CAR[-5,+5]",
    "CAR_m10_p10": "CAR[-10,+10]",
})

variable_labels = OrderedDict({
    "Intercept": "Positive activity (intercept)",
    "C(event_type_final)[T.positive_comeback]": "Positive comeback",
    "C(event_type_final)[T.positive_concert]": "Positive concert",
    "C(event_type_final)[T.positive_resolution]": "Positive resolution",
    "C(event_type_final)[T.negative_PR_crisis]": "Negative PR crisis",
    "C(event_type_final)[T.negative_contract_crisis]": "Negative contract crisis",
    "C(event_type_final)[T.dating]": "Dating",
    "C(event_type_final)[T.artist_transition]": "Artist transition",
    "log_market_cap_c": "Log market cap (centered)",
    "log_youtube_channel_subscribers_c": "Log YouTube subscribers (centered)",
})

def significance_stars(p):
    if pd.isna(p):
        return ""
    if p < 0.01:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.10:
        return "*"
    return ""

SCALE = 100  # show coefficients in percentage points

def format_coef_se(coef, se, p):
    return f"{coef * SCALE:.2f}{significance_stars(p)}\n({se * SCALE:.2f})"

table_rows = []

for term, label in variable_labels.items():
    row = {"Variable": label}
    for dv, dv_label in window_labels.items():
        tmp = all_window_results[
            (all_window_results["DV"] == dv) &
            (all_window_results["term"] == term)
        ]

        if tmp.empty:
            row[dv_label] = ""
        else:
            coef = tmp.iloc[0]["coef"]
            se = tmp.iloc[0]["std_err"]
            p = tmp.iloc[0]["p_value"]
            row[dv_label] = format_coef_se(coef, se, p)

    table_rows.append(row)

# Model-level statistics
for stat_name, source_col, decimals in [
    ("Observations", "nobs", 0),
    ("Adjusted R²", "adj_r2", 3),
    ("Model p-value", "model_p_value", 3),
]:
    row = {"Variable": stat_name}

    for dv, dv_label in window_labels.items():
        tmp = all_window_results[all_window_results["DV"] == dv]

        if tmp.empty:
            row[dv_label] = ""
        else:
            value = tmp.iloc[0][source_col]
            if decimals == 0:
                row[dv_label] = f"{int(value)}"
            else:
                row[dv_label] = f"{value:.{decimals}f}"

    table_rows.append(row)

publication_table = pd.DataFrame(table_rows)

publication_table.to_csv(
    OUTPUT_DIR / "regression_comparison_table_centered.csv",
    index=False
)

try:
    publication_table.to_excel(
        OUTPUT_DIR / "regression_comparison_table_centered.xlsx",
        index=False
    )
except Exception as e:
    print("Excel export failed. Install openpyxl if needed:")
    print("python -m pip install openpyxl")
    print("Error:", e)


# Robustness 1: replace YouTube subscribers with Spotify monthly listeners
if "log_spotify_monthly_listeners" in reg_df.columns:
    reg_df["log_spotify_monthly_listeners_c"] = (
        reg_df["log_spotify_monthly_listeners"]
        - reg_df["log_spotify_monthly_listeners"].mean()
    )

    spotify_formula = (
        f"{MAIN_DV} ~ C(event_type_final) "
        "+ log_market_cap_c "
        "+ log_spotify_monthly_listeners_c"
    )
    spotify_model = smf.ols(spotify_formula, data=reg_df).fit(cov_type="HC3")

    with open(OUTPUT_DIR / f"regression_robustness_spotify_{MAIN_DV}.txt", "w", encoding="utf-8") as f:
        f.write(spotify_model.summary().as_text())

    regression_to_dataframe(spotify_model, MAIN_DV).to_csv(
        OUTPUT_DIR / f"regression_robustness_spotify_{MAIN_DV}.csv",
        index=False
    )

# Robustness 2: composite z-score weights
if {"company_scale_weight", "fanbase_weight"}.issubset(reg_df.columns):
    composite_formula = (
        f"{MAIN_DV} ~ C(event_type_final) "
        "+ company_scale_weight "
        "+ fanbase_weight"
    )
    composite_model = smf.ols(composite_formula, data=reg_df).fit(cov_type="HC3")

    with open(OUTPUT_DIR / f"regression_robustness_composite_{MAIN_DV}.txt", "w", encoding="utf-8") as f:
        f.write(composite_model.summary().as_text())

    regression_to_dataframe(composite_model, MAIN_DV).to_csv(
        OUTPUT_DIR / f"regression_robustness_composite_{MAIN_DV}.csv",
        index=False
    )

# VIF for main model
vif_df = calculate_vif(main_formula, reg_df)
vif_df.to_csv(OUTPUT_DIR / "main_model_vif.csv", index=False)


# ==============================
# 13. Confounding / overlapping event flag
# ==============================
# Simplified version:
# Mark event as confounded if same company has another event whose t=0 date
# is within [-10, +10] trading days of this event's t=0 date.

event0_info = event_level[["event_id", "company", "event0_date"]].dropna().copy()
event0_info["event0_date"] = pd.to_datetime(event0_info["event0_date"])

confounded_ids = set()

for company, sub in event0_info.groupby("company"):
    sub = sub.sort_values("event0_date").reset_index(drop=True)

    company_stock_dates = (
        stock_ar[stock_ar["company"] == company]
        .sort_values("date")["date"]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    date_to_idx = {d: i for i, d in enumerate(company_stock_dates)}

    for i in range(len(sub)):
        id_i = sub.loc[i, "event_id"]
        date_i = sub.loc[i, "event0_date"]
        if date_i not in date_to_idx:
            continue
        idx_i = date_to_idx[date_i]

        for j in range(len(sub)):
            if i == j:
                continue
            id_j = sub.loc[j, "event_id"]
            date_j = sub.loc[j, "event0_date"]
            if date_j not in date_to_idx:
                continue
            idx_j = date_to_idx[date_j]

            if abs(idx_j - idx_i) <= 10:
                confounded_ids.add(id_i)

event_level["confounded_same_company_m10_p10"] = event_level["event_id"].isin(confounded_ids)

event_level[[
    "event_id", "company", "event0_date",
    "event_type_final", "confounded_same_company_m10_p10"
]].to_csv(OUTPUT_DIR / "confounding_flags.csv", index=False)

clean_df = reg_df[
    ~reg_df["event_id"].isin(confounded_ids)
].copy()

clean_regression_results = []
if len(clean_df) > 20:
    clean_df["event_type_final"] = pd.Categorical(
        clean_df["event_type_final"],
        categories=final_order,
        ordered=False
    )

    clean_df["log_market_cap_c"] = (
        clean_df["log_market_cap"] - clean_df["log_market_cap"].mean()
    )
    clean_df["log_youtube_channel_subscribers_c"] = (
        clean_df["log_youtube_channel_subscribers"]
        - clean_df["log_youtube_channel_subscribers"].mean()
    )

    for dv in ROBUSTNESS_DVS:
        formula = (
            f"{dv} ~ C(event_type_final) "
            "+ log_market_cap_c "
            "+ log_youtube_channel_subscribers_c"
        )
        model = smf.ols(formula, data=clean_df).fit(cov_type="HC3")

        with open(OUTPUT_DIR / f"regression_clean_{dv}.txt", "w", encoding="utf-8") as f:
            f.write(model.summary().as_text())

        clean_regression_results.append(regression_to_dataframe(model, dv))

    clean_regression_results = pd.concat(clean_regression_results, ignore_index=True)
    clean_regression_results.to_csv(
        OUTPUT_DIR / "regression_results_all_windows_clean_sample.csv",
        index=False
    )

    clean_counts = (
        clean_df["event_type_final"]
        .value_counts()
        .rename_axis("event_type_final")
        .reset_index(name="N_clean")
    )
    clean_counts.to_csv(OUTPUT_DIR / "event_type_final_counts_clean_sample.csv", index=False)


# ==============================
# 14. Print summary
# ==============================

print("\nDone. All outputs saved in:", OUTPUT_DIR.resolve())
print("\nFinal event type counts:")
print(event_type_counts.to_string(index=False))

print("\nMain model:")
print(main_model.summary())

print("\nImportant output files:")
print("- event_level_CAR_dataset_final.csv")
print("- event_day_panel_AR.csv")
print("- CAAR_by_final_event_type.png")
print("- weight_variables_correlation_heatmap.png")
print("- regression_main_CAR_m1_p1.txt")
print("- regression_results_all_windows.csv")
print("- regression_comparison_table_centered.csv")
print("- regression_comparison_table_centered.xlsx")
print("- event_list_with_final_classification.csv")
print("- mixed_events_reclassified_list.csv")
