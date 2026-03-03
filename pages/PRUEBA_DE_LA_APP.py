import streamlit as st
import pandas as pd
import random
from datetime import datetime
import pytz

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema V&T", layout="wide")

# --- 2. CSS DE REINICIO TOTAL (SIN HUECOS, SIN BORDES, SIN ESPACIOS) ---
st.markdown("""
    <style>
    /* 1. ELIMINAR CUALQUIER ELEMENTO ADICIONAL DE STREAMLIT */
    div[data-testid="stNumberInput"] button { display: none !important; }
    
    /* 2. FORZAR AL CONTENEDOR A NO TENER ALTURA EXTRA NI ESPACIOS (HUECOS) */
    div[data-testid="stNumberInput"], 
    div[data-testid="stNumberInput"] > div, 
    div[data-testid="stNumberInput"] div[data-baseweb="input"],
    div[data-testid="stNumberInput"] div[data-baseweb="base-input"] {
        border: none !important;
        background-color: transparent !important;
        box-shadow: none !important;
        padding: 0px !important;
        margin: 0px !important;
        min-height: auto !important;
        height: 20px !important;
    }

    /* 3. EL INPUT COMO UNA LÍNEA PLANA */
    input {
        border: none !important;
        background-color: transparent !important;
        box-shadow: none !important;
        outline: none !important;
        height: 20px !important;
        width: 100% !important;
        font-family: monospace !important;
        font-size: 1rem !important;
        text-align: left !important; /* Alineado a la izquierda para seguir la línea */
        color: #000 !important;
        margin: 0px !important;
        padding: 0px !important;
        appearance: none !important;
    }

    /* 4. PEGAR LAS COLUMNAS QUIRÚRGICAMENTE */
    [data-testid="column"] {
        display: flex !important;
        align-items: center !important;
        height: 20px !important; 
        padding: 0px 1px !important; /* Espacio mínimo entre datos */
        margin: 0px !important;
    }

    /* Eliminar el espacio entre filas que genera Streamlit */
    [data-testid="stVerticalBlock"] {
        gap: 0px !important;
    }
    
    div.element-container {
        margin: 0px !important;
        padding: 0px !important;
    }

    /* 5. ESTILO DE TEXTO PLANO */
    .txt-flat {
        font-size: 0.9rem;
        font-family: monospace;
        margin: 0px !important;
        line-height: 20px !important;
        white-space: nowrap;
    }
    .txt-prod { color: #cc0000; font-weight: bold; }

    /* Línea divisoria de módulos muy fina */
    .mod-header {
        border-bottom: 1px solid #000;
        font-size: 0.7rem;
        margin-top: 5px;
        margin-bottom: 2px;
        color: #000;
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
st.markdown(f"**V&T | REGISTRO: {fecha_hoy}**")

# --- 6. DISEÑO DE FILAS ---
def render_fila_plana(idx):
    item = st.session_state.form_data[idx]
    
    # Proporciones ajustadas para que no haya huecos
    # ID | PROD | INICIO | FINAL (INPUT) | GL
    c1, c2, c3, c4, c5 = st.columns([0.2, 0.3, 0.6, 0.6, 0.4])
    
    with c1: st.markdown(f'<p class="txt-flat">{item["id"]}</p>', unsafe_allow_html=True)
    with c2: st.markdown(f'<p class="txt-flat txt-prod">{item["producto"]}</p>', unsafe_allow_html=True)
    with c3: st.markdown(f'<p class="txt-flat">{item["inicio"]:09d}</p>', unsafe_allow_html=True)
    with c4:
        # El input ahora es una continuación de la línea de texto
        nuevo_final = st.number_input(
            label=f"f_{idx}", 
            value=int(item['final']), 
            step=1, 
            key=f"in_{idx}", 
            label_visibility="collapsed"
        )
    st.session_state.form_data[idx]['final'] = nuevo_final
    
    galones = nuevo_final - item["inicio"]
    with c5:
        color = "blue" if galones > 0 else "#ccc"
        st.markdown(f'<p class="txt-flat" style="color:{color}">{galones:,.2f}</p>', unsafe_allow_html=True)

# --- RENDERIZADO POR MÓDULOS ---
st.markdown('<div class="mod-header">MODULO 1</div>', unsafe_allow_html=True)
for i in range(0, 8): render_fila_plana(i)

st.markdown('<div class="mod-header">MODULO 2</div>', unsafe_allow_html=True)
for i in range(8, 16): render_fila_plana(i)

st.markdown('<div class="mod-header">MODULO 3</div>', unsafe_allow_html=True)
for i in range(16, 22): render_fila_plana(i)

# --- RESUMEN FINAL ---
st.divider()
venta_total = sum((it['final'] - it['inicio']) * PRECIOS[it['producto']] for it in st.session_state.form_data)
st.markdown(f"**VENTA TOTAL: S/ {venta_total:,.2f}**")
