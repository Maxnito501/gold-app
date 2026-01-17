import streamlit as st
import yfinance as yf
import pandas_ta as ta
import time
from datetime import datetime

# --- 1. ตั้งค่าหน้าเว็บ ---
st.set_page_config(
    page_title="AI Gold Pro",
    page_icon="🏆",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- CSS ตกแต่ง ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    div[data-testid="metric-container"] {
        background-color: #262730; border: 1px solid #444;
        padding: 15px; border-radius: 12px;
    }
    div[data-testid="metric-container"] > label { color: #D4AF37 !important; }
    div[data-testid="metric-container"] > div[data-testid="stMetricValue"] { color: #FFF !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ฟังก์ชันดึงข้อมูล ---
def get_gold_data():
    try:
        tickers = yf.Tickers("GC=F THB=X")
        gold_hist = tickers.tickers['GC=F'].history(period="60d")
        thb_hist = tickers.tickers['THB=X'].history(period="5d")

        if gold_hist.empty or thb_hist.empty: return None

        spot = gold_hist['Close'].iloc[-1]
        thb = thb_hist['Close'].iloc[-1]
        rsi = gold_hist.ta.rsi(length=14).iloc[-1]

        return {'spot': spot, 'thb': thb, 'rsi': rsi}
    except:
        return None

# --- 3. ส่วนจำข้อมูล (Session State) *สำคัญมาก* ---
# ถ้ายังไม่มีที่เก็บของ ให้สร้างกระเป๋าว่างๆ ไว้ก่อน
if 'market_data' not in st.session_state:
    st.session_state['market_data'] = None
if 'last_update' not in st.session_state:
    st.session_state['last_update'] = "ยังไม่อัปเดต"

# --- 4. Sidebar ปรับจูน (Calibration) ---
with st.sidebar:
    st.header("🔧 ตั้งค่าความแม่นยำ")
    st.write("ปรับส่วนต่างราคา (Premium) ให้ตรงกับหน้าร้าน")
    
    # เปลี่ยนเป็น Slider จะใช้ง่ายกว่าบนมือถือ
    premium = st.slider(
        "บวกค่า Premium (บาท)", 
        min_value=0, 
        max_value=500, 
        value=150, 
        step=10
    )
    
    st.info(f"💡 กำลังบวกเพิ่ม: {premium} บาท")

# --- 5. ส่วนแสดงผลหลัก ---
st.title("🏆 AI Gold Pro")
st.caption(f"ข้อมูลล่าสุด: {st.session_state['last_update']}")

# ปุ่มกดอัปเดต (ดึงข้อมูลใหม่)
if st.button('🔄 ดึงราคาตลาดโลกเดี๋ยวนี้', use_container_width=True):
    with st.spinner('กำลังดึงข้อมูล...'):
        data = get_gold_data()
        if data:
            # บันทึกลงความจำ (Session)
            st.session_state['market_data'] = data
            st.session_state['last_update'] = datetime.now().strftime('%H:%M:%S')
        else:
            st.error("ดึงข้อมูลไม่สำเร็จ")

# --- 6. คำนวณและแสดงผล (ดึงจากความจำมาคำนวณ) ---
# ส่วนนี้จะทำงานทุกครั้งที่คุณเลื่อนตัวปรับจูน โดยไม่ต้องดึงเน็ตใหม่
if st.session_state['market_data']:
    data = st.session_state['market_data']
    
    # คำนวณใหม่สดๆ ตามค่า Premium ที่เพิ่งปรับ
    raw_thai = (data['spot'] * data['thb'] * 0.965 * 15.244) / 31.1035
    final_thai_price = round((raw_thai + premium) / 50) * 50

    # แสดงผล
    st.markdown("---")
    c_main, c_side = st.columns([2,1])
    with c_main:
        st.metric("🇹🇭 ราคาทองคำแท่ง", f"{final_thai_price:,} บาท", f"Premium +{premium}")
    with c_side:
        st.caption(f"Spot: ${data['spot']:,.0f}")
        st.caption(f"USD: {data['thb']:.2f}฿")

    # ข้อมูลย่อย
    col1, col2 = st.columns(2)
    col1.metric("Gold Spot", f"${data['spot']:,.2f}")
    col2.metric("USD/THB", f"{data['thb']:.2f} บาท")

    # RSI
    st.markdown("---")
    st.subheader("📊 สัญญาณเทคนิค (RSI)")
    st.progress(int(data['rsi']))
    
    if data['rsi'] <= 30:
        st.success(f"✅ RSI {data['rsi']:.1f}: ถูกมาก (Oversold) - น่าซื้อ")
    elif data['rsi'] >= 70:
        st.error(f"🔥 RSI {data['rsi']:.1f}: แพงไป (Overbought) - ระวัง")
    else:
        st.warning(f"⚖️ RSI {data['rsi']:.1f}: ราคากลางๆ (Neutral)")

else:
    st.info("👆 กดปุ่มด้านบนเพื่อเริ่มดึงข้อมูลครั้งแรก")