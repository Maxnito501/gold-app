import streamlit as st
import yfinance as yf
import pandas_ta as ta
import time
from datetime import datetime

# --- 1. ตั้งค่าหน้าเว็บ (Config) ---
st.set_page_config(
    page_title="AI Gold Pro",
    page_icon="🏆",
    layout="centered",
    initial_sidebar_state="collapsed" # ซ่อนแถบข้างไว้ก่อน เพื่อความคลีน
)

# --- 2. ตกแต่ง CSS (ธีมสีทอง-ดำ ระดับพรีเมียม) ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    div[data-testid="metric-container"] {
        background-color: #262730;
        border: 1px solid #444;
        padding: 15px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    div[data-testid="metric-container"] > label {
        color: #D4AF37 !important; /* สีทอง */
        font-weight: bold;
    }
    div[data-testid="metric-container"] > div[data-testid="stMetricValue"] {
        color: #FFFFFF !important;
    }
    .stProgress > div > div > div > div {
        background-image: linear-gradient(to right, #4CAF50, #FFC107, #FF5252);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. ส่วนตั้งค่าความแม่นยำ (Sidebar) ---
with st.sidebar:
    st.header("🔧 ตั้งค่าความแม่นยำ (Calibration)")
    st.write("ปรับค่าเพื่อให้ตรงกับราคาสมาคมฯ หน้างาน")
    
    # ตัวปรับ Premium (ค่ากำเหน็จ/ค่าการตลาด)
    premium = st.number_input(
        "บวกค่า Premium (บาท)", 
        min_value=0, 
        max_value=500, 
        value=150, 
        step=10,
        help="ปกติราคาไทยจะบวกเพิ่มจากสูตรโลกประมาณ 100-200 บาท"
    )

# --- 4. ฟังก์ชันดึงข้อมูล (Logic) ---
def get_gold_data():
    try:
        # ดึงข้อมูล Real-time
        tickers = yf.Tickers("GC=F THB=X")
        
        # ดึงประวัติย้อนหลังเพื่อคำนวณ RSI
        gold_hist = tickers.tickers['GC=F'].history(period="60d")
        thb_hist = tickers.tickers['THB=X'].history(period="5d")

        if gold_hist.empty or thb_hist.empty:
            return None

        # ข้อมูลล่าสุด
        spot = gold_hist['Close'].iloc[-1]
        thb = thb_hist['Close'].iloc[-1]
        
        # คำนวณ RSI (14 วัน)
        rsi = gold_hist.ta.rsi(length=14).iloc[-1]

        return spot, thb, rsi
    except Exception as e:
        return None

# --- 5. ส่วนแสดงผลหลัก (Main UI) ---
st.title("🏆 AI Gold Pro")
st.caption(f"อัปเดตข้อมูล: {datetime.now().strftime('%H:%M:%S')}")

# ปุ่มกดอัปเดต
if st.button('🔄 อัปเดตราคาตลาด', use_container_width=True):
    
    with st.spinner('📡 AI กำลังเชื่อมต่อตลาดโลก...'):
        # ดึงข้อมูล
        spot, thb, rsi = get_gold_data()
        time.sleep(0.5) # หน่วงนิดนึงให้ดูสมูท

    if spot:
        # --- คำนวณราคาไทย (สูตร + Premium) ---
        # สูตร: (Spot * Rate * 0.965 * 15.244) / 31.1035
        raw_thai = (spot * thb * 0.965 * 15.244) / 31.1035
        
        # บวก Premium ที่ตั้งค่าไว้ แล้วปัดเศษ 50
        final_thai_price = round((raw_thai + premium) / 50) * 50

        # แสดงผล: ราคาทองคำแท่ง
        st.markdown("---")
        col_main, col_cal = st.columns([2, 1])
        
        with col_main:
            st.metric(
                label="🇹🇭 ราคาทองคำแท่ง (96.5%)",
                value=f"{final_thai_price:,} บาท",
                delta=f"Spot ${spot:,.0f}"
            )
        
        with col_cal:
            # แสดงค่าที่ใช้คำนวณ
            st.caption(f"USD: {thb:.2f}฿")
            st.caption(f"Premium: +{premium}฿")

        # ข้อมูลย่อย
        c1, c2 = st.columns(2)
        c1.metric("🌍 Gold Spot", f"${spot:,.2f}")
        c2.metric("🇺🇸 USD/THB", f"{thb:.2f} บาท")

        # --- ส่วนวิเคราะห์เทคนิค (RSI) ---
        st.markdown("---")
        st.subheader("📊 สัญญาณเทคนิค (RSI)")
        
        st.progress(int(rsi))
        
        if rsi <= 30:
            st.success(f"✅ **RSI = {rsi:.2f} (Oversold)**\n\n**AI แนะนำ:** ราคาลงมาลึกมาก เป็นจังหวะ 'ซื้อสะสม' ที่ดี (Buy on Dip)")
        elif rsi >= 70:
            st.error(f"🔥 **RSI = {rsi:.2f} (Overbought)**\n\n**AI แนะนำ:** ราคาพุ่งแรงเกินไป เสี่ยงโดนเทขาย ให้ระวัง หรือแบ่งขายทำกำไร")
        else:
            st.warning(f"⚖️ **RSI = {rsi:.2f} (Neutral)**\n\n**AI แนะนำ:** ราคาทรงตัว ให้รอจังหวะที่ชัดเจนกว่านี้ (Wait & See)")

    else:
        st.error("⚠️ ไม่สามารถดึงข้อมูลได้ (ตลาดอาจปิดหรือเน็ตหลุด)")

else:
    st.info("👆 กดปุ่มด้านบนเพื่อเริ่มคำนวณราคา")

# Footer
st.markdown("---")
st.caption("หมายเหตุ: ราคาเป็นการคำนวณทางทฤษฎี โปรดตรวจสอบกับหน้าร้านอีกครั้ง | Developed by Engineer & AI Partner")