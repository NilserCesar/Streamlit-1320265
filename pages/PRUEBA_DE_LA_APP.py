import streamlit as st
import pandas as pd
import random
from datetime import datetime
import pytz

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema V&T", layout="wide")

# --- 2. CSS DE REINICIO Y ESTILOS (MEJORADO) ---
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

    /* ALINEACIÓN DE COLUMNAS PARA QUE TODO ESTÉ EN UNA LÍNEA */
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
        margin-top: 55px; /* Los 2 espacios extra que pediste */
        margin-bottom: 10px;
        font-weight: bold;
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

# --- 3. CONFIGURACIÓN DE TIEMPO Y PRECIOS ---
tz = pytz.timezone('America/Lima')
ahora = datetime.now(tz)
fecha_hoy = ahora.strftime("%d/%m/%Y")
PRECIOS = {"DL": 14.0, "90": 14.0, "95": 15.0}

# --- 4. INICIALIZACIÓN DE DATOS (RESPETANDO TU LÓGICA) ---
if 'form_data' not in st.session_state:
    st.session_state.form_data = [
        {"id": f"D-{i:02d}", "producto": random.choice(["90", "95", "DL"]),
         "inicio": random.randint(100000, 500000)} for i in range(1, 23)
    ]
    for item in st.session_state.form_data:
        item["final"] = item["inicio"]

if 'gastos' not in st.session_state: st.session_state.gastos = []
if 'vales' not in st.session_state: st.session_state.vales = []

# --- 5. ENCABEZADO Y WIDGETS ---
st.subheader(f"V&T | REGISTRO DE VENTAS | {fecha_hoy}")

# Widgets de precio arriba
c_p1, c_p2, c_p3 = st.columns(3)
c_p1.metric("PRECIO DL", f"S/ {PRECIOS['DL']:.2f}")
c_p2.metric("PRECIO 90", f"S/ {PRECIOS['90']:.2f}")
c_p3.metric("PRECIO 95", f"S/ {PRECIOS['95']:.2f}")

# --- 6. PESTAÑAS (INCLUYENDO VALES) ---
tab1, tab2, tab3, tab4 = st.tabs(["🛒 VENTAS", "💸 GASTOS", "🎫 VALES", "💰 SALDO"])

with tab1:
    def render_bloque(inicio_idx, fin_idx, nombre_modulo):
        st.markdown(f'<div class="mod-header">{nombre_modulo}</div>', unsafe_allow_html=True)
        
        # Cabeceras
        h = st.columns([0.2, 0.3, 0.6, 0.6, 0.4, 0.5])
        h[0].caption("ID")
        h[1].caption("PROD")
        h[2].caption("L. INICIO")
        h[3].caption("L. FINAL")
        h[4].caption("GL")
        h[5].caption("SOLES")

        total_mod_soles = 0.0

        for i in range(inicio_idx, fin_idx):
            item = st.session_state.form_data[i]
            cols = st.columns([0.2, 0.3, 0.6, 0.6, 0.4, 0.5])
            
            with cols[0]: st.markdown(f'<p class="txt-flat"><b>{item["id"]}</b></p>', unsafe_allow_html=True)
            with cols[1]: st.markdown(f'<p class="txt-flat txt-prod">{item["producto"]}</p>', unsafe_allow_html=True)
            # Inicio como entero puro
            with cols[2]: st.markdown(f'<p class="txt-flat">{int(item["inicio"])}</p>', unsafe_allow_html=True)
            
            with cols[3]:
                st.markdown('<div class="input-verde">', unsafe_allow_html=True)
                nuevo_final = st.number_input(
                    label=f"in_{i}", 
                    value=int(item['final']), 
                    step=1, 
                    key=f"k_{i}", 
                    label_visibility="collapsed"
                )
                st.markdown('</div>', unsafe_allow_html=True)
            
            item['final'] = nuevo_final
            galones = item["final"] - item["inicio"]
            subtotal = galones * PRECIOS[item["producto"]]
            total_mod_soles += subtotal
            
            with cols[4]: st.markdown(f'<p class="txt-flat" style="color:blue">{galones:,.2f}</p>', unsafe_allow_html=True)
            with cols[5]: st.markdown(f'<p class="txt-flat txt-soles">S/ {subtotal:,.2f}</p>', unsafe_allow_html=True)

        st.markdown(f'<div class="mod-footer">SUBTOTAL {nombre_modulo}: S/ {total_mod_soles:,.2f}</div>', unsafe_allow_html=True)
        return total_mod_soles

    m1 = render_bloque(0, 8, "MÓDULO 1")
    m2 = render_bloque(8, 16, "MÓDULO 2")
    m3 = render_bloque(16, 22, "MÓDULO 3")
    
    venta_bruta_total = m1 + m2 + m3

with tab2:
    st.markdown("### Registro de Gastos")
    with st.form("f_gastos", clear_on_submit=True):
        c1, c2 = st.columns([3,1])
        d = c1.text_input("Gasto / Concepto")
        m = c2.number_input("Monto S/", min_value=0.0)
        if st.form_submit_button("Añadir"):
            if d: st.session_state.gastos.append({"D": d, "M": m}); st.rerun()
    if st.session_state.gastos: st.table(st.session_state.gastos)

with tab3:
    st.markdown("### Registro de Vales")
    with st.form("f_vales", clear_on_submit=True):
        c1, c2 = st.columns([3,1])
        cl = c1.text_input("Cliente / Placa")
        v = c2.number_input("S/", min_value=0.0)
        if st.form_submit_button("Añadir Vale"):
            if cl: st.session_state.vales.append({"C": cl, "M": v}); st.rerun()
    if st.session_state.vales: st.table(st.session_state.vales)

with tab4:
    total_g = sum(g["M"] for g in st.session_state.gastos)
    total_v = sum(v["M"] for v in st.session_state.vales)
    neto = venta_bruta_total - total_g - total_v
    
    st.markdown(f"""
        <div style="border:2px solid #000; padding:25px; text-align:center; background-color:#fff;">
            <h2 style="margin:0;">CIERRE DE CAJA</h2>
            <hr>
            <h4 style="margin:5px;">Venta Bruta: S/ {venta_bruta_total:,.2f}</h4>
            <h4 style="margin:5px; color:red;">Total Gastos: S/ {total_g:,.2f}</h4>
            <h4 style="margin:5px; color:orange;">Total Vales: S/ {total_v:,.2f}</h4>
            <h1 style="color:green; font-size:3rem; margin:15px 0;">NETO: S/ {neto:,.2f}</h1>
        </div>
    """, unsafe_allow_html=True)
