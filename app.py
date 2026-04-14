import streamlit as st
import requests
from bs4 import BeautifulSoup
import json

# Hàm tạo cấu trúc JSON chuẩn Similarweb
def generate_similar_json(domain, visits, rank, seo_score):
    return {
        "domain": domain,
        "category": "News & Media" if ".vn" in domain else "General",
        "globalRank": rank * 100,
        "countryRank": rank,
        "country": "Vietnam",
        "monthlyVisits": visits,
        "visitChange": 2.5,
        "avgDuration": f"{3 + seo_score//20}m {10 + seo_score}s",
        "bounceRate": 45 + (100 - seo_score)//5,
        "pagesPerVisit": round(2 + seo_score/50, 2),
        "trafficByMonth": [
            {"month": "Jan", "visits": int(visits * 0.85)},
            {"month": "Feb", "visits": int(visits * 0.9)},
            {"month": "Mar", "visits": visits}
        ],
        "devices": [
            {"name": "Mobile", "value": 70 if seo_score > 50 else 40},
            {"name": "Desktop", "value": 30 if seo_score > 50 else 60}
        ],
        "trafficSources": [
            {"source": "Direct", "percent": 40},
            {"source": "Search", "percent": min(50, 20 + seo_score//2)},
            {"source": "Social", "percent": 10}
        ]
    }

def analyze_domain(domain):
    # Ưu tiên các trang báo lớn (Dữ liệu thực tế 2025)
    targets = {
        "vnexpress.net": (70500000, 1),
        "thanhnien.vn": (12820000, 5),
        "vietnamnet.vn": (12760000, 6)
    }
    
    if domain in targets:
        v, r = targets[domain]
        return generate_similar_json(domain, v, r, 90)

    # Thuật toán quét SEO thực tế nếu không có trong danh sách mẫu
    try:
        res = requests.get(f"https://{domain}", timeout=5, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(res.text, "html.parser")
        
        seo = 0
        if soup.title: seo += 30
        if soup.find("meta", attrs={"name": "description"}): seo += 30
        if soup.find_all("h1"): seo += 20
        
        estimated_visits = 50000 + (seo * 2000)
        return generate_similar_json(domain, estimated_visits, 5000, seo)
    except:
        return generate_similar_json(domain, 10000, 9999, 10)

# Giao diện Streamlit dùng làm API Mockup
st.set_page_config(page_title="WebScope Backend", page_icon="📡")
st.title("API Backend Analyzer")

query = st.text_input("Domain cần quét:")
if query:
    data = analyze_domain(query.strip().lower())
    st.write("Dữ liệu trả về cho Frontend:")
    st.json(data)
