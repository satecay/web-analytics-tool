import requests
from bs4 import BeautifulSoup
from pytrends.request import TrendReq
import xml.etree.ElementTree as ET

pytrends = TrendReq()

# ===== GOOGLE SUGGEST =====
def get_keywords(domain):
    keyword = domain.split('.')[0]
    url = f"https://suggestqueries.google.com/complete/search?client=firefox&q={keyword}"
    try:
        res = requests.get(url)
        data = res.json()[1]
        return data[:5]
    except:
        return [keyword]

# ===== TREND =====
def get_trend(keyword):
    try:
        pytrends.build_payload([keyword], timeframe='today 3-m')
        df = pytrends.interest_over_time()
        return int(df[keyword].mean()) if not df.empty else 10
    except:
        return 10

# ===== SITEMAP =====
def get_pages(domain):
    try:
        res = requests.get(f"https://{domain}/sitemap.xml", timeout=5)
        root = ET.fromstring(res.content)
        return len(root.findall(".//{*}loc"))
    except:
        return 50

# ===== SEO SCORE =====
def get_seo_score(soup):
    score = 0
    if soup.title: score += 20
    if soup.find("meta", attrs={"name":"description"}): score += 20
    if soup.find_all("h1"): score += 20
    if soup.find_all("h2"): score += 10
    return score

# ===== KEYWORD VOLUME (estimate thông minh) =====
def estimate_volume(keyword, trend):
    base = len(keyword) * 1000
    return int(base * (trend / 50 + 0.5))

# ===== COUNTRY ESTIMATE =====
def detect_country(domain, soup):
    if ".vn" in domain:
        return {"Vietnam": 85, "USA":5, "Japan":2, "Korea":2}
    lang = soup.html.get("lang") if soup.html else ""
    if "en" in str(lang):
        return {"USA": 60, "UK":10, "India":10}
    return {"Global":100}

# ===== MAIN =====
def analyze(domain):
    res = requests.get(f"https://{domain}", headers={"User-Agent":"Mozilla/5.0"}, timeout=5)
    soup = BeautifulSoup(res.text, "html.parser")

    keywords = get_keywords(domain)
    trend = get_trend(keywords[0])
    pages = get_pages(domain)
    seo = get_seo_score(soup)

    # TRAFFIC MODEL PRO
    traffic = int(
        trend * 1200 *
        (1 + pages/400) *
        (1 + seo/100)
    )

    # DEVICE
    mobile = 70 if soup.find("meta", attrs={"name":"viewport"}) else 40
    desktop = 100 - mobile
    tablet = 5

    # SOURCES (smart hơn)
    search = min(70, 30 + seo//2)
    referral = min(25, pages//40)
    direct = 100 - (search + referral + 10)

    sources = {
        "Direct": direct,
        "Search": search,
        "Social": 10,
        "Referral": referral,
        "Email": 3,
        "Display": 2
    }

    # MONTHLY TREND
    monthly = [int(trend * (0.7 + i*0.04)) for i in range(12)]

    # KEYWORD TABLE
    keyword_data = []
    for k in keywords:
        vol = estimate_volume(k, trend)
        keyword_data.append({
            "Keyword": k,
            "Volume": f"{vol:,}",
            "Share": f"{round(vol/traffic*100,2)}%"
        })

    countries = detect_country(domain, soup)

    return {
        "traffic": traffic,
        "keywords": keyword_data,
        "countries": countries,
        "sources": sources,
        "monthly": monthly,
        "mobile": mobile,
        "desktop": desktop,
        "tablet": tablet,
        "pages": round(3 + pages/100,1),
        "bounce": f"{35 + seo//5}%",
        "time": f"{3 + seo//20}m {10 + seo}s"
    }
