import streamlit as st
import plotly.express as px
import pandas as pd
import random

st.set_page_config(layout="wide")

# ===== STYLE =====
st.markdown("""
<style>
body {background-color: #0b1220;}
.block {
    background: linear-gradient(145deg,#111827,#1f2937);
    padding:20px;
    border-radius:15px;
    box-shadow:0 4px 20px rgba(0,0,0,0.3);
}
.metric {
    font-size:28px;
    font-weight:bold;
}
.small {color:#9ca3af;font-size:14px;}
</style>
""", unsafe_allow_html=True)

# ===== HEADER =====
st.title("📊 Phân tích traffic website")
domain = st.text_input("", placeholder="Nhập domain...")

# ===== FAKE DATA (demo UI trước) =====
def generate_data():
    return {
        "traffic": "48.5M",
        "time": "4m 45s",
        "bounce": "38%",
        "pages": "5.8",
        "mobile": 63,
        "desktop": 32,
        "tablet": 5
    }

# ===== MAIN =====
if st.button("Phân tích"):
    data = generate_data()

    # ===== KPI =====
    col1, col2, col3, col4 = st.columns(4)

    col1.markdown(f'<div class="block"><div class="small">LƯỢT TRUY CẬP</div><div class="metric">{data["traffic"]}</div></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="block"><div class="small">THỜI GIAN TB</div><div class="metric">{data["time"]}</div></div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="block"><div class="small">BOUNCE RATE</div><div class="metric">{data["bounce"]}</div></div>', unsafe_allow_html=True)
    col4.markdown(f'<div class="block"><div class="small">PAGES / VISIT</div><div class="metric">{data["pages"]}</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    # ===== LINE CHART =====
    st.subheader("📈 Lưu lượng theo tháng")
    months = list(range(1,13))
    traffic = [random.randint(20,100) for _ in months]

    df = pd.DataFrame({"Month": months, "Traffic": traffic})
    fig = px.line(df, x="Month", y="Traffic")
    fig.update_layout(template="plotly_dark")

    st.plotly_chart(fig, use_container_width=True)

    # ===== ROW 2 =====
    col5, col6 = st.columns(2)

    # DEVICE
    device_df = pd.DataFrame({
        "Device": ["Desktop","Mobile","Tablet"],
        "Value": [data["desktop"], data["mobile"], data["tablet"]]
    })

    fig2 = px.pie(device_df, names="Device", values="Value", hole=0.6)
    fig2.update_layout(template="plotly_dark")

    col5.subheader("💻 Thiết bị truy cập")
    col5.plotly_chart(fig2, use_container_width=True)

    # SOURCES
    sources = {
        "Direct":42,
        "Search":33,
        "Social":14,
        "Referral":6,
        "Email":3,
        "Display":2
    }

    col6.subheader("🔗 Nguồn truy cập")
    for k,v in sources.items():
        col6.progress(v/100)
        col6.write(f"{k}: {v}%")

    # ===== ROW 3 =====
    col7, col8 = st.columns(2)

    # TOP COUNTRY
    country_df = pd.DataFrame({
        "Country":["Vietnam","USA","Australia","France","Japan"],
        "Value":[88,4,2,1.5,1.2]
    })

    col7.subheader("🌍 Top quốc gia")
    fig3 = px.bar(country_df, x="Value", y="Country", orientation='h')
    fig3.update_layout(template="plotly_dark")
    col7.plotly_chart(fig3, use_container_width=True)

    # KEYWORDS
    keyword_df = pd.DataFrame({
        "Keyword":["vnexpress","tin tức","bóng đá","thời sự","covid việt nam"],
        "Volume":["9.2M","3.4M","2.1M","1.5M","980K"],
        "Share":["18%","7%","4.3%","3.1%","2%"]
    })

    col8.subheader("🔎 Top Keywords")
    col8.dataframe(keyword_df)
