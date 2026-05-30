import streamlit as st
import yfinance as yf
import pandas as pd
import ta
import plotly.graph_objects as go
import google.generativeai as genai

st.set_page_config(
    page_title="VN AI Stock Analyst",
    page_icon="📈",
    layout="wide"
)

st.title("🇻🇳 AI Stock Analyst Vietnam")
st.caption("AI + Technical + Fundamental (50/50)")

# -------------------------
# INPUT
# -------------------------
api_key = st.text_input(
    "Gemini API Key",
    type="password"
)

ticker = st.text_input(
    "Nhập mã cổ phiếu",
    "FPT"
)

# -------------------------
# FUNCTIONS
# -------------------------

def recommendation(score):
    if score >= 80:
        return "BUY"
    elif score >= 65:
        return "WATCH"
    elif score >= 50:
        return "HOLD"
    else:
        return "AVOID"


def calc_score(latest_price, ma20, ma50, ma200, rsi, macd):
    technical_score = 0

    if latest_price > ma20:
        technical_score += 15

    if latest_price > ma50:
        technical_score += 15

    if latest_price > ma200:
        technical_score += 10

    if 40 <= rsi <= 65:
        technical_score += 10

    if macd > 0:
        technical_score += 10

    return technical_score


# -------------------------
# ANALYSIS
# -------------------------

if st.button("Phân tích"):

    try:
        symbol = ticker.upper() + ".VN"

        data = yf.download(
            symbol,
            period="1y",
            interval="1d"
        )

        if data.empty:
            st.error("Không tìm thấy dữ liệu.")
            st.stop()

        close = data["Close"].squeeze()

        ma20 = close.rolling(20).mean()
        ma50 = close.rolling(50).mean()
        ma200 = close.rolling(200).mean()

        rsi = ta.momentum.RSIIndicator(close).rsi()

        macd_indicator = ta.trend.MACD(close)
        macd = macd_indicator.macd()

        latest_price = float(close.iloc[-1])
        latest_rsi = float(rsi.iloc[-1])
        latest_macd = float(macd.iloc[-1])

        tech_score = calc_score(
            latest_price,
            float(ma20.iloc[-1]),
            float(ma50.iloc[-1]),
            float(ma200.iloc[-1]),
            latest_rsi,
            latest_macd
        )

        # fundamental demo (temporary)
        fundamental_score = 50

        total_score = int(
            (tech_score * 0.5) +
            (fundamental_score * 0.5)
        )

        action = recommendation(total_score)

        # -------------------------
        # DASHBOARD
        # -------------------------

        st.subheader("Investment Report")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("Price", f"{latest_price:,.0f}")
        c2.metric("RSI", f"{latest_rsi:.2f}")
        c3.metric("Technical", f"{tech_score}/60")
        c4.metric("Score", f"{total_score}/100")

        st.success(f"Recommendation: {action}")

        # -------------------------
        # TECHNICAL DETAIL
        # -------------------------

        st.subheader("Technical Analysis")

        notes = []

        if latest_price > ma20.iloc[-1]:
            notes.append("✓ Giá trên MA20 → xu hướng ngắn hạn tích cực")
        else:
            notes.append("✗ Giá dưới MA20 → short-term momentum yếu")

        if latest_price > ma50.iloc[-1]:
            notes.append("✓ Giá trên MA50 → trung hạn tích cực")
        else:
            notes.append("✗ Giá dưới MA50 → trend trung hạn chưa mạnh")

        if latest_rsi < 30:
            notes.append("✓ RSI oversold → có khả năng hồi phục")
        elif latest_rsi > 70:
            notes.append("✗ RSI overbought → cần chú ý điều chỉnh")
        else:
            notes.append("✓ RSI trung tính")

        if latest_macd > 0:
            notes.append("✓ MACD tích cực")
        else:
            notes.append("✗ MACD yếu")

        for n in notes:
            st.write(n)

        # -------------------------
        # CHART
        # -------------------------

        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=data.index,
            y=close,
            name="Price"
        ))

        fig.add_trace(go.Scatter(
            x=data.index,
            y=ma20,
            name="MA20"
        ))

        fig.add_trace(go.Scatter(
            x=data.index,
            y=ma50,
            name="MA50"
        ))

        fig.add_trace(go.Scatter(
            x=data.index,
            y=ma200,
            name="MA200"
        ))

        fig.update_layout(
            template="plotly_dark",
            height=500
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # -------------------------
        # GEMINI AI
        # -------------------------

        if api_key:

            genai.configure(api_key=api_key)

            model = genai.GenerativeModel(
                "gemini-2.5-flash"
            )

            prompt = f"""
            Bạn là chuyên gia phân tích đầu tư.

            Hãy phân tích cổ phiếu {ticker}
            theo phong cách nhà đầu tư chuyên nghiệp.

            Dữ liệu:

            Giá hiện tại: {latest_price}
            RSI: {latest_rsi}
            MACD: {latest_macd}

            MA20: {float(ma20.iloc[-1])}
            MA50: {float(ma50.iloc[-1])}
            MA200: {float(ma200.iloc[-1])}

            Recommendation hiện tại:
            {action}

            Hãy viết:

            1. nhận xét kỹ thuật
            2. risk
            3. thesis đầu tư
            4. kết luận BUY/WATCH/HOLD/AVOID
            """

            response = model.generate_content(prompt)

            st.subheader("AI Investment Insight")

            st.write(response.text)

    except Exception as e:
        st.error(str(e))
