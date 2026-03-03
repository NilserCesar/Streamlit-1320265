import streamlit as st
import pandas as pd
import random
from datetime import datetime
import pytz

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema V&T", layout="wide")

# --- 2. CSS AVANZADO PARA ELIMINAR BOTONES +/- Y COMPACTAR ---
st.markdown("""
    <style>
    /* 1. ELIMINAR BOTONES +/- TOTALMENTE */
    /* Para Chrome, Safari, Edge */
    input::-webkit-outer-spin-button, 
    input::-webkit-inner-spin-button { 
        -webkit-appearance: none !important; 
        margin: 0 !important; 
    }
    /* Para Firefox */
    input[type=number] { 
        -moz-appearance: textfield !important; 
    }

    /* 2. DISEÑO CUADRÁTICO Y SIN ESPACIOS */
    * { border-radius: 0px !important; }

    /* Forzar que el contenedor del input no tenga padding extra */
    div[data-testid="stNumberInput"] div[data-baseweb="input"] {
        padding-right: 0px !important;
    }
    
    /* 3. PEGAR FILAS AL MÁXIMO */
    [data-testid="stVerticalBlock"] > div { 
        gap: 0px !important; 
        padding-top: 0px !important; 
        padding-bottom: 0px !important; 
    }
    [data-testid="column"] { 
        padding: 0px 5px !important; 
    }

    /* 4. ESTILO DEL RECUADRO DE TEXTO */
    input { 
        height: 28px !important; 
        border: 1px solid #333 !important; 
        background-color: #fff !important;
        font-family: 'Courier New', monospace !important;
        font-weight: bold !important;
        text-align: center !important;
    }

    /* 5. ENCABEZADOS DE MÓDULO */
    .mod-header {
        background-color: #000;
        color: #fff;
        padding: 2px 10px;
        font-size: 0.8rem;
        margin-top: 10px;
        margin-bottom: 2px;
    }

    .txt-row { font-size: 0.85rem; }
    .txt-prod { color: #dc3545; font-weight: bold; }
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
st.write(f"### ⛽ V&T | {fecha_hoy}")

# --- 6. PESTAÑAS ---
tab1, tab2, tab3, tab4 = st.tabs(["🛒 VENTAS", "💸 GASTOS", "🎫 VALES", "💰 SALDO"])

with tab1:
    venta_bruta_acumulada = 0

    def render_fila(idx):
        global venta_bruta_acumulada
        item = st.session_state.form_data[idx]
        
        # Grid compacto: ID | PROD | INICIO | INPUT | GALONES
        c1, c2, c3, c4, c5 = st.columns([0.3, 0.4, 1.2, 1.5, 1.0])
        
        with c1: st.markdown(f"**{item['id']}**")
        with c2: st.markdown(f'<span class="txt-prod">{item["producto"]}</span>', unsafe_allow_html=True)
        with c3: st.markdown(f'<span style="color:#666; font-size:0.8rem;">{item["inicio"]:09d}</span>', unsafe_allow_html=True)
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
                st.markdown(f"**{galones:,.2f}**")

    # --- BLOQUES ---
    st.markdown('<div class="mod-header">MÓDULO 1</div>', unsafe_allow_html=True)
    for i in range(0, 8): render_fila(i)

    st.markdown('<div class="mod-header">MÓDULO 2</div>', unsafe_allow_html=True)
    for i in range(8, 16): render_fila(i)

    st.markdown('<div class="mod-header">MÓDULO 3</div>', unsafe_allow_html=True)
    for i in range(16, 22): render_fila(i)

    st.divider()
    st.write(f"**Venta Bruta Total: S/ {venta_bruta_acumulada:,.2f}**")

# --- OTRAS PESTAÑAS (Resumidas) ---
with tab2:
    st.subheader("Gastos")
    with st.form("g", clear_on_submit=True):
        c1, c2 = st.columns([2,1])
        d = c1.text_input("Gasto")
        m = c2.number_input("S/", min_value=0.0, step=1.0, key="g_input", label_visibility="visible")
        if st.form_submit_button("Añadir"):
            if d: st.session_state.gastos.append({"D": d, "M": m}); st.rerun()
    if st.session_state.gastos: st.table(st.session_state.gastos)

with tab3:
    st.subheader("Vales")
    with st.form("v", clear_on_submit=True):
        c1, c2 = st.columns([2,1])
        cl = c1.text_input("Cliente")
        v = c2.number_input("S/", min_value=0.0, step=1.0, key="v_input")
        if st.form_submit_button("Añadir"):
            if cl: st.session_state.vales.append({"C": cl, "M": v}); st.rerun()
    if st.session_state.vales: st.table(st.session_state.vales)

with tab4:
    total_g = sum(g["M"] for g in st.session_state.gastos)
    total_v = sum(v["M"] for v in st.session_state.vales)
    st.success(f"## NETO: S/ {venta_bruta_acumulada - total_g - total_v:,.2f}")
    if st.button("GUARDAR CIERRE", use_container_width=True):
        st.balloons()
