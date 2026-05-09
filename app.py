import sqlite3
from datetime import datetime, date
from pathlib import Path

import akshare as ak
import pandas as pd
import streamlit as st


DB_PATH = Path("virtual_trader.db")
INIT_CASH = 100000.0
FEE_RATE = 0.00025
MIN_FEE = 1.0
LOT_SIZE = 100

DEFAULT_WATCHLIST = [
    ("510300", "沪深300ETF"),
    ("159919", "沪深300ETF"),
    ("159915", "创业板ETF"),
    ("588000", "科创50ETF"),
    ("512100", "中证1000ETF"),
]


def connect_db():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def table_has_column(conn, table_name, column_name):
    rows = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
    return any(row["name"] == column_name for row in rows)


def init_db():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS account (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            cash REAL NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS positions (
            symbol TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            qty INTEGER NOT NULL,
            cost REAL NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trade_time TEXT NOT NULL,
            side TEXT NOT NULL,
            symbol TEXT NOT NULL,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            qty INTEGER NOT NULL,
            fee REAL NOT NULL,
            amount REAL NOT NULL
        )
    """)

    if not table_has_column(conn, "trades", "note"):
        cur.execute("ALTER TABLE trades ADD COLUMN note TEXT DEFAULT ''")

    cur.execute("""
        CREATE TABLE IF NOT EXISTS snapshots (
            snapshot_date TEXT PRIMARY KEY,
            snapshot_time TEXT NOT NULL,
            cash REAL NOT NULL,
            market_value REAL NOT NULL,
            total_assets REAL NOT NULL,
            total_pnl REAL NOT NULL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS watchlist (
            symbol TEXT PRIMARY KEY,
            name TEXT NOT NULL
        )
    """)

    cur.execute("SELECT COUNT(*) AS c FROM account")
    if cur.fetchone()["c"] == 0:
        cur.execute("INSERT INTO account (id, cash) VALUES (1, ?)", (INIT_CASH,))

    cur.execute("SELECT COUNT(*) AS c FROM watchlist")
    if cur.fetchone()["c"] == 0:
        cur.executemany(
            "INSERT OR IGNORE INTO watchlist(symbol, name) VALUES (?, ?)",
            DEFAULT_WATCHLIST,
        )

    conn.commit()
    conn.close()


def get_cash():
    conn = connect_db()
    cash = conn.execute("SELECT cash FROM account WHERE id = 1").fetchone()["cash"]
    conn.close()
    return float(cash)


def set_cash(cash):
    conn = connect_db()
    conn.execute("UPDATE account SET cash = ? WHERE id = 1", (float(cash),))
    conn.commit()
    conn.close()


def reset_account():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM trades")
    cur.execute("DELETE FROM positions")
    cur.execute("DELETE FROM snapshots")
    cur.execute("UPDATE account SET cash = ? WHERE id = 1", (INIT_CASH,))
    conn.commit()
    conn.close()


@st.cache_data(ttl=8)
def load_etf_spot():
    return ak.fund_etf_spot_em()


@st.cache_data(ttl=8)
def load_stock_spot():
    return ak.stock_zh_a_spot_em()


def get_quote(symbol: str):
    symbol = symbol.strip()
    if not symbol:
        return None

    try:
        etf = load_etf_spot()
        row = etf[etf["代码"].astype(str) == symbol]
        if not row.empty:
            r = row.iloc[0]
            return {
                "symbol": symbol,
                "name": str(r["名称"]),
                "price": float(r["最新价"]),
                "type": "ETF",
                "pct": r.get("涨跌幅", None),
            }
    except Exception:
        pass

    try:
        stock = load_stock_spot()
        row = stock[stock["代码"].astype(str) == symbol]
        if not row.empty:
            r = row.iloc[0]
            return {
                "symbol": symbol,
                "name": str(r["名称"]),
                "price": float(r["最新价"]),
                "type": "股票",
                "pct": r.get("涨跌幅", None),
            }
    except Exception:
        pass

    return None


def calc_qty_by_amount(target_amount: float, price: float, lot_size: int = LOT_SIZE) -> int:
    if target_amount <= 0 or price <= 0:
        return 0
    raw_qty = int(target_amount // price)
    return raw_qty // lot_size * lot_size


def calc_fee(amount: float) -> float:
    if amount <= 0:
        return 0.0
    return max(amount * FEE_RATE, MIN_FEE)


def get_positions():
    conn = connect_db()
    rows = conn.execute("SELECT symbol, name, qty, cost FROM positions ORDER BY symbol").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_position(symbol):
    conn = connect_db()
    row = conn.execute(
        "SELECT symbol, name, qty, cost FROM positions WHERE symbol = ?",
        (symbol,),
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def upsert_position(symbol, name, qty, cost):
    conn = connect_db()
    conn.execute("""
        INSERT INTO positions(symbol, name, qty, cost)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(symbol) DO UPDATE SET
            name = excluded.name,
            qty = excluded.qty,
            cost = excluded.cost
    """, (symbol, name, int(qty), float(cost)))
    conn.commit()
    conn.close()


def delete_position(symbol):
    conn = connect_db()
    conn.execute("DELETE FROM positions WHERE symbol = ?", (symbol,))
    conn.commit()
    conn.close()


def add_trade(side, symbol, name, price, qty, fee, amount, note=""):
    conn = connect_db()
    conn.execute("""
        INSERT INTO trades(trade_time, side, symbol, name, price, qty, fee, amount, note)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        side,
        symbol,
        name,
        float(price),
        int(qty),
        float(fee),
        float(amount),
        note or "",
    ))
    conn.commit()
    conn.close()


