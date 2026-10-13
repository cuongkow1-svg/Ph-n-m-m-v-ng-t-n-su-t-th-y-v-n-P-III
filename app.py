import io
from datetime import date
import hmac
import requests
import base64
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy.stats import gamma, norm

st.set_page_config(page_title="THỦY VĂN P-III | HydroStat Pro", page_icon="🌊", layout="wide", initial_sidebar_state="expanded")
def image_css(filename):
    path = Path(__file__).resolve().parent / filename
    return base64.b64encode(path.read_bytes()).decode("ascii") if path.exists() else ""

hero_image = image_css("anh_ho_chua_dau_trang.jpg")
sidebar_image = image_css("anh_ho_chua_menu.jpg")
st.markdown(f"""<style>
:root {{--navy:#0c3158;--blue:#0e72ce}}
[data-testid="stAppViewContainer"] {{background:#f0f5fb}}
[data-testid="stSidebar"] {{
 background:linear-gradient(180deg,#06284e 0%,#0c4c86 57%,rgba(7,35,65,.20) 100%),url("data:image/jpeg;base64,{sidebar_image}") bottom center / 100% auto no-repeat,#092d53;
 border-right:1px solid #ffffff22;
}}
[data-testid="stSidebar"] * {{color:#f5faff!important}}
[data-testid="stSidebar"] div[data-baseweb="select"] * {{color:#102d49!important}}
[data-testid="stSidebar"] input {{color:#142e48!important}}
[data-testid="stSidebar"] textarea {{color:#142e48!important}}
.block-container {{max-width:1680px;padding-top:.55rem;padding-bottom:2rem}}
h1,h2,h3 {{color:#0b3d70!important;letter-spacing:-.02em}}
div[data-testid="stMetric"] {{background:#fff;border:1px solid #d9e7f4;border-radius:11px;padding:15px 18px;box-shadow:0 4px 15px #143e6610}}
div[data-testid="stMetricLabel"] {{color:#5b7187}}
div[data-testid="stMetricValue"] {{color:#123f6b}}
div[data-testid="stVerticalBlockBorderWrapper"] > div {{border-radius:16px!important}}
.stButton>button[kind="primary"], .stDownloadButton>button[kind="primary"] {{background:#0878d7;border-radius:9px}}
[data-testid="stDataFrame"] {{border-radius:10px;overflow:hidden}}
.hero {{padding:28px 34px;border-radius:13px;color:white;background:linear-gradient(90deg,#06274c 0%,#083f70 34%,rgba(8,53,88,.25) 100%),url("data:image/jpeg;base64,{hero_image}") center / cover no-repeat,#0a3a66;margin-bottom:18px;box-shadow:0 8px 24px #15467522;min-height:160px;display:flex;flex-direction:column;justify-content:center}}
.hero h1 {{color:white!important;margin:0;font-size:2.35rem}}
.hero .brand {{font-size:1.0rem;font-weight:800;letter-spacing:.24em;color:#a7e5ff;margin-bottom:9px;text-transform:uppercase}}
.hero p {{color:#d4eafb;margin:6px 0 0}}
.section {{font-size:1.09rem;font-weight:800;color:#095098;margin:7px 0 13px;letter-spacing:.01em}}
.note {{color:#60768d;font-size:.87rem}}
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {{background:#1479db;border-radius:10px}}
[data-testid="stSidebar"] div[role="radiogroup"] label {{padding:7px 10px;transition:background .2s}}
div[data-testid="stMetric"] {{border-top:3px solid #1678d5}}
div[data-testid="stVerticalBlockBorderWrapper"] {{box-shadow:0 4px 16px #0c467010}}
.stDownloadButton button {{border-radius:9px}}
/* Professional UI polish: color-coded bottom cards and controls */
[data-testid="stMainBlockContainer"] .stButton>button {{border-radius:9px;font-weight:700}}
[data-testid="stMainBlockContainer"] .stDownloadButton>button {{background:#04a875;color:white;border:0;font-weight:750}}
[data-testid="stMainBlockContainer"] .stDownloadButton>button:hover {{background:#078968;color:white}}
[data-testid="stMainBlockContainer"] div[data-testid="stVerticalBlockBorderWrapper"]:has(.section) {{
 border:1px solid #dce7f2!important;background:#fff!important;
}}
[data-testid="stMainBlockContainer"] div[data-testid="stHorizontalBlock"]:has(.stSelectbox) > div:nth-child(1) div[data-testid="stVerticalBlockBorderWrapper"] {{
 background:linear-gradient(130deg,#fff4f5,#ffebee)!important;border-color:#ffdade!important;
}}
[data-testid="stMainBlockContainer"] div[data-testid="stHorizontalBlock"]:has(.stSelectbox) > div:nth-child(2) div[data-testid="stVerticalBlockBorderWrapper"] {{
 background:linear-gradient(130deg,#f0f8ff,#e6f2ff)!important;border-color:#d2e7fc!important;
}}
[data-testid="stMainBlockContainer"] div[data-testid="stHorizontalBlock"]:has(.stSelectbox) > div:nth-child(3) div[data-testid="stVerticalBlockBorderWrapper"] {{
 background:linear-gradient(130deg,#effbf3,#e0f7e9)!important;border-color:#c8eed6!important;
}}
[data-testid="stSidebar"] .stRadio label {{font-weight:600}}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h2 {{color:white!important}}
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] h3 {{color:#d6eaff!important}}
[data-testid="stSidebar"] div[data-testid="stTextInput"] label {{color:#eaf4ff!important}}
[data-testid="stSidebar"] div[data-testid="stNumberInput"] label {{color:#eaf4ff!important}}
[data-testid="stSidebar"] [data-testid="stSidebarContent"] {{padding-top:1.1rem}}
[data-testid="stMainBlockContainer"] .stDataFrame {{border:1px solid #dbe7f3}}
@media (max-width:900px) {{
 .hero {{min-height:115px;padding:16px 20px}}
 .hero h1 {{font-size:1.55rem}}
}}
</style>""",unsafe_allow_html=True)
st.markdown('<div class="hero"><div class="brand">VINH TRAN APP</div><h1>🌊 THỦY VĂN P-III <span style="font-size:15px;background:#ffffff24;padding:5px 10px;border-radius:15px">PRO 4.1.2</span></h1><p>QUAN TRẮC Q · H · MƯA HẰNG NGÀY • TẦN SUẤT PEARSON III</p></div>',unsafe_allow_html=True)


