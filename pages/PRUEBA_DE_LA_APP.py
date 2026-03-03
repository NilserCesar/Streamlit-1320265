import streamlit as st
import pandas as pd
import random
from datetime import datetime
import pytz

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema V&T", layout="wide")

# --- 2. CSS DE MÁXIMA COMPACTACIÓN Y ALINEACIÓN ---
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

    /* ALINEACIÓN DE COLUMNAS PARA QUE TODO ESTÉ EN UNA LÍNEA */
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
        white-space: nowrap;
    }
    .txt-prod { color: #cc0000; font-weight: bold; }
    .txt-soles { color: #28a745; font-weight: bold; }

    /* CABECERA DE MÓDULOS */
    .mod-header {
        border-bottom: 1px solid #000;
        font-size: 0.75rem;
        margin-top: 15px;
        margin-bottom: 5px;
        font-weight: bold;
        color: #555;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. CONFIGURACIÓN DE PRECIOS Y TIEMPO ---
PRECIOS = {"DL": 14.00, "90": 14.00, "95": 15.00}
tz = pytz.timezone('America/Lima')
fecha_hoy = datetime.now(tz).strftime("%d/%m/%Y")

# --- 4. INICIALIZACIÓN DE DATOS ---
if 'form_data' not in st.session_state:
    # Generar 22 mangueras de ejemplo
    productos_lista = ["DL", "90", "95"]
    st.session_state.form_data = [
        {"id": f"M-{i+1:02d}", "producto": productos_lista[i % 3],
         "inicio": 100000 + (i * 100)} for i in range(22)
    ]
    for item in st.session_state.form_data:
        item["final"] = item["inicio"]

if 'gastos' not in st.session_state: st.session_state.gastos = []

# --- 5. INTERFAZ PRINCIPAL ---
st.title(f"⛽ V&T | {fecha_hoy}")

# --- WIDGETS DE PRECIOS ACTUALES ---
c_p1, c_p2, c_p3 = st.columns(3)
c_p1.metric("DL", f"S/ {PRECIOS['DL']:.2f}")
c_p2.metric("90", f"S/ {PRECIOS['90']:.2f}")
c_p3.metric("95", f"S/ {PRECIOS['95']:.2f}")

tab1, tab2, tab3 = st.tabs(["🛒 VENTAS", "💸 GASTOS", "💰 CIERRE"])

with tab1:
    # Encabezados de tabla manuales para claridad
    h1, h2, h3, h4, h5, h6 = st.columns([0.2, 0.3, 0.6, 0.6, 0.4, 0.5])
    h1.caption("ID")
    h2.caption("PROD")
    h3.caption("LECT. INI")
    h4.caption("LECT. FIN")
    h5.caption("GL")
    h6.caption("SOLES (S/) ")

    total_soles_ventas = 0.0

    def render_fila_operativa(idx):
        global total_soles_ventas
        it = st.session_state.form_data[idx]
        precio_unit = PRECIOS[it["producto"]]
        
        # Grid: ID | PROD | INICIO | INPUT | GALONES | SOLES
        cols = st.columns([0.2, 0.3, 0.6, 0.6, 0.4, 0.5])
        
        cols[0].markdown(f'<p class="txt-flat"><b>{it["id"]}</b></p>', unsafe_allow_html=True)
        cols[1].markdown(f'<p class="txt-flat txt-prod">{it["producto"]}</p>', unsafe_allow_html=True)
        cols[2].markdown(f'<p class="txt-flat">{it["inicio"]:,.2f}</p>', unsafe_allow_html=True)
        
        with cols[3]:
            # Input pegado al texto
            nuevo_fin = st.number_input(
                label=f"fin_{idx}", value=float(it['final']), 
                step=0.01, key=f"k_{idx}", label_visibility="collapsed"
            )
        
        st.session_state.form_data[idx]['final'] = nuevo_fin
        galones = nuevo_fin - it["inicio"]
        subtotal_soles = galones * precio_unit
        total_soles_ventas += subtotal_soles
        
        cols[4].markdown(f'<p class="txt-flat" style="color:blue">{galones:,.2f}</p>', unsafe_allow_html=True)
        cols[5].markdown(f'<p class="txt-flat txt-soles">S/ {subtotal_soles:,.2f}</p>', unsafe_allow_html=True)

    # Renderizado de mangueras
    st.markdown('<div class="mod-header">SURTIDORES</div>', unsafe_allow_html=True)
    for i in range(len(st.session_state.form_data)):
        render_fila_operativa(i)

    # --- TOTALES AL FINAL DE LA COLUMNA DE SOLES ---
    st.markdown("---")
    tf1, tf2 = st.columns([2.1, 0.5])
    tf1.markdown("<p style='text-align:right; font-weight:bold;'>TOTAL VENTAS BRUTAS:</p>", unsafe_allow_html=True)
    tf2.markdown(f"<p class='txt-soles' style='font-size:1.2rem;'>S/ {total_soles_ventas:,.2f}</p>", unsafe_allow_html=True)

with tab2:
    st.subheader("Gastos del Turno")
    with st.form("gasto_form", clear_on_submit=True):
        cg1, cg2 = st.columns([3,1])
        desc = cg1.text_input("Concepto")
        monto = cg2.number_input("Monto S/", min_value=0.0)
        if st.form_submit_button("Registrar Gasto"):
            if desc: 
                st.session_state.gastos.append({"D": desc, "M": monto})
                st.rerun()
    if st.session_state.gastos:
        st.table(st.session_state.gastos)

with tab3:
    total_g = sum(g["M"] for g in st.session_state.gastos)
    neto_final = total_soles_ventas - total_g
    
    st.markdown(f"""
        <div style="border:2px solid #000; padding:20px; text-align:center;">
            <h3>LIQUIDACIÓN FINAL</h3>
            <h1 style="color:#28a745;">S/ {neto_final:,.2f}</h1>
            <p>Ventas: S/ {total_soles_ventas:,.2f} | Gastos: S/ {total_g:,.2f}</p>
        </div>
    """, unsafe_allow_html=True)
