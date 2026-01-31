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
# 2. LOGIKA MAPPING SECTION
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
@st.cache_data(ttl=600)
def load_data():
    file_id = '1QzrAMTpCvRjBjjACY9kSLD4_U44zKaFO' 
    url = f'https://drive.google.com/uc?id={file_id}'
    output = 'data_kpi.csv'

    try:
        gdown.download(url, output, quiet=True, fuzzy=True)
        df = pd.read_csv(output)
        
        mod_time = os.path.getmtime(output)
        tz = pytz.timezone('Asia/Jakarta')
        tgl_str = datetime.fromtimestamp(mod_time, tz).strftime("%d %b %Y, %H:%M")
    except Exception as e:
        return None, str(e)
    
    df['KODE_ID'] = df['NAMA UNIT'].astype(str).str.split(':').str[0]
    cols_num = ['ACH BULANAN', 'ACH TAHUNAN', 'KPI BULANAN', 'KPI TAHUNAN', 'BOBOT', 'TARGET BULANAN', 'TARGET TAHUNAN', 'REALISASI']
    for col in cols_num:
        if col in df.columns: df[col] = df[col].fillna(0)
            
    df['KATEGORI_RANK'] = df['KATEGORI UNIT'].apply(lambda x: 'GABUNGAN CP & CPS' if x in ['CP', 'CPS'] else ('GABUNGAN GADAI & REG' if x in ['GADAI', 'REGULAR'] else x))
    df['SECTION_PDF'] = df['KODE KPI'].apply(assign_section)
    
    return df, tgl_str

df, tgl_update = load_data()

# ==========================================
# 4. SESSION & LOGIN
# ==========================================
if 'status_login' not in st.session_state: st.session_state.status_login = False

def format_pilihan_login(opsi):
    if opsi in ['CP', 'CPS']: return "CABANG KONSOLIDASI"
    elif opsi in ['REGULAR']: return "OUTLET (REGULAR)"
    elif opsi in ['GADAI']: return "OUTLET (GADAI)"
    else: return opsi

