import streamlit as st
import plotly.express as px
import pandas as pd
import requests
from bs4 import BeautifulSoup
from pytrends.request import TrendReq
import xml.etree.ElementTree as ET

pytrends = TrendReq()

st.set_page_config(layout="wide")

# ===== STYLE =====
st.markdown("""
<style>
body {background-color: #0b1220;}
.block {
    background: linear-gradient(145deg,#111827,#1f2937);
    padding:20px;
    border-radius:15px;
}
.metric {font-size:28px;font-weight:bold;}
.small {color:#9ca3af;font-size:14px;}
</style>
""", unsafe_allow_html=True)

# ===== HEADER =====
st.title("📊 Phân tích traffic website")
domain = st.text_input("", placeholder="Nhập domain...")

# ===== ANALYZER =====
@st.cache_data(ttl=3600)
def analyze(domain):
    res = requests.get(f"https://{domain}", headers={"User-Agent":"Mozilla/5.0"}, timeout=5)
    soup = BeautifulSoup(res.text, "html.parser")

    # Trend
    keyword = domain.split('.')[0]
    try:
        pytrends.build_payload([keyword], timeframe='today 3-m')
        df = pytrends.interest_over_time()
        trend = int(df[keyword].mean()) if not df.empty else 10
    except:
        trend = 10

    # Pages
    try:
        res_map = requests.get(f"https://{domain}/sitemap.xml", timeout=5)
        root = ET.fromstring(res_map.content)
        pages = len(root.findall(".//{*}loc"))
    except:
        pages = 50

    # SEO
    seo = 0
    if soup.title: seo += 20
    if soup.find("meta", attrs={"name":"description"}): seo += 20
    if soup.find_all("h1"): seo += 20

    # Traffic estimate
    traffic = int(trend * 1000 * (1 + pages/500) * (1 + seo/100))

    # Device
    mobile = 70 if soup.find("meta", attrs={"name":"viewport"}) else 40
    desktop = 100 - mobile
    tablet = 5

    # Sources
    sources = {
        "Direct": 40,
        "Search": min(70, 30 + seo // 2),
        "Social": 10,
        "Referral": min(20, pages // 50),
        "Email": 3,
        "Display": 2
    }

    # Monthly trend fake (dựa trend)
    monthly = [int(trend * (0.8 + i*0.03)) for i in range(12)]

    # Country (estimate)
    countries = {
        "Vietnam": 80,
        "USA": 5,
        "Australia": 3,
        "France": 2,
        "Japan": 1
    }

    # Keywords (estimate)
    keywords = [
        {"k": keyword, "v": "High", "s": "Top"},
        {"k": keyword + " news", "v": "Medium", "s": "Mid"},
        {"k": keyword + " online", "v": "Medium", "s": "Mid"}
    ]

    return {
        "traffic": traffic,
        "time": "4m 20s",
        "bounce": "35%",
        "pages": round(3 + pages/100,1),
        "mobile": mobile,
        "desktop": desktop,
        "tablet": tablet,
        "sources": sources,
        "monthly": monthly,
        "countries": countries,
        "keywords": keywords
    }

# ===== MAIN =====
if st.button("Phân tích"):
    if domain:
        with st.spinner("Đang phân tích..."):
            data = analyze(domain)

        # KPI
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Visits", f"{data['traffic']:,}")
        col2.metric("Time", data["time"])
        col3.metric("Bounce", data["bounce"])
        col4.metric("Pages", data["pages"])

        st.divider()

        # Monthly chart
        df = pd.DataFrame({
            "Month": list(range(1,13)),
            "Traffic": data["monthly"]
        })
        fig = px.line(df, x="Month", y="Traffic")
        fig.update_layout(template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

        # Row 2
        col5, col6 = st.columns(2)

        # Device
        device_df = pd.DataFrame({
            "Device":["Desktop","Mobile","Tablet"],
            "Value":[data["desktop"],data["mobile"],data["tablet"]]
        })
        fig2 = px.pie(device_df, names="Device", values="Value", hole=0.6)
        fig2.update_layout(template="plotly_dark")
        col5.plotly_chart(fig2, use_container_width=True)

        # Sources
        col6.subheader("Nguồn truy cập")
        for k,v in data["sources"].items():
            col6.progress(v/100)
            col6.write(f"{k}: {v}%")

        # Row 3
        col7, col8 = st.columns(2)

        # Country
        country_df = pd.DataFrame({
            "Country": list(data["countries"].keys()),
            "Value": list(data["countries"].values())
        })
        fig3 = px.bar(country_df, x="Value", y="Country", orientation='h')
        fig3.update_layout(template="plotly_dark")
        col7.plotly_chart(fig3, use_container_width=True)

        # Keywords
        kw_df = pd.DataFrame(data["keywords"])
        kw_df.columns = ["Keyword","Volume","Rank"]
        col8.dataframe(kw_df)

    else:
        st.warning("Nhập domain trước 😄")
