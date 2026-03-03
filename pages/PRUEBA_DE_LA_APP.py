import streamlit as st
import pandas as pd
import random
from datetime import datetime
import pytz

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema V&T", layout="wide")

# --- 2. CSS AGRESIVO PARA COMPACTACIÓN CUADRÁTICA ---
st.markdown("""
    <style>
    /* 1. Eliminar bordes redondeados en todo el sitio */
    * { border-radius: 0px !important; }

    /* 2. Eliminar botones +/- de los inputs numéricos */
    input::-webkit-outer-spin-button, input::-webkit-inner-spin-button { 
        -webkit-appearance: none; margin: 0; 
    }
    input[type=number] { -moz-appearance: textfield; }

    /* 3. Pegar líneas: reducir espacio vertical de widgets y columnas */
    [data-testid="stVerticalBlock"] > div { 
        padding-top: 0rem !important; 
        padding-bottom: 0rem !important; 
        gap: 0px !important;
    }
    [data-testid="column"] { 
        padding: 1px 5px !important; 
    }
    .stNumberInput { 
        margin-top: -10px !important; 
        margin-bottom: -10px !important; 
    }

    /* 4. Estilo de los inputs (Cuadrados y compactos) */
    input {
        background-color: #f8f9fa !important;
        border: 1px solid #ced4da !important;
        height: 28px !important;
        font-family: monospace !important;
        font-size: 1rem !important;
    }

    /* 5. Encabezados de módulo minimalistas */
    .mod-header {
        background-color: #343a40;
        color: white;
        padding: 2px 10px;
        font-size: 0.9rem;
        font-weight: bold;
        margin-top: 10px;
        margin-bottom: 2px;
    }

    /* 6. Etiquetas de texto */
    .txt-small { font-size: 0.85rem; font-family: sans-serif; }
    .txt-id { font-weight: bold; color: #1a1a1a; }
    .txt-prod { font-weight: bold; color: #dc3545; }
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
st.markdown(f"### ⛽ V&T - REGISTRO DE VENTAS | {fecha_hoy}")

# --- 6. PESTAÑAS ---
tab1, tab2, tab3, tab4 = st.tabs(["🛒 VENTAS", "💸 GASTOS", "🎫 VALES", "💰 SALDO"])

with tab1:
    venta_bruta_acumulada = 0

    def render_fila_pistero(idx):
        global venta_bruta_acumulada
        item = st.session_state.form_data[idx]
        
        # Columnas proporcionales para que todo entre en una línea
        c1, c2, c3, c4, c5 = st.columns([0.4, 0.4, 1.2, 1.5, 1.2])
        
        with c1: st.markdown(f'<span class="txt-small txt-id">{item["id"]}</span>', unsafe_allow_html=True)
        with c2: st.markdown(f'<span class="txt-small txt-prod">{item["producto"]}</span>', unsafe_allow_html=True)
        with c3: st.markdown(f'<span class="txt-small" style="color:#777">L: {item["inicio"]:09d}</span>', unsafe_allow_html=True)
        with c4:
            nuevo_final = st.number_input(
                label=f"f_{idx}", value=int(item['final']), 
                min_value=int(item['inicio']), step=1, 
                key=f"in_{idx}", label_visibility="collapsed"
            )
        
        item['final'] = nuevo_final
        galones = item["final"] - item["inicio"]
        subtotal = galones * PRECIOS[item["producto"]]
        venta_bruta_acumulada += subtotal
        
        with c5:
            if galones > 0:
                st.markdown(f'<span class="txt-small" style="color:#28a745">+{galones:,.2f} gl</span>', unsafe_allow_html=True)

    # --- BLOQUES DE FILAS ---
    st.markdown('<div class="mod-header">MODULO 1 (01 - 08)</div>', unsafe_allow_html=True)
    for i in range(0, 8): render_fila_pistero(i)

    st.markdown('<div class="mod-header">MODULO 2 (09 - 16)</div>', unsafe_allow_html=True)
    for i in range(8, 16): render_fila_pistero(i)

    st.markdown('<div class="mod-header">MODULO 3 (17 - 22)</div>', unsafe_allow_html=True)
    for i in range(16, 22): render_fila_pistero(i)

    st.divider()
    st.metric("VENTA TOTAL ACUMULADA", f"S/ {venta_bruta_acumulada:,.2f}")

# --- PESTAÑAS SECUNDARIAS ---
with tab2:
    st.markdown('<div class="mod-header">GASTOS OPERATIVOS</div>', unsafe_allow_html=True)
    with st.form("g", clear_on_submit=True):
        c1, c2 = st.columns([3,1])
        d = c1.text_input("Concepto")
        m = c2.number_input("S/", min_value=0.0)
        if st.form_submit_button("Añadir"):
            if d: st.session_state.gastos.append({"Descripción": d, "Monto": m}); st.rerun()
    st.table(pd.DataFrame(st.session_state.gastos)) if st.session_state.gastos else None

with tab3:
    st.markdown('<div class="mod-header">VALES DE CRÉDITO</div>', unsafe_allow_html=True)
    with st.form("v", clear_on_submit=True):
        c1, c2 = st.columns([3,1])
        cl = c1.text_input("Cliente/Placa")
        v = c2.number_input("S/", min_value=0.0)
        if st.form_submit_button("Añadir"):
            if cl: st.session_state.vales.append({"Cliente": cl, "Monto": v}); st.rerun()
    st.table(pd.DataFrame(st.session_state.vales)) if st.session_state.vales else None

with tab4:
    total_g = sum(g["Monto"] for g in st.session_state.gastos)
    total_v = sum(v["Monto"] for v in st.session_state.vales)
    neto = venta_bruta_acumulada - total_g - total_v
    
    st.markdown(f"""
        <div style="background-color:white; border:2px solid black; padding:15px;">
            <h3 style="margin-top:0;">RESUMEN FINAL</h3>
            Venta Bruta: S/ {venta_bruta_acumulada:,.2f}<br>
            Gastos: S/ {total_g:,.2f}<br>
            Vales: S/ {total_v:,.2f}<hr>
            <h2 style="margin:0; color:green;">NETO A DEPOSITAR: S/ {neto:,.2f}</h2>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("FINALIZAR TURNO", use_container_width=True):
        st.success("REGISTRO GUARDADO.")
