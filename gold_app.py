import streamlit as st
import yfinance as yf
import pandas_ta as ta
import time

# --- 1. ตั้งค่าหน้าเว็บ (Config) ---
st.set_page_config(
    page_title="Gold AI Trader",
    page_icon="🏆",
    layout="centered" # จัดกึ่งกลางเพื่อให้ดูดีบนมือถือ
)

# --- 2. ฟังก์ชันคำนวณ (Logic เดิม) ---
def get_data():
    try:
        tickers = yf.Tickers("GC=F THB=X")
        gold_hist = tickers.tickers['GC=F'].history(period="60d")
        thb_hist = tickers.tickers['THB=X'].history(period="5d")
        
        spot = gold_hist['Close'].iloc[-1]
        thb = thb_hist['Close'].iloc[-1]
        
        # RSI Calculation
        rsi = gold_hist.ta.rsi(length=14).iloc[-1]
        
        # Thai Price Calculation
        thai = (spot * thb * 0.965 * 15.244) / 31.1035
        thai = round(thai / 50) * 50
        
        return spot, thb, thai, rsi
    except:
        return None, None, None, None

# --- 3. ส่วนแสดงผล (UI) ---
st.title("🏆 AI Gold Trader")
st.caption(f"Update: {time.strftime('%H:%M:%S')}")

# ปุ่มกดอัปเดต
if st.button('🔄 อัปเดตราคาล่าสุด'):
    with st.spinner('กำลังดึงข้อมูลตลาดโลก...'):
        spot, thb, thai, rsi = get_data()
        
        if spot:
            # การ์ดแสดงราคาใหญ่
            st.metric(label="ราคาทองคำแท่ง (96.5%)", value=f"{thai:,} บาท")
            
            # ข้อมูลย่อย 2 คอลัมน์
            col1, col2 = st.columns(2)
            col1.metric("Gold Spot", f"${spot:,.2f}")
            col2.metric("USD/THB", f"{thb:.2f} ฿")
            
            # เกจวัด RSI
            st.write("---")
            st.subheader("📊 สัญญาณเทคนิค (RSI)")
            st.progress(int(rsi)) # สร้าง Progress Bar ตามค่า RSI
            
            if rsi <= 30:
                st.success(f"✅ RSI: {rsi:.2f} - น่าซื้อสะสม (Oversold)")
            elif rsi >= 70:
                st.error(f"⚠️ RSI: {rsi:.2f} - ระวังดอย (Overbought)")
            else:
                st.warning(f"👀 RSI: {rsi:.2f} - รอจังหวะ (Neutral)")
        else:
            st.error("ไม่สามารถดึงข้อมูลได้ กรุณาลองใหม่")