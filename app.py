import streamlit as st
import requests
from bs4 import BeautifulSoup
from pytrends.request import TrendReq
import xml.etree.ElementTree as ET

pytrends = TrendReq()

st.title("📊 Mini SimilarWeb (Free Version)")

domain = st.text_input("Nhập domain (vd: vnexpress.net)")

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

    sources = {
        "Search": min(70, 30 + seo // 2),
        "Direct": 20,
        "Social": 10,
        "Referral": 100 - (30 + seo // 2 + 20 + 10)
    }

    return traffic, mobile, 100-mobile, sources


if st.button("Analyze"):
    if domain:
        with st.spinner("Đang phân tích..."):
            traffic, mobile, desktop, sources = analyze(domain)

        st.success(f"🚀 {traffic} visits / month")

        st.subheader("📱 Device")
        st.write({"Mobile": mobile, "Desktop": desktop})

        st.bar_chart(sources)

    else:
        st.warning("Nhập domain đi 😄")
