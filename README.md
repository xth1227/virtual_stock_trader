# Virtual Stock Trader

English | [简体中文](README.zh-CN.md)

## Project Note

This is a vibe coding project built mainly for learning and experimentation. Most of the code, documentation, and feature design were generated with AI assistance, then reviewed, tested, and adjusted by a human.

Virtual Stock Trader is a local paper-trading app:

- Starting virtual cash: 100,000 CNY
- Market data: public quotes fetched through AkShare
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
streamlit run app.py
```

### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

On first launch, the app will automatically create a local `virtual_trader.db` database file to store the virtual account, positions, watchlist, snapshots, and trade history. This file is intentionally not uploaded to GitHub.

## Usage

Open the URL shown by Streamlit in your browser. It is usually:

```text
http://localhost:8501
```

Example symbols:

- 510300: CSI 300 ETF
- 159919: CSI 300 ETF
- 600519: Kweichow Moutai
- 000001: Ping An Bank

## Notes

Public free market data may not be strictly real-time. It may have delays, rate limits, or upstream API field changes. This project is intended for practice and experimentation, not for real trading decisions.
