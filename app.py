from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

DATA_PATH = Path(__file__).resolve().parent / "NIFTY50_with_indicators.csv"


def load_nifty_data(path: str | Path = DATA_PATH) -> pd.DataFrame:
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Dataset not found: {csv_path}")
    if csv_path.stat().st_size == 0:
        raise ValueError(f"Dataset is empty: {csv_path}. Save the CSV before running the dashboard.")

    df = pd.read_csv(csv_path)

    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    required_columns = ["Date", "Close", "SMA_50", "RSI"]
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    for column in ["Close", "High", "Low", "Open", "Volume", "Daily_Return", "SMA_20", "SMA_50", "SMA_100", "EMA_20", "RSI", "macd"]:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    df = df.dropna(subset=["Date", "Close"]).sort_values("Date").reset_index(drop=True)
    return df


def main() -> None:
    st.set_page_config(page_title="NIFTY 50 Dashboard", layout="wide")
    st.markdown(
        """
        <style>
        :root {
            --bg: #050b16;
            --bg-2: #0a1220;
            --panel: rgba(15, 23, 42, 0.78);
            --panel-strong: rgba(10, 17, 29, 0.96);
            --text: #e5eefb;
            --muted: #8ea2bc;
            --border: rgba(148, 163, 184, 0.2);
            --accent: #4cc9f0;
            --accent-2: #4ade80;
            --amber: #fbbf24;
            --danger: #f87171;
            --glow: rgba(76, 201, 240, 0.45);
        }
        html, body, [data-testid="stAppViewContainer"] {
            background:
                radial-gradient(circle at 15% 15%, rgba(76, 201, 240, 0.18), transparent 22%),
                radial-gradient(circle at 85% 0%, rgba(74, 222, 128, 0.12), transparent 28%),
                linear-gradient(135deg, #050b16 0%, #0b1220 45%, #0f172a 100%) !important;
            color: var(--text) !important;
        }
        [data-testid="stSidebar"] {
            background: rgba(8, 13, 24, 0.92) !important;
            border-right: 1px solid var(--border) !important;
            color: var(--text) !important;
            backdrop-filter: blur(14px);
            box-shadow: 8px 0 30px rgba(0,0,0,0.18);
        }
        .stApp {
            background: transparent;
        }
        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
        }
        h1 {
            color: #f8fbff !important;
            letter-spacing: 0.03em;
            text-shadow: 0 0 20px rgba(76, 201, 240, 0.2);
        }
        .stMetric {
            background: linear-gradient(180deg, rgba(15, 23, 42, 0.88), rgba(9, 14, 24, 0.96));
            border: 1px solid rgba(76, 201, 240, 0.18);
            border-radius: 18px;
            padding: 12px 14px 10px 14px;
            box-shadow: 0 10px 22px rgba(0,0,0,0.28), inset 0 1px 0 rgba(255,255,255,0.04);
        }
        .stMetric [data-testid="stMetricLabel"] {
            color: var(--muted) !important;
            font-weight: 700;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            font-size: 0.72rem;
        }
        .stMetric [data-testid="stMetricValue"] {
            color: #f8fbff !important;
            font-weight: 800;
            font-size: 1.7rem !important;
        }
        .stDataFrame, .stTable {
            background: rgba(15, 23, 42, 0.72) !important;
            border: 1px solid var(--border) !important;
            border-radius: 16px;
        }
        div[data-testid="stMarkdownContainer"] p,
        div[data-testid="stMarkdownContainer"] li,
        div[data-testid="stMarkdownContainer"] code {
            color: var(--text) !important;
        }
        .stTextInput > div > div > input,
        .stDateInput > div > div > input {
            background: rgba(15, 23, 42, 0.95) !important;
            color: var(--text) !important;
            border: 1px solid rgba(76, 201, 240, 0.25) !important;
            border-radius: 10px !important;
            box-shadow: inset 0 0 0 1px rgba(76, 201, 240, 0.1);
        }
        .stMultiSelect > div, .stSelectbox > div {
            background: rgba(15, 23, 42, 0.95) !important;
            color: var(--text) !important;
            border: 1px solid rgba(76, 201, 240, 0.2) !important;
            border-radius: 10px !important;
        }
        .stButton > button {
            background: linear-gradient(135deg, var(--accent-2), #16a34a);
            color: white;
            border: none;
            border-radius: 10px;
            box-shadow: 0 12px 28px rgba(34, 197, 94, 0.32);
            font-weight: 700;
        }
        .stWarning, .stError, .stSuccess {
            border-radius: 12px;
        }
        .premium-banner {
            padding: 16px 20px;
            border-radius: 16px;
            background: linear-gradient(135deg, rgba(34, 197, 94, 0.15), rgba(76, 201, 240, 0.12));
            border: 1px solid rgba(255,255,255,0.1);
            box-shadow: 0 12px 30px rgba(2, 6, 23, 0.38), inset 0 1px 0 rgba(255,255,255,0.06);
            color: white;
            font-weight: 800;
            text-align: center;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }
        .premium-banner span {
            font-weight: 900;
            text-shadow: 0 0 12px rgba(76, 201, 240, 0.25);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    try:
        df = load_nifty_data()
    except Exception as exc:  # pragma: no cover - Streamlit UI path
        st.error(f"Unable to load NIFTY data: {exc}")
        st.stop()

    st.title("📈 NIFTY 50 Stock Market Dashboard")

    st.sidebar.header("Dashboard Controls")

    search_date = st.sidebar.text_input("Search date (YYYY-MM-DD)", value="")
    start_date = st.sidebar.date_input(
        "Start date",
        min_value=df["Date"].min().date(),
        max_value=df["Date"].max().date(),
        value=df["Date"].min().date(),
    )
    end_date = st.sidebar.date_input(
        "End date",
        min_value=df["Date"].min().date(),
        max_value=df["Date"].max().date(),
        value=df["Date"].max().date(),
    )
    selected_mas = st.sidebar.multiselect(
        "Moving averages to display",
        options=["SMA_20", "SMA_50", "SMA_100", "EMA_20"],
        default=["SMA_50"],
    )
    show_raw_price = st.sidebar.checkbox("Show closing price", value=True)
    show_candles = st.sidebar.checkbox("Show candlestick view", value=False)

    if search_date:
        try:
            search_ts = pd.Timestamp(search_date)
            filtered_df = df[(df["Date"] >= search_ts) & (df["Date"] <= search_ts + pd.Timedelta(days=30))].copy()
        except ValueError:
            st.sidebar.warning("Use a valid date format: YYYY-MM-DD")
            filtered_df = df[(df["Date"] >= pd.Timestamp(start_date)) & (df["Date"] <= pd.Timestamp(end_date))].copy()
    else:
        filtered_df = df[(df["Date"] >= pd.Timestamp(start_date)) & (df["Date"] <= pd.Timestamp(end_date))].copy()

    if filtered_df.empty:
        st.warning("No data available for the selected date range.")
        st.stop()

    current_close = float(filtered_df["Close"].iloc[-1])
    previous_close = float(filtered_df["Close"].iloc[-2]) if len(filtered_df) > 1 else current_close
    percent_change = ((current_close - previous_close) / previous_close) * 100 if previous_close else 0.0
    last_rsi = float(filtered_df["RSI"].dropna().iloc[-1]) if filtered_df["RSI"].notna().any() else 0.0

    sma_20 = filtered_df["SMA_20"].dropna().iloc[-1] if filtered_df["SMA_20"].notna().any() else current_close
    sma_50 = filtered_df["SMA_50"].dropna().iloc[-1] if filtered_df["SMA_50"].notna().any() else current_close
    if current_close > sma_20 and current_close > sma_50:
        market_regime = "Bullish"
        regime_color = "green"
    elif current_close < sma_20 and current_close < sma_50:
        market_regime = "Bearish"
        regime_color = "red"
    else:
        market_regime = "Neutral"
        regime_color = "orange"

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Latest Close", f"₹{current_close:,.2f}")
    col2.metric("Daily Change", f"{percent_change:+.2f}%")
    col3.metric("RSI", f"{last_rsi:.2f}")
    col4.metric("Market Regime", market_regime, delta_color="normal")

    st.markdown(
        f"<div class='premium-banner' style='background: linear-gradient(135deg, rgba(34, 197, 94, 0.18), rgba(59, 130, 246, 0.16)); border-color: {regime_color}; box-shadow: 0 10px 28px rgba(0,0,0,0.18), inset 0 1px 0 rgba(255,255,255,0.05);'>Current market view: <span style='color: {regime_color};'>{market_regime}</span></div>",
        unsafe_allow_html=True,
    )

    st.subheader("Closing Price Trend")
    fig = go.Figure()
    if show_raw_price:
        fig.add_trace(go.Scatter(x=filtered_df["Date"], y=filtered_df["Close"], mode="lines", name="Close Price", line=dict(color="#1f77b4", width=3)))
    for ma in selected_mas:
        if ma in filtered_df.columns:
            fig.add_trace(go.Scatter(x=filtered_df["Date"], y=filtered_df[ma], mode="lines", name=ma, line=dict(width=2)))
    fig.update_layout(
        title="NIFTY 50 Price & Trend Lines",
        xaxis_title="Date",
        yaxis_title="Price",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        template="plotly_dark",
        paper_bgcolor="#0f172a",
        plot_bgcolor="#0f172a",
        font=dict(color="#e2e8f0"),
    )
    st.plotly_chart(fig, use_container_width=True)

    if show_candles:
        st.subheader("Candlestick View")
        candlestick = go.Figure(data=[go.Candlestick(
            x=filtered_df["Date"],
            open=filtered_df["Open"],
            high=filtered_df["High"],
            low=filtered_df["Low"],
            close=filtered_df["Close"],
            increasing_line_color="green",
            decreasing_line_color="red",
        )])
        candlestick.update_layout(
            title="NIFTY 50 Candlestick Chart",
            xaxis_title="Date",
            yaxis_title="Price",
            template="plotly_dark",
            paper_bgcolor="#0f172a",
            plot_bgcolor="#0f172a",
            font=dict(color="#e2e8f0"),
        )
        st.plotly_chart(candlestick, use_container_width=True)

    if "Volume" in filtered_df.columns:
        st.subheader("Volume Analysis")
        volume_fig = go.Figure()
        volume_fig.add_trace(go.Bar(x=filtered_df["Date"], y=filtered_df["Volume"], name="Volume", marker_color="rgba(75, 192, 192, 0.75)"))
        volume_fig.update_layout(
            title="NIFTY 50 Volume",
            xaxis_title="Date",
            yaxis_title="Volume",
            template="plotly_dark",
            paper_bgcolor="#0f172a",
            plot_bgcolor="#0f172a",
            font=dict(color="#e2e8f0"),
        )
        st.plotly_chart(volume_fig, use_container_width=True)

    if "macd" in filtered_df.columns and filtered_df["macd"].notna().any():
        st.subheader("MACD Trend")
        macd_fig = go.Figure()
        macd_fig.add_trace(go.Scatter(x=filtered_df["Date"], y=filtered_df["macd"], mode="lines", name="MACD", line=dict(color="#9467bd", width=2)))
        macd_fig.add_hline(y=0, line_dash="solid", line_color="gray", annotation_text="Zero line")
        macd_fig.update_layout(
            title="MACD",
            xaxis_title="Date",
            yaxis_title="MACD",
            template="plotly_dark",
            paper_bgcolor="#0f172a",
            plot_bgcolor="#0f172a",
            font=dict(color="#e2e8f0"),
        )
        st.plotly_chart(macd_fig, use_container_width=True)

    st.subheader("RSI Indicator")
    fig3 = go.Figure()
    fig3.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought")
    fig3.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold")
    fig3.add_trace(go.Scatter(x=filtered_df["Date"], y=filtered_df["RSI"], mode="lines", name="RSI", line=dict(color="#ff7f0e", width=2)))
    fig3.update_layout(
        title="Relative Strength Index (RSI)",
        xaxis_title="Date",
        yaxis_title="RSI",
        template="plotly_dark",
        paper_bgcolor="#0f172a",
        plot_bgcolor="#0f172a",
        font=dict(color="#e2e8f0"),
    )
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Dataset Preview")
    st.dataframe(filtered_df.tail(10), use_container_width=True)


if __name__ == "__main__":
    main()