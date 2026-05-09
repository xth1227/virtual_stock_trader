# Virtual Stock Trader

English | [简体中文](README.zh-CN.md) | [日本語](README.ja.md)

## Project Note

This is a vibe coding project built mainly for learning and experimentation. Most of the code, documentation, and feature design were generated with AI assistance, then reviewed, tested, and adjusted by a human.

Virtual Stock Trader is a local paper-trading app with separate China-market, US-market, and Japan-market entry points:

- Starting virtual cash: 100,000 CNY for the China-market version, 100,000 USD for the US-market version, and 10,000,000 JPY for the Japan-market version
- China-market data: public quotes fetched through AkShare
- US-market data: public quotes fetched through Yahoo Finance via yfinance
- Japan-market data: public quotes fetched through Yahoo Finance via yfinance
- Trading: updates only a local SQLite database; it does not connect to any real broker or move real money
- Features: stock/ETF lookup, buy, sell, portfolio view, trade history, watchlist, and daily account snapshots

## Installation

Python 3.9 or later is recommended.

Clone the repository:

```bash
git clone https://github.com/xth1227/virtual_stock_trader.git
cd virtual_stock_trader
```

Create a Python virtual environment:

```bash
python -m venv .venv
```

### macOS / Linux

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Run the China-market version:

```bash
streamlit run app.py
```

Run the US-market version:

```bash
streamlit run app_us.py
```

Run the Japan-market version:

```bash
streamlit run app_jp.py
```

On first launch, the app will automatically create a local database file to store the virtual account, positions, watchlist, snapshots, and trade history. The China-market version uses `virtual_trader.db`; the US-market version uses `virtual_trader_us.db`; the Japan-market version uses `virtual_trader_jp.db`. These files are intentionally not uploaded to GitHub.

## Usage

Open the URL shown by Streamlit in your browser. It is usually:

```text
http://localhost:8501
```

Example symbols:

China-market version:

- 510300: CSI 300 ETF
- 159919: CSI 300 ETF
- 600519: Kweichow Moutai
- 000001: Ping An Bank

US-market version:

- AAPL: Apple
- MSFT: Microsoft
- NVDA: NVIDIA
- SPY: SPDR S&P 500 ETF Trust
- QQQ: Invesco QQQ Trust

Japan-market version:

- 7203 or 7203.T: Toyota Motor
- 6758 or 6758.T: Sony Group
- 9984 or 9984.T: SoftBank Group
- 8306 or 8306.T: Mitsubishi UFJ Financial Group
- 1306 or 1306.T: TOPIX ETF

## Notes

Public free market data may not be strictly real-time. It may have delays, rate limits, or upstream API field changes. This project is intended for practice and experimentation, not for real trading decisions.