COL_DATE = "Ngày"
METRICS = {"Lưu lượng Q": ("Q (m³/s)", "m³/s"), "Mực nước H": ("H (m)", "m"), "Lượng mưa": ("Mưa (mm)", "mm")}

@st.cache_data
def example_data():
    rng = np.random.default_rng(2026)
    dates = pd.date_range("2020-01-01", "2025-12-31", freq="D")
    t = np.arange(len(dates))
    q = 1050 + 350 * np.sin(2 * np.pi * (t - 100) / 365.25) + rng.gamma(2.2, 90, len(t))
    h = 10.2 + 0.0028 * q + rng.normal(0, 0.11, len(t))
    rain = np.where(rng.random(len(t)) < .42, rng.gamma(1.35, 15, len(t)), 0)
    return pd.DataFrame({COL_DATE: dates, "Q (m³/s)": np.round(q, 1), "H (m)": np.round(h, 2), "Mưa (mm)": np.round(rain, 1)})


def parse_daily_excel(uploaded_file):
    data = pd.read_excel(uploaded_file, sheet_name=0)
    required = [COL_DATE] + [v[0] for v in METRICS.values()]
    missing = [x for x in required if x not in data.columns]
    if missing:
        raise ValueError("Thiếu cột: " + ", ".join(missing) + ". Hãy dùng file mẫu.")
    data = data[required].copy()
    if pd.api.types.is_numeric_dtype(data[COL_DATE]):
        data[COL_DATE] = pd.to_datetime(data[COL_DATE], unit="D", origin="1899-12-30", errors="coerce")
    else:
        data[COL_DATE] = pd.to_datetime(data[COL_DATE], dayfirst=True, errors="coerce")
    if data[COL_DATE].isna().any():
        raise ValueError("Cột Ngày có ô trống hoặc ngày không hợp lệ.")
    for c in required[1:]:
        data[c] = pd.to_numeric(data[c], errors="coerce")
    if data[required[1:]].notna().sum().sum() == 0:
        raise ValueError("Không có giá trị Q, H hoặc mưa hợp lệ.")
    if (data[["Q (m³/s)", "Mưa (mm)"]] < 0).any().any():
        raise ValueError("Lưu lượng Q hoặc lượng mưa đang có số âm. Vui lòng kiểm tra dữ liệu.")
    if data[COL_DATE].duplicated().any():
        dup = data.loc[data[COL_DATE].duplicated(), COL_DATE].iloc[0]
        raise ValueError(f"Ngày {dup:%d/%m/%Y} bị trùng. Mỗi ngày chỉ nhập một dòng.")
    return data.sort_values(COL_DATE).reset_index(drop=True)

