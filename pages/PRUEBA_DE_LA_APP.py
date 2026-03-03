import streamlit as st
import pandas as pd
import random

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema V&T", layout="wide")

# --- 2. CSS PARA ALINEACIÓN QUIRÚRGICA (INPUT FLRACO Y RECTO) ---
st.markdown("""
    <style>
    /* 1. ELIMINAR BOTONES Y MARGENES QUE "ENGORDAN" EL INPUT */
    div[data-testid="stNumberInput"] button { display: none !important; }
    
    /* Adelgazar el contenedor del input al máximo */
    div[data-testid="stNumberInput"] > div[data-baseweb="input"] {
        border: none !important;
        background-color: transparent !important;
        padding: 0px !important;
        margin: 0px !important;
        min-height: auto !important; /* Quita lo gordo */
        height: 24px !important;
    }

    /* 2. FORZAR AL TEXTO DE ADENTRO A ESTAR EN LA LÍNEA */
    input {
        border: none !important;
        background-color: transparent !important;
        height: 24px !important;
        padding: 0px !important;
        margin: 0px !important;
        line-height: 24px !important; /* Igual a la altura de la fila */
        font-family: monospace !important;
        font-size: 1rem !important;
        vertical-align: middle !important;
    }

    /* 3. ALINEAR TODA LA FILA (TEXTO + INPUT) AL CENTRO VERTICAL */
    [data-testid="column"] {
        display: flex !important;
        align-items: center !important; /* ESTO LO PONE RECTO */
        height: 24px !important; 
        padding: 0px 5px !important;
    }

    /* Quitar espacios entre filas */
    [data-testid="stVerticalBlock"] { gap: 0px !important; }
    div.element-container { margin: 0px !important; padding: 0px !important; }

    /* 4. TEXTO PLANO SIN MÁRGENES */
    .txt-flat {
        font-size: 0.9rem;
        font-family: monospace;
        margin: 0px !important;
        padding: 0px !important;
        display: inline-block;
        line-height: 24px !important;
    }
    
    .txt-prod { color: #cc0000; font-weight: bold; }

    /* Línea de módulo minimalista */
    .mod-header {
        border-bottom: 1px solid #000;
        font-size: 0.7rem;
        margin-top: 10px;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. DATOS ---
if 'form_data' not in st.session_state:
    st.session_state.form_data = [
        {"id": f"D-{i:02d}", "producto": random.choice(["90", "95", "DL"]),
         "inicio": random.randint(100000, 500000)} for i in range(1, 23)
    ]
    for item in st.session_state.form_data:
        item["final"] = item["inicio"]

# --- 4. FUNCIÓN DE RENDERIZADO RECTO ---
def fila_pistero(idx):
    item = st.session_state.form_data[idx]
    
    # ID | PROD | INICIAL | INPUT | RESULTADO
    c1, c2, c3, c4, c5 = st.columns([0.2, 0.3, 0.6, 0.6, 0.4])
    
    with c1: st.markdown(f'<span class="txt-flat"><b>{item["id"]}</b></span>', unsafe_allow_html=True)
    with c2: st.markdown(f'<span class="txt-flat txt-prod">{item["producto"]}</span>', unsafe_allow_html=True)
    with c3: st.markdown(f'<span class="txt-flat">{item["inicio"]:09d}</span>', unsafe_allow_html=True)
    with c4:
        # Aquí el input ya no tiene "aire" arriba ni abajo
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
            st.markdown(f'<span class="txt-flat" style="color:blue">+{galones:,.2f}</span>', unsafe_allow_html=True)

# --- 5. ESTRUCTURA ---
st.write("**GRIFO V&T - REGISTRO DE VENTAS**")

st.markdown('<div class="mod-header">MODULO 1</div>', unsafe_allow_html=True)
for i in range(0, 8): fila_pistero(i)

st.markdown('<div class="mod-header">MODULO 2</div>', unsafe_allow_html=True)
for i in range(8, 16): fila_pistero(i)

st.markdown('<div class="mod-header">MODULO 3</div>', unsafe_allow_html=True)
for i in range(16, 22): fila_pistero(i)

st.divider()
total = sum((it['final'] - it['inicio']) * 15.0 for it in st.session_state.form_data)
st.write(f"Total Acumulado: S/ {total:,.2f}")
