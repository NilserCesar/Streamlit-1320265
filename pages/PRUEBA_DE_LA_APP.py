import streamlit as st
import pandas as pd
import random

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema V&T", layout="wide")

# --- 2. CSS PARA ELIMINAR LOS "HUECOS BLANCOS" Y EL MARCO GRIS ---
st.markdown("""
    <style>
    /* 1. ELIMINAR BOTONES Y CUALQUIER MARGEN INTERNO DE LA CAJA */
    div[data-testid="stNumberInput"] button { display: none !important; }
    
    /* ESTO ELIMINA EL "AIRE" BLANCO Y EL FONDO GRIS QUE VES EN TU IMAGEN */
    div[data-testid="stNumberInput"] > div,
    div[data-testid="stNumberInput"] div[data-baseweb="input"],
    div[data-testid="stNumberInput"] div[data-baseweb="base-input"] {
        background-color: transparent !important; /* Quita el gris */
        border: none !important;                 /* Quita el borde plomo */
        padding: 0px !important;                 /* Quita el espacio blanco de los lados */
        margin: 0px !important;
        min-height: auto !important;             /* Quita lo alto/gordo */
        height: 20px !important;
    }

    /* 2. ESTILO DEL NÚMERO (INPUT) PARA QUE SEA UNA LÍNEA PLANA */
    input {
        background-color: transparent !important;
        border: none !important;
        height: 20px !important;
        line-height: 20px !important;
        padding: 0px !important;
        margin: 0px !important;
        font-family: monospace !important;
        font-size: 1rem !important;
        color: #000 !important;
        outline: none !important;
        box-shadow: none !important;
    }

    /* 3. ALINEACIÓN TOTAL DE LA FILA */
    [data-testid="column"] {
        display: flex !important;
        align-items: center !important; /* Alinea texto e input al centro exacto */
        height: 22px !important; 
        padding: 0px 2px !important;
    }

    /* Quitar el espacio entre filas */
    [data-testid="stVerticalBlock"] { gap: 0px !important; }
    div.element-container { margin: 0px !important; padding: 0px !important; }

    .txt-flat {
        font-size: 0.9rem;
        font-family: monospace;
        margin: 0px !important;
        line-height: 22px !important;
    }
    .txt-prod { color: #cc0000; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- 3. INICIALIZACIÓN DE DATOS ---
if 'form_data' not in st.session_state:
    st.session_state.form_data = [
        {"id": f"D-{i:02d}", "producto": random.choice(["90", "95", "DL"]),
         "inicio": random.randint(100000, 500000)} for i in range(1, 23)
    ]
    for item in st.session_state.form_data:
        item["final"] = item["inicio"]

# --- 4. RENDERIZADO DE FILAS SIN "HUECOS" ---
def render_fila(idx):
    item = st.session_state.form_data[idx]
    c1, c2, c3, c4, c5 = st.columns([0.2, 0.3, 0.6, 0.6, 0.4])
    
    with c1: st.markdown(f'<p class="txt-flat"><b>{item["id"]}</b></p>', unsafe_allow_html=True)
    with c2: st.markdown(f'<p class="txt-flat txt-prod">{item["producto"]}</p>', unsafe_allow_html=True)
    with c3: st.markdown(f'<p class="txt-flat">{item["inicio"]:09d}</p>', unsafe_allow_html=True)
    with c4:
        # Este input ya no tiene fondo gris ni bordes blancos
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
        if galones > 0:
            st.markdown(f'<p class="txt-flat" style="color:blue">+{galones:,.2f}</p>', unsafe_allow_html=True)

# --- 5. ESTRUCTURA VISUAL ---
st.write("**CONTROL DE SURTIDORES**")

for i in range(0, 22):
    render_fila(i)
