# 虚拟炒股系统

[English](README.md) | 简体中文

## 项目说明

这是一个 vibe coding 项目，主要用于学习和实验。项目的大部分代码、文档和功能设计由 AI 辅助生成，再由人工检查、运行和调整。

虚拟炒股系统是一个本地运行的模拟交易小程序，包含 A 股/ETF、美股/ETF 和日本股票/ETF 三个独立入口：

- 初始虚拟本金：A 股版本 100,000 元，美股版本 100,000 美元，日本版 10,000,000 日元
- A 股行情数据：通过 AkShare 获取公开行情
- 美股行情数据：通过 yfinance 获取 Yahoo Finance 行情
- 日本行情数据：通过 yfinance 获取 Yahoo Finance 行情
- 交易方式：只修改本地 SQLite 数据库，不连接真实券商，不会动真钱
- 支持功能：股票/ETF 代码查询、买入、卖出、持仓、自选列表、交易记录和每日账户快照

## 安装

建议使用 Python 3.9 或更高版本。

克隆仓库：

```bash
git clone https://github.com/xth1227/virtual_stock_trader.git
cd virtual_stock_trader
```

创建 Python 虚拟环境：

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

运行 A 股/ETF 版本：

```bash
streamlit run app.py
```

运行美股/ETF 版本：

```bash
streamlit run app_us.py
```

运行日本股票/ETF 版本：

```bash
streamlit run app_jp.py
```

首次运行时，程序会自动在本地创建数据库文件，用来保存虚拟账户、持仓、自选列表、快照和交易记录。A 股版本使用 `virtual_trader.db`，美股版本使用 `virtual_trader_us.db`，日本版使用 `virtual_trader_jp.db`。这些文件不会上传到 GitHub。

## 使用

浏览器打开 Streamlit 显示的地址，一般是：

```text
http://localhost:8501
```

示例代码：

A 股/ETF 版本：

- 510300：沪深300ETF
- 159919：沪深300ETF
- 600519：贵州茅台
- 000001：平安银行

美股/ETF 版本：

- AAPL：Apple
- MSFT：Microsoft
- NVDA：NVIDIA
- SPY：SPDR S&P 500 ETF Trust
- QQQ：Invesco QQQ Trust

日本股票/ETF 版本：

- 7203 或 7203.T：Toyota Motor
- 6758 或 6758.T：Sony Group
- 9984 或 9984.T：SoftBank Group
- 8306 或 8306.T：Mitsubishi UFJ Financial Group
- 1306 或 1306.T：TOPIX ETF

## 注意

免费公开行情可能不是严格实时行情，也可能有延迟、频率限制或接口字段变化。这个项目适合练习和实验，不适合用于真实交易决策。
