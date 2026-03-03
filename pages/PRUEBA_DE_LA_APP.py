import streamlit as st
import pandas as pd
import random
from datetime import datetime
import pytz

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema V&T", layout="wide")

# --- 2. CSS QUIRÚRGICO PARA ELIMINAR AIRE VERTICAL Y DOBLE RECUADRO ---
st.markdown("""
    <style>
    /* 1. ELIMINAR BOTONES Y ESPACIOS DE CONTENEDOR */
    div[data-testid="stNumberInput"] button { display: none !important; }
    
    /* Quitar el recuadro gris/plomo externo de Streamlit */
    div[data-testid="stNumberInput"] > div[data-baseweb="input"] {
        border: none !important;
        background-color: transparent !important;
        padding: 0px !important;
        min-height: 20px !important;
    }

    /* 2. AJUSTE DEL INPUT (RECUADRO DE ESCRITURA) */
    input {
        height: 20px !important;    /* Altura mínima */
        width: 90px !important;     /* Más angosto */
        border: 1px solid #000 !important; /* Un solo borde negro fino */
        font-family: monospace !important;
        font-size: 0.9rem !important;
        text-align: center !important;
        margin: 0px !important;
        padding: 0px !important;
        line-height: 20px !important;
    }

    /* 3. PEGAR FILAS: ALTURA DE COLUMNA MÍNIMA */
    [data-testid="column"] {
        display: flex !important;
        align-items: center !important; /* Centra el texto con el input */
        height: 22px !important;        /* Altura total de la fila */
        padding: 0px 2px !important;
    }

    /* Eliminar el margen que Streamlit mete a cada bloque */
    [data-testid="stVerticalBlock"] > div {
        gap: 0px !important;
        padding: 0px !important;
        margin: 0px !important;
    }
    
    .stNumberInput {
        margin: 0px !important;
        padding: 0px !important;
    }

    /* 4. TEXTO PLANO PARA QUE NO "EMPUJE" LA FILA */
    .txt-flat {
        font-size: 0.8rem;
        font-family: monospace;
        margin: 0px !important;
        padding: 0px !important;
        line-height: 1 !important;
    }
    .txt-prod { color: #cc0000; font-weight: bold; }

    /* 5. ENCABEZADOS PLANOS */
    .mod-header {
        background-color: #333;
        color: #fff;
        font-size: 0.7rem;
        padding: 1px 5px;
        margin-top: 5px;
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

    def render_fila_monotona(idx):
        global venta_bruta_acumulada
        item = st.session_state.form_data[idx]
        
        # Columnas proporcionales pegadas
        c1, c2, c3, c4, c5 = st.columns([0.2, 0.3, 0.7, 0.8, 0.5])
        
        with c1: st.markdown(f'<p class="txt-flat"><b>{item["id"]}</b></p>', unsafe_allow_html=True)
        with c2: st.markdown(f'<p class="txt-flat txt-prod">{item["producto"]}</p>', unsafe_allow_html=True)
        with c3: st.markdown(f'<p class="txt-flat">{item["inicio"]:09d}</p>', unsafe_allow_html=True)
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
        venta_bruta_acumulada += (galones * PRECIOS[item["producto"]])
        
        with c5:
            if galones > 0:
                st.markdown(f'<p class="txt-flat" style="color:blue">+{galones:,.2f}</p>', unsafe_allow_html=True)

    # --- LISTA COMPACTA ---
    st.markdown('<div class="mod-header">M1</div>', unsafe_allow_html=True)
    for i in range(0, 8): render_fila_monotona(i)

    st.markdown('<div class="mod-header">M2</div>', unsafe_allow_html=True)
    for i in range(8, 16): render_fila_monotona(i)

    st.markdown('<div class="mod-header">M3</div>', unsafe_allow_html=True)
    for i in range(16, 22): render_fila_monotona(i)

    st.divider()
    st.write(f"Total Venta: S/ {venta_bruta_acumulada:,.2f}")

# (Las otras pestañas se mantienen mínimas para no estorbar el diseño de ventas)
with tab2:
    if 'gastos' not in st.session_state: st.session_state.gastos = []
    d = st.text_input("Gasto")
    m = st.number_input("S/", key="m_gasto")
    if st.button("OK"): st.session_state.gastos.append({"D":d, "M":m}); st.rerun()
    st.table(st.session_state.gastos)

with tab3:
    total_g = sum(g["M"] for g in st.session_state.gastos)
    st.metric("NETO A DEPOSITAR", f"S/ {venta_bruta_acumulada - total_g:,.2f}")
