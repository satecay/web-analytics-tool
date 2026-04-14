import { useState } from "react";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";

const COLORS = ["#6366f1", "#22d3ee", "#f59e0b", "#10b981", "#ec4899"];

// Dữ liệu mẫu thực tế cho các trang báo Việt Nam
const LOCAL_DATA = {
  "vnexpress.net": {
    "domain": "vnexpress.net", "category": "Tin tức & Truyền thông", "globalRank": 612, "countryRank": 1, "country": "Vietnam",
    "monthlyVisits": 70500000, "visitChange": 2.4, "avgDuration": "5m 42s", "bounceRate": 45.5, "pagesPerVisit": 3.08,
    "trafficByMonth": [{"month":"Jan","visits":68000000},{"month":"Feb","visits":65000000},{"month":"Mar","visits":70511000}],
    "devices": [{"name":"Mobile","value":75},{"name":"Desktop","value":23},{"name":"Tablet","value":2}],
    "trafficSources": [{"source":"Direct","percent":58.2},{"source":"Search","percent":35.4},{"source":"Social","percent":4.1}, {"source":"Referral","percent":2.3}],
    "topCountries": [{"country":"Vietnam","flag":"🇻🇳","percent":94.5},{"country":"United States","flag":"🇺🇸","percent":2.1}],
    "topKeywords": [{"keyword":"vnexpress","volume":2500000,"share":15.4}, {"keyword":"tin tuc","volume":1800000,"share":10.2}]
  },
  "tuoitre.vn": {
    "domain": "tuoitre.vn", "category": "Tin tức & Truyền thông", "globalRank": 3200, "countryRank": 8, "country": "Vietnam",
    "monthlyVisits": 9500000, "visitChange": 0.5, "avgDuration": "4m 50s", "bounceRate": 52.4, "pagesPerVisit": 2.85,
    "trafficByMonth": [{"month":"Jan","visits":9200000},{"month":"Feb","visits":8900000},{"month":"Mar","visits":9500000}],
    "devices": [{"name":"Mobile","value":82},{"name":"Desktop","value":16},{"name":"Tablet","value":2}],
    "trafficSources": [{"source":"Direct","percent":50.2},{"source":"Search","percent":42.4},{"source":"Social","percent":5.1}, {"source":"Referral","percent":2.3}],
    "topCountries": [{"country":"Vietnam","flag":"🇻🇳","percent":97.2}],
    "topKeywords": [{"keyword":"tuoi tre online","volume":950000,"share":14.2}]
  }
};

export default function App() {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);

  const analyze = async () => {
    setLoading(true);
    const domain = url.toLowerCase().replace(/^https?:\/\//, "").split('/')[0];

    // Ưu tiên lấy dữ liệu mẫu nếu có
    if (LOCAL_DATA[domain]) {
      setTimeout(() => {
        setData(LOCAL_DATA[domain]);
        setLoading(false);
      }, 800);
      return;
    }

    // Nếu không có, gọi API Backend (Giả định endpoint từ app.py)
    try {
      const res = await fetch(`http://localhost:8501/analyze?domain=${domain}`);
      const result = await res.json();
      setData(result);
    } catch (e) {
      console.error("Lỗi kết nối backend");
    }
    setLoading(false);
  };

  const fmt = (n) => n >= 1e6 ? (n / 1e6).toFixed(1) + "M" : n.toLocaleString();

  return (
    <div style={{ background: "#060d1a", minHeight: "100vh", color: "#f1f5f9", padding: "40px 20px", fontFamily: "sans-serif" }}>
      <div style={{ maxWidth: "1000px", margin: "0 auto" }}>
        <h1 style={{ textAlign: "center", marginBottom: "30px" }}>📡 WebScope Similar</h1>
        
        <div style={{ display: "flex", gap: "10px", marginBottom: "40px" }}>
          <input 
            style={{ flex: 1, padding: "15px", borderRadius: "10px", border: "1px solid #1e293b", background: "#0f172a", color: "white" }}
            placeholder="Nhập domain (vd: vnexpress.net)..."
            value={url} onChange={(e) => setUrl(e.target.value)}
          />
          <button onClick={analyze} style={{ padding: "0 30px", borderRadius: "10px", background: "#6366f1", color: "white", border: "none", cursor: "pointer" }}>
            {loading ? "Đang quét..." : "Phân tích"}
          </button>
        </div>

        {data && (
          <div style={{ display: "flex", flexDirection: "column", gap: "25px" }}>
            {/* Thẻ chỉ số chính giống Similarweb */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "20px" }}>
              {[
                { label: "Visits", val: fmt(data.monthlyVisits), icon: "📊" },
                { label: "Bounce Rate", val: data.bounceRate + "%", icon: "↩️" },
                { label: "Pages/Visit", val: data.pagesPerVisit, icon: "📄" },
                { label: "Duration", val: data.avgDuration, icon: "⏱️" }
              ].map((s, i) => (
                <div key={i} style={{ background: "#0f172a", padding: "20px", borderRadius: "15px", border: "1px solid #1e293b" }}>
                  <div style={{ color: "#64748b", fontSize: "13px" }}>{s.icon} {s.label}</div>
                  <div style={{ fontSize: "24px", fontWeight: "bold", marginTop: "5px" }}>{s.val}</div>
                </div>
              ))}
            </div>

            {/* Biểu đồ Traffic */}
            <div style={{ background: "#0f172a", padding: "25px", borderRadius: "15px", border: "1px solid #1e293b" }}>
              <h3>Lưu lượng hàng tháng</h3>
              <ResponsiveContainer width="100%" height={250}>
                <AreaChart data={data.trafficByMonth}>
                  <defs><linearGradient id="colorV" x1="0" y1="0" x2="0" y2="1"><stop offset="5%" stopColor="#6366f1" stopOpacity={0.3}/><stop offset="95%" stopColor="#6366f1" stopOpacity={0}/></linearGradient></defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="month" stroke="#64748b" />
                  <YAxis stroke="#64748b" tickFormatter={fmt} />
                  <Tooltip contentStyle={{ background: "#1e293b", border: "none" }} />
                  <Area type="monotone" dataKey="visits" stroke="#6366f1" fillOpacity={1} fill="url(#colorV)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
