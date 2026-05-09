# バーチャル株式トレーダー

[English](README.md) | [简体中文](README.zh-CN.md) | 日本語

## プロジェクトについて

これは学習と実験を目的とした vibe coding プロジェクトです。コード、ドキュメント、機能設計の大部分は AI の支援によって生成され、その後、人間が確認、実行、調整しています。

バーチャル株式トレーダーは、ローカルで動作するペーパートレーディングアプリです。中国市場、米国市場、日本市場向けに、それぞれ独立した起動ファイルがあります。

- 初期仮想資金：中国市場版は 100,000 CNY、米国市場版は 100,000 USD、日本市場版は 10,000,000 JPY
- 中国市場データ：AkShare から公開相場データを取得
- 米国市場データ：yfinance 経由で Yahoo Finance から取得
- 日本市場データ：yfinance 経由で Yahoo Finance から取得
- 取引：ローカルの SQLite データベースだけを更新します。実際の証券会社には接続せず、実際のお金も動きません
- 機能：株式/ETF の検索、買付、売却、ポートフォリオ表示、ウォッチリスト、取引履歴、日次アカウントスナップショット

## インストール

Python 3.9 以降を推奨します。

リポジトリをクローンします。

```bash
git clone https://github.com/xth1227/virtual_stock_trader.git
cd virtual_stock_trader
```

Python 仮想環境を作成します。

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

中国市場版を起動します。

```bash
streamlit run app.py
```

米国市場版を起動します。

```bash
streamlit run app_us.py
```

日本市場版を起動します。

```bash
streamlit run app_jp.py
```

初回起動時に、仮想口座、保有銘柄、ウォッチリスト、スナップショット、取引履歴を保存するためのローカルデータベースが自動作成されます。中国市場版は `virtual_trader.db`、米国市場版は `virtual_trader_us.db`、日本市場版は `virtual_trader_jp.db` を使用します。これらのファイルは GitHub にはアップロードされません。

## 使い方

Streamlit が表示する URL をブラウザで開きます。通常は次の URL です。

```text
http://localhost:8501
```

銘柄コードの例：

中国市場版：

- 510300：CSI 300 ETF
- 159919：CSI 300 ETF
- 600519：Kweichow Moutai
- 000001：Ping An Bank

米国市場版：

- AAPL：Apple
- MSFT：Microsoft
- NVDA：NVIDIA
- SPY：SPDR S&P 500 ETF Trust
- QQQ：Invesco QQQ Trust

日本市場版：

- 7203 または 7203.T：Toyota Motor
- 6758 または 6758.T：Sony Group
- 9984 または 9984.T：SoftBank Group
- 8306 または 8306.T：Mitsubishi UFJ Financial Group
- 1306 または 1306.T：TOPIX ETF

日本市場版では、`7203` のような数字だけのコードを入力すると、自動的に Yahoo Finance 形式の `7203.T` として検索します。

## 注意事項

無料の公開相場データは、必ずしも完全なリアルタイムデータではありません。遅延、レート制限、または上流 API のフィールド変更が発生する場合があります。このプロジェクトは練習と実験を目的としており、実際の投資判断には適していません。
