# akshare — Claude Code Plugin

Financial market data query tool for A-shares, HK stocks, US stocks, and spot commodities via [AKShare](https://github.com/akfamily/akshare).

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

The skill auto-activates when you ask about stock prices, market data, or commodities.

You can also invoke directly:

```
/akshare cn 600519 --start 2024-01-01
/akshare us AAPL --fields close,volume
/akshare commodity AU
```

## Supported Markets

| Market | Code | Examples |
|--------|------|----------|
| A-shares | `cn` | `000001` (平安银行), `600519` (贵州茅台) |
| Hong Kong | `hk` | `00700` (腾讯), `09988` (阿里巴巴) |
| US stocks | `us` | `AAPL`, `MSFT`, `TSLA` |
| Commodities | `commodity` | `AU` (黄金), `AG` (白银), `OIL` (原油) |

## Dependencies

Auto-installed on first run (into a local `.venv`):
- Python 3.10+
- akshare
- pandas
