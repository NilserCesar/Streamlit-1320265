import streamlit as st
import pandas as pd
import random
from datetime import datetime
import pytz

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema V&T", layout="wide")

# --- 2. CSS PARA INPUT INVISIBLE (SOLO NÚMEROS FLOTANTES) ---
st.markdown("""
    <style>
    /* ELIMINAR BOTONES Y CONTENEDORES DE STREAMLIT */
    div[data-testid="stNumberInput"] button { display: none !important; }
    
    /* Quitar bordes, fondos y sombras de todos los contenedores padres */
    div[data-testid="stNumberInput"], 
    div[data-testid="stNumberInput"] > div, 
    div[data-testid="stNumberInput"] div[data-baseweb="input"],
    div[data-testid="stNumberInput"] div[data-baseweb="base-input"] {
        border: none !important;
        background-color: transparent !important;
        box-shadow: none !important;
        padding: 0px !important;
        outline: none !important;
    }

    /* ESTILO FINAL DEL INPUT: TOTALMENTE LIMPIO */
    input {
        border: none !important;
        background-color: transparent !important;
        box-shadow: none !important;
        outline: none !important;
        height: 20px !important;
        width: 100% !important;
        font-family: monospace !important;
        font-size: 1rem !important;
        text-align: center !important;
        color: #000 !important;
        margin: 0px !important;
        padding: 0px !important;
    }

    /* Evitar que aparezca cualquier borde al hacer clic (focus) */
    input:focus {
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
        background-color: #f0f0f0 !important; /* Un toque gris muy tenue al escribir para orientarse */
    }

    /* COMPACTACIÓN DE FILAS */
    [data-testid="column"] {
        display: flex !important;
        align-items: center !important;
        height: 22px !important; 
        padding: 0px 2px !important;
    }

    [data-testid="stVerticalBlock"] > div {
        gap: 0px !important;
        padding: 0px !important;
    }

    .txt-flat {
        font-size: 0.9rem;
        font-family: monospace;
        margin: 0px !important;
    }
    .txt-prod { color: #cc0000; font-weight: bold; }

    .mod-header {
        border-bottom: 1px solid #ddd;
        color: #666;
        font-size: 0.7rem;
        margin-top: 10px;
        text-transform: uppercase;
    }
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

PRECIOS = {"90": 14.0, "95": 15.0, "DL": 15.0}

# --- 5. ENCABEZADO ---
st.markdown(f"**V&T | {fecha_hoy}**")

# --- 6. PESTAÑAS ---
tab1, tab2, tab3 = st.tabs(["VENTAS", "GASTOS", "CIERRE"])

with tab1:
    venta_bruta_acumulada = 0

    def render_fila_invisible(idx):
        global venta_bruta_acumulada
        item = st.session_state.form_data[idx]
        
        # Columnas: ID | PROD | INICIO | INPUT (FINAL) | DIFERENCIA
        c1, c2, c3, c4, c5 = st.columns([0.2, 0.3, 0.7, 0.8, 0.5])
        
        with c1: st.markdown(f'<p class="txt-flat"><b>{item["id"]}</b></p>', unsafe_allow_html=True)
        with c2: st.markdown(f'<p class="txt-flat txt-prod">{item["producto"]}</p>', unsafe_allow_html=True)
        with c3: st.markdown(f'<p class="txt-flat" style="color:#666">{item["inicio"]:09d}</p>', unsafe_allow_html=True)
        with c4:
            nuevo_final = st.number_input(
                label=f"f_{idx}", 
                value=int(item['final']), 
                step=1, 
                key=f"in_{idx}", 
                label_visibility="collapsed"
            )
        
        item['final'] = nuevo_final
        galones = item["final"] - item["inicio"]
        venta_bruta_acumulada += (galones * PRECIOS[item["producto"]])
        
        with c5:
            if galones > 0:
                st.markdown(f'<p class="txt-flat" style="color:blue">+{galones:,.2f}</p>', unsafe_allow_html=True)
            else:
                st.markdown('<p class="txt-flat" style="color:#eee">0.00</p>', unsafe_allow_html=True)

    # --- LISTA LIMPIA ---
    st.markdown('<div class="mod-header">Modulo 01</div>', unsafe_allow_html=True)
    for i in range(0, 8): render_fila_invisible(i)

    st.markdown('<div class="mod-header">Modulo 02</div>', unsafe_allow_html=True)
    for i in range(8, 16): render_fila_invisible(i)

    st.markdown('<div class="mod-header">Modulo 03</div>', unsafe_allow_html=True)
    for i in range(16, 22): render_fila_invisible(i)

    st.divider()
    st.write(f"**Venta Bruta: S/ {venta_bruta_acumulada:,.2f}**")

# Pestañas adicionales minimizadas
with tab2:
    if 'gastos' not in st.session_state: st.session_state.gastos = []
    with st.form("g"):
        d = st.text_input("Gasto")
        m = st.number_input("S/")
        if st.form_submit_button("Guardar"):
            st.session_state.gastos.append({"D":d, "M":m}); st.rerun()

with tab3:
    total_g = sum(g["M"] for g in st.session_state.gastos)
    st.header(f"Total Neto: S/ {venta_bruta_acumulada - total_g:,.2f}")
