from __future__ import annotations

import csv
from datetime import date
from pathlib import Path

import yfinance as yf


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "data" / "weights" / "company_weights.csv"


COMPANIES = [
    {"company": "HYBE", "ticker": "352820.KS"},
    {"company": "JYP", "ticker": "035900.KQ"},
    {"company": "SM", "ticker": "041510.KQ"},
    {"company": "YG", "ticker": "122870.KQ"},
]


FIELDNAMES = [
    "company",
    "ticker",
    "market_cap",
    "revenue",
    "company_scale_weight",
    "source_date",
    "source_url",
    "notes",
]


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def collect_company_weight(company: dict) -> dict:
    ticker_symbol = company["ticker"]

    base_row = {
        "company": company["company"],
        "ticker": ticker_symbol,
        "market_cap": "",
        "revenue": "",
        "company_scale_weight": "",
        "source_date": date.today().isoformat(),
        "source_url": "Yahoo Finance via yfinance",
        "notes": "market_cap is used as company size proxy",
    }

    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info

        base_row["market_cap"] = info.get("marketCap", "")
        base_row["revenue"] = info.get("totalRevenue", "")

        if not base_row["market_cap"]:
            base_row["notes"] = "market_cap missing from yfinance response"

    except Exception as exc:
        base_row["notes"] = f"yfinance collection failed: {type(exc).__name__}: {exc}"

    return base_row


def main() -> None:
    rows = []

    for company in COMPANIES:
        print(f"Collecting {company['company']}...")
        rows.append(collect_company_weight(company))

    write_csv(OUTPUT_PATH, rows)

    print(f"Wrote {len(rows)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()