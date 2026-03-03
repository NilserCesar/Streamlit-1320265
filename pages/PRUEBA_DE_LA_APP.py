import streamlit as st
import pandas as pd
from datetime import datetime
import pytz

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema V&T", layout="wide")

# --- 2. CSS DE MÁXIMA COMPACTACIÓN Y ESTILOS ESPECÍFICOS ---
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
        color: #1a7f37 !important; /* Verde simple */
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
    
    /* ESTILO DE TEXTO */
    .txt-flat {
        font-size: 0.9rem;
        font-family: monospace;
        margin: 0px !important;
        line-height: 24px !important;
    }
    .txt-prod { color: #cc0000; font-weight: bold; }
    .txt-soles { color: #28a745; font-weight: bold; }

    /* CABECERA DE MÓDULOS CON MÁS ESPACIO */
    .mod-header {
        background-color: #f0f2f6;
        border-bottom: 2px solid #000;
        padding: 4px 10px;
        font-size: 0.85rem;
        margin-top: 25px; /* Más espacio arriba del módulo */
        margin-bottom: 8px;
        font-weight: bold;
        letter-spacing: 1px;
    }
    
    /* TOTAL POR MÓDULO */
    .mod-footer {
        border-top: 1px dashed #999;
        margin-bottom: 15px;
        padding-top: 4px;
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

# --- 4. TÍTULO Y PRECIOS ---
st.subheader(f"⛽ V&T | REGISTRO DIARIO | {fecha_hoy}")

c_p1, c_p2, c_p3 = st.columns(3)
c_p1.metric("PRECIO DL", f"S/ {PRECIOS['DL']:.2f}")
c_p2.metric("PRECIO 90", f"S/ {PRECIOS['90']:.2f}")
c_p3.metric("PRECIO 95", f"S/ {PRECIOS['95']:.2f}")

# --- 5. LÓGICA DE RENDERIZADO ---
def render_bloque(inicio_idx, fin_idx, nombre_modulo):
    st.markdown(f'<div class="mod-header">{nombre_modulo}</div>', unsafe_allow_html=True)
    
    # Encabezados
    h = st.columns([0.2, 0.3, 0.6, 0.6, 0.4, 0.5])
    h[0].caption("ID")
    h[1].caption("PRODUCTO")
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
        
        # L. INICIO sin comas ni puntos (formato entero)
        cols[2].markdown(f'<p class="txt-flat">{int(it["inicio"])}</p>', unsafe_allow_html=True)
        
        with cols[3]:
            # L. FINAL con clase CSS verde y formato entero (step=1)
            st.markdown('<div class="input-verde">', unsafe_allow_html=True)
            n_fin = st.number_input(
                label=f"f_{i}", 
                value=int(it['final']), 
                step=1, # Solo números enteros
                key=f"key_{i}", 
                label_visibility="collapsed"
            )
            st.markdown('</div>', unsafe_allow_html=True)
            st.session_state.form_data[i]['final'] = n_fin
        
        galones = n_fin - it["inicio"]
        subtotal = galones * PRECIOS[it["producto"]]
        total_modulo += subtotal
        
        # Galones y Soles sí mantienen decimales por ser contables
        cols[4].markdown(f'<p class="txt-flat" style="color:blue">{galones:,.2f}</p>', unsafe_allow_html=True)
        cols[5].markdown(f'<p class="txt-flat txt-soles">S/ {subtotal:,.2f}</p>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="mod-footer">TOTAL {nombre_modulo}: S/ {total_modulo:,.2f}</div>', unsafe_allow_html=True)
    return total_modulo

# --- 6. PESTAÑAS ---
t1, t2, t3 = st.tabs(["🛒 VENTAS", "💸 GASTOS", "💰 CIERRE"])

with t1:
    m1 = render_bloque(0, 8, "MÓDULO 1")
    m2 = render_bloque(8, 16, "MÓDULO 2")
    m3 = render_bloque(16, 22, "MÓDULO 3")
    
    total_bruto = m1 + m2 + m3
    st.divider()
    st.markdown(f"### VENTA TOTAL BRUTA: S/ {total_bruto:,.2f}")

with t2:
    with st.form("f_gasto", clear_on_submit=True):
        cg1, cg2 = st.columns([3,1])
        d = cg1.text_input("Concepto")
        m = cg2.number_input("S/", min_value=0.0)
        if st.form_submit_button("Añadir Gasto"):
            if d: st.session_state.gastos.append({"D": d, "M": m}); st.rerun()
    if st.session_state.gastos: st.table(st.session_state.gastos)

with t3:
    total_g = sum(g["M"] for g in st.session_state.gastos)
    neto = total_bruto - total_g
    st.markdown(f"""
        <div style="border:2px solid #000; padding:20px; text-align:center; background-color:#fff;">
            <h2>MONTO NETO A DEPOSITAR</h2>
            <h1 style="color:green;">S/ {neto:,.2f}</h1>
            <p>Suma Módulos: S/ {total_bruto:,.2f} | Gastos: S/ {total_g:,.2f}</p>
        </div>
    """, unsafe_allow_html=True)
