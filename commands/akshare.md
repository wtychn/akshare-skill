---
name: akshare
description: Query financial market data (A-shares, HK, US, commodities)
arguments:
  - name: query
    description: "Market and symbol, e.g. 'cn 600519 --start 2024-01-01'"
    required: true
---

# AKShare Market Data Query

Run the akshare query script with the provided arguments.

```bash
${CLAUDE_PLUGIN_ROOT}/bin/akshare_query.py $ARGUMENTS
```

## Argument Format

```
<market> <symbol> [--start YYYY-MM-DD] [--end YYYY-MM-DD] [--fields close,volume,open,high,low]
```

## Examples

- `/akshare cn 600519` — 贵州茅台 recent 30 days
- `/akshare us AAPL --start 2024-01-01 --fields close,volume` — Apple with volume
- `/akshare commodity AU --start 2024-06-01` — Gold spot price
- `/akshare hk 00700` — Tencent recent prices