with st.sidebar:
    st.markdown("## 🌊 VINH TRAN APP")
    st.caption("THỦY VĂN P-III • PHIÊN BẢN 4.1.2")
    section = st.radio("DANH MỤC", ["🏠 Tổng quan", "🔎 Tra cứu số liệu", "💾 Kho dữ liệu", "📅 Quan trắc hằng ngày", "📋 Nhập số liệu", "📊 Thống kê năm", "📈 Đường tần suất P-III", "📘 Bảng Φp", "📥 Xuất kết quả", "❔ Hướng dẫn"], label_visibility="collapsed")
    st.divider()
    st.markdown("### ⚙️ DỰ ÁN & DỮ LIỆU")
    project = st.text_input("Tên dự án", "Công trình thủy văn")
    location = st.text_input("Vị trí", "")
    source = st.radio("Nguồn dữ liệu", ["Dữ liệu mẫu", "Tải Excel theo ngày", "Dữ liệu đã lưu"])
    uploaded = st.file_uploader("Tải Excel (.xlsx)", type=["xlsx"], help="Gồm Ngày, Q (m³/s), H (m), Mưa (mm)") if source == "Tải Excel theo ngày" else None
    st.divider()
    metric_name = st.selectbox("Phân tích tần suất cho", list(METRICS.keys()))
    metric_col, metric_unit = METRICS[metric_name]
    if metric_name == "Lượng mưa":
        aggregation = st.radio("Chỉ tiêu thống kê", ["Mưa ngày lớn nhất năm", "Tổng lượng mưa năm"])
    else:
        aggregation = "Giá trị lớn nhất năm"

if source == "Dữ liệu đã lưu":
    daily = None
elif source == "Tải Excel theo ngày" and uploaded is None:
    st.info("Chưa có Excel được tải lên. Đang hiển thị dữ liệu mẫu để bạn thử các chức năng.")
    daily = example_data()
elif uploaded is not None:
    try:
        daily = parse_daily_excel(uploaded)
    except Exception as exc:
        st.error(f"Không đọc được Excel: {exc}")
        st.stop()
else:
    daily = example_data()

# KHO LƯU TRỮ BỀN VỮNG: Supabase PostgREST, không dùng SQLite cục bộ trên Streamlit Cloud.
# Chỉ truy cập bằng service role key ở phía máy chủ, có lớp mật khẩu ứng dụng.
def secret(name):
    try:
        return str(st.secrets.get(name, "")).strip()
    except Exception:
        return ""

DB_URL = secret("SUPABASE_URL").rstrip("/")
DB_KEY = secret("SUPABASE_SERVICE_ROLE_KEY")
APP_PASSWORD = secret("APP_PASSWORD")
db_configured = bool(DB_URL and DB_KEY and APP_PASSWORD)

