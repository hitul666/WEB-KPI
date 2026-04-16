import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components
import gdown
import os
from datetime import datetime
import pytz

# ==========================================
# 1. KONFIGURASI HALAMAN & CSS ORIGINAL
# ==========================================
st.set_page_config(
    page_title="KPI Dashboard 2026",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Mengembalikan gaya CSS dashboard Cemara yang lama
st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #1a1a2e; }
    .stApp { background-color: #0f0f1b; color: #EAEAEA; }
    .metric-card {
        background: linear-gradient(145deg, #1e1e30, #252540);
        padding: 20px; border-radius: 15px;
        border: 1px solid #3e3e5e; text-align: center;
        box-shadow: 5px 5px 15px rgba(0,0,0,0.5);
    }
    .stProgress > div > div > div > div { background-color: #00E676; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. LOGIKA MAPPING & DATA
# ==========================================
def assign_section(kode_kpi):
    mapping = {
        'A.AVG GADAI': "1. Outstanding Loan", 'B.AVG NON GADAI': "1. Outstanding Loan",
        'C.AVG EMAS': "1. Outstanding Loan", 'D.0SL GROSS': "1. Outstanding Loan",
        'E.LABA': "2. Laba Usaha", 'F. CIR': "3. Efisiensi (CIR)",
        'G. NSBH BARU': "4. Nasabah", 'H. NSBH BARU AGEN': "4. Nasabah",
        'I. NSBH TAHUNAN': "4. Nasabah", 'J. NSBH TE': "4. Nasabah",
        'K. NPL GADAI': "5. Kualitas Kredit", 'L. NPL NON GADAI': "5. Kualitas Kredit",
        'M. NPL EMAS': "5. Kualitas Kredit", 'N. LAR GADAI': "5. Kualitas Kredit",
        'O. LAR NON GADAI': "5. Kualitas Kredit", 'P. LAR EMAS': "5. Kualitas Kredit",
        'Q. BRAND AWARENESS': "6. Revamp Brand",
        'R.DEPOSITO EMAS': "7. Gold Ecosystem", 'S.TABUNGAN EMAS': "7. Gold Ecosystem", 'T. G24': "7. Gold Ecosystem",
        'U. NASABAH TRING': "8. Pegadaian Digital (Tring!)", 'V. OSL TRING': "8. Pegadaian Digital (Tring!)",
        'W. FREX TRING': "8. Pegadaian Digital (Tring!)",
        'X. DISBURS BRI': "9. Sinergi Holding UMi", 'Y. OSL SINERGI HOLDING': "9. Sinergi Holding UMi",
        'Z. TE SINERGI HOLDING': "9. Sinergi Holding UMi",
        'Z1.OSL CICIL EMAS': "10. KPI Stretch Goal (Cicil Emas)" 
    }
    return mapping.get(str(kode_kpi).strip(), "Lainnya")

@st.cache_data(ttl=300)
def load_data():
    file_id = '1QzrAMTpCvRjBjjACY9kSLD4_U44zKaFO' 
    url = f'https://drive.google.com/uc?id={file_id}'
    output = 'data_kpi.csv'
    try:
        # Perbaikan bug 'fuzzy' tanpa mengubah fungsi download
        gdown.download(url, output, quiet=True) 
        df = pd.read_csv(output)
        df['KODE_ID'] = df['NAMA UNIT'].astype(str).str.split(':').str[0].str.strip()
        cols_num = ['ACH BULANAN', 'ACH TAHUNAN', 'KPI BULANAN', 'KPI TAHUNAN', 'BOBOT', 'TARGET BULANAN', 'TARGET TAHUNAN', 'REALISASI']
        for col in cols_num:
            if col in df.columns: df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        df['SECTION_PDF'] = df['KODE KPI'].apply(assign_section)
        tz = pytz.timezone('Asia/Jakarta')
        tgl_str = datetime.fromtimestamp(os.path.getmtime(output), tz).strftime("%d %b %Y, %H:%M")
        return df, tgl_str
    except Exception as e:
        return None, str(e)

df, tgl_update = load_data()

# ==========================================
# 3. LOGIN SISTEM
# ==========================================
if 'status_login' not in st.session_state:
    st.session_state.status_login = False

if not st.session_state.status_login:
    st.markdown("<h1 style='text-align: center; margin-top: 50px;'>🔐 LOGIN CEMARA</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        kode_input = st.text_input("Masukkan Kode Unit", placeholder="Contoh: 00709")
        if st.button("Masuk"):
            hasil = df[df['KODE_ID'] == kode_input.strip()]
            if not hasil.empty:
                st.session_state.user_nama = hasil.iloc[0]['NAMA UNIT']
                st.session_state.user_kategori = hasil['KATEGORI UNIT'].iloc[0]
                st.session_state.status_login = True
                st.rerun()
            else:
                st.error("Kode Unit Salah")
else:
    # ==========================================
    # 4. TAMPILAN DASHBOARD ORIGINAL
    # ==========================================
    # Sidebar Navigation & Filter (Persis versi sebelumnya)
    with st.sidebar:
        st.image("https://upload.wikimedia.org/wikipedia/id/thumb/a/a7/Logo_Pegadaian.svg/1200px-Logo_Pegadaian.svg.png", width=150)
        st.divider()
        st.write(f"👤 **{st.session_state.user_nama}**")
        st.write(f"🏢 Tipe: {st.session_state.user_kategori}")
        st.divider()
        periode = st.selectbox("Pilih Periode", ["BULANAN", "TAHUNAN"])
        if st.button("Keluar"):
            st.session_state.status_login = False
            st.rerun()

    # Layout Utama
    st.title("📊 Cemara Analytics")
    st.caption(f"Terakhir diperbarui: {tgl_update} WIB")

    df_user = df[(df['NAMA UNIT'] == st.session_state.user_nama) & (df['KATEGORI UNIT'] == st.session_state.user_kategori)].copy()
    col_score = 'KPI BULANAN' if periode == "BULANAN" else 'KPI TAHUNAN'
    col_ach = 'ACH BULANAN' if periode == "BULANAN" else 'ACH TAHUNAN'

    # Metrik Atas
    m1, m2 = st.columns(2)
    with m1:
        st.markdown(f"<div class='metric-card'><small>TOTAL SKOR</small><h2>{df_user[col_score].sum():.2f}</h2></div>", unsafe_allow_html=True)
    with m2:
        avg_ach = df_user[col_ach].mean() * 100
        st.markdown(f"<div class='metric-card'><small>RATA-RATA ACH</small><h2>{avg_ach:.1f}%</h2></div>", unsafe_allow_html=True)

    st.write("---")

    # Grouping Berdasarkan 10 Section Utama
    sections = [
        "1. Outstanding Loan", "2. Laba Usaha", "3. Efisiensi (CIR)", 
        "4. Nasabah", "5. Kualitas Kredit", "6. Revamp Brand", 
        "7. Gold Ecosystem", "8. Pegadaian Digital (Tring!)", 
        "9. Sinergi Holding UMi", "10. KPI Stretch Goal (Cicil Emas)"
    ]

    for sec in sections:
        data_sec = df_user[df_user['SECTION_PDF'] == sec]
        if not data_sec.empty:
            st.subheader(sec)
            for _, row in data_sec.iterrows():
                val_ach = row[col_ach]
                c1, c2 = st.columns([3, 1])
                with c1:
                    st.write(f"{row['KODE KPI']}")
                    st.progress(min(float(val_ach), 1.0))
                with c2:
                    st.write(f"**{val_ach*100:.1f}%**")
                    st.caption(f"Target: {row['TARGET '+periode]:,.0f}")
            st.write("")