if not st.session_state.status_login:
    st.markdown("<br><br><h1 style='text-align: center;'>🔐 KPI ACCESS 2026</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        kode_input = st.text_input("Kode Unit", max_chars=5, label_visibility="collapsed", placeholder="10xxx")
        if st.button("LOGIN SYSTEM", type="primary"):
            hasil = df[df['KODE_ID'] == kode_input]
            if hasil.empty: st.error("🚫 Kode Unit tidak ditemukan!")
            else:
                st.session_state.temp_kode, st.session_state.temp_nama = kode_input, hasil.iloc[0]['NAMA UNIT']
                st.session_state.temp_kategori_list = hasil['KATEGORI UNIT'].unique()
                st.rerun()

    if 'temp_kode' in st.session_state:
        st.info(f"Unit: **{st.session_state.temp_nama}**")
        pilihan = st.radio("Pilih Jenis Laporan:", st.session_state.temp_kategori_list, horizontal=True, format_func=format_pilihan_login)
        if st.button("MASUK DASHBOARD"):
            st.session_state.user_nama, st.session_state.user_kategori = st.session_state.temp_nama, pilihan
            st.session_state.user_kategori_rank = df[(df['NAMA UNIT'] == st.session_state.temp_nama) & (df['KATEGORI UNIT'] == pilihan)]['KATEGORI_RANK'].iloc[0]
            st.session_state.status_login = True
            st.rerun()

# ==========================================
# 5. DASHBOARD UTAMA
# ==========================================
else:
    st.markdown(f"<p style='text-align: center; color: #888; font-size: 0.8rem; margin-bottom: -10px;'>Terakhir diperbarui: {tgl_update} WIB</p>", unsafe_allow_html=True)
    
    nama, kategori, kat_rank = st.session_state.user_nama, st.session_state.user_kategori, st.session_state.user_kategori_rank
    df_user = df[(df['NAMA UNIT'] == nama) & (df['KATEGORI UNIT'] == kategori)].copy()

    with st.sidebar:
        st.title("User Profile")
        if st.button("Logout"):
            st.session_state.status_login = False
            st.rerun()

    badge_color = "#6A1B9A" if kategori == 'AREA' else ("#C62828" if kategori == 'KANWIL' else ("#2962FF" if kategori in ['CP', 'CPS'] else "#00C853"))
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 30px;">
        <h3 style="color: #FFD700; margin-bottom: 5px; font-weight: normal; letter-spacing: 2px;">MONITORING KPI 2026</h3>
        <h1 style="color: white; font-size: 2.2rem; font-weight: 800; margin: 0; text-shadow: 0px 0px 10px rgba(255,255,255,0.2);">{nama}</h1>
        <div style="display: inline-block; background-color: {badge_color}; color: white; padding: 5px 20px; border-radius: 20px; margin-top: 15px; font-weight: bold; font-size: 0.9rem; letter-spacing: 1.5px;">{kategori}</div>
    </div>
    """, unsafe_allow_html=True)

    periode = st.radio("", ["BULANAN", "TAHUNAN"], horizontal=True, label_visibility="collapsed")
    col_ach, col_score, col_target = ('ACH BULANAN', 'KPI BULANAN', 'TARGET BULANAN') if periode == "BULANAN" else ('ACH TAHUNAN', 'KPI TAHUNAN', 'TARGET TAHUNAN')
    label_total = f"TOTAL SCORE ({'BLN' if periode == 'BULANAN' else 'THN'})"

    # Leaderboard Logic
    base_score = df_user[col_score].sum()
    rank_df = df[df['KATEGORI_RANK'] == kat_rank].groupby('NAMA UNIT')[col_score].sum().sort_values(ascending=False).reset_index()
    try: my_rank = rank_df[rank_df['NAMA UNIT'] == nama].index[0] + 1
    except: my_rank = "-"

    leaderboard_html = "<div class='leaderboard-container'>"
    for idx, row in rank_df.iterrows():
        is_me = row['NAMA UNIT'] == nama
        bg, txt, rid = ("#00E676", "black", "id='my-rank'") if is_me else ("#3E3E5E", "#AAA", "")
        leaderboard_html += f"<div class='leaderboard-row' {rid} style='background-color:{bg}; color:{txt}; font-weight:{'bold' if is_me else 'normal'};'><span style='width:25px;'>#{idx+1}</span><span style='flex-grow:1; margin-left:5px;'>{row['NAMA UNIT'].split(':')[-1][:18]}</span><span style='text-align:right;'>{row[col_score]:.2f}</span></div>"
    leaderboard_html += "</div>"
    
    components.html(f"<script>setTimeout(() => {{ var target = window.parent.document.getElementById('my-rank'); if (target) target.scrollIntoView({{behavior: 'smooth', block: 'center'}}); }}, 1000);</script>", height=0)

    c1, c2 = st.columns(2)
    with c1: st.markdown(f"<div class='metric-card'><p class='small-text'>{label_total}</p><h1 class='big-text' style='color:#4FC3F7;'>{base_score:.2f}</h1></div>", unsafe_allow_html=True)
    with c2: st.markdown(f"<div class='metric-card' style='padding:10px; border:1px solid #00E676; display:block;'><p class='small-text' style='margin-bottom:5px; font-weight:bold; color:white;'>RANK #{my_rank}</p>{leaderboard_html}</div>", unsafe_allow_html=True)

    # Plot Function
    def plot_kpi_chart(df_data, title_text):
        st.subheader(title_text)
        df_plot = df_data.sort_values(by='KODE KPI', ascending=False).reset_index(drop=True)
        df_plot['ACH_PERSEN'] = df_plot[col_ach] * 100
        df_plot['VISUAL_BAR'] = df_plot['ACH_PERSEN'].apply(lambda x: 120 if x > 120 else x)
        
        fig = go.Figure()
        for i, row in df_plot.iterrows():
            color = "#66BB6A" if row['ACH_PERSEN'] >= 100 else ("#FFEE58" if row['ACH_PERSEN'] > 90 else "#EF5350")
            txt_val = f"{row['REALISASI']:,.0f}" if 'npl' not in row['KODE KPI'].lower() else f"{row['REALISASI']:.2f}%"
            
            fig.add_trace(go.Bar(y=[i], x=[100], orientation='h', marker_color='rgba(255,255,255,0.1)', hoverinfo='none', width=0.45))
            fig.add_trace(go.Bar(y=[i], x=[row['VISUAL_BAR']], orientation='h', text=f"  {txt_val}", textposition='inside' if row['VISUAL_BAR'] > 20 else 'outside', marker_color=color, width=0.45))
            fig.add_annotation(x=0, y=i, text=f"<b>{row['KODE KPI']}</b> <span style='color:{color}'>({row['ACH_PERSEN']:.1f}%)</span>", showarrow=False, xanchor="left", yanchor="bottom", yshift=22, font=dict(color="white", size=12))
            fig.add_trace(go.Scatter(x=[145], y=[i], text=f"T: {row[col_target]:,.0f}", mode="text", textposition="middle right", textfont=dict(color="#AAA", size=13), hoverinfo='none'))
            fig.add_shape(type="line", x0=100, y0=i-0.4, x1=100, y1=i+0.4, line=dict(color="white", width=1, dash="dot"))

        fig.update_layout(barmode='overlay', plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', showlegend=False, height=50+(len(df_plot)*65), margin=dict(l=0,r=0,t=20,b=0), xaxis=dict(range=[0, 250], showticklabels=False, showgrid=False), yaxis=dict(showticklabels=False))
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False, 'staticPlot': True})

    ordered_sections = ["1. Outstanding Loan", "2. Laba Usaha", "3. Efisiensi (CIR)", "4. Nasabah", "5. Kualitas Kredit", "6. Revamp Brand", "7. Gold Ecosystem", "8. Pegadaian Digital (Tring!)", "9. Sinergi Holding UMi", "10. KPI Stretch Goal (Cicil Emas)"]
    df_active = df_user[(df_user['BOBOT'] > 0) | (df_user['KODE KPI'].str.contains('CICIL EMAS', case=False))].copy()
    
    for section in ordered_sections:
        df_sec = df_active[df_active['SECTION_PDF'] == section]
        if not df_sec.empty:
            plot_kpi_chart(df_sec, section)
            st.markdown("---")