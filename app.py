
import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import gamma
import plotly.graph_objects as go
from io import BytesIO

# ==================================
# 1. CAU HINH GIAO DIEN
# ==================================

st.set_page_config(
    page_title="Phan mem tan suat thuy van",
    page_icon="🌊",
    layout="wide"
)

st.title("🌊 PHẦN MỀM TẦN SUẤT THỦY VĂN")
st.subheader("Phân tích tần suất Pearson III (P-III)")

st.info(
    "Nhập số liệu thủy văn để tính toán "
    "và vẽ đường tần suất."
)

# ==================================
# 2. NHAP SO LIEU
# ==================================

st.sidebar.header("1. NHẬP SỐ LIỆU")

uploaded_file = st.sidebar.file_uploader(
    "Tải file Excel",
    type=["xlsx"]
)

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    st.subheader("Bảng số liệu đầu vào")
    st.dataframe(df, use_container_width=True)

    numeric_cols = df.select_dtypes(
        include="number"
    ).columns.tolist()

    if not numeric_cols:
        st.error("Excel không có cột số liệu dạng số.")
        st.stop()

    selected_col = st.selectbox(
        "Chọn cột số liệu thủy văn",
        numeric_cols
    )

    values = pd.to_numeric(
        df[selected_col],
        errors="coerce"
    ).dropna().to_numpy(dtype=float)

else:
    st.warning(
        "Chưa tải Excel. Đang sử dụng số liệu mẫu."
    )

    values = np.array([
        850, 920, 1050, 1100, 1250,
        1320, 1400, 1550, 1680, 1750,
        1900, 2100, 2300, 2600, 2950
    ], dtype=float)

if (
    len(values) < 3
    or not np.all(np.isfinite(values))
    or np.any(values <= 0)
):
    st.error(
        "Cần ít nhất 3 số liệu dương và hợp lệ."
    )
    st.stop()

# ==================================
# 3. TINH THONG SO THONG KE
# ==================================

n = len(values)
mean = np.mean(values)
std = np.std(values, ddof=1)
cv_sample = std / mean

st.sidebar.header("2. THÔNG SỐ P-III")

cv = st.sidebar.number_input(
    "Hệ số biến thiên Cv",
    min_value=0.01,
    max_value=3.0,
    value=float(np.clip(cv_sample, 0.01, 3.0)),
    step=0.01
)

cs = st.sidebar.number_input(
    "Hệ số thiên lệch Cs",
    min_value=0.01,
    max_value=6.0,
    value=float(np.clip(2 * cv, 0.01, 6.0)),
    step=0.01
)

# ==================================
# 4. HAM TINH PHI P VA QP
# ==================================

def calculate_phi(p, cs_value):
    shape = 4.0 / (cs_value ** 2)

    phi = (
        gamma.ppf(
            1 - np.asarray(p) / 100,
            a=shape
        ) - shape
    ) / np.sqrt(shape)

    return phi


def calculate_q(p):
    phi = calculate_phi(p, cs)
    kp = 1 + cv * phi
    return mean * kp


# ==================================
# 5. HIEN THI THONG SO
# ==================================

st.subheader("Thông số thống kê")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Số năm quan trắc", n)
col2.metric("Giá trị trung bình", f"{mean:,.2f}")
col3.metric("Cv", f"{cv:.3f}")
col4.metric("Cs", f"{cs:.3f}")

# ==================================
# 6. TAN SUAT KINH NGHIEM
# ==================================

sorted_values = np.sort(values)[::-1]

rank = np.arange(1, n + 1)

p_empirical = rank / (n + 1) * 100

empirical_df = pd.DataFrame({
    "Thứ hạng": rank,
    "Giá trị quan trắc": sorted_values,
    "Tần suất P (%)": p_empirical
})

# ==================================
# 7. VE DUONG TAN SUAT
# ==================================

st.subheader("📈 ĐƯỜNG TẦN SUẤT THỦY VĂN")

p_curve = np.linspace(0.1, 99.9, 500)
q_curve = calculate_q(p_curve)

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=p_curve,
        y=q_curve,
        mode="lines",
        name="Đường lý luận P-III",
        line=dict(
            color="red",
            width=3
        )
    )
)

fig.add_trace(
    go.Scatter(
        x=p_empirical,
        y=sorted_values,
        mode="markers",
        name="Tần suất kinh nghiệm",
        marker=dict(
            color="blue",
            size=9
        )
    )
)

fig.update_layout(
    title="Biểu đồ đường tần suất",
    xaxis_title="Tần suất P (%)",
    yaxis_title="Giá trị thủy văn",
    height=550,
    hovermode="closest"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.caption(
    "Trục P hiện chia tuyến tính. "
    "Phiên bản nâng cấp sẽ có giấy xác suất "
    "thủy văn chuyên dụng."
)

# ==================================
# 8. BANG TAN SUAT KINH NGHIEM
# ==================================

st.subheader("📋 BẢNG TẦN SUẤT KINH NGHIỆM")

st.dataframe(
    empirical_df,
    use_container_width=True
)

# ==================================
# 9. BANG TRA PHI P
# ==================================

st.subheader("📘 BẢNG Φp - Kp - Qp")

p_values = np.array([
    0.1, 0.2, 0.5, 1, 2,
    5, 10, 20, 50, 75,
    90, 95, 99
])

phi_values = calculate_phi(
    p_values,
    cs
)

kp_values = 1 + cv * phi_values

qp_values = mean * kp_values

result_df = pd.DataFrame({
    "P (%)": p_values,
    "Φp": phi_values,
    "Kp": kp_values,
    "Qp thiết kế": qp_values
})

st.dataframe(
    result_df.style.format({
        "Φp": "{:.4f}",
        "Kp": "{:.4f}",
        "Qp thiết kế": "{:.2f}"
    }),
    use_container_width=True
)

# ==================================
# 10. TRA GIA TRI BAT KY
# ==================================

st.subheader("🔎 TRA GIÁ TRỊ THEO TẦN SUẤT")

p_custom = st.number_input(
    "Nhập tần suất P (%)",
    min_value=0.01,
    max_value=99.99,
    value=1.0,
    step=0.1
)

phi_custom = float(
    calculate_phi(p_custom, cs)
)

kp_custom = 1 + cv * phi_custom

q_custom = mean * kp_custom

a, b, c = st.columns(3)

a.metric("Φp", f"{phi_custom:.4f}")
b.metric("Kp", f"{kp_custom:.4f}")
c.metric("Qp thiết kế", f"{q_custom:.2f}")

# ==================================
# 11. XUAT KET QUA EXCEL
# ==================================

st.subheader("📥 XUẤT KẾT QUẢ")

output = BytesIO()

with pd.ExcelWriter(
    output,
    engine="xlsxwriter"
) as writer:

    empirical_df.to_excel(
        writer,
        sheet_name="Tan suat kinh nghiem",
        index=False
    )

    result_df.to_excel(
        writer,
        sheet_name="Gia tri thiet ke",
        index=False
    )

st.download_button(
    label="📥 Tải kết quả Excel",
    data=output.getvalue(),
    file_name="ket_qua_tan_suat_thuy_van.xlsx",
    mime=(
        "application/vnd.openxmlformats-"
        "officedocument.spreadsheetml.sheet"
    )
)

st.divider()

st.caption(
    "Phần mềm thử nghiệm. Giá trị Φp được "
    "tính bằng phân phối Pearson III, "
    "chưa đối chiếu với bảng tra thủy văn "
    "Việt Nam. Cần kiểm định phương pháp "
    "và kết quả trước khi dùng trong thiết kế."
)
