from __future__ import annotations

import argparse
from datetime import timedelta

import yfinance as yf

from common import FINAL_DIR, PROJECT_ROOT, START_DATE, END_DATE, ensure_dirs, write_csv


FIELDNAMES = ["company", "ticker", "date", "open", "high", "low", "close", "adj_close", "volume"]

TICKERS = {
    "JYP": "035900.KQ",
    "SM": "041510.KQ",
    "YG": "122870.KQ",
    "HYBE": "352820.KS",
}


def resolve_path(value: str):
    from pathlib import Path

    path = Path(value)
    return path if path.is_absolute() else PROJECT_ROOT / path


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect daily stock prices from Yahoo Finance.")
    parser.add_argument("--output", default=str(FINAL_DIR / "stock_daily.csv"))
    args = parser.parse_args()

    ensure_dirs()
    rows = []
    for company, ticker in TICKERS.items():
        # yfinance treats end as exclusive, so add one day to include 2026-01-01.
        end_exclusive = (END_DATE + timedelta(days=1)).isoformat()
        df = yf.download(ticker, start=START_DATE.isoformat(), end=end_exclusive, progress=False)
        if df.empty:
            continue
        for idx, record in df.iterrows():
            rows.append(
                {
                    "company": company,
                    "ticker": ticker,
                    "date": idx.date().isoformat(),
                    "open": float(record.get("Open", 0)),
                    "high": float(record.get("High", 0)),
                    "low": float(record.get("Low", 0)),
                    "close": float(record.get("Close", 0)),
                    "adj_close": float(record.get("Adj Close", record.get("Close", 0))),
                    "volume": int(record.get("Volume", 0)),
                }
            )

    write_csv(resolve_path(args.output), rows, FIELDNAMES)
    print(f"Wrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