def db_request(method, params=None, payload=None):
    if not db_configured:
        raise RuntimeError("Chưa cấu hình Supabase và mật khẩu trong Streamlit Secrets.")
    headers = {"apikey": DB_KEY, "Authorization": f"Bearer {DB_KEY}", "Content-Type":"application/json",
               "Prefer":"resolution=merge-duplicates,return=minimal"}
    resp = requests.request(method, DB_URL + "/rest/v1/hydro_daily", headers=headers,
                            params=params, json=payload, timeout=25)
    resp.raise_for_status()
    return resp.json() if resp.content else []

def check_access():
    if not db_configured:
        st.warning("Chưa kết nối kho lưu trữ. Bạn vẫn tra cứu Excel được; muốn lưu lâu dài cần cấu hình Supabase theo HƯỚNG_DẪN_4_1.txt.")
        return False
    typed = st.text_input("Mật khẩu quản trị kho dữ liệu", type="password", key="db_pass")
    if not typed or not hmac.compare_digest(typed, APP_PASSWORD):
        st.info("Nhập mật khẩu quản trị để đọc hoặc lưu dữ liệu trên kho trực tuyến.")
        return False
    return True

def read_db():
    rows = []
    offset = 0
    while True:
        chunk = db_request("GET", params={"select":"obs_date,q,h,rain","order":"obs_date.asc",
                                           "limit":1000,"offset":offset})
        rows.extend(chunk)
        if len(chunk) < 1000:
            break
        offset += len(chunk)
    if not rows:
        return pd.DataFrame(columns=[COL_DATE]+[v[0] for v in METRICS.values()])
    result = pd.DataFrame(rows).rename(columns={"obs_date":COL_DATE,"q":"Q (m³/s)","h":"H (m)","rain":"Mưa (mm)"})
    result[COL_DATE] = pd.to_datetime(result[COL_DATE])
    return result

def save_db(df):
    records = []
    for row in df.itertuples(index=False, name=None):
        date, q, h, rain = row
        def number(v):
            return None if pd.isna(v) else float(v)
        records.append({"obs_date":pd.Timestamp(date).strftime("%Y-%m-%d"),
                        "q":number(q),"h":number(h),"rain":number(rain)})
    for i in range(0,len(records),300):
        db_request("POST",params={"on_conflict":"obs_date"},payload=records[i:i+300])

if source == "Dữ liệu đã lưu":
    if not db_configured:
        st.error("Chưa cấu hình kho Supabase. Xem file HƯỚNG_DẪN_4_1.txt trong ZIP.")
        st.stop()
    if not check_access():
        st.stop()
    try:
        daily = read_db()
    except Exception as exc:
        st.error(f"Không tải được dữ liệu từ kho: {exc}")
        st.stop()
    if daily.empty:
        st.info("Kho chưa có dữ liệu. Hãy chọn Tải Excel theo ngày, vào Kho dữ liệu và lưu lên kho.")
        st.stop()

# Display date as datetime; never silently replace a user's uploaded data with the sample.
first_date = daily[COL_DATE].min().date()
last_date = daily[COL_DATE].max().date()

with st.sidebar:
    st.markdown("### 📅 LỌC NGÀY")
    chosen = st.date_input("Khoảng ngày xem biểu đồ", value=(first_date, max(last_date, date.today())), min_value=date(1900, 1, 1), max_value=date(2100, 12, 31))
if isinstance(chosen, (tuple, list)) and len(chosen) == 2:
    begin, end = chosen
else:
    begin, end = first_date, last_date
filtered = daily.loc[daily[COL_DATE].dt.date.between(begin, end)].copy()

annual_input = daily[[COL_DATE, metric_col]].dropna().copy()
annual_input["Năm"] = annual_input[COL_DATE].dt.year
if aggregation == "Tổng lượng mưa năm":
    annual = annual_input.groupby("Năm", as_index=False)[metric_col].sum()
else:
    annual = annual_input.groupby("Năm", as_index=False)[metric_col].max()
