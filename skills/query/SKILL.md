---
name: query
description: |
  Fetch financial market closing/price data for cross-validation.
  Supports A-shares (CN), Hong Kong stocks (HK), US stocks, stock indices,
  commodity futures, and spot commodities.
  Triggers: "stock price", "closing price", "market data", "akshare",
  "A股", "港股", "美股", "商品", "现货", "cross-validate price",
  "price comparison", "金价", "oil price", "commodity price",
  "index", "指数", "上证", "沪深300", "恒生", "纳斯达克", "标普",
  "futures", "期货", "螺纹钢", "铁矿石", "焦炭", "豆粕", "棕榈油".
---

# AKShare Market Data Query

## Usage

```bash
${CLAUDE_PLUGIN_ROOT}/bin/akshare_query.py <market> <symbol> [--start YYYY-MM-DD] [--end YYYY-MM-DD] [--fields close,volume,open,high,low]
```

## Markets & Symbol Conventions

| Market | Code | Symbol Format | Examples |
|--------|------|--------------|----------|
| A-shares | `cn` | 6-digit code (no prefix) | `000001` (平安银行), `600519` (贵州茅台), `300750` (宁德时代) |
| Hong Kong | `hk` | 5-digit code | `00700` (腾讯), `09988` (阿里巴巴), `01810` (小米) |
| US stocks | `us` | Ticker symbol | `AAPL`, `MSFT`, `TSLA`, `NVDA` |
| Indices | `index` | Code or alias | `000001`/`上证指数`, `HS300`/`沪深300`, `HSI`/`恒生指数`, `SPX`/`标普500` |
| Futures | `futures` | Contract code or name | `RB`/`螺纹钢`, `I`/`铁矿石`, `CU`/`铜`, `IF`/`沪深300期货` |
| Commodities (spot) | `commodity` | Commodity code or name | `AU`/`黄金`, `CU`/`铜`, `RB`/`螺纹钢`, `OIL`/`原油`, `M`/`豆粕`, `CF`/`棉花` |

### Index Symbol Quick Reference

| Region | Symbol | Alias | Name |
|--------|--------|-------|------|
| CN | `000001` | `上证指数`, `SH` | 上证综指 |
| CN | `399001` | `深证成指`, `SZ` | 深证成指 |
| CN | `000300` | `沪深300`, `HS300` | 沪深300 |
| CN | `000016` | `上证50`, `SZ50` | 上证50 |
| CN | `000905` | `中证500`, `ZZ500` | 中证500 |
| CN | `000852` | `中证1000`, `ZZ1000` | 中证1000 |
| CN | `399006` | `创业板指`, `CYB` | 创业板指 |
| CN | `000688` | `科创50`, `KC50` | 科创50 |
| HK | — | `HSI`, `恒生指数` | 恒生指数 |
| HK | — | `HSTECH`, `恒生科技` | 恒生科技指数 |
| US | — | `SPX`, `标普500` | S&P 500 |
| US | — | `IXIC`, `纳斯达克` | NASDAQ Composite |
| US | — | `DJI`, `道琼斯` | Dow Jones |

### Futures Symbol Quick Reference

| Category | Symbol | Alias | Name |
|----------|--------|-------|------|
| 黑色系 | `RB` | `螺纹钢` | 螺纹钢 |
| 黑色系 | `I` | `铁矿石` | 铁矿石 |
| 黑色系 | `J` | `焦炭` | 焦炭 |
| 黑色系 | `JM` | `焦煤` | 焦煤 |
| 黑色系 | `HC` | `热卷` | 热轧卷板 |
| 有色 | `CU` | `铜`, `沪铜` | 铜 |
| 有色 | `AL` | `铝`, `沪铝` | 铝 |
| 有色 | `ZN` | `锌`, `沪锌` | 锌 |
| 有色 | `NI` | `镍`, `沪镍` | 镍 |
| 能化 | `SC` | `原油期货` | 原油 (INE) |
| 能化 | `MA` | `甲醇` | 甲醇 |
| 能化 | `TA` | `PTA` | PTA |
| 能化 | `PP` | `聚丙烯` | 聚丙烯 |
| 能化 | `L` | `塑料`, `LLDPE` | LLDPE |
| 农产品 | `M` | `豆粕` | 豆粕 |
| 农产品 | `Y` | `豆油` | 豆油 |
| 农产品 | `P` | `棕榈油` | 棕榈油 |
| 农产品 | `CF` | `棉花` | 棉花 |
| 农产品 | `SR` | `白糖` | 白糖 |
| 农产品 | `AP` | `苹果` | 苹果 |
| 农产品 | `LH` | `生猪` | 生猪 |
| 金融 | `IF` | `沪深300期货` | 沪深300股指期货 |
| 金融 | `IC` | `中证500期货` | 中证500股指期货 |
| 金融 | `IH` | `上证50期货` | 上证50股指期货 |
| 金融 | `IM` | `中证1000期货` | 中证1000股指期货 |
| 金融 | `T` | `十年国债` | 10年国债期货 |
| 金融 | `TF` | `五年国债` | 5年国债期货 |

