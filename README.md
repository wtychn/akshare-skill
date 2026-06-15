# akshare — Claude Code Plugin

Financial market data query tool for A-shares, HK stocks, US stocks, indices, futures, and spot commodities via [AKShare](https://github.com/akfamily/akshare).

## Install

```bash
# Clone or copy to plugins directory
cp -r akshare-skill ~/.claude/plugins/akshare

# Or symlink
ln -s /path/to/akshare-skill ~/.claude/plugins/akshare
```

Enable in `.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "akshare": true
  }
}
```

## Usage

The skill auto-activates when you ask about stock prices, market data, indices, futures, or commodities.

You can also invoke directly:

```
/akshare cn 600519 --start 2024-01-01
/akshare us AAPL --fields close,volume
/akshare index 上证指数 --start 2024-06-01
/akshare index HSI --start 2024-06-01
/akshare futures RB --start 2024-06-01 --fields close,volume
/akshare commodity AU
```

## Supported Markets

| Market | Code | Examples |
|--------|------|----------|
| A-shares | `cn` | `000001` (平安银行), `600519` (贵州茅台) |
| Hong Kong | `hk` | `00700` (腾讯), `09988` (阿里巴巴) |
| US stocks | `us` | `AAPL`, `MSFT`, `TSLA` |
| Indices | `index` | `上证指数`, `沪深300`, `HSI` (恒生), `SPX` (标普500), `纳斯达克` |
| Futures | `futures` | `RB` (螺纹钢), `I` (铁矿石), `CU` (铜), `IF` (沪深300期货) |
| Commodities (spot) | `commodity` | `AU` (黄金), `AG` (白银), `OIL` (原油) |

## Output Format

JSON array for LLM consumption:

```json
[
  {"date": "2024-01-02", "close": 10.52},
  {"date": "2024-01-03", "close": 10.68}
]
```

## Data Sources

| Market | Primary Source | Fallback |
|--------|---------------|----------|
| A-shares (`cn`) | Sina (`stock_zh_a_daily`) | — |
| HK stocks (`hk`) | Sina (`stock_hk_daily`) | — |
| US stocks (`us`) | Sina (`stock_us_daily`) | — |
| CN indices | Sina (`stock_zh_index_daily`) | — |
| HK indices | Sina (`stock_hk_index_daily_sina`) | 东方财富 (`stock_hk_index_daily_em`) |
| US indices | Sina (`index_us_stock_sina`) | — |
| Futures | Sina (`futures_zh_daily_sina`) | — |
| Commodities | 生意社 (`futures_spot_price_daily`) | — |
| Crude Oil | Sina (`futures_foreign_hist`) | — |

## Dependencies

Auto-installed on first run (into a local `.venv`):
- Python 3.10+
- akshare
- pandas