annual.rename(columns={metric_col: "Giá trị năm"}, inplace=True)
annual_values = annual["Giá trị năm"].to_numpy(dtype=float)
valid_piii = len(annual_values) >= 3 and np.all(np.isfinite(annual_values)) and np.all(annual_values > 0) and annual_values.mean() > 0
mean = float(np.mean(annual_values)) if len(annual_values) else np.nan
cv_est = float(np.std(annual_values, ddof=1) / mean) if valid_piii else np.nan
with st.sidebar:
    st.markdown("### 🎛️ HIỆU CHỈNH P-III")
    if valid_piii:
        cv = st.number_input("Cv", min_value=.01, max_value=3.0, value=float(np.clip(cv_est, .01, 3)), step=.01, format="%.3f")
        cs = st.number_input("Cs", min_value=.01, max_value=6.0, value=float(np.clip(2*cv, .01, 6)), step=.01, format="%.3f")
    else:
        st.caption("Chưa đủ chuỗi giá trị năm hợp lệ để tính P-III.")

p_design = np.array([.1,.2,.5,1,2,5,10,20,50,75,90,95,99])
if valid_piii:
    def phi(p):
        a = 4 / cs**2
        return (gamma.isf(np.asarray(p, dtype=float)/100, a=a) - a) / np.sqrt(a)
    def kp(p): return 1 + cv * phi(p)
    def qp(p): return mean * kp(p)
    ranks = np.arange(1, len(annual_values)+1)
    emp_p = ranks/(len(annual_values)+1)*100
    emp_y = np.sort(annual_values)[::-1]
    emp = pd.DataFrame({"Thứ hạng": ranks, "Giá trị năm": emp_y, "P kinh nghiệm (%)": emp_p})
    design = pd.DataFrame({"P (%)": p_design, "Φp": phi(p_design), "Kp": kp(p_design), f"Giá trị thiết kế ({metric_unit})": qp(p_design)})
    def prob_x(p): return norm.ppf(1-np.asarray(p)/100)
    p_line = np.linspace(.05, 99.95, 1000)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=prob_x(p_line), y=qp(p_line), name="Đường lý luận P-III", mode="lines", line=dict(color="#f32440", width=3.2), customdata=p_line, hovertemplate="P=%{customdata:.2f}%<br>Giá trị=%{y:.2f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=prob_x(emp_p), y=emp_y, name="Điểm kinh nghiệm", mode="markers", marker=dict(color="#1479d4", size=9, line=dict(color="white", width=1)), customdata=emp_p, hovertemplate="P=%{customdata:.2f}%<br>Giá trị=%{y:.2f}<extra></extra>"))
    fig.update_layout(height=460, template="plotly_white", xaxis=dict(title="Tần suất vượt P (%) — trục xác suất chuẩn", tickmode="array", tickvals=prob_x(p_design), ticktext=[f"{x:g}" for x in p_design], autorange="reversed"), yaxis_title=f"{metric_name} ({metric_unit})", legend=dict(orientation="h", y=1.12), margin=dict(l=10,r=10,t=55,b=30), paper_bgcolor="white")


def show_daily_chart():
    fig_d = go.Figure()
    fig_d.add_trace(go.Scatter(x=filtered[COL_DATE], y=filtered["Q (m³/s)"], mode="lines", name="Q (m³/s)", line=dict(color="#1278c6", width=2)))
    fig_d.add_trace(go.Scatter(x=filtered[COL_DATE], y=filtered["H (m)"], mode="lines", name="H (m)", yaxis="y2", line=dict(color="#11a2a4", width=2)))
    fig_d.add_trace(go.Bar(x=filtered[COL_DATE], y=filtered["Mưa (mm)"], name="Mưa (mm)", yaxis="y3", marker_color="#76b7ed", opacity=.36))
    fig_d.update_layout(height=460, template="plotly_white", barmode="overlay", legend=dict(orientation="h", y=1.14), xaxis_title="Ngày", yaxis=dict(title="Q (m³/s)"), yaxis2=dict(title="H (m)", overlaying="y", side="right", showgrid=False), yaxis3=dict(overlaying="y", side="right", anchor="free", position=.94, visible=False, rangemode="tozero"), margin=dict(l=10,r=15,t=55,b=30))
    st.plotly_chart(fig_d, use_container_width=True, key="daily_chart", config={"displaylogo":False})
    st.caption("Q, H và mưa có đơn vị khác nhau; xem giá trị chính xác khi di chuột. Mưa sử dụng trục riêng (ẩn) để minh họa diễn biến.")


