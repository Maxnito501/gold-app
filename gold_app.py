import streamlit as st
import yfinance as yf
import pandas_ta as ta
import time
from datetime import datetime

# --- 1. ตั้งค่าหน้าเว็บ & นำเข้าฟอนต์ ---
st.set_page_config(
    page_title="AI Gold Pro",
    page_icon="🏆",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. Custom CSS: แต่งหน้าตาให้เหมือนแอปมือถือ ---
st.markdown("""
    <style>
        /* นำเข้าฟอนต์ Prompt */
        @import url('https://fonts.googleapis.com/css2?family=Prompt:wght@300;400;600&display=swap');

        /* พื้นหลังแอป */
        .stApp {
            background-color: #0F1115; /* สีดำด้าน */
            font-family: 'Prompt', sans-serif;
        }

        /* การ์ดข้อมูล (Container) */
        .custom-card {
            background-color: #1E2229;
            border-radius: 20px;
            padding: 20px;
            margin-bottom: 15px;
            border: 1px solid #333;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }

        /* การ์ดราคาทอง (สีทองเด่น) */
        .gold-card {
            background: linear-gradient(145deg, #252A33, #1E2229);
            border-radius: 25px;
            padding: 25px;
            text-align: center;
            border: 1px solid #D4AF37; /* ขอบทอง */
            box-shadow: 0 0 20px rgba(212, 175, 55, 0.15);
            margin-bottom: 20px;
        }

        /* ตัวเลขราคาทองใหญ่ๆ */
        .big-price {
            font-size: 3.5rem;
            font-weight: 600;
            color: #FFD700;
            margin: 0;
            line-height: 1.2;
            text-shadow: 0 0 10px rgba(255, 215, 0, 0.3);
        }

        /* หน่วยเงิน */
        .unit-label {
            color: #AAAAAA;
            font-size: 1rem;
            font-weight: 300;
        }

        /* หัวข้อการ์ด */
        .card-title {
            color: #D4AF37;
            font-size: 0.9rem;
            margin-bottom: 5px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* ตัวเลขย่อย */
        .sub-val {
            font-size: 1.4rem;
            font-weight: 500;
            color: #FFFFFF;
        }

        /* ซ่อน Header/Footer ของ Streamlit เพื่อความคลีน */
        header {visibility: hidden;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* ปรับปุ่มกดให้สวย */
        div.stButton > button {
            width: 100%;
            background-color: #D4AF37;
            color: #000000;
            font-weight: 600;
            border-radius: 12px;
            border: none;
            padding: 15px;
            transition: all 0.3s;
        }
        div.stButton > button:hover {
            background-color: #F9E076;
            transform: scale(1.02);
        }
        
    </style>
""", unsafe_allow_html=True)

# --- 3. ระบบความจำ (Session State) ---
if 'market_data' not in st.session_state:
    st.session_state['market_data'] = None
if 'last_update' not in st.session_state:
    st.session_state['last_update'] = "รออัปเดต"

# --- 4. ฟังก์ชันดึงข้อมูล (Logic) ---
def get_gold_data():
    try:
        tickers = yf.Tickers("GC=F THB=X")
        
        # ดึงย้อนหลัง 6 เดือน (6mo) เพื่อนำมาพลอตกราฟให้สวยงาม
        gold_hist = tickers.tickers['GC=F'].history(period="6mo")
        thb_hist = tickers.tickers['THB=X'].history(period="5d")

        if gold_hist.empty or thb_hist.empty: return None

        return {
            'spot': gold_hist['Close'].iloc[-1],
            'thb': thb_hist['Close'].iloc[-1],
            'rsi': gold_hist.ta.rsi(length=14).iloc[-1],
            'history': gold_hist['Close'] # ส่งข้อมูลกราฟออกไปด้วย
        }
    except:
        return None

# --- 5. ส่วนแสดงผลหน้าจอ (UI Layout) ---

# Header แบบมินิมอล
c1, c2 = st.columns([3, 1])
with c1:
    st.markdown("<h3 style='margin:0; color:#FFF;'>AI Gold Pro 🏆</h3>", unsafe_allow_html=True)
with c2:
    st.caption(f"Updated:\n{st.session_state['last_update']}")

st.write("") # เว้นบรรทัด

# ปุ่มอัปเดต
if st.button("🔄 อัปเดตราคาล่าสุด"):
    with st.spinner("กำลังเชื่อมต่อตลาดโลก..."):
        data = get_gold_data()
        if data:
            st.session_state['market_data'] = data
            st.session_state['last_update'] = datetime.now().strftime('%H:%M:%S')

# --- ส่วนปรับจูนราคา ---
with st.expander("⚙️ ปรับจูนราคา / ตั้งค่า Premium"):
    st.write("ปรับค่าเพื่อให้ตรงกับหน้าร้าน")
    premium = st.slider("บวกค่า Premium (บาท)", 0, 500, 150, 10)
    st.caption(f"ราคาคำนวณจะบวกเพิ่ม: {premium} บาท")

# แสดงผลเมื่อมีข้อมูล
if st.session_state['market_data']:
    d = st.session_state['market_data']
    
    # คำนวณราคาไทย
    raw_thai = (d['spot'] * d['thb'] * 0.965 * 15.244) / 31.1035
    final_thai = round((raw_thai + premium) / 50) * 50

    # 1. การ์ดราคาทองคำ
    st.markdown(f"""
        <div class="gold-card">
            <div style="color: #FFD700; font-size: 1rem; margin-bottom: 10px;">ทองคำแท่ง 96.5%</div>
            <div class="big-price">{final_thai:,}</div>
            <div class="unit-label">บาท (รวม Premium +{premium})</div>
        </div>
    """, unsafe_allow_html=True)

    # 2. ข้อมูลย่อย (Spot & THB)
    c_spot, c_thb = st.columns(2)
    with c_spot:
        st.markdown(f"""
            <div class="custom-card">
                <div class="card-title">🌍 Gold Spot</div>
                <div class="sub-val">${d['spot']:,.2f}</div>
            </div>
        """, unsafe_allow_html=True)
    with c_thb:
        st.markdown(f"""
            <div class="custom-card">
                <div class="card-title">🇺🇸 USD/THB</div>
                <div class="sub-val">{d['thb']:.2f} ฿</div>
            </div>
        """, unsafe_allow_html=True)

    # 3. ส่วนวิเคราะห์ RSI (ปรับปรุง Logic ตามสั่ง)
    rsi_val = d['rsi']
    
    # Logic คำแนะนำ
    if rsi_val <= 30:
        rsi_color = "#00E676" # เขียวสด
        msg = "✅ ราคาถูกมาก! รีบเข้าซื้อ (Strong Buy)"
    elif rsi_val <= 45: # เพิ่มช่วงราคาถูก (แต่ยังไม่ Over)
        rsi_color = "#64DD17" # เขียวอ่อน
        msg = "🟢 ราคาถูก เพิ่มเข้าซื้อ (Accumulate)"
    elif rsi_val >= 70:
        rsi_color = "#FF1744" # แดง
        msg = "🔥 ราคาแพง! แจ้งเตือนระวังดอย (Warning)"
    else:
        rsi_color = "#FFC400" # เหลือง
        msg = "⚖️ ราคากลางๆ ชะลอรอดูทิศทาง (Wait & See)"

    st.markdown(f"""
        <div class="custom-card" style="border-left: 5px solid {rsi_color};">
            <div style="display:flex; justify-content:space-between;">
                <div class="card-title">📊 สัญญาณเทคนิค (RSI)</div>
                <div style="color:{rsi_color}; font-weight:bold;">{rsi_val:.1f}</div>
            </div>
            <div style="margin-top:10px; color:#DDD; font-size:0.9rem;">
                {msg}
            </div>
        </div>
    """, unsafe_allow_html=True)
    st.progress(int(rsi_val))

    # 4. กราฟราคาทองคำ
    st.markdown("---")
    st.markdown("<div style='color:#D4AF37; margin-bottom:10px;'>📈 แนวโน้มราคา (6 เดือนล่าสุด)</div>", unsafe_allow_html=True)
    
    # วาดกราฟเส้น (Line Chart) สีทอง
    st.line_chart(d['history'], color="#D4AF37", use_container_width=True)

else:
    st.info("👆 กดปุ่ม 'อัปเดตราคาล่าสุด' เพื่อเริ่มใช้งาน")