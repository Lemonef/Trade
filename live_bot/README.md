# Paper-trading bot — validated trend basket

Forward-tests the validated strategy with **no real money**: Donchian 55/20 + 200-MA filter,
long-only, ATR stop, ATR-risk sizing, ~20-coin Binance basket (each coin = equal-capital sub-account).

**Runs itself in GitHub's cloud** via GitHub Actions every 4h — no server, no PC, free.

## Files
- `paper_bot.py` — one trading cycle (fetch Binance data → signals → paper fills → save/log → web data).
- `status.py` — local snapshot of signals + equity (for debugging; optional).
- `state.json`, `equity_log.csv`, `trades.csv` — paper account + logs (auto-created, committed by the Action).

## How it runs (GitHub Actions)
`.github/workflows/paper_bot.yml` runs every 4h: installs deps, runs one cycle, commits state +
`web/data.json` back to the repo, and (optionally) pings Telegram. Trigger manually anytime:
repo → **Actions** → **paper-bot** → **Run workflow**.

## Tracking
- **Dashboard:** `web/index.html` (hosted on GitHub Pages) — equity chart + positions, auto-refresh.
- **Telegram:** set repo secrets `TG_TOKEN` + `TG_CHAT` (Settings → Secrets → Actions) → DMs each cycle.
  - @BotFather → `/newbot` → token. Chat id: message your bot, open
    `https://api.telegram.org/bot<TOKEN>/getUpdates`.
- **Raw:** `equity_log.csv` / `trades.csv` in the repo.

## Config (top of paper_bot.py)
- `LEVERAGE` (currently 3.0; 1.0 safe, 2.0 ≈ half-Kelly), `RISK_PCT`, `ATR_STOP`, `ENTRY/EXIT`,
  `MA_LEN`, `COINS`.

## How to read it
- **All coins below 200-MA → 0 positions, 100% cash.** Correct: the strategy sits out downtrends.
- Buys a coin when: close > its 55-bar high **and** ADX>25 **and** price>200-MA.
- Exits on: close < 20-bar low **or** ATR(2.5) stop.

## Run locally (optional, for testing)
```
pip install requests pandas numpy
python paper_bot.py     # one cycle
python status.py        # see signals
```

## Goal of this phase
Run 1-3 months. Confirm live behavior matches the backtest. If it tracks → graduate to real capital
(swap paper fills for CCXT live orders + Binance API keys stored as Action secrets). Don't skip paper.