def show_freq_chart(key):
    if not valid_piii:
        st.warning("Cần ít nhất 3 năm có giá trị dương của chỉ tiêu đã chọn. Hãy bổ sung thêm dữ liệu ngày qua Excel.")
        return
    st.plotly_chart(fig, use_container_width=True, key=key, config={"displaylogo":False,"toImageButtonOptions":{"format":"png","filename":"duong_tan_suat_PIII","scale":2}})
    if len(annual_values) < 10:
        st.warning(f"Chỉ có {len(annual_values)} năm dữ liệu. Kết quả tần suất thiết kế chưa đủ tin cậy, đặc biệt ở P nhỏ.")
    if np.any(kp(p_design) <= 0):
        st.warning("Một số Kp ≤ 0. Cần kiểm tra lại bộ thông số Cv/Cs.")


def show_design():
    if valid_piii:
        st.dataframe(design.style.format(precision=3), use_container_width=True, hide_index=True)
    else:
        st.info("Chưa đủ số năm để tính bảng thiết kế.")


def show_export():
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="xlsxwriter", datetime_format="dd/mm/yyyy") as writer:
        daily.to_excel(writer, sheet_name="So lieu hang ngay", index=False)
        annual.to_excel(writer, sheet_name="Thong ke theo nam", index=False)
        if valid_piii:
            emp.to_excel(writer, sheet_name="Tan suat kinh nghiem", index=False)
            design.to_excel(writer, sheet_name="Gia tri thiet ke", index=False)
        pd.DataFrame({"Thông số":["Dự án","Vị trí","Chỉ tiêu","Cách tổng hợp","Số ngày","Số năm","Trung bình năm","Cv dùng tính","Cs dùng tính"],"Giá trị":[project,location,metric_name,aggregation,len(daily),len(annual),mean,cv if valid_piii else None,cs if valid_piii else None]}).to_excel(writer, sheet_name="Thong so", index=False)
    st.download_button("📥 Xuất Excel kết quả", data=buf.getvalue(), file_name="VinhTranApp_ThuyVan_Q_H_Mua.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", type="primary", use_container_width=True)

if section == "🏠 Tổng quan":
    st.markdown('<div class="section">📋 TỔNG QUAN QUAN TRẮC THỦY VĂN</div>', unsafe_allow_html=True)
    st.caption(f"**Dự án:** {project}　|　**Vị trí:** {location or 'Chưa nhập'}　|　**Dữ liệu:** {first_date:%d/%m/%Y} – {last_date:%d/%m/%Y}")
    a,b,c,d = st.columns(4)
    a.metric("Ngày quan trắc", f"{len(daily):,}")
    b.metric("Số năm dữ liệu", len(annual))
    c.metric("Cv năm", f"{cv:.3f}" if valid_piii else "—")
    d.metric("Cs hiệu chỉnh", f"{cs:.3f}" if valid_piii else "—")
    with st.container(border=True):
        st.markdown('<div class="section">📅 DIỄN BIẾN Q – H – MƯA HẰNG NGÀY</div>', unsafe_allow_html=True)
        show_daily_chart()
    with st.container(border=True):
        st.markdown(f'<div class="section">📈 TẦN SUẤT P-III • {metric_name.upper()}</div>', unsafe_allow_html=True)
        show_freq_chart("overview_freq")
    left,right=st.columns(2)
    with left:
        with st.container(border=True):
            st.markdown('<div class="section">📊 TỔNG HỢP THEO NĂM</div>', unsafe_allow_html=True)
            st.dataframe(annual, use_container_width=True, hide_index=True)
    with right:
        with st.container(border=True):
            st.markdown('<div class="section">📘 BẢNG GIÁ TRỊ THIẾT KẾ</div>', unsafe_allow_html=True)
            show_design()
    with st.container(border=True):
        st.markdown('<div class="section">📥 XUẤT KẾT QUẢ</div>', unsafe_allow_html=True)
        show_export()
