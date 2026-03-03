import streamlit as st
import pandas as pd
import random
from datetime import datetime
import pytz

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema V&T", layout="wide")

# --- 2. CSS PARA FILAS MONÓTONAS, RECTAS Y PEGADAS ---
st.markdown("""
    <style>
    /* 1. ELIMINAR BOTONES +/- Y ESPACIOS LATERALES FORZADO */
    div[data-testid="stNumberInput"] button { display: none !important; }
    div[data-testid="stNumberInput"] div[data-baseweb="input"] { padding-right: 0px !important; }
    input::-webkit-outer-spin-button, input::-webkit-inner-spin-button { -webkit-appearance: none !important; margin: 0 !important; }
    input[type=number] { -moz-appearance: textfield !important; }

    /* 2. RECTITUD Y CERO REDONDEO */
    * { border-radius: 0px !important; }

    /* 3. FILAS DE TAMAÑO ÚNICO Y MONÓTONO */
    [data-testid="column"] {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 32px !important; /* Altura fija para toda la fila */
        padding: 0px 2px !important;
    }
    
    /* 4. ELIMINAR ESPACIO ENTRE LÍNEAS (GAP CERO) */
    [data-testid="stVerticalBlock"] > div {
        gap: 0px !important;
        padding: 0px !important;
    }

    /* 5. INPUTS CUADRADOS E IGUALES */
    input {
        height: 26px !important;
        border: 1px solid #000 !important;
        font-family: monospace !important;
        font-size: 1rem !important;
        text-align: center !important;
        width: 100% !important;
    }

    /* 6. ENCABEZADOS PLANOS */
    .mod-header {
        background-color: #222;
        color: #fff;
        font-size: 0.75rem;
        padding: 2px 10px;
        margin-top: 5px;
        text-align: left;
        width: 100%;
    }

    /* 7. TEXTO PLANO */
    .txt-flat {
        font-size: 0.9rem;
        font-family: monospace;
        margin: 0;
        padding: 0;
        white-space: nowrap;
    }
    .txt-prod { color: #cc0000; font-weight: bold; }
    
    /* Ajuste para que el number_input no genere margen superior */
    .stNumberInput { margin: 0px !important; padding: 0px !important; width: 100% !important; }
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
st.markdown(f"**V&T | REGISTRO DIARIO | {fecha_hoy}**")

# --- 6. PESTAÑAS ---
tab1, tab2, tab3, tab4 = st.tabs(["VENTAS", "GASTOS", "VALES", "SALDO"])

with tab1:
    venta_bruta_acumulada = 0

    def render_fila_recta(idx):
        global venta_bruta_acumulada
        item = st.session_state.form_data[idx]
        
        # Grid: ID | PROD | INICIO | INPUT | GALONES
        c1, c2, c3, c4, c5 = st.columns([0.3, 0.4, 1.0, 1.2, 0.8])
        
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
            valor_gl = f"{galones:,.2f}" if galones > 0 else "0.00"
            st.markdown(f'<p class="txt-flat" style="color:blue">{valor_gl}</p>', unsafe_allow_html=True)

    # --- MÓDULOS EN FILAS MONÓTONAS ---
    st.markdown('<div class="mod-header">MODULO 01 (01-08)</div>', unsafe_allow_html=True)
    for i in range(0, 8): render_fila_recta(i)

    st.markdown('<div class="mod-header">MODULO 02 (09-16)</div>', unsafe_allow_html=True)
    for i in range(8, 16): render_fila_recta(i)

    st.markdown('<div class="mod-header">MODULO 03 (17-22)</div>', unsafe_allow_html=True)
    for i in range(16, 22): render_fila_recta(i)

    st.divider()
    st.markdown(f"**VENTA TOTAL: S/ {venta_bruta_acumulada:,.2f}**")

# --- OTRAS PESTAÑAS ---
with tab2:
    st.subheader("Gastos")
    with st.form("g", clear_on_submit=True):
        c1, c2 = st.columns([2,1])
        d = c1.text_input("Gasto")
        m = c2.number_input("Monto", min_value=0.0)
        if st.form_submit_button("Añadir"):
            if d: st.session_state.gastos.append({"D": d, "M": m}); st.rerun()
    if st.session_state.gastos: st.table(st.session_state.gastos)

with tab3:
    st.subheader("Vales")
    with st.form("v", clear_on_submit=True):
        c1, c2 = st.columns([2,1])
        cl = c1.text_input("Cliente")
        v = c2.number_input("S/", min_value=0.0)
        if st.form_submit_button("Añadir"):
            if cl: st.session_state.vales.append({"C": cl, "M": v}); st.rerun()
    if st.session_state.vales: st.table(st.session_state.vales)

with tab4:
    total_g = sum(g["M"] for g in st.session_state.gastos)
    total_v = sum(v["M"] for v in st.session_state.vales)
    neto = venta_bruta_acumulada - total_g - total_v
    st.markdown(f"<h2 style='border:2px solid #000; padding:10px;'>NETO: S/ {neto:,.2f}</h2>", unsafe_allow_html=True)