def buy(symbol, qty, note=""):
    quote = get_quote(symbol)
    if not quote:
        raise ValueError("没有查到行情，不能买入。")
    if qty < LOT_SIZE:
        raise ValueError("买入数量至少需要 100 股/份。")

    price = quote["price"]
    name = quote["name"]
    gross = price * qty
    fee = calc_fee(gross)
    total_cost = gross + fee
    cash = get_cash()

    if cash < total_cost:
        raise ValueError(f"虚拟现金不足：需要 {total_cost:.2f}，当前 {cash:.2f}")

    pos = get_position(symbol)
    if pos:
        old_value = pos["qty"] * pos["cost"]
        new_value = gross + fee
        new_qty = pos["qty"] + qty
        new_cost = (old_value + new_value) / new_qty
    else:
        new_qty = qty
        new_cost = (gross + fee) / qty

    set_cash(cash - total_cost)
    upsert_position(symbol, name, new_qty, new_cost)
    add_trade("买入", symbol, name, price, qty, fee, total_cost, note)


def sell(symbol, qty, note=""):
    quote = get_quote(symbol)
    if not quote:
        raise ValueError("没有查到行情，不能卖出。")
    if qty < LOT_SIZE:
        raise ValueError("卖出数量至少需要 100 股/份。")

    pos = get_position(symbol)
    if not pos:
        raise ValueError("你没有这个持仓。")
    if pos["qty"] < qty:
        raise ValueError(f"持仓不足：当前只有 {pos['qty']}。")

    price = quote["price"]
    name = quote["name"]
    gross = price * qty
    fee = calc_fee(gross)
    income = gross - fee
    cash = get_cash()

    set_cash(cash + income)

    remain = pos["qty"] - qty
    if remain == 0:
        delete_position(symbol)
    else:
        upsert_position(symbol, pos["name"], remain, pos["cost"])

    add_trade("卖出", symbol, name, price, qty, fee, income, note)