elif section == "🔎 Tra cứu số liệu":
    st.subheader("🔎 Tra cứu Q – H – Mưa theo ngày")
    st.caption("Tra cứu từ nguồn dữ liệu đã chọn ở menu bên trái: Excel đang tải lên hoặc kho đã lưu.")
    c1,c2 = st.columns(2)
    with c1:
        lookup_start = st.date_input("Từ ngày", value=first_date, min_value=date(1900, 1, 1), max_value=date(2100, 12, 31), key="lookup_from")
    with c2:
        lookup_end = st.date_input("Đến ngày", value=max(last_date, date.today()), min_value=date(1900, 1, 1), max_value=date(2100, 12, 31), key="lookup_to")
    st.caption(f"Dữ liệu hiện có: {first_date:%d/%m/%Y} – {last_date:%d/%m/%Y}. Bạn có thể chọn ngày đến năm 2100; các ngày chưa có số liệu sẽ không xuất hiện trong bảng.")
    if lookup_start > lookup_end:
        st.error("Ngày bắt đầu phải trước hoặc bằng ngày kết thúc.")
    else:
        lookup = daily.loc[daily[COL_DATE].dt.date.between(lookup_start,lookup_end)].copy()
        search_metric = st.selectbox("Chỉ tiêu cần xem", ["Cả ba chỉ tiêu"]+list(METRICS.keys()))
        if search_metric != "Cả ba chỉ tiêu":
            lookup = lookup[[COL_DATE, METRICS[search_metric][0]]]
        st.metric("Số ngày tìm thấy",len(lookup))
        if lookup.empty:
            st.info("Không có dữ liệu trong khoảng thời gian đã chọn.")
        st.dataframe(lookup,use_container_width=True,hide_index=True)
        if not lookup.empty:
            st.download_button("📥 Xuất kết quả tra cứu (.csv)",lookup.to_csv(index=False).encode("utf-8-sig"),
                               file_name="Tra_cuu_thuy_van.csv",mime="text/csv",key="lookup_csv")
            numeric = lookup.select_dtypes(include="number")
            if not numeric.empty:
                for c in numeric.columns:
                    idxmax = numeric[c].idxmax()
                    st.write(f"**{c}:** lớn nhất {numeric.loc[idxmax,c]:,.2f} vào {lookup.loc[idxmax,COL_DATE]:%d/%m/%Y}")
elif section == "💾 Kho dữ liệu":
    st.subheader("💾 Lưu và tra cứu dữ liệu lâu dài")
    st.info("Kho trực tuyến dùng Supabase. Tải Excel lên trước, sau đó bấm lưu. Trùng ngày sẽ cập nhật theo dữ liệu Excel mới.")
    if check_access():
        if source == "Dữ liệu mẫu":
            st.warning("Không cho lưu dữ liệu mẫu vào kho. Hãy chọn Tải Excel theo ngày.")
        elif source == "Tải Excel theo ngày" and uploaded is None:
            st.warning("Bạn chưa tải file Excel.")
        elif source == "Tải Excel theo ngày":
            st.write(f"Chuẩn bị lưu **{len(daily):,} ngày** từ Excel.")
            confirm = st.checkbox("Tôi xác nhận đây là số liệu cần lưu/cập nhật", key="confirm_db")
            if st.button("💾 Lưu dữ liệu lên kho",type="primary",disabled=not confirm):
                try:
                    save_db(daily)
                    st.success(f"Đã lưu/cập nhật {len(daily):,} ngày lên Supabase.")
                except Exception as exc:
                    st.error(f"Không lưu được: {exc}")
        else:
            st.success(f"Đang đọc {len(daily):,} ngày từ kho dữ liệu.")
            st.dataframe(daily.tail(20),use_container_width=True,hide_index=True)
    st.caption("Không công khai mật khẩu hoặc service role key. Dữ liệu lưu trong Supabase, không phụ thuộc máy quán net.")
