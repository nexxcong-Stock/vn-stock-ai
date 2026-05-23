import streamlit as st
import pandas as pd
import yfinance as yf
import ta
import google.generativeai as genai

st.set_page_config(
    page_title="VN Stock AI",
    page_icon="📈",
    layout="wide"
)

st.title("🇻🇳 AI Stock Analyst Vietnam")

st.markdown("Phân tích kỹ thuật + AI nhận xét")

api_key = st.text_input(
    "Gemini API Key",
    type="password"
)

ticker = st.text_input(
    "Nhập mã cổ phiếu",
    "FPT"
)

if st.button("Phân tích"):

    try:
        symbol = ticker.upper() + ".VN"

        data = yf.download(
            symbol,
            period="6mo",
            interval="1d"
        )

        if data.empty:
            st.error("Không tìm thấy dữ liệu")
            st.stop()

        close = data["Close"]

        rsi = ta.momentum.RSIIndicator(close).rsi().iloc[-1]

        ma20 = close.rolling(20).mean().iloc[-1]
        ma50 = close.rolling(50).mean().iloc[-1]

        latest_price = close.iloc[-1]

        technical_score = 0

        if latest_price > ma20:
            technical_score += 3

        if latest_price > ma50:
            technical_score += 3

        if rsi < 70:
            technical_score += 4

        st.subheader("Kỹ thuật")

        col1, col2, col3 = st.columns(3)

        col1.metric("Giá", f"{latest_price:.2f}")
        col2.metric("RSI", f"{rsi:.2f}")
        col3.metric("Technical Score", f"{technical_score}/10")

        st.line_chart(close)

        if api_key:

            genai.configure(api_key=api_key)

            model = genai.GenerativeModel(
                "gemini-2.5-flash"
            )

            prompt = f'''
            Hãy phân tích cổ phiếu {ticker}

            Giá hiện tại: {latest_price}
            RSI: {rsi}
            MA20: {ma20}
            MA50: {ma50}
            Technical score: {technical_score}/10

            Hãy đưa ra:
            - BUY/WATCH/HOLD/AVOID
            - giải thích ngắn gọn
            - risk
            '''

            response = model.generate_content(prompt)

            st.subheader("AI Investment Insight")

            st.write(response.text)

    except Exception as e:
        st.error(str(e))