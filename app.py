import streamlit as st
import requests
from bs4 import BeautifulSoup
from pytrends.request import TrendReq
import xml.etree.ElementTree as ET
import plotly.express as px

pytrends = TrendReq()

# ================= UI CONFIG =================
st.set_page_config(page_title="Mini SimilarWeb", layout="wide")

# Dark style
st.markdown("""
<style>
body { background-color: #0f172a; color: white; }
.card {
    background: #1e293b;
    padding: 20px;
    border-radius: 12px;
}
.metric {
    font-size: 28px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 Mini SimilarWeb")

domain = st.text_input("Nhập domain", placeholder="vd: vnexpress.net")

# ================= LOGIC =================
def get_trend(domain):
    keyword = domain.split('.')[0]
    try:
        pytrends.build_payload([keyword], timeframe='today 3-m')
        df = pytrends.interest_over_time()
        return int(df[keyword].mean()) if not df.empty else 10
    except:
        return 10

def get_pages(domain):
    try:
        res = requests.get(f"https://{domain}/sitemap.xml", timeout=5)
        root = ET.fromstring(res.content)
        return len(root.findall(".//{*}loc"))
    except:
        return 50

def analyze(domain):
    res = requests.get(f"https://{domain}", headers={"User-Agent":"Mozilla/5.0"}, timeout=5)
    soup = BeautifulSoup(res.text, "html.parser")

    trend = get_trend(domain)
    pages = get_pages(domain)

    seo = 0
    if soup.title: seo += 20
    if soup.find("meta", attrs={"name":"description"}): seo += 20
    if soup.find_all("h1"): seo += 20

    traffic = int(trend * 1000 * (1 + pages/500) * (1 + seo/100))

    mobile = 70 if soup.find("meta", attrs={"name":"viewport"}) else 40
    desktop = 100 - mobile

    sources = {
        "Search": min(70, 30 + seo // 2),
        "Direct": 20,
        "Social": 10,
        "Referral": 100 - (30 + seo // 2 + 20 + 10)
    }

    return traffic, mobile, desktop, sources


# ================= MAIN =================
if st.button("Analyze"):
    if domain:
        with st.spinner("Đang phân tích..."):
            traffic, mobile, desktop, sources = analyze(domain)

        # KPI
        col1, col2, col3 = st.columns(3)

        col1.metric("🚀 Visits / Month", f"{traffic:,}")
        col2.metric("📱 Mobile %", f"{mobile}%")
        col3.metric("💻 Desktop %", f"{desktop}%")

        st.divider()

        col4, col5 = st.columns(2)

        # Device Chart
        device_df = {"Device": ["Mobile", "Desktop"], "Value": [mobile, desktop]}
        fig1 = px.pie(device_df, names="Device", values="Value", hole=0.5)
        fig1.update_layout(template="plotly_dark")

        col4.plotly_chart(fig1, use_container_width=True)

        # Traffic Sources
        source_df = {"Source": list(sources.keys()), "Value": list(sources.values())}
        fig2 = px.bar(source_df, x="Source", y="Value")
        fig2.update_layout(template="plotly_dark")

        col5.plotly_chart(fig2, use_container_width=True)

    else:
        st.warning("Nhập domain trước 😄")