def trade_history(limit=200):
    conn = connect_db()
    rows = conn.execute("""
        SELECT trade_time AS 时间, side AS 方向, symbol AS 代码, name AS 名称,
               price AS 价格, qty AS 数量, fee AS 手续费, amount AS 成交金额, note AS 备注
        FROM trades
        ORDER BY id DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return pd.DataFrame([dict(r) for r in rows])


def portfolio_table():
    rows = []
    total_market_value = 0.0
    total_cost_value = 0.0

    for pos in get_positions():
        quote = get_quote(pos["symbol"])
        if not quote:
            current_price = None
            market_value = None
            pnl = None
            pnl_rate = None
        else:
            current_price = quote["price"]
            market_value = current_price * pos["qty"]
            cost_value = pos["cost"] * pos["qty"]
            pnl = market_value - cost_value
            pnl_rate = pnl / cost_value * 100 if cost_value else 0

            total_market_value += market_value
            total_cost_value += cost_value

        rows.append({
            "代码": pos["symbol"],
            "名称": pos["name"],
            "数量": pos["qty"],
            "成本价": round(pos["cost"], 4),
            "现价": round(current_price, 4) if current_price else None,
            "市值": round(market_value, 2) if market_value else None,
            "盈亏": round(pnl, 2) if pnl is not None else None,
            "收益率": f"{pnl_rate:.2f}%" if pnl_rate is not None else None,
        })

    return pd.DataFrame(rows), total_market_value, total_cost_value


def save_today_snapshot(cash, market_value, total_assets, total_pnl):
    conn = connect_db()
    conn.execute("""
        INSERT INTO snapshots(snapshot_date, snapshot_time, cash, market_value, total_assets, total_pnl)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(snapshot_date) DO UPDATE SET
            snapshot_time = excluded.snapshot_time,
            cash = excluded.cash,
            market_value = excluded.market_value,
            total_assets = excluded.total_assets,
            total_pnl = excluded.total_pnl
    """, (
        date.today().isoformat(),
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        float(cash),
        float(market_value),
        float(total_assets),
        float(total_pnl),
    ))
    conn.commit()
    conn.close()


def snapshot_history():
    conn = connect_db()
    rows = conn.execute("""
        SELECT snapshot_date AS 日期, snapshot_time AS 保存时间, cash AS 现金,
               market_value AS 持仓市值, total_assets AS 总资产, total_pnl AS 总盈亏
        FROM snapshots
        ORDER BY snapshot_date
    """).fetchall()
    conn.close()
    return pd.DataFrame([dict(r) for r in rows])


def get_watchlist():
    conn = connect_db()
    rows = conn.execute("SELECT symbol, name FROM watchlist ORDER BY symbol").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def add_watch(symbol, name):
    conn = connect_db()
    conn.execute("INSERT OR REPLACE INTO watchlist(symbol, name) VALUES (?, ?)", (symbol, name))
    conn.commit()
    conn.close()


def remove_watch(symbol):
    conn = connect_db()
    conn.execute("DELETE FROM watchlist WHERE symbol = ?", (symbol,))
    conn.commit()
    conn.close()


def main():
    st.set_page_config(page_title="虚拟炒股系统 v3", layout="wide")
    init_db()

    st.title("虚拟炒股系统 v3")
    st.caption("虚拟本金交易，行情数据来自公开接口；不连接券商，不会动真钱。")

    with st.sidebar:
        st.header("账户设置")
        st.write(f"初始虚拟本金：{INIT_CASH:,.2f}")

        if st.button("保存今日账户快照", width="stretch"):
            cash = get_cash()
            _, market_value, cost_value = portfolio_table()
            total_assets = cash + market_value
            total_pnl = market_value - cost_value
            save_today_snapshot(cash, market_value, total_assets, total_pnl)
            st.success("已保存今日快照。")

        if st.button("重置账户", type="secondary", width="stretch"):
            reset_account()
            st.success("已重置账户。")
            st.rerun()

    left, right = st.columns([1, 1])

    with left:
        watch = get_watchlist()
        watch_options = ["手动输入"] + [f"{item['symbol']} {item['name']}" for item in watch]
        selected_watch = st.selectbox("自选列表", watch_options)

        if selected_watch == "手动输入":
            symbol = st.text_input("股票/ETF 代码", value="510300", help="例如：510300、159919、600519、000001")
        else:
            symbol = selected_watch.split()[0]
            st.text_input("股票/ETF 代码", value=symbol, disabled=True)

        quote = get_quote(symbol)

        if quote:
            st.subheader(f"{quote['name']}（{quote['symbol']}）")
            st.metric("最新价", f"{quote['price']:.4f} 元", delta=f"{quote['pct']}%" if quote["pct"] is not None else None)
            st.write(f"类型：{quote['type']}")

            w1, w2 = st.columns(2)
            with w1:
                if st.button("加入自选", width="stretch"):
                    add_watch(quote["symbol"], quote["name"])
                    st.success("已加入自选。")
                    st.rerun()
            with w2:
                if st.button("从自选删除", width="stretch"):
                    remove_watch(quote["symbol"])
                    st.success("已从自选删除。")
                    st.rerun()
        else:
            st.warning("没查到行情。检查代码是否正确，或稍后再试。")

    with right:
        cash = get_cash()
        pos_df, market_value, cost_value = portfolio_table()
        total_assets = cash + market_value
        total_pnl = market_value - cost_value

        c1, c2, c3 = st.columns(3)
        c1.metric("虚拟现金", f"{cash:,.2f}")
        c2.metric("持仓市值", f"{market_value:,.2f}")
        c3.metric("总资产", f"{total_assets:,.2f}", delta=f"{total_assets - INIT_CASH:,.2f}")

        st.caption(f"持仓浮动盈亏：{total_pnl:,.2f}")

        allocation_rows = []
        if cash > 0:
            allocation_rows.append({"资产": "现金", "金额": round(cash, 2)})
        if not pos_df.empty:
            for _, row in pos_df.iterrows():
                if pd.notna(row["市值"]):
                    allocation_rows.append({"资产": f"{row['代码']} {row['名称']}", "金额": row["市值"]})
        if allocation_rows:
            allocation_df = pd.DataFrame(allocation_rows)
            st.subheader("资产配置")
            st.bar_chart(allocation_df.set_index("资产")["金额"])

    st.divider()

    st.subheader("下单区")

    trade_mode = st.radio(
        "交易方式",
        ["按金额买入", "按数量交易"],
        horizontal=True,
    )

    note = st.text_area(
        "交易备注",
        placeholder="例如：按计划建仓；今天下跌后模拟加仓；我有点冲动，先记录原因。",
        height=80,
    )

    if trade_mode == "按金额买入":
        target_amount = st.number_input(
            "计划买入金额",
            min_value=100.0,
            step=1000.0,
            value=30000.0,
        )

        if quote:
            qty = calc_qty_by_amount(target_amount, quote["price"])
            estimated_amount = quote["price"] * qty
            estimated_fee = calc_fee(estimated_amount)
            estimated_total = estimated_amount + estimated_fee
            unused_cash = target_amount - estimated_amount

            st.success(
                f"按当前价 {quote['price']:.4f} 元计算，"
                f"{target_amount:,.2f} 元大约可以买 {qty:,} 股/份。"
            )

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("可买数量", f"{qty:,}")
            c2.metric("预计成交金额", f"{estimated_amount:,.2f}")
            c3.metric("预计手续费", f"{estimated_fee:,.2f}")
            c4.metric("预计总花费", f"{estimated_total:,.2f}")

            st.caption(f"因为 A 股/ETF 通常按 100 股/份整数倍交易，金额取整后约剩余 {unused_cash:,.2f} 元。")
        else:
            qty = 0
            st.warning("没有行情，暂时无法按金额计算数量。")

        buy_col, sell_col = st.columns(2)
        with buy_col:
            if st.button("按金额换算数量后买入", width="stretch", type="primary"):
                try:
                    buy(symbol, int(qty), note)
                    st.success("买入成功。")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

        with sell_col:
            st.button("按金额模式不支持卖出", width="stretch", disabled=True)
            st.caption("卖出请切换到“按数量交易”，避免误卖。")

    else:
        qty = st.number_input(
            "交易数量（A股/ETF 简化为 100 的整数倍）",
            min_value=100,
            step=100,
            value=100,
        )

        if quote:
            estimated_amount = quote["price"] * qty
            estimated_fee = calc_fee(estimated_amount)
            st.info(f"预计成交金额：{estimated_amount:,.2f} 元，手续费约：{estimated_fee:,.2f} 元")
        else:
            st.warning("没有行情，暂时无法估算成交金额。")

        buy_col, sell_col = st.columns(2)
        with buy_col:
            if st.button("按最新价买入", width="stretch", type="primary"):
                try:
                    buy(symbol, int(qty), note)
                    st.success("买入成功。")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

        with sell_col:
            if st.button("按最新价卖出", width="stretch"):
                try:
                    sell(symbol, int(qty), note)
                    st.success("卖出成功。")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))

    st.divider()

    tabs = st.tabs(["当前持仓", "交易记录", "每日快照", "导出数据"])

    with tabs[0]:
        if not pos_df.empty:
            st.dataframe(pos_df, width="stretch", hide_index=True)
        else:
            st.info("暂无持仓。")

    with tabs[1]:
        hist = trade_history()
        if not hist.empty:
            st.dataframe(hist, width="stretch", hide_index=True)
        else:
            st.info("暂无交易记录。")

    with tabs[2]:
        snap = snapshot_history()
        if not snap.empty:
            st.line_chart(snap.set_index("日期")["总资产"])
            st.dataframe(snap, width="stretch", hide_index=True)
        else:
            st.info("暂无快照。点击侧边栏“保存今日账户快照”即可记录。")

    with tabs[3]:
        hist = trade_history()
        snap = snapshot_history()

        st.download_button(
            "导出交易记录 CSV",
            data=hist.to_csv(index=False).encode("utf-8-sig") if not hist.empty else b"",
            file_name="trades.csv",
            mime="text/csv",
            disabled=hist.empty,
            width="stretch",
        )

        st.download_button(
            "导出每日快照 CSV",
            data=snap.to_csv(index=False).encode("utf-8-sig") if not snap.empty else b"",
            file_name="snapshots.csv",
            mime="text/csv",
            disabled=snap.empty,
            width="stretch",
        )


if __name__ == "__main__":
    main()
