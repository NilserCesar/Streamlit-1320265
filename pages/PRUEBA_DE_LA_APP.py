import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema V&T", layout="wide")

# --- 2. CSS DE MÁXIMA COMPACTACIÓN Y AJUSTES VISUALES ---
st.markdown("""
    <style>
    /* ELIMINAR CONTENEDORES Y BORDES DEL INPUT */
    div[data-testid="stNumberInput"] button { display: none !important; }
    div[data-testid="stNumberInput"] > div,
    div[data-testid="stNumberInput"] div[data-baseweb="input"],
    div[data-testid="stNumberInput"] div[data-baseweb="base-input"],
    input {
        background-color: transparent !important;
        border: none !important;
        padding: 0px !important;
        margin: 0px !important;
        min-height: auto !important;
        height: 22px !important;
        box-shadow: none !important;
        outline: none !important;
        font-family: monospace !important;
        font-size: 1rem !important;
        text-align: left !important;
    }

    /* COLOR VERDE PARA LA COLUMNA L. FINAL */
    .input-verde input {
        color: #1a7f37 !important; 
        font-weight: bold !important;
    }

    /* ALINEACIÓN DE COLUMNAS */
    [data-testid="column"] {
        display: flex !important;
        align-items: center !important;
        height: 24px !important; 
        padding: 0px 5px !important;
    }

    [data-testid="stVerticalBlock"] { gap: 0px !important; }
    
    /* ESTILO DE TEXTO PLANO */
    .txt-flat {
        font-size: 0.9rem;
        font-family: monospace;
        margin: 0px !important;
        line-height: 24px !important;
    }
    .txt-prod { color: #cc0000; font-weight: bold; }
    .txt-soles { color: #28a745; font-weight: bold; }

    /* CABECERA DE MÓDULOS CON DOBLE ESPACIO EXTRA */
    .mod-header {
        background-color: #f8f9fa;
        border-bottom: 2px solid #333;
        padding: 6px 12px;
        font-size: 0.85rem;
        margin-top: 50px; /* Doble espacio para que no se pegue al anterior */
        margin-bottom: 10px;
        font-weight: bold;
        letter-spacing: 1.5px;
        color: #333;
    }
    
    /* TOTAL POR MÓDULO */
    .mod-footer {
        border-top: 1px dashed #bbb;
        margin-bottom: 20px;
        padding-top: 5px;
        text-align: right;
        font-family: monospace;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. CONFIGURACIÓN DE DATOS Y PRECIOS ---
PRECIOS = {"DL": 14.00, "90": 14.00, "95": 15.00}
tz = pytz.timezone('America/Lima')
fecha_hoy = datetime.now(tz).strftime("%d/%m/%Y")

if 'form_data' not in st.session_state:
    prod_map = ["90", "95", "DL"]
    st.session_state.form_data = [
        {"id": f"M-{i+1:02d}", "producto": prod_map[i % 3], 
         "inicio": 123456, "final": 123456} for i in range(22)
    ]

if 'gastos' not in st.session_state: st.session_state.gastos = []

# --- 4. TÍTULO Y WIDGETS DE PRECIO ---
st.subheader(f"⛽ V&T | REGISTRO DE VENTAS | {fecha_hoy}")

cp1, cp2, cp3 = st.columns(3)
cp1.metric("PRECIO DL", f"S/ {PRECIOS['DL']:.2f}")
cp2.metric("PRECIO 90", f"S/ {PRECIOS['90']:.2f}")
cp3.metric("PRECIO 95", f"S/ {PRECIOS['95']:.2f}")

# --- 5. FUNCIÓN DE RENDERIZADO POR MÓDULO ---
def render_bloque(inicio_idx, fin_idx, nombre_modulo):
    st.markdown(f'<div class="mod-header">{nombre_modulo}</div>', unsafe_allow_html=True)
    
    # Encabezados de tabla
    h = st.columns([0.2, 0.3, 0.6, 0.6, 0.4, 0.5])
    h[0].caption("ID")
    h[1].caption("PROD.")
    h[2].caption("L. INICIO")
    h[3].caption("L. FINAL")
    h[4].caption("GL")
    h[5].caption("SOLES")

    total_modulo = 0.0

    for i in range(inicio_idx, fin_idx):
        it = st.session_state.form_data[i]
        cols = st.columns([0.2, 0.3, 0.6, 0.6, 0.4, 0.5])
        
        cols[0].markdown(f'<p class="txt-flat"><b>{it["id"]}</b></p>', unsafe_allow_html=True)
        cols[1].markdown(f'<p class="txt-flat txt-prod">{it["producto"]}</p>', unsafe_allow_html=True)
        
        # Lectura Inicio (Entero puro)
        cols[2].markdown(f'<p class="txt-flat">{int(it["inicio"])}</p>', unsafe_allow_html=True)
        
        with cols[3]:
            # Lectura Final (Verde, Entero puro)
            st.markdown('<div class="input-verde">', unsafe_allow_html=True)
            n_fin = st.number_input(
                label=f"input_{i}", 
                value=int(it['final']), 
                step=1, 
                key=f"k_{i}", 
                label_visibility="collapsed"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            st.session_state.form_data[i]['final'] = n_fin
        
        galones = n_fin - it["inicio"]
        subtotal = galones * PRECIOS[it["producto"]]
        total_modulo += subtotal
        
        cols[4].markdown(f'<p class="txt-flat" style="color:blue">{galones:,.2f}</p>', unsafe_allow_html=True)
        cols[5].markdown(f'<p class="txt-flat txt-soles">S/ {subtotal:,.2f}</p>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="mod-footer">SUBTOTAL {nombre_modulo}: S/ {total_modulo:,.2f}</div>', unsafe_allow_html=True)
    return total_modulo

# --- 6. PESTAÑAS PRINCIPALES ---
t1, t2, t3 = st.tabs(["🛒 REGISTRO", "💸 GASTOS", "💰 TOTALES"])

with t1:
    m1 = render_bloque(0, 8, "MÓDULO 1")
    m2 = render_bloque(8, 16, "MÓDULO 2")
    m3 = render_bloque(16, 22, "MÓDULO 3")
    
    total_bruto = m1 + m2 + m3

with t2:
    st.markdown("### Registro de Gastos")
    with st.form("form_gastos", clear_on_submit=True):
        cg1, cg2 = st.columns([3,1])
        d = cg1.text_input("Descripción del gasto")
        m = cg2.number_input("Monto S/", min_value=0.0)
        if st.form_submit_button("Agregar"):
            if d: 
                st.session_state.gastos.append({"D": d, "M": m})
                st.rerun()
    if st.session_state.gastos:
        st.table(st.session_state.gastos)

with t3:
    total_g = sum(g["M"] for g in st.session_state.gastos)
    st.markdown(f"""
        <div style="border:2px solid #333; padding:30px; text-align:center; background-color:#fff; margin-top:20px;">
            <h2 style="margin:0;">RESUMEN DE CIERRE</h2>
            <hr>
            <h4 style="margin:5px;">Ventas Brutas: S/ {total_bruto:,.2f}</h4>
            <h4 style="margin:5px; color:red;">Total Gastos: S/ {total_g:,.2f}</h4>
            <h1 style="color:green; font-size:3rem; margin:15px 0;">NETO: S/ {total_bruto - total_g:,.2f}</h1>
        </div>
    """, unsafe_allow_html=True)