elif section == "📅 Quan trắc hằng ngày":
    st.subheader("📅 Diễn biến Q, H và lượng mưa theo ngày")
    show_daily_chart()
    st.dataframe(filtered, use_container_width=True, hide_index=True)
elif section == "📋 Nhập số liệu":
    st.subheader("📋 Nhập và kiểm tra dữ liệu ngày")
    st.info("File Excel cần có 4 cột: Ngày, Q (m³/s), H (m), Mưa (mm). Chọn 'Tải Excel theo ngày' ở thanh bên trái để cập nhật.")
    st.dataframe(daily, use_container_width=True, hide_index=True)
    st.caption("Bạn có thể bổ sung ngày mới vào file Excel gốc và tải lại. Để lưu lâu dài, vào mục Kho dữ liệu và cấu hình Supabase.")
elif section == "📊 Thống kê năm":
    st.subheader(f"📊 {aggregation} — {metric_name}")
    st.dataframe(annual, use_container_width=True, hide_index=True)
    if len(annual):
        st.bar_chart(annual.set_index("Năm")["Giá trị năm"], color="#1479d4")
    st.caption("Giá trị năm được tổng hợp từ toàn bộ dữ liệu Excel, không phụ thuộc bộ lọc ngày của biểu đồ.")
    st.warning("Năm thiếu nhiều ngày có thể làm sai lệch cực trị hoặc tổng lượng mưa. Hãy kiểm tra độ đầy đủ dữ liệu trước khi tính thiết kế.")
elif section == "📈 Đường tần suất P-III":
    st.subheader(f"📈 Tần suất P-III — {metric_name}")
    show_freq_chart("frequency_page")
    show_design()
elif section == "📘 Bảng Φp":
    st.subheader("📘 Bảng Φp – Kp – giá trị thiết kế")
    st.warning("Φp tính theo mô hình Gamma/P-III, chưa phải bảng tra được đối chiếu với tiêu chuẩn hoặc tài liệu Việt Nam.")
    show_design()
    if valid_piii:
        p_custom=st.number_input("Tần suất vượt P (%)", min_value=.01, max_value=99.99, value=1., step=.1)
        a,b,c=st.columns(3)
        a.metric("Φp", f"{float(phi(p_custom)):.4f}")
        b.metric("Kp", f"{float(kp(p_custom)):.4f}")
        c.metric(f"Giá trị thiết kế ({metric_unit})", f"{float(qp(p_custom)):,.2f}")
elif section == "📥 Xuất kết quả":
    st.subheader("📥 Tải dữ liệu và bảng kết quả")
    show_export()
    show_freq_chart("export_freq")
    st.caption("Để lưu hình PNG, bấm biểu tượng máy ảnh trên biểu đồ Plotly.")
else:
    st.subheader("❔ Hướng dẫn sử dụng")
    st.markdown("1. Chuẩn bị Excel gồm **Ngày, Q (m³/s), H (m), Mưa (mm)**.\n2. Ở thanh bên trái chọn **Tải Excel theo ngày** và tải file lên.\n3. Chọn chỉ tiêu Q/H/Mưa và cách tổng hợp theo năm.\n4. Xem **Quan trắc hằng ngày**, **Thống kê năm**, **Đường tần suất P-III**.\n5. Điều chỉnh Cv/Cs, xuất Excel hoặc PNG.\n6. Khi có số liệu ngày mới, **thêm vào file Excel gốc rồi tải lại**.")
    st.warning("Không dùng chuỗi dữ liệu ngày như các mẫu độc lập cho tần suất cực trị năm. Phân tích thiết kế cần chuỗi đủ dài, đầy đủ và được kiểm định.")
st.divider()
st.caption("VINH TRAN APP • THỦY VĂN P-III 4.1.2 • Số liệu mẫu để thử nghiệm; kết quả không thay thế thẩm định kỹ thuật.")
