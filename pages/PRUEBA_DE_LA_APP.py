import streamlit as st
import pandas as pd
import random
from datetime import datetime
import pytz

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema V&T", layout="wide")

# --- 2. CSS DE MÁXIMA COMPACTACIÓN (FORZADO) ---
st.markdown("""
    <style>
    /* 1. ELIMINAR BOTONES +/- Y ESPACIOS */
    div[data-testid="stNumberInput"] button { display: none !important; }
    div[data-testid="stNumberInput"] div[data-baseweb="input"] { padding-right: 0px !important; }
    input::-webkit-outer-spin-button, input::-webkit-inner-spin-button { -webkit-appearance: none !important; margin: 0 !important; }
    input[type=number] { -moz-appearance: textfield !important; }

    /* 2. RECTITUD TOTAL */
    * { border-radius: 0px !important; }

    /* 3. ACHICAR RECUADRO DE ENTRADA (Ancho y Alto) */
    .stNumberInput { 
        width: 100px !important; /* Menos ancho */
        margin: 0px !important; 
        padding: 0px !important; 
    }
    input {
        height: 22px !important; /* Menos alto */
        border: 1px solid #000 !important;
        font-family: monospace !important;
        font-size: 0.9rem !important;
        text-align: center !important;
        padding: 0px !important;
    }

    /* 4. PEGAR FILAS AL MÁXIMO */
    [data-testid="column"] {
        display: flex;
        align-items: center;
        height: 24px !important; /* Altura de fila ultra corta */
        padding: 0px 2px !important;
    }
    [data-testid="stVerticalBlock"] > div {
        gap: 0px !important;
        padding: 0px !important;
    }

    /* 5. ENCABEZADOS Y TEXTO PLANO */
    .mod-header {
        background-color: #444;
        color: #fff;
        font-size: 0.7rem;
        padding: 1px 10px;
        margin-top: 8px;
    }
    .txt-flat {
        font-size: 0.85rem;
        font-family: monospace;
        margin: 0;
        white-space: nowrap;
    }
    .txt-prod { color: #cc0000; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 3. CONFIGURACIÓN DE TIEMPO ---
tz = pytz.timezone('America/Lima')
ahora = datetime.now(tz)
fecha_hoy = ahora.strftime("%d/%m/%Y")

# --- 4. INICIALIZACIÓN DE DATOS ---
if 'form_data' not in st.session_state:
    st.session_state.form_data = [
        {"id": f"D-{i:02d}", "producto": random.choice(["90", "95", "DL"]),
         "inicio": random.randint(100000, 500000)} for i in range(1, 23)
    ]
    for item in st.session_state.form_data:
        item["final"] = item["inicio"]

if 'gastos' not in st.session_state: st.session_state.gastos = []
if 'vales' not in st.session_state: st.session_state.vales = []

PRECIOS = {"90": 14.0, "95": 15.0, "DL": 15.0}

# --- 5. ENCABEZADO ---
st.markdown(f"**V&T | {fecha_hoy}**")

# --- 6. PESTAÑAS ---
tab1, tab2, tab3, tab4 = st.tabs(["VENTAS", "GASTOS", "VALES", "SALDO"])

with tab1:
    venta_bruta_acumulada = 0

    def render_fila_ultra_compacta(idx):
        global venta_bruta_acumulada
        item = st.session_state.form_data[idx]
        
        # Grid: ID | PROD | INICIO | INPUT | GALONES
        c1, c2, c3, c4, c5 = st.columns([0.2, 0.3, 0.8, 0.8, 0.6])
        
        with c1: st.markdown(f'<p class="txt-flat"><b>{item["id"]}</b></p>', unsafe_allow_html=True)
        with c2: st.markdown(f'<p class="txt-flat txt-prod">{item["producto"]}</p>', unsafe_allow_html=True)
        with c3: st.markdown(f'<p class="txt-flat" style="color:#666">{item["inicio"]:09d}</p>', unsafe_allow_html=True)
        with c4:
            nuevo_final = st.number_input(
                label=f"f_{idx}", 
                value=int(item['final']), 
                min_value=int(item['inicio']), 
                step=1, 
                key=f"in_{idx}", 
                label_visibility="collapsed"
            )
        
        item['final'] = nuevo_final
        galones = item["final"] - item["inicio"]
        subtotal = galones * PRECIOS[item["producto"]]
        venta_bruta_acumulada += subtotal
        
        with c5:
            if galones > 0:
                st.markdown(f'<p class="txt-flat" style="color:blue">+{galones:,.2f}</p>', unsafe_allow_html=True)

    # --- LISTA MONÓTONA ---
    st.markdown('<div class="mod-header">M1</div>', unsafe_allow_html=True)
    for i in range(0, 8): render_fila_ultra_compacta(i)

    st.markdown('<div class="mod-header">M2</div>', unsafe_allow_html=True)
    for i in range(8, 16): render_fila_ultra_compacta(i)

    st.markdown('<div class="mod-header">M3</div>', unsafe_allow_html=True)
    for i in range(16, 22): render_fila_ultra_compacta(i)

    st.divider()
    st.write(f"Total: S/ {venta_bruta_acumulada:,.2f}")

# --- PESTAÑAS SECUNDARIAS ---
with tab2:
    st.subheader("Gastos")
    with st.form("g", clear_on_submit=True):
        c1, c2 = st.columns([2,1])
        d = c1.text_input("Gasto")
        m = c2.number_input("Monto", min_value=0.0)
        if st.form_submit_button("Añadir"):
            if d: st.session_state.gastos.append({"D": d, "M": m}); st.rerun()
    if st.session_state.gastos: st.table(st.session_state.gastos)

with tab4:
    total_g = sum(g["M"] for g in st.session_state.gastos)
    total_v = sum(v["M"] for v in st.session_state.vales)
    neto = venta_bruta_acumulada - total_g - total_v
    st.markdown(f"<h3 style='border:1px solid #000; padding:5px;'>NETO: S/ {neto:,.2f}</h3>", unsafe_allow_html=True)
