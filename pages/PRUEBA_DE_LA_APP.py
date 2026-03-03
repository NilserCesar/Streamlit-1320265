import streamlit as st
import pandas as pd
import random
from datetime import datetime
import pytz

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema V&T", layout="wide")

# --- 2. CSS DE REINICIO TOTAL (DISEÑO PLANO Y PEGADO) ---
st.markdown("""
    <style>
    /* 1. ELIMINAR BOTONES +/- Y ELEMENTOS DE STREAMLIT */
    div[data-testid="stNumberInput"] button { display: none !important; }
    
    /* 2. LIMPIEZA RADICAL DEL INPUT (SIN CAJAS, SIN GRIS, SIN HUECOS) */
    div[data-testid="stNumberInput"] > div,
    div[data-testid="stNumberInput"] div[data-baseweb="input"],
    div[data-testid="stNumberInput"] div[data-baseweb="base-input"],
    input {
        background-color: transparent !important; /* Quita fondo gris */
        border: none !important;                 /* Quita bordes plomos */
        padding: 0px !important;                 /* Quita espacios blancos */
        margin: 0px !important;                  /* Quita márgenes */
        min-height: auto !important;             /* Quita lo gordo */
        height: 20px !important;                 /* Altura de texto */
        box-shadow: none !important;             /* Quita sombras */
        outline: none !important;                /* Quita borde azul al clicar */
        font-family: monospace !important;
        font-size: 1rem !important;
        text-align: left !important;
    }

    /* 3. ALINEACIÓN QUIRÚRGICA DE LA FILA */
    [data-testid="column"] {
        display: flex !important;
        align-items: center !important;         /* Pone todo en la misma línea recta */
        height: 22px !important; 
        padding: 0px 2px !important;
    }

    /* Eliminar el aire entre filas */
    [data-testid="stVerticalBlock"] { gap: 0px !important; }
    div.element-container { margin: 0px !important; padding: 0px !important; }

    /* 4. TEXTO PLANO */
    .txt-flat {
        font-size: 0.9rem;
        font-family: monospace;
        margin: 0px !important;
        line-height: 22px !important;
        white-space: nowrap;
    }
    .txt-prod { color: #cc0000; font-weight: bold; }

    /* Encabezados de módulo planos */
    .mod-header {
        border-bottom: 1px solid #ddd;
        color: #666;
        font-size: 0.7rem;
        margin-top: 10px;
        margin-bottom: 2px;
        text-transform: uppercase;
        font-weight: bold;
    }
    
    /* Pestañas más compactas */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { height: 30px; padding: 0px 10px; }
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
st.markdown(f"**⛽ V&T | CONTROL DE VENTAS | {fecha_hoy}**")

# --- 6. PESTAÑAS ---
tab1, tab2, tab3, tab4 = st.tabs(["🛒 VENTAS", "💸 GASTOS", "🎫 VALES", "💰 SALDO"])

with tab1:
    venta_bruta_acumulada = 0

    def render_fila_recta(idx):
        global venta_bruta_acumulada
        item = st.session_state.form_data[idx]
        
        # Grid: ID | PROD | INICIO | INPUT (FINAL) | DIFERENCIA
        c1, c2, c3, c4, c5 = st.columns([0.2, 0.3, 0.6, 0.6, 0.4])
        
        with c1: st.markdown(f'<p class="txt-flat"><b>{item["id"]}</b></p>', unsafe_allow_html=True)
        with c2: st.markdown(f'<p class="txt-flat txt-prod">{item["producto"]}</p>', unsafe_allow_html=True)
        with c3: st.markdown(f'<p class="txt-flat" style="color:#666">{item["inicio"]:09d}</p>', unsafe_allow_html=True)
        with c4:
            # Input totalmente desnudo, pegado al texto
            nuevo_final = st.number_input(
                label=f"f_{idx}", 
                value=int(item['final']), 
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
                st.markdown(f'<p class="txt-flat" style="color:blue; font-weight:bold;">+{galones:,.2f}</p>', unsafe_allow_html=True)
            else:
                st.markdown('<p class="txt-flat" style="color:#eee">0.00</p>', unsafe_allow_html=True)

    # --- MÓDULOS ---
    st.markdown('<div class="mod-header">Módulo 1</div>', unsafe_allow_html=True)
    for i in range(0, 8): render_fila_recta(i)

    st.markdown('<div class="mod-header">Módulo 2</div>', unsafe_allow_html=True)
    for i in range(8, 16): render_fila_recta(i)

    st.markdown('<div class="mod-header">Módulo 3</div>', unsafe_allow_html=True)
    for i in range(16, 22): render_fila_recta(i)

    st.divider()
    st.markdown(f"### Venta Bruta Total: S/ {venta_bruta_acumulada:,.2f}")

with tab2:
    st.markdown("**Registro de Gastos**")
    with st.form("g", clear_on_submit=True):
        c1, c2 = st.columns([3,1])
        d = c1.text_input("Descripción")
        m = c2.number_input("S/", min_value=0.0)
        if st.form_submit_button("Añadir"):
            if d: st.session_state.gastos.append({"D": d, "M": m}); st.rerun()
    if st.session_state.gastos: st.table(st.session_state.gastos)

with tab3:
    st.markdown("**Registro de Vales**")
    with st.form("v", clear_on_submit=True):
        c1, c2 = st.columns([3,1])
        cl = c1.text_input("Cliente/Placa")
        v = c2.number_input("S/", min_value=0.0)
        if st.form_submit_button("Añadir"):
            if cl: st.session_state.vales.append({"C": cl, "M": v}); st.rerun()
    if st.session_state.vales: st.table(st.session_state.vales)

with tab4:
    total_g = sum(g["M"] for g in st.session_state.gastos)
    total_v = sum(v["M"] for v in st.session_state.vales)
    neto = venta_bruta_acumulada - total_g - total_v
    
    st.markdown(f"""
        <div style="border:1px solid #000; padding:15px; background-color:#fff; text-align:center;">
            <h2 style="margin:0;">TOTAL NETO A DEPOSITAR</h2>
            <h1 style="color:green; margin:10px 0;">S/ {neto:,.2f}</h1>
            <p style="font-size:0.8rem; color:#666;">
                Venta: {venta_bruta_acumulada} | Gastos: -{total_g} | Vales: -{total_v}
            </p>
        </div>
    """, unsafe_allow_html=True)
