import requests
from bs4 import BeautifulSoup
from pytrends.request import TrendReq
import xml.etree.ElementTree as ET

pytrends = TrendReq()

# 🔹 Lấy trend score
def get_trend(domain):
    keyword = domain.split('.')[0]
    try:
        pytrends.build_payload([keyword], timeframe='today 3-m')
        df = pytrends.interest_over_time()
        return int(df[keyword].mean()) if not df.empty else 10
    except:
        return 10


# 🔹 Đếm số page từ sitemap
def get_page_count(domain):
    try:
        url = f"https://{domain}/sitemap.xml"
        res = requests.get(url, timeout=5)

        root = ET.fromstring(res.content)
        return len(root.findall(".//{*}loc"))
    except:
        return 50  # fallback


# 🔹 SEO score
def get_seo_score(soup):
    score = 0

    if soup.title: score += 20
    if soup.find("meta", attrs={"name": "description"}): score += 20
    if soup.find_all("h1"): score += 20
    if soup.find_all("h2"): score += 10

    return score


# 🔹 Estimate traffic (improved)
def estimate_traffic(trend, pages, seo):
    base = trend * 1000
    page_factor = 1 + (pages / 500)
    seo_factor = 1 + (seo / 100)

    return int(base * page_factor * seo_factor)


# 🔹 Traffic sources logic
def get_sources(seo, pages):
    search = min(70, 30 + seo // 2)
    referral = min(30, pages // 50)
    social = 10
    direct = 100 - (search + referral + social)

    return {
        "Search": search,
        "Direct": direct,
        "Social": social,
        "Referral": referral
    }


# 🔹 Device detection
def get_device(soup):
    viewport = soup.find("meta", attrs={"name": "viewport"})
    mobile = 70 if viewport else 40
    return mobile, 100 - mobile


# 🔹 MAIN
def analyze_website(domain):
    try:
        res = requests.get(f"https://{domain}", headers={"User-Agent":"Mozilla/5.0"}, timeout=5)
        soup = BeautifulSoup(res.text, "html.parser")

        trend = get_trend(domain)
        pages = get_page_count(domain)
        seo = get_seo_score(soup)

        traffic = estimate_traffic(trend, pages, seo)
        sources = get_sources(seo, pages)
        mobile, desktop = get_device(soup)

        return {
            "domain": domain,
            "title": soup.title.string if soup.title else "",
            "traffic": traffic,
            "trend": trend,
            "pages": pages,
            "seo": seo,
            "sources": sources,
            "mobile": mobile,
            "desktop": desktop
        }

    except Exception as e:
        return {"error": str(e)}