### Spot Commodity Quick Reference

Uses `futures_spot_price_daily` for 80+ commodities. Common ones:

| Category | Symbol | Alias | Name |
|----------|--------|-------|------|
| 贵金属 | `AU` | `黄金`, `GOLD` | 黄金 |
| 贵金属 | `AG` | `白银`, `SILVER` | 白银 |
| 有色 | `CU` | `铜`, `沪铜` | 铜 |
| 有色 | `AL` | `铝`, `沪铝` | 铝 |
| 有色 | `ZN` | `锌` | 锌 |
| 有色 | `NI` | `镍` | 镍 |
| 黑色系 | `RB` | `螺纹钢` | 螺纹钢 |
| 黑色系 | `I` | `铁矿石` | 铁矿石 |
| 黑色系 | `HC` | `热卷` | 热轧卷板 |
| 黑色系 | `J` | `焦炭` | 焦炭 |
| 能源 | `OIL` | `原油`, `CRUDE` | WTI原油 (国际) |
| 能源 | `FU` | `燃油` | 燃料油 |
| 能源 | `BU` | `沥青` | 石油沥青 |
| 化工 | `MA` | `甲醇` | 甲醇 |
| 化工 | `TA` | `PTA` | PTA |
| 化工 | `PP` | `聚丙烯` | 聚丙烯 |
| 化工 | `L` | `塑料`, `LLDPE` | LLDPE |
| 化工 | `SA` | `纯碱` | 纯碱 |
| 农产品 | `M` | `豆粕` | 豆粕 |
| 农产品 | `Y` | `豆油` | 豆油 |
| 农产品 | `P` | `棕榈油` | 棕榈油 |
| 农产品 | `CF` | `棉花` | 棉花 |
| 农产品 | `SR` | `白糖` | 白糖 |
| 农产品 | `LH` | `生猪` | 生猪 |
| 农产品 | `JD` | `鸡蛋` | 鸡蛋 |

> **Note:** Spot prices include basis data. Use `--fields close,dom_basis` to see spot vs futures spread.

## Output Format

JSON array of objects:

```json
[
  {"date": "2024-01-02", "close": 10.52},
  {"date": "2024-01-03", "close": 10.68}
]
```

With `--fields close,volume`:
```json
[
  {"date": "2024-01-02", "close": 10.52, "volume": 1234567},
  {"date": "2024-01-03", "close": 10.68, "volume": 2345678}
]
```

## Defaults

- `--start`: 30 days ago
- `--end`: today
- `--fields`: `close` only

## When to Use

- User asks for stock/commodity/index/futures prices
- Cross-validation of market data across sources
- Comparing price movements between assets
- Checking historical closing prices
- Tracking index performance (上证、恒生、标普等)
- Monitoring futures prices (螺纹钢、铁矿石、豆粕等)

## Common Patterns

```bash
# Major index comparison
${CLAUDE_PLUGIN_ROOT}/bin/akshare_query.py index 上证指数 --start 2024-06-01
${CLAUDE_PLUGIN_ROOT}/bin/akshare_query.py index HS300 --start 2024-06-01
${CLAUDE_PLUGIN_ROOT}/bin/akshare_query.py index HSI --start 2024-06-01
${CLAUDE_PLUGIN_ROOT}/bin/akshare_query.py index SPX --start 2024-06-01

# Futures prices
${CLAUDE_PLUGIN_ROOT}/bin/akshare_query.py futures RB --start 2024-06-01  # 螺纹钢
${CLAUDE_PLUGIN_ROOT}/bin/akshare_query.py futures 铁矿石 --start 2024-06-01
${CLAUDE_PLUGIN_ROOT}/bin/akshare_query.py futures CU --start 2024-06-01 --fields close,volume

# Stock index futures vs spot index
${CLAUDE_PLUGIN_ROOT}/bin/akshare_query.py index HS300 --start 2024-06-01
${CLAUDE_PLUGIN_ROOT}/bin/akshare_query.py futures IF --start 2024-06-01

# Compare gold and oil recent prices
${CLAUDE_PLUGIN_ROOT}/bin/akshare_query.py commodity AU --start 2024-06-01
${CLAUDE_PLUGIN_ROOT}/bin/akshare_query.py commodity OIL --start 2024-06-01

# A-share vs HK dual-listed comparison
${CLAUDE_PLUGIN_ROOT}/bin/akshare_query.py cn 601318 --start 2024-01-01  # 中国平安 A
${CLAUDE_PLUGIN_ROOT}/bin/akshare_query.py hk 02318 --start 2024-01-01   # 中国平安 H

# US tech with volume
${CLAUDE_PLUGIN_ROOT}/bin/akshare_query.py us AAPL --start 2024-01-01 --fields close,volume
```

## Error Handling

The script retries up to 3 times on network errors. If a symbol is not found, it returns:
```json
{"error": "Symbol not found", "market": "index", "symbol": "UNKNOWN"}
```

## First Run

On first invocation, the script auto-creates a Python venv and installs `akshare` + `pandas`. This takes ~30 seconds. Subsequent calls are instant.
