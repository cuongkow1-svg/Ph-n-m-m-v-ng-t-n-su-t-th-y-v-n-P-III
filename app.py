import io
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scipy.stats import gamma, norm

st.set_page_config(page_title='Thủy văn P-III | Phân tích tần suất', page_icon='🌊', layout='wide')
st.markdown('''<style>
.block-container {padding-top:1.4rem;max-width:1500px}
h1,h2,h3 {color:#124a80}
[data-testid="stMetric"] {background:#eef5fb;padding:12px;border-radius:12px}
</style>''', unsafe_allow_html=True)
st.title('🌊 PHẦN MỀM PHÂN TÍCH TẦN SUẤT THỦY VĂN')
st.caption('Phiên bản 2.0 • Pearson III (P-III) • Giao diện tiếng Việt')

with st.sidebar:
    st.header('⚙️ Thiết lập')
    source = st.radio('Nguồn dữ liệu', ['Dữ liệu mẫu', 'Nhập trực tiếp', 'Tải Excel'])
    unit = st.text_input('Đơn vị đo', 'm³/s')
    if source == 'Tải Excel':
        uploaded = st.file_uploader('Chọn Excel (.xlsx)', type=['xlsx'])
    elif source == 'Nhập trực tiếp':
        manual = st.text_area('Nhập mỗi giá trị một dòng (hoặc cách nhau bằng dấu ;)', '850\n920\n1050\n1100\n1250\n1320\n1400\n1550\n1680\n1750\n1900\n2100\n2300\n2600\n2950', height=220)

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
    st.subheader('Tham số đường P-III')
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
fig.add_trace(go.Scatter(x=prob_x(p_line), y=q_line, mode='lines', name='Đường lý luận P-III', line=dict(color='#d32f2f',width=3), customdata=p_line, hovertemplate='P=%{customdata:.2f}%<br>Q=%{y:.2f}<extra></extra>'))
fig.add_trace(go.Scatter(x=prob_x(emp_p), y=emp_q, mode='markers', name='Điểm kinh nghiệm', marker=dict(color='#1876d2',size=9), customdata=emp_p, hovertemplate='P=%{customdata:.2f}%<br>Quan trắc=%{y:.2f}<extra></extra>'))
ticks=np.array([.1,.2,.5,1,2,5,10,20,50,75,90,95,99])
fig.update_layout(height=540,template='plotly_white',xaxis=dict(title='Tần suất vượt P (%) — trục xác suất chuẩn',tickmode='array',tickvals=prob_x(ticks),ticktext=[f'{x:g}' for x in ticks],autorange='reversed'),yaxis_title=f'Giá trị ({unit})',legend=dict(orientation='h',y=1.1),margin=dict(l=20,r=20,t=45,b=30))

pages=st.tabs(['🏠 Tổng quan','📋 Số liệu','📈 Biểu đồ','📘 Bảng Φp','📥 Xuất kết quả'])
with pages[0]:
    a,b,c,d=st.columns(4)
    a.metric('Số giá trị',len(values));b.metric(f'Trung bình ({unit})',f'{mean:,.2f}');c.metric('Cv',f'{cv:.3f}');d.metric('Cs',f'{cs:.3f}')
    st.plotly_chart(fig,use_container_width=True)
    st.caption('Trục P dùng phép biến đổi xác suất chuẩn. Đường P-III được tính từ phân phối Gamma; không phải bản số hóa giấy xác suất chuyên ngành.')
with pages[1]:
    st.subheader('Bảng tần suất kinh nghiệm')
    st.dataframe(emp,use_container_width=True,hide_index=True)
    st.caption('Công thức vị trí vẽ: P = m/(n+1) × 100%. Dùng cho chuỗi cực đại năm.')
with pages[2]:
    st.subheader('Đường tần suất kinh nghiệm và lý luận')
    st.plotly_chart(fig,use_container_width=True,key="bieu_do_tan_suat_chinh")
    st.caption('Lưu hình PNG bằng biểu tượng máy ảnh trên thanh công cụ biểu đồ (nếu trình duyệt hỗ trợ).')
with pages[3]:
    st.subheader('Bảng Φp – Kp – giá trị thiết kế')
    st.warning('Bảng Φp ở đây tính theo Gamma/P-III, CHƯA phải bảng tra in trong tài liệu Việt Nam. Cần đối chiếu trước khi dùng cho hồ sơ thiết kế.')
    st.dataframe(design.style.format(precision=4),use_container_width=True,hide_index=True)
    p_custom=st.number_input('Tra P bất kỳ (%)',min_value=.01,max_value=99.99,value=1.0,step=.1)
    x,y,z=st.columns(3)
    x.metric('Φp',f'{float(phi(p_custom)):.4f}');y.metric('Kp',f'{float(kp(p_custom)):.4f}');z.metric(f'Qp ({unit})',f'{float(qp(p_custom)):,.2f}')
    if np.any(kp(p_design)<=0):
        st.error('Một số Kp ≤ 0: tham số hiện tại không phù hợp để mô tả đại lượng dương ở các tần suất này.')
with pages[4]:
    st.subheader('Xuất bảng tính')
    buf=io.BytesIO()
    with pd.ExcelWriter(buf,engine='xlsxwriter') as writer:
        emp.to_excel(writer,sheet_name='Tan suat kinh nghiem',index=False)
        design.to_excel(writer,sheet_name='Gia tri thiet ke',index=False)
        pd.DataFrame({'Thong so':['So gia tri','Trung binh','Cv','Cs','Don vi'],'Gia tri':[len(values),mean,cv,cs,unit]}).to_excel(writer,sheet_name='Thong so',index=False)
    st.download_button('📥 Tải Excel kết quả',buf.getvalue(),file_name='ket_qua_tan_suat_PIII.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    st.plotly_chart(fig,use_container_width=True)
    st.caption('Tải hình biểu đồ bằng nút máy ảnh trên biểu đồ.')

st.divider()
st.caption('⚠️ Công cụ tham khảo. Chưa kiểm định bảng tra Việt Nam, cách ước lượng tham số và quy chuẩn thiết kế; không dùng trực tiếp để phê duyệt công trình.')
