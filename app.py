import io
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy.stats import gamma, norm

st.set_page_config(page_title="THỦY VĂN P-III | HydroStat Pro", page_icon="🌊", layout="wide", initial_sidebar_state="expanded")
st.markdown("""<style>
:root {--navy:#0c3158;--blue:#0e72ce}
[data-testid="stAppViewContainer"] {background:#f2f6fb}
[data-testid="stSidebar"] {background:linear-gradient(160deg,#092c50,#124b7d 68%,#09243d)}
[data-testid="stSidebar"] * {color:#f5faff!important}
[data-testid="stSidebar"] div[data-baseweb="select"] * {color:#102d49!important}
[data-testid="stSidebar"] input {color:#142e48!important}
[data-testid="stSidebar"] textarea {color:#142e48!important}
.block-container {max-width:1550px;padding-top:1.0rem;padding-bottom:2rem}
h1,h2,h3 {color:#0b3d70!important;letter-spacing:-.02em}
div[data-testid="stMetric"] {background:#fff;border:1px solid #dce8f5;border-radius:14px;padding:13px 16px;box-shadow:0 3px 13px #133d6610}
div[data-testid="stMetricLabel"] {color:#5b7187}
div[data-testid="stMetricValue"] {color:#123f6b}
div[data-testid="stVerticalBlockBorderWrapper"] > div {border-radius:16px!important}
.stButton>button[kind="primary"], .stDownloadButton>button[kind="primary"] {background:#0878d7;border-radius:9px}
[data-testid="stDataFrame"] {border-radius:10px;overflow:hidden}
.hero {padding:24px 28px;border-radius:18px;color:white;background:linear-gradient(105deg,#082947,#145b91 70%,#2a8aca);margin-bottom:18px;box-shadow:0 8px 24px #15467522}
.hero h1 {color:white!important;margin:0;font-size:2.05rem}
.hero .brand {font-size:1.0rem;font-weight:800;letter-spacing:.24em;color:#a7e5ff;margin-bottom:9px;text-transform:uppercase}
.hero p {color:#d4eafb;margin:6px 0 0}
.section {font-size:1.12rem;font-weight:750;color:#0d457a;margin:12px 0}
.note {color:#60768d;font-size:.87rem}
</style>""",unsafe_allow_html=True)
st.markdown('<div class="hero"><div class="brand">VINH TRAN APP</div><h1>🌊 THỦY VĂN P-III <span style="font-size:15px;background:#ffffff24;padding:5px 10px;border-radius:15px">PRO 3.0</span></h1><p>PHÂN TÍCH TẦN SUẤT THỦY VĂN • PEARSON III • BẢNG TÍNH THIẾT KẾ</p></div>',unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🌊 VINH TRAN APP")
    st.caption("Phần mềm phân tích tần suất thủy văn")
    section=st.radio("DANH MỤC",["🏠 Tổng quan","📋 Nhập số liệu","📊 Phân tích thống kê","📈 Đường tần suất P-III","📘 Bảng tra Φp","📥 Xuất kết quả","❔ Hướng dẫn"],label_visibility="collapsed")
    st.divider()
    st.markdown("### ⚙️ THIẾT LẬP")
    project=st.text_input("Tên dự án","Công trình thủy văn")
    location=st.text_input("Vị trí","")
    source=st.radio("Nguồn dữ liệu",["Dữ liệu mẫu","Nhập trực tiếp","Tải Excel"])
    unit=st.text_input("Đơn vị","m³/s")
    if source=="Tải Excel":
        uploaded=st.file_uploader("Tải file Excel (.xlsx)",type=["xlsx"])
    elif source=="Nhập trực tiếp":
        manual=st.text_area("Mỗi giá trị một dòng", "850\\n920\\n1050\\n1100\\n1250\\n1320\\n1400\\n1550\\n1680\\n1750\\n1900\\n2100\\n2300\\n2600\\n2950".replace("\\n","\n"),height=150)
sample = np.array([850,920,1050,1100,1250,1320,1400,1550,1680,1750,1900,2100,2300,2600,2950], dtype=float)
values = sample.copy()
if source == 'Nhập trực tiếp':
    try:
        values = np.array([float(x.strip().replace(',', '.')) for x in manual.replace(';','\n').splitlines() if x.strip()], dtype=float)
    except ValueError:
        st.error('Số liệu nhập chưa đúng. Mỗi dòng cần là một số.'); st.stop()
elif source == 'Tải Excel':
    if uploaded is None:
        st.info('Hãy tải Excel để thay thế dữ liệu mẫu.')
    else:
        try:
            incoming = pd.read_excel(uploaded)
        except Exception as e:
            st.error(f'Không đọc được Excel: {e}'); st.stop()
        options = list(incoming.columns)
        if not options:
            st.error('File Excel không có cột dữ liệu.'); st.stop()
        col = st.selectbox('Chọn cột chứa giá trị thủy văn', options)
        values = pd.to_numeric(incoming[col], errors='coerce').dropna().to_numpy(dtype=float)

if len(values) < 3 or not np.all(np.isfinite(values)) or np.any(values <= 0):
    st.error('Cần ít nhất 3 giá trị dương, hữu hạn.'); st.stop()
mean = float(values.mean())
cv_est = float(values.std(ddof=1)/mean)
with st.sidebar:
    st.divider()
    st.subheader('Hiệu chỉnh P-III')
    cv = st.number_input('Cv', min_value=0.01, max_value=3.0, value=float(np.clip(cv_est, .01, 3)), step=.01, format='%.3f')
    cs = st.number_input('Cs (dương)', min_value=.01, max_value=6., value=float(np.clip(2*cv, .01, 6)), step=.01, format='%.3f')
    st.caption('Giá trị khởi tạo Cs = 2Cv chỉ là giả định ban đầu; có thể hiệu chỉnh.')

# Phi_p is the standardized gamma upper-tail quantile, not a digitized Vietnamese table.
def phi(p):
    a = 4.0/(cs**2)
    return (gamma.isf(np.asarray(p, dtype=float)/100.0, a=a)-a)/np.sqrt(a)
def kp(p):
    return 1.0+cv*phi(p)
def qp(p):
    return mean*kp(p)

ranks = np.arange(1,len(values)+1)
emp_p = ranks/(len(values)+1)*100
emp_q = np.sort(values)[::-1]
emp = pd.DataFrame({'Thứ hạng':ranks, 'Giá trị':emp_q, 'P kinh nghiệm (%)':emp_p})
p_design = np.array([.1,.2,.5,1,2,5,10,20,50,75,90,95,99])
design = pd.DataFrame({'P (%)':p_design, 'Φp':phi(p_design), 'Kp':kp(p_design), f'Qp ({unit})':qp(p_design)})

# Standard normal probability-paper coordinate: ticks are nonuniform in P.
def prob_x(p):
    return norm.ppf(1-np.asarray(p)/100)
p_line = np.linspace(.05,99.95,1000)
q_line = qp(p_line)
fig = go.Figure()
fig.add_trace(go.Scatter(x=prob_x(p_line), y=q_line, mode='lines', name='Đường lý luận P-III', line=dict(color='#ed3545',width=3.2), customdata=p_line, hovertemplate='P=%{customdata:.2f}%<br>Q=%{y:.2f}<extra></extra>'))
fig.add_trace(go.Scatter(x=prob_x(emp_p), y=emp_q, mode='markers', name='Điểm kinh nghiệm', marker=dict(color='#1479d4',size=9,line=dict(color='white',width=1)), customdata=emp_p, hovertemplate='P=%{customdata:.2f}%<br>Quan trắc=%{y:.2f}<extra></extra>'))
ticks=np.array([.1,.2,.5,1,2,5,10,20,50,75,90,95,99])
fig.update_layout(height=480,template='plotly_white',xaxis=dict(title='Tần suất vượt P (%) — trục xác suất chuẩn',tickmode='array',tickvals=prob_x(ticks),ticktext=[f'{x:g}' for x in ticks],autorange='reversed'),yaxis_title=f'Giá trị ({unit})',legend=dict(orientation='h',y=1.1),margin=dict(l=12,r=12,t=45,b=30),paper_bgcolor='white',plot_bgcolor='white',font=dict(color='#34516c'))



def show_chart(key):
    st.plotly_chart(fig, use_container_width=True, key=key, config={"displaylogo":False,"toImageButtonOptions":{"format":"png","filename":"duong_tan_suat_PIII","scale":2}})

def show_design():
    st.dataframe(design.style.format(precision=3),use_container_width=True,hide_index=True)

def show_emp():
    st.dataframe(emp.style.format(precision=2),use_container_width=True,hide_index=True)

def show_export():
    buf=io.BytesIO()
    with pd.ExcelWriter(buf,engine="xlsxwriter") as writer:
        emp.to_excel(writer,sheet_name="Tan suat kinh nghiem",index=False)
        design.to_excel(writer,sheet_name="Gia tri thiet ke",index=False)
        pd.DataFrame({"Thong so":["Du an","Vi tri","So gia tri","Trung binh","Cv","Cs","Don vi"],"Gia tri":[project,location,len(values),mean,cv,cs,unit]}).to_excel(writer,sheet_name="Thong so",index=False)
    st.download_button("📥 Xuất Excel (.xlsx)",buf.getvalue(),file_name="ThuyVan_PIII_ket_qua.xlsx",mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",type="primary",use_container_width=True)

if section=="🏠 Tổng quan":
    st.markdown('<div class="section">📋 TỔNG QUAN DỰ ÁN</div>',unsafe_allow_html=True)
    st.caption(f"**Dự án:** {project}　 | 　**Vị trí:** {location or 'Chưa nhập'}　 | 　**Đơn vị:** {unit}")
    a,b,c,d=st.columns(4)
    a.metric("Số năm / giá trị",len(values))
    b.metric(f"Trung bình ({unit})",f"{mean:,.2f}")
    c.metric("Hệ số Cv",f"{cv:.3f}")
    d.metric("Hệ số Cs",f"{cs:.3f}")
    with st.container(border=True):
        st.markdown('<div class="section">📈 ĐƯỜNG TẦN SUẤT PEARSON III</div>',unsafe_allow_html=True)
        show_chart("overview_chart")
    l,r=st.columns(2,gap="medium")
    with l:
        with st.container(border=True):
            st.markdown('<div class="section">📘 BẢNG KẾT QUẢ TẦN SUẤT</div>',unsafe_allow_html=True)
            show_design()
    with r:
        with st.container(border=True):
            st.markdown('<div class="section">📋 BẢNG SỐ LIỆU THỦY VĂN</div>',unsafe_allow_html=True)
            show_emp()
    x,y,z=st.columns([1.1,1.1,1])
    with x:
        with st.container(border=True):
            st.markdown('<div class="section">🎯 GIÁ TRỊ THIẾT KẾ</div>',unsafe_allow_html=True)
            p_choice=st.selectbox("Tần suất vượt P (%)",[.1,.2,.5,1,2,5,10,20,50],index=3)
            st.metric(f"Qp ({unit})",f"{float(qp(p_choice)):,.2f}")
    with y:
        with st.container(border=True):
            st.markdown('<div class="section">🧮 CÔNG THỨC TÍNH</div>',unsafe_allow_html=True)
            st.latex(r"Q_p=\\overline{Q}(1+C_v\\Phi_p)")
            st.caption("Φp được tính theo phân phối Gamma/P-III.")
    with z:
        with st.container(border=True):
            st.markdown('<div class="section">📥 XUẤT KẾT QUẢ</div>',unsafe_allow_html=True)
            show_export()
            st.caption("Tải PNG qua biểu tượng máy ảnh trên biểu đồ.")
elif section=="📋 Nhập số liệu":
    st.subheader("📋 Nhập và kiểm tra số liệu")
    st.info("Chọn nguồn dữ liệu ở thanh menu bên trái. Dữ liệu mẫu chỉ phục vụ thử nghiệm.")
    show_emp()
elif section=="📊 Phân tích thống kê":
    st.subheader("📊 Các thông số thống kê")
    a,b,c,d=st.columns(4)
    a.metric("Số giá trị",len(values));b.metric("Trung bình",f"{mean:,.3f}");c.metric("Cv mẫu",f"{cv_est:.4f}");d.metric("Cs hiệu chỉnh",f"{cs:.4f}")
    st.write("Cv, Cs sử dụng cho đường lý luận có thể chỉnh ở thanh bên trái. Cs mặc định = 2Cv chỉ là giả định ban đầu.")
    show_emp()
elif section=="📈 Đường tần suất P-III":
    st.subheader("📈 Đường tần suất kinh nghiệm và lý luận")
    show_chart("frequency_chart")
    st.caption("Trục P dùng biến đổi xác suất chuẩn; chưa phải bản số hóa giấy xác suất chuyên ngành Việt Nam.")
elif section=="📘 Bảng tra Φp":
    st.subheader("📘 Bảng Φp – Kp – Qp")
    st.warning("Φp tính theo Gamma/P-III, KHÔNG phải bảng tra đã kiểm định từ tài liệu Việt Nam. Cần đối chiếu trước khi dùng trong hồ sơ thiết kế.")
    show_design()
    p_custom=st.number_input("Tra tần suất vượt P bất kỳ (%)",min_value=.01,max_value=99.99,value=1.0,step=.1)
    a,b,c=st.columns(3)
    a.metric("Φp",f"{float(phi(p_custom)):.4f}")
    b.metric("Kp",f"{float(kp(p_custom)):.4f}")
    c.metric(f"Qp ({unit})",f"{float(qp(p_custom)):,.2f}")
    if np.any(kp(p_design)<=0):
        st.error("Một số Kp ≤ 0: bộ thông số hiện tại không phù hợp với đại lượng dương ở những tần suất đó.")
elif section=="📥 Xuất kết quả":
    st.subheader("📥 Xuất kết quả")
    show_export()
    st.caption("Xuất hình PNG: nhấn biểu tượng máy ảnh trên biểu đồ.")
    show_chart("export_chart")
else:
    st.subheader("❔ Hướng dẫn nhanh")
    st.markdown("1. Chọn **Dữ liệu mẫu**, **Nhập trực tiếp** hoặc **Tải Excel** ở thanh bên trái.\n2. Kiểm tra đơn vị và số liệu.\n3. Điều chỉnh **Cv**, **Cs**.\n4. Xem đường tần suất, bảng Φp và giá trị Qp.\n5. Xuất bảng Excel hoặc ảnh biểu đồ.")
    st.warning("Công cụ tham khảo, chưa được kiểm định theo quy chuẩn thiết kế và bảng tra Việt Nam.")

st.divider()
st.caption("HYDROSTAT PRO 3.0 • Phân phối P-III qua Gamma • Số liệu mẫu không dùng cho thiết kế chính thức. Không dùng kết quả để phê duyệt công trình khi chưa được kiểm chứng.")
