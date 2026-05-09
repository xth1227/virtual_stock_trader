# 虚拟炒股系统

## 项目说明

这是一个 vibe coding 项目，主要用于学习和实验。项目的大部分代码、文档和功能设计由 AI 辅助生成，再由人工检查、运行和调整。

这是一个本地运行的虚拟炒股小程序：

- 虚拟本金：100,000 元
- 行情数据：通过 AkShare 获取公开行情
- 交易：只修改本地 SQLite 数据库，不连接真实券商，不会动真钱
- 支持：股票/ETF 代码查询、买入、卖出、持仓、交易记录

## 安装

建议使用 Python 3.9 或更高版本。

```bash
cd virtual_stock_trader
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

## 使用

浏览器打开 Streamlit 给出的地址，一般是：

```text
http://localhost:8501
```

输入代码，例如：

- 510300：沪深300ETF
- 159919：沪深300ETF
- 600519：贵州茅台
- 000001：平安银行

## 注意

免费公开行情可能不是严格实时行情，也可能有延迟、频率限制或接口字段变化。这个程序适合练手，不适合真实交易决策。
