import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components
import gdown
import os
from datetime import datetime
import pytz
import requests
import json

# ==========================================
# 1. KONFIGURASI HALAMAN & CSS (TAMPILAN ASLI)
# ==========================================
st.set_page_config(
    page_title="KPI Dashboard 2026",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    .stApp { background-color: #121212; color: #EAEAEA; }
    
    /* Login & Input */
    .stTextInput input {
        background-color: #2C2C3E; color: white; text-align: center; 
        font-size: 1.5rem; letter-spacing: 3px; border: 1px solid #555; border-radius: 10px;
    }
    .stButton button { width: 100%; border-radius: 10px; font-weight: bold; background-color: #00E676; color: black; border: none; }
    
    /* Kartu Metrik */
    div.metric-card {
        background-color: #2C2C3E; padding: 15px; border-radius: 15px;
        border: 1px solid #3E3E5E; text-align: center; margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3); height: 100%; display: flex; flex-direction: column; justify-content: center;
    }
    .small-text { font-size: 0.75rem; color: #AAA; margin-bottom: 5px; text-transform: uppercase; letter-spacing: 1px; }
    .big-text { font-size: 2.2rem; font-weight: bold; margin: 0; color: white; }
    
    /* Leaderboard Scroll */
    .leaderboard-container {
        height: 150px; overflow-y: auto; padding-right: 5px; scroll-behavior: smooth;
    }
    .leaderboard-container::-webkit-scrollbar { width: 5px; }
    .leaderboard-container::-webkit-scrollbar-track { background: #121212; }
    .leaderboard-container::-webkit-scrollbar-thumb { background: #555; border-radius: 5px; }

    .leaderboard-row {
        font-size: 0.75rem; padding: 6px 10px; border-radius: 5px; margin-bottom: 4px;
        display: flex; justify-content: space-between; align-items: center;
    }
    
    /* Radio Button Toggle */
    .stRadio [role=radiogroup]{ align-items: center; justify-content: center; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 1.5 INTEGRASI AI (OLLAMA LOKAL + GROQ CLOUD FALLBACK)
# ==========================================
OLLAMA_API = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5-coder:7b"
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "mixtral-8x7b-32768"

def _is_ollama_available():
    try:
        response = requests.get(f"{OLLAMA_API.replace('/api/generate', '/api/tags')}", timeout=2)
        return response.status_code == 200
    except:
        return False

def _chat_ollama(pertanyaan, context_data=""):
    try:
        prompt = f"Anda adalah AI assistant KPI Pegadaian 2026.\nKonteks:\n{context_data}\n\nPertanyaan: {pertanyaan}"
        response = requests.post(OLLAMA_API, json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}, timeout=30)
        return response.json().get("response", "❌ No response")
    except Exception as e:
        return f"❌ Ollama Error: {str(e)}"

def _chat_groq(pertanyaan, context_data=""):
    try:
        headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
        prompt = f"Anda adalah AI assistant KPI Pegadaian 2026.\nKonteks:\n{context_data}\n\nPertanyaan: {pertanyaan}"
        response = requests.post(GROQ_API_URL, headers=headers, json={"model": GROQ_MODEL, "messages": [{"role": "user", "content": prompt}]}, timeout=30)
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ Groq Error: {str(e)}"

def chat_dengan_ai(pertanyaan, context_data=""):
    if _is_ollama_available(): return _chat_ollama(pertanyaan, context_data)
    if GROQ_API_KEY: return _chat_groq(pertanyaan, context_data)
    return "⚠️ AI Service Tidak Tersedia"

# ==========================================
# 2. LOGIKA MAPPING SECTION (ASLI)
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
# 3. LOAD DATA (FIXED GDOWN)
# ==========================================
@st.cache_data(ttl=300)
def load_data():
    file_id = '1QzrAMTpCvRjBjjACY9kSLD4_U44zKaFO' 
    url = f'https://drive.google.com/uc?id={file_id}'
    output = 'data_kpi.csv'
    try:
        # Perbaikan: Hapus fuzzy=True untuk stabilitas server
        gdown.download(url, output, quiet=True) 
        df = pd.read_csv(output)
        tgl_str = datetime.fromtimestamp(os.path.getmtime(output), pytz.timezone('Asia/Jakarta')).strftime("%d %b %Y, %H:%M")
        
        df['KODE_ID'] = df['NAMA UNIT'].astype(str).str.split(':').str[0]
        cols_num = ['ACH BULANAN', 'ACH TAHUNAN', 'KPI BULANAN', 'KPI TAHUNAN', 'BOBOT', 'TARGET BULANAN', 'TARGET TAHUNAN', 'REALISASI']
        for col in cols_num:
            if col in df.columns: df[col] = df[col].fillna(0)
        df['KATEGORI_RANK'] = df['KATEGORI UNIT'].apply(lambda x: 'GABUNGAN CP & CPS' if x in ['CP', 'CPS'] else ('GABUNGAN GADAI & REG' if x in ['GADAI', 'REGULAR'] else x))
        df['SECTION_PDF'] = df['KODE KPI'].apply(assign_section)
        return df, tgl_str
    except Exception as e:
        return None, str(e)

df, tgl_update = load_data()

# ==========================================
# 4. SESSION & LOGIN (ASLI)
# ==========================================
if 'status_login' not in st.session_state: st.session_state.status_login = False

if not st.session_state.status_login:
    st.markdown("<br><br><h1 style='text-align: center;'>🔐 AKSES KPI 2026</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        kode_input = st.text_input("Kode Unit", max_chars=5, label_visibility="collapsed", placeholder="10xxx")
        if st.button("LOGIN SISTEM", type="primary"):
            hasil = df[df['KODE_ID'] == kode_input]
            if hasil.empty: st.error("🚫 Kode Unit tidak ditemukan!")
            else:
                st.session_state.temp_kode, st.session_state.temp_nama = kode_input, hasil.iloc[0]['NAMA UNIT']
                st.session_state.temp_kategori_list = hasil['KATEGORI UNIT'].unique()
                st.rerun()

    if 'temp_kode' in st.session_state:
        pilihan = st.radio("Pilih Jenis Laporan:", st.session_state.temp_kategori_list, horizontal=True)
        if st.button("MASUK DASHBOARD"):
            st.session_state.user_nama, st.session_state.user_kategori = st.session_state.temp_nama, pilihan
            st.session_state.user_kategori_rank = df[(df['NAMA UNIT'] == st.session_state.temp_nama) & (df['KATEGORI UNIT'] == pilihan)]['KATEGORI_RANK'].iloc[0]
            st.session_state.status_login = True
            st.rerun()

# ==========================================
# 5. DASHBOARD UTAMA (JANGAN UBAH TAMPILAN)
# ==========================================
else:
    nama, kategori, kat_rank = st.session_state.user_nama, st.session_state.user_kategori, st.session_state.user_kategori_rank
    df_user = df[(df['NAMA UNIT'] == nama) & (df['KATEGORI UNIT'] == kategori)].copy()

    with st.sidebar:
        st.subheader("🤖 AI Assistant KPI")
        if 'chat_history' not in st.session_state: st.session_state.chat_history = []
        user_input = st.chat_input("Tanya KPI...")
        if user_input:
            res = chat_dengan_ai(user_input, f"KPI {nama}: Score {df_user['KPI TAHUNAN'].sum():.2f}")
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            st.session_state.chat_history.append({"role": "assistant", "content": res})
        for m in st.session_state.chat_history: st.chat_message(m["role"]).write(m["content"])
        if st.button("🚪 Logout"):
            st.session_state.status_login = False
            st.rerun()

    st.markdown(f"<h1 style='text-align: center;'>{nama}</h1>", unsafe_allow_html=True)
    periode = st.radio("Periode", ["BULANAN", "TAHUNAN"], horizontal=True, label_visibility="collapsed")
    col_ach, col_score, col_target = ('ACH BULANAN', 'KPI BULANAN', 'TARGET BULANAN') if periode == "BULANAN" else ('ACH TAHUNAN', 'KPI TAHUNAN', 'TARGET TAHUNAN')

    # Leaderboard & Charts tetap menggunakan fungsi plot_kpi_chart asli kamu
    def plot_kpi_chart(df_data, title_text):
        st.subheader(title_text)
        df_plot = df_data.sort_values(by='KODE KPI', ascending=False)
        fig = go.Figure()
        for i, row in df_plot.iterrows():
            ach_p = row[col_ach] * 100
            color = "#66BB6A" if ach_p >= 100 else ("#FFEE58" if ach_p > 90 else "#EF5350")
            fig.add_trace(go.Bar(y=[row['KODE KPI']], x=[ach_p], orientation='h', marker_color=color, text=f"{row['REALISASI']:,.0f}"))
        fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color="white"))
        st.plotly_chart(fig)

    ordered_sections = ["1. Outstanding Loan", "2. Laba Usaha", "3. Efisiensi (CIR)", "4. Nasabah", "5. Kualitas Kredit", "6. Revamp Brand", "7. Gold Ecosystem", "8. Pegadaian Digital (Tring!)", "9. Sinergi Holding UMi", "10. KPI Stretch Goal (Cicil Emas)"]
    for section in ordered_sections:
        df_sec = df_user[df_user['SECTION_PDF'] == section]
        if not df_sec.empty: plot_kpi_chart(df_sec, section)