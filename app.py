import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components
import gdown
import os
from datetime import datetime
import pytz

# ==========================================
# 1. KONFIGURASI HALAMAN & CSS
# ==========================================
st.set_page_config(
    page_title="KPI Dashboard 2026",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .stApp { background-color: #121212; color: #EAEAEA; }
    .stTextInput input {
        background-color: #2C2C3E; color: white; text-align: center; 
        font-size: 1.5rem; letter-spacing: 3px; border: 1px solid #555; border-radius: 10px;
    }
    .stButton button { width: 100%; border-radius: 10px; font-weight: bold; background-color: #00E676; color: black; border: none; }
    div.metric-card {
        background-color: #2C2C3E; padding: 15px; border-radius: 15px;
        border: 1px solid #3E3E5E; text-align: center; margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3); height: 100%; display: flex; flex-direction: column; justify-content: center;
    }
    .small-text { font-size: 0.75rem; color: #AAA; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 1px; }
    .big-text { font-size: 2.2rem; font-weight: bold; margin: 0; color: white; }
    .leaderboard-container { height: 150px; overflow-y: auto; padding-right: 5px; scroll-behavior: smooth; }
    .leaderboard-row { font-size: 0.75rem; padding: 6px 10px; border-radius: 5px; margin-bottom: 4px; display: flex; justify-content: space-between; align-items: center; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. LOGIKA MAPPING
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

# ==========================================
# 3. LOAD DATA (DARI GOOGLE DRIVE)
# ==========================================
@st.cache_data(ttl=300)
def load_data():
    file_id = '1QzrAMTpCvRjBjjACY9kSLD4_U44zKaFO' 
    url = f'https://drive.google.com/uc?id={file_id}'
    output = 'data_kpi.csv'
    try:
        # Perbaikan utama: hapus fuzzy=True agar jalan di Python terbaru
        gdown.download(url, output, quiet=True) 
        df = pd.read_csv(output)
        
        # Bersihkan data
        df['KODE_ID'] = df['NAMA UNIT'].astype(str).str.split(':').str[0].str.strip()
        cols_num = ['ACH BULANAN', 'ACH TAHUNAN', 'KPI BULANAN', 'KPI TAHUNAN', 'BOBOT', 'TARGET BULANAN', 'TARGET TAHUNAN', 'REALISASI']
        for col in cols_num:
            if col in df.columns: 
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        df['KATEGORI_RANK'] = df['KATEGORI UNIT'].apply(lambda x: 'GABUNGAN CP & CPS' if x in ['CP', 'CPS'] else ('GABUNGAN GADAI & REG' if x in ['GADAI', 'REGULAR'] else x))
        df['SECTION_PDF'] = df['KODE KPI'].apply(assign_section)
        
        tz = pytz.timezone('Asia/Jakarta')
        tgl_str = datetime.fromtimestamp(os.path.getmtime(output), tz).strftime("%d %b %Y, %H:%M")
        return df, tgl_str
    except Exception as e:
        return None, str(e)

df, tgl_update = load_data()

# ==========================================
# 4. PROTEKSI & LOGIN
# ==========================================
if df is None:
    st.error(f"❌ DATABASE TIDAK TERHUBUNG: {tgl_update}")
    st.info("Pastikan internet stabil atau ID Google Drive benar.")
    st.stop()

if 'status_login' not in st.session_state:
    st.session_state.status_login = False

if not st.session_state.status_login:
    st.markdown("<br><br><h1 style='text-align: center;'>🔐 AKSES KPI 2026</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        kode_input = st.text_input("Kode Unit", max_chars=5, label_visibility="collapsed", placeholder="Contoh: 00709")
        if st.button("LOGIN SISTEM", type="primary"):
            hasil = df[df['KODE_ID'] == kode_input.strip()]
            if not hasil.empty:
                st.session_state.temp_nama = hasil.iloc[0]['NAMA UNIT']
                st.session_state.temp_kategori_list = hasil['KATEGORI UNIT'].unique()
                st.session_state.temp_kode = kode_input.strip()
            else:
                st.error("🚫 Kode Unit tidak ditemukan!")

    if 'temp_kode' in st.session_state:
        st.info(f"Unit: **{st.session_state.temp_nama}**")
        pilihan = st.radio("Pilih Jenis Laporan:", st.session_state.temp_kategori_list, horizontal=True)
        if st.button("MASUK DASHBOARD"):
            st.session_state.user_nama = st.session_state.temp_nama
            st.session_state.user_kategori = pilihan
            st.session_state.user_kategori_rank = df[(df['NAMA UNIT'] == st.session_state.user_nama) & (df['KATEGORI UNIT'] == pilihan)]['KATEGORI_RANK'].iloc[0]
            st.session_state.status_login = True
            st.rerun()

# ==========================================
# 5. DASHBOARD UTAMA
# ==========================================
else:
    # Header Info
    st.markdown(f"<p style='text-align: center; color: #888; font-size: 0.8rem; margin-top: 10px;'>Pembaruan Data: {tgl_update} WIB</p>", unsafe_allow_html=True)
    
    nama = st.session_state.user_nama
    kategori = st.session_state.user_kategori
    df_user = df[(df['NAMA UNIT'] == nama) & (df['KATEGORI UNIT'] == kategori)].copy()

    # Sidebar
    with st.sidebar:
        st.title("👤 Profil")
        st.write(f"**Unit:** {nama}")
        st.write(f"**Tipe:** {kategori}")
        st.divider()
        if st.button("🚪 Logout"):
            st.session_state.status_login = False
            st.rerun()

    # UI Atas
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 20px;">
        <h1 style="color: white; font-size: 1.8rem; font-weight: 800; margin: 0;">{nama}</h1>
        <div style="display: inline-block; background-color: #00E676; color: black; padding: 2px 15px; border-radius: 15px; margin-top: 10px; font-weight: bold; font-size: 0.8rem;">{kategori}</div>
    </div>
    """, unsafe_allow_html=True)

    periode = st.radio("Pilih Periode Analisis:", ["BULANAN", "TAHUNAN"], horizontal=True)
    col_score = 'KPI BULANAN' if periode == "BULANAN" else 'KPI TAHUNAN'
    col_ach = 'ACH BULANAN' if periode == "BULANAN" else 'ACH TAHUNAN'

    # Metrik Utama
    total_skor = df_user[col_score].sum()
    st.markdown(f"""
        <div class='metric-card'>
            <p class='small-text'>TOTAL SKOR {periode}</p>
            <h1 class='big-text' style='color:#00E676;'>{total_skor:.2f}</h1>
        </div>
    """, unsafe_allow_html=True)

    # List KPI per Section
    sections = ["1. Outstanding Loan", "2. Laba Usaha", "3. Efisiensi (CIR)", "4. Nasabah", "5. Kualitas Kredit"]
    for sec in sections:
        df_sec = df_user[df_user['SECTION_PDF'] == sec]
        if not df_sec.empty:
            with st.expander(f"📂 {sec}", expanded=True):
                for _, row in df_sec.iterrows():
                    ach_val = row[col_ach] * 100
                    st.write(f"**{row['KODE KPI']}**")
                    st.progress(min(ach_val/100, 1.0))
                    st.caption(f"Pencapaian: {ach_val:.1f}% | Realisasi: {row['REALISASI']:,.0f}")