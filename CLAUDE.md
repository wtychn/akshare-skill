# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A Claude Code plugin providing financial market data via AKShare. It's a **skills-only plugin** — no MCP servers, hooks, or agents. The single skill (`skills/query/SKILL.md`) auto-triggers on price/market data queries and invokes the CLI script.

## Architecture

```
bin/akshare_query.py    — Main CLI entry point (Python). Self-bootstraps a .venv on first run.
skills/query/SKILL.md   — Skill definition (triggers, docs, usage patterns for the LLM)
commands/akshare.md     — /akshare slash command (thin wrapper calling the script)
.claude-plugin/         — Plugin manifest (plugin.json) + marketplace.json
```

The script supports 6 market types: `cn` (A-shares), `hk`, `us`, `index`, `futures`, `commodity` (spot prices).

## Running & Testing

```bash
# Verify syntax
python3 -c "import ast; ast.parse(open('bin/akshare_query.py').read())"

# Test a query (requires network; first run installs venv ~30s)
python3 bin/akshare_query.py index 上证指数 --start 2025-01-01 --end 2025-01-10 --fields close
python3 bin/akshare_query.py futures RB --start 2025-06-01 --fields close,volume
python3 bin/akshare_query.py commodity CU --start 2025-06-01 --fields close,dom_basis

# First run with PyPI mirror (useful in China)
python3 bin/akshare_query.py cn 600519 --mirror https://pypi.tuna.tsinghua.edu.cn/simple

# Check help
python3 bin/akshare_query.py --help
```

No test suite — validation is done by running the CLI against live AKShare APIs.

## Key Design Decisions

- **Self-contained venv**: The script creates `.venv/` adjacent to the repo root on first run and re-execs itself inside it. No system-level pip install needed.
- **`--mirror` option**: Allows specifying a PyPI mirror URL (e.g. `https://pypi.tuna.tsinghua.edu.cn/simple`) for dependency installation. Parsed early from `sys.argv` before argparse runs, since `ensure_venv()` executes before `main()`.
- **`${CLAUDE_PLUGIN_ROOT}`**: All paths in SKILL.md use this variable for portability across installations.
- **Retry logic**: 3 retries with exponential backoff for network failures.
- **Output format**: Always JSON (array of `{date, close, ...}` objects) for LLM consumption.
- **Realtime index fallback**: When `--end` includes today and daily data hasn't been published yet, automatically falls back to `stock_zh_index_spot_sina` (A-share indices) or `stock_hk_index_spot_sina` (HK indices) for same-day prices. Transparent — no extra flags needed.
- **Multi-source resilience**: HK indices prefer Sina (`stock_hk_index_daily_sina`) for stability, falling back to 东方财富 (`stock_hk_index_daily_em`) if Sina fails.
- **Commodity spot uses `futures_spot_price_daily`**: Covers 80+ commodities with basis data. Crude oil is special-cased to `futures_foreign_hist` (WTI/Brent) since it has no domestic spot market.
- **Index/futures support Chinese aliases**: e.g. `上证指数`, `沪深300`, `螺纹钢`, `铁矿石` all resolve to correct internal codes.

## Adding a New Market or Data Source

1. Write a `fetch_<name>(symbol, start_date, end_date)` function in `akshare_query.py`
2. Add it to `MARKET_FETCHERS` dict
3. Add the choice to `parser.add_argument("market", choices=[...])`
4. Document in `skills/query/SKILL.md` (triggers, symbol table, examples)
5. Test with `python3 bin/akshare_query.py <new_market> <symbol> --start ... --fields close`

## Common akshare API Functions Used

| Function | Purpose | Source |
|----------|---------|--------|
| `stock_zh_a_daily` | A-share individual stocks | Sina |
| `stock_hk_daily` | HK stocks | Sina |
| `stock_us_daily` | US stocks | Sina |
| `stock_zh_index_daily` | Chinese indices | Sina |
| `stock_zh_index_spot_sina` | Chinese indices realtime (fallback) | Sina |
| `stock_hk_index_daily_sina` | HK indices (primary) | Sina |
| `stock_hk_index_daily_em` | HK indices (fallback) | 东方财富 |
| `stock_hk_index_spot_sina` | HK indices realtime (fallback) | Sina |
| `index_us_stock_sina` | US indices | Sina |
| `futures_zh_daily_sina` | Chinese futures (main contract) | Sina |
| `futures_spot_price_daily` | Commodity spot prices + basis | 生意社 |
| `futures_foreign_hist` | International futures (WTI, Brent) | Sina |

## Plugin Installation

Symlink or copy to `~/.claude/plugins/akshare`, then enable in `.claude/settings.json`:
```json
{"enabledPlugins": {"akshare": true}}
```
