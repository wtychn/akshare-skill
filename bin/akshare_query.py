#!/usr/bin/env python3
"""AKShare market data query CLI for Claude Code.

Fetches closing/price data for A-shares, HK stocks, US stocks, and spot commodities.
Outputs JSON for easy consumption by LLMs.

Usage:
    akshare_query.py <market> <symbol> [--start YYYY-MM-DD] [--end YYYY-MM-DD] [--fields f1,f2,...]

Markets: cn, hk, us, commodity
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

VENV_DIR = Path(__file__).parent.parent / ".venv"
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds


def ensure_venv():
    """Create venv and install dependencies if not present."""
    if (VENV_DIR / "bin" / "python3").exists():
        return

    print(json.dumps({"status": "setup", "message": "Installing dependencies (first run)..."}), file=sys.stderr)

    subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)
    pip = str(VENV_DIR / "bin" / "pip")
    subprocess.run(
        [pip, "install", "-q", "akshare", "pandas"],
        check=True,
        capture_output=True,
    )


def relaunch_in_venv():
    """Re-execute this script inside the venv Python."""
    venv_python = str(VENV_DIR / "bin" / "python3")
    if sys.executable == venv_python:
        return  # already in venv
    os.execv(venv_python, [venv_python] + sys.argv)


def retry(fn, retries=MAX_RETRIES, delay=RETRY_DELAY):
    """Retry a function with exponential backoff."""
    last_err = None
    for attempt in range(retries):
        try:
            return fn()
        except Exception as e:
            last_err = e
            if attempt < retries - 1:
                time.sleep(delay * (attempt + 1))
    raise last_err


def fetch_cn(symbol, start_date, end_date):
    """Fetch A-share (China) historical data via Sina source."""
    import akshare as ak
    import pandas as pd

    # Determine exchange prefix: 6xx = Shanghai, others = Shenzhen
    if symbol.startswith("6") or symbol.startswith("9"):
        prefixed = f"sh{symbol}"
    else:
        prefixed = f"sz{symbol}"

    df = ak.stock_zh_a_daily(
        symbol=prefixed,
        start_date=start_date.replace("-", ""),
        end_date=end_date.replace("-", ""),
        adjust="qfq",
    )
    # Columns already English: date, open, high, low, close, volume
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
    return df


def fetch_hk(symbol, start_date, end_date):
    """Fetch Hong Kong stock historical data via Sina source."""
    import akshare as ak
    import pandas as pd

    df = ak.stock_hk_daily(symbol=symbol, adjust="qfq")
    # Columns already English: date, open, high, low, close, volume
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
    return df


def fetch_us(symbol, start_date, end_date):
    """Fetch US stock historical data via Sina source."""
    import akshare as ak
    import pandas as pd

    df = ak.stock_us_daily(symbol=symbol, adjust="qfq")
    # Columns already English: date, open, high, low, close, volume
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
    return df


def fetch_index(symbol, start_date, end_date):
    """Fetch stock index historical data.

    Supports Chinese indices (上证指数, 沪深300, etc.), HK indices (恒生指数),
    and US indices (S&P500, NASDAQ, Dow Jones).
    """
    import akshare as ak
    import pandas as pd

    symbol_upper = symbol.upper()

    # Chinese index aliases → internal code
    CN_INDEX_MAP = {
        "000001": "sh000001", "上证指数": "sh000001", "上证综指": "sh000001", "SH": "sh000001",
        "399001": "sz399001", "深证成指": "sz399001", "SZ": "sz399001",
        "399006": "sz399006", "创业板指": "sz399006", "创业板": "sz399006", "CYB": "sz399006",
        "000300": "sh000300", "沪深300": "sh000300", "HS300": "sh000300",
        "000016": "sh000016", "上证50": "sh000016", "SZ50": "sh000016",
        "000905": "sh000905", "中证500": "sh000905", "ZZ500": "sh000905",
        "000852": "sh000852", "中证1000": "sh000852", "ZZ1000": "sh000852",
        "399673": "sz399673", "创业板50": "sz399673",
        "000688": "sh000688", "科创50": "sh000688", "KC50": "sh000688",
    }

    # HK index aliases
    HK_INDEX_MAP = {
        "HSI": "HSI", "恒生指数": "HSI", "恒指": "HSI",
        "HSTECH": "HSTECH", "恒生科技": "HSTECH", "恒生科技指数": "HSTECH",
        "HSCEI": "HSCEI", "国企指数": "HSCEI", "H股指数": "HSCEI",
    }

    # US index aliases
    US_INDEX_MAP = {
        "SPX": "SPX", "SP500": "SPX", "标普500": "SPX", "标普": "SPX", ".INX": "SPX",
        "IXIC": "IXIC", "NASDAQ": "IXIC", "纳斯达克": "IXIC", "纳指": "IXIC",
        "DJI": "DJI", "DJIA": "DJI", "道琼斯": "DJI", "道指": "DJI",
    }

    if symbol_upper in CN_INDEX_MAP or symbol in CN_INDEX_MAP:
        code = CN_INDEX_MAP.get(symbol_upper) or CN_INDEX_MAP.get(symbol)
        df = ak.stock_zh_index_daily(symbol=code)
        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    elif symbol_upper in HK_INDEX_MAP or symbol in HK_INDEX_MAP:
        code = HK_INDEX_MAP.get(symbol_upper) or HK_INDEX_MAP.get(symbol)
        df = ak.stock_hk_index_daily_em(symbol=code)
        df = df.rename(columns={
            "日期": "date", "开盘": "open", "最高": "high",
            "最低": "low", "收盘": "close", "成交量": "volume",
        })
        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    elif symbol_upper in US_INDEX_MAP or symbol in US_INDEX_MAP:
        code = US_INDEX_MAP.get(symbol_upper) or US_INDEX_MAP.get(symbol)
        # Use sina US index interface
        df = ak.index_us_stock_sina(symbol=f".{code}")
        df = df.rename(columns={"date": "date", "close": "close", "open": "open", "high": "high", "low": "low", "volume": "volume"})
        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    else:
        # Try as raw Chinese index code (6 digits → add prefix)
        if len(symbol) == 6 and symbol.isdigit():
            if symbol.startswith("0") or symbol.startswith("9"):
                code = f"sh{symbol}"
            else:
                code = f"sz{symbol}"
            df = ak.stock_zh_index_daily(symbol=code)
            df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
        else:
            raise ValueError(f"Unknown index symbol: {symbol}")

    df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
    return df


def fetch_futures(symbol, start_date, end_date):
    """Fetch Chinese commodity/financial futures data (main continuous contract).

    Supports common futures by symbol code or Chinese name alias.
    """
    import akshare as ak
    import pandas as pd

    symbol_upper = symbol.upper()

    # Futures aliases → sina main contract symbol
    FUTURES_MAP = {
        # 黑色系
        "RB": "RB0", "螺纹钢": "RB0", "螺纹": "RB0",
        "I": "I0", "铁矿石": "I0", "铁矿": "I0",
        "J": "J0", "焦炭": "J0",
        "JM": "JM0", "焦煤": "JM0",
        "HC": "HC0", "热卷": "HC0", "热轧卷板": "HC0",
        "SS": "SS0", "不锈钢": "SS0",
        # 有色金属
        "CU": "CU0", "铜": "CU0", "沪铜": "CU0",
        "AL": "AL0", "铝": "AL0", "沪铝": "AL0",
        "ZN": "ZN0", "锌": "ZN0", "沪锌": "ZN0",
        "NI": "NI0", "镍": "NI0", "沪镍": "NI0",
        "SN": "SN0", "锡": "SN0", "沪锡": "SN0",
        "PB": "PB0", "铅": "PB0", "沪铅": "PB0",
        # 能源化工
        "SC": "SC0", "原油": "SC0", "原油期货": "SC0",
        "FU": "FU0", "燃油": "FU0", "燃料油": "FU0",
        "LU": "LU0", "低硫燃油": "LU0",
        "BU": "BU0", "沥青": "BU0",
        "MA": "MA0", "甲醇": "MA0",
        "EG": "EG0", "乙二醇": "EG0",
        "TA": "TA0", "PTA": "TA0",
        "PP": "PP0", "聚丙烯": "PP0",
        "L": "L0", "塑料": "L0", "聚乙烯": "L0", "LLDPE": "L0",
        "V": "V0", "PVC": "V0",
        "EB": "EB0", "苯乙烯": "EB0",
        "PG": "PG0", "LPG": "PG0", "液化气": "PG0",
        # 农产品
        "A": "A0", "豆一": "A0", "大豆": "A0",
        "B": "B0", "豆二": "B0",
        "M": "M0", "豆粕": "M0",
        "Y": "Y0", "豆油": "Y0",
        "P": "P0", "棕榈油": "P0",
        "OI": "OI0", "菜油": "OI0", "菜籽油": "OI0",
        "RM": "RM0", "菜粕": "RM0",
        "CF": "CF0", "棉花": "CF0",
        "SR": "SR0", "白糖": "SR0",
        "AP": "AP0", "苹果": "AP0",
        "CJ": "CJ0", "红枣": "CJ0",
        "PK": "PK0", "花生": "PK0",
        "C": "C0", "玉米": "C0",
        "CS": "CS0", "淀粉": "CS0", "玉米淀粉": "CS0",
        "JD": "JD0", "鸡蛋": "JD0",
        "LH": "LH0", "生猪": "LH0",
        "SP": "SP0", "纸浆": "SP0",
        # 金融期货
        "IF": "IF0", "沪深300期货": "IF0", "IF300": "IF0",
        "IC": "IC0", "中证500期货": "IC0",
        "IH": "IH0", "上证50期货": "IH0",
        "IM": "IM0", "中证1000期货": "IM0",
        "T": "T0", "十年国债": "T0", "国债期货": "T0",
        "TF": "TF0", "五年国债": "TF0",
        "TS": "TS0", "两年国债": "TS0",
    }

    # Resolve symbol
    futures_code = FUTURES_MAP.get(symbol_upper) or FUTURES_MAP.get(symbol)
    if not futures_code:
        # Try appending "0" for main contract if raw code given
        futures_code = f"{symbol_upper}0"

    df = ak.futures_zh_daily_sina(symbol=futures_code)
    df = df.rename(columns={
        "日期": "date", "开盘价": "open", "最高价": "high",
        "最低价": "low", "收盘价": "close", "成交量": "volume", "持仓量": "open_interest",
    })
    # Handle column name variants
    if "date" not in df.columns and "日期" not in df.columns:
        # Some versions use English columns already
        pass
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
    df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
    return df


def fetch_commodity(symbol, start_date, end_date):
    """Fetch spot commodity prices via futures_spot_price_daily.

    Covers 80+ commodities: metals, energy, chemicals, agriculture, etc.
    Also includes basis data (spot vs futures spread).
    """
    import akshare as ak
    import pandas as pd

    symbol_upper = symbol.upper()

    # Map common aliases to the vars_list code used by futures_spot_price_daily
    SPOT_ALIAS_MAP = {
        # 贵金属
        "GOLD": "AU", "黄金": "AU",
        "SILVER": "AG", "白银": "AG",
        # 有色金属
        "铜": "CU", "沪铜": "CU", "COPPER": "CU",
        "铝": "AL", "沪铝": "AL",
        "锌": "ZN", "沪锌": "ZN",
        "铅": "PB", "沪铅": "PB",
        "镍": "NI", "沪镍": "NI",
        "锡": "SN", "沪锡": "SN",
        # 黑色系
        "螺纹钢": "RB", "螺纹": "RB",
        "铁矿石": "I", "铁矿": "I",
        "热卷": "HC", "热轧卷板": "HC",
        "焦炭": "J",
        "焦煤": "JM",
        "不锈钢": "SS",
        # 能源
        "燃油": "FU", "燃料油": "FU",
        "沥青": "BU",
        "LPG": "PG", "液化气": "PG", "液化石油气": "PG",
        # 化工
        "甲醇": "MA",
        "PTA": "TA",
        "乙二醇": "EG",
        "聚丙烯": "PP",
        "塑料": "L", "聚乙烯": "L", "LLDPE": "L",
        "PVC": "V", "聚氯乙烯": "V",
        "苯乙烯": "EB",
        "纯碱": "SA",
        "玻璃": "FG",
        "尿素": "UR",
        # 农产品
        "豆粕": "M",
        "豆油": "Y",
        "棕榈油": "P",
        "菜油": "OI", "菜籽油": "OI",
        "菜粕": "RM",
        "大豆": "A", "豆一": "A",
        "豆二": "B",
        "玉米": "C",
        "淀粉": "CS", "玉米淀粉": "CS",
        "棉花": "CF",
        "白糖": "SR",
        "苹果": "AP",
        "红枣": "CJ",
        "花生": "PK",
        "鸡蛋": "JD",
        "生猪": "LH",
        "纸浆": "SP",
        # 金融
        "沪深300": "IF",
        "中证500": "IC",
        "上证50": "IH",
        "中证1000": "IM",
    }

    # Special handling for crude oil (no domestic spot market, use international futures)
    OIL_ALIASES = {"原油", "OIL", "CRUDE", "SC", "WTI", "BRENT"}
    if symbol_upper in OIL_ALIASES or symbol in OIL_ALIASES:
        # WTI = CL, Brent = B
        oil_code = "B" if symbol_upper in ("BRENT", "布伦特") else "CL"
        df = ak.futures_foreign_hist(symbol=oil_code)
        df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
        df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
        return df

    # Resolve to vars_list code
    code = SPOT_ALIAS_MAP.get(symbol_upper) or SPOT_ALIAS_MAP.get(symbol) or symbol_upper

    df = ak.futures_spot_price_daily(
        start_day=start_date.replace("-", ""),
        end_day=end_date.replace("-", ""),
        vars_list=[code],
    )

    if df is None or df.empty:
        raise ValueError(f"No spot data for symbol: {symbol}")

    # Rename to standard format; include basis info as extra fields
    df = df.rename(columns={
        "date": "date",
        "spot_price": "close",
        "near_contract_price": "near_price",
        "dominant_contract_price": "dom_price",
        "near_basis": "near_basis",
        "dom_basis": "dom_basis",
        "near_basis_rate": "near_basis_rate",
        "dom_basis_rate": "dom_basis_rate",
    })
    df["open"] = df["close"]
    df["high"] = df["close"]
    df["low"] = df["close"]
    df["volume"] = 0

    # date format: 20250610 → 2025-06-10
    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d").dt.strftime("%Y-%m-%d")
    df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
    return df


MARKET_FETCHERS = {
    "cn": fetch_cn,
    "hk": fetch_hk,
    "us": fetch_us,
    "commodity": fetch_commodity,
    "index": fetch_index,
    "futures": fetch_futures,
}


def main():
    parser = argparse.ArgumentParser(description="Fetch market data via AKShare")
    parser.add_argument("market", choices=["cn", "hk", "us", "commodity", "index", "futures"])
    parser.add_argument("symbol", help="Stock code or commodity symbol")
    parser.add_argument("--start", default=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"))
    parser.add_argument("--end", default=datetime.now().strftime("%Y-%m-%d"))
    parser.add_argument("--fields", default="close", help="Comma-separated: close,open,high,low,volume")

    args = parser.parse_args()
    fields = [f.strip() for f in args.fields.split(",")]

    fetcher = MARKET_FETCHERS[args.market]

    try:
        df = retry(lambda: fetcher(args.symbol, args.start, args.end))
    except Exception as e:
        error_msg = str(e)
        if "not found" in error_msg.lower() or "404" in error_msg or "empty" in error_msg.lower():
            print(json.dumps({"error": "Symbol not found", "market": args.market, "symbol": args.symbol}))
        else:
            print(json.dumps({"error": error_msg, "market": args.market, "symbol": args.symbol}))
        sys.exit(1)

    if df is None or df.empty:
        print(json.dumps({"error": "No data returned", "market": args.market, "symbol": args.symbol}))
        sys.exit(1)

    # Ensure date column is string
    if "date" in df.columns:
        df["date"] = df["date"].astype(str)

    # Select requested fields + date
    output_cols = ["date"] + [f for f in fields if f in df.columns]
    result = df[output_cols].to_dict(orient="records")

    print(json.dumps(result, ensure_ascii=False, default=str))


if __name__ == "__main__":
    ensure_venv()
    relaunch_in_venv()
    main()
