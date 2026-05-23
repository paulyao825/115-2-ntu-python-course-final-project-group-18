"""
Collect daily stock price data for K-pop entertainment companies.

This script downloads daily OHLCV stock data for JYP, SM, YG, and HYBE
from Yahoo Finance and saves the cleaned output to:

    data/final/stock_daily.csv

Output columns:
    date, company, ticker, open, high, low, close, adj_close, volume, daily_return
"""

from pathlib import Path

import pandas as pd
import yfinance as yf


START_DATE = "2020-12-25"
END_DATE = "2026-01-16"

TICKERS = {
    "JYP": "035900.KQ",
    "SM": "041510.KQ",
    "YG": "122870.KQ",
    "HYBE": "352820.KS",
}


def download_stock_data(company: str, ticker: str) -> pd.DataFrame:
    """Download and clean daily stock data for one company."""
    print(f"Downloading {company} ({ticker})...")

    df = yf.download(
        ticker,
        start=START_DATE,
        end=END_DATE,
        progress=False,
        auto_adjust=False,
    )

    if df.empty:
        raise ValueError(f"No stock data downloaded for {company} ({ticker}).")

    df = df.reset_index()

    # yfinance may return multi-index columns in some versions.
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

    df["company"] = company
    df["ticker"] = ticker

    df = df.rename(
        columns={
            "Date": "date",
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Adj Close": "adj_close",
            "Volume": "volume",
        }
    )

    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    df["daily_return"] = df["adj_close"].pct_change()

    return df[
        [
            "date",
            "company",
            "ticker",
            "open",
            "high",
            "low",
            "close",
            "adj_close",
            "volume",
            "daily_return",
        ]
    ]


def validate_stock_data(stock_daily: pd.DataFrame) -> None:
    """Print basic validation results for the collected stock data."""
    print("\nValidation summary")
    print("-" * 40)

    print("Rows:", len(stock_daily))
    print("Columns:", list(stock_daily.columns))
    print("Date range:", stock_daily["date"].min(), "to", stock_daily["date"].max())

    print("\nRows by company:")
    print(stock_daily.groupby(["company", "ticker"]).size())

    print("\nMissing values:")
    print(stock_daily.isna().sum())

    duplicate_count = stock_daily.duplicated(["date", "ticker"]).sum()
    print("\nDuplicated date + ticker rows:", duplicate_count)

    if duplicate_count > 0:
        raise ValueError("Duplicated date + ticker rows found.")

    expected_tickers = set(TICKERS.values())
    actual_tickers = set(stock_daily["ticker"].unique())

    if expected_tickers != actual_tickers:
        raise ValueError(
            f"Ticker mismatch. Expected {expected_tickers}, got {actual_tickers}."
        )


def main() -> None:
    """Download all stock data and save the final CSV."""
    output_path = Path("data/final/stock_daily.csv")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    all_data = []

    for company, ticker in TICKERS.items():
        company_data = download_stock_data(company, ticker)
        all_data.append(company_data)

    stock_daily = pd.concat(all_data, ignore_index=True)

    validate_stock_data(stock_daily)

    stock_daily.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"\nSaved stock data to {output_path}")


if __name__ == "__main__":
    main()
