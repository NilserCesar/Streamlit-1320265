import streamlit as st
import pandas as pd
import random
from datetime import datetime
import pytz

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema Grifo V&T", layout="wide")

# --- 2. ESTILO CSS PARA COMPACTAR ---
st.markdown("""
    <style>
    /* Eliminar flechas de inputs numéricos */
    input::-webkit-outer-spin-button, input::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }
    input[type=number] { -moz-appearance: textfield; }

    /* Reducir espacio entre widgets de Streamlit */
    .stNumberInput { margin-bottom: -15px !important; }
    .stCaption { margin-top: -5px !important; font-size: 0.75rem !important; }
    
    /* Estilo para las cajitas de cada dispensador */
    .dispensador-box {
        padding: 8px;
        border: 1px solid #e0e0e0;
        border-radius: 5px;
        background-color: #fcfcfc;
        margin-bottom: 5px;
    }
    
    .label-id { font-weight: bold; color: #003366; font-size: 0.9rem; }
    .label-prod { color: #d32f2f; font-weight: bold; float: right; }

    .titulo-principal { font-size: 28px; font-weight: bold; color: #003366; text-align: center; }
    .sub-info { font-size: 14px; text-align: center; color: #555555; margin-bottom: 10px; }
    .header-modulo { 
        background-color: #003366; color: white; padding: 5px 15px; 
        border-radius: 5px; margin-top: 15px; margin-bottom: 10px; font-size: 1.1rem;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. CONFIGURACIÓN DE TIEMPO ---
tz = pytz.timezone('America/Lima')
ahora = datetime.now(tz)
fecha_hoy = ahora.strftime("%d/%m/%Y")
hora_hoy = ahora.strftime("%I:%M %p")

# --- 4. INICIALIZACIÓN DE DATOS ---
if 'form_data' not in st.session_state:
    # 22 Dispensadores
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
st.markdown('<div class="titulo-principal">SISTEMA DE CONTROL DE VENTAS - GRIFO V&T</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-info">📅 {fecha_hoy} | 🕒 {hora_hoy}</div>', unsafe_allow_html=True)

# --- 6. PESTAÑAS ---
tab1, tab2, tab3, tab4 = st.tabs(["🛒 VENTAS", "💸 GASTOS", "🎫 VALES", "💰 SALDO FINAL"])

with tab1:
    venta_bruta_acumulada = 0
    
    def render_surtidor(idx):
        global venta_bruta_acumulada
        item = st.session_state.form_data[idx]
        
        with st.container():
            st.markdown(f'''<div class="dispensador-box">
                <span class="label-id">{item["id"]}</span>
                <span class="label-prod">{item["producto"]}</span>
                <div style="font-family: monospace; font-size: 0.8rem; color: #666;">In: {item["inicio"]:09d}</div>
            </div>''', unsafe_allow_html=True)
            
            nuevo_final = st.number_input(
                label=f"F_{idx}", value=int(item['final']), 
                min_value=int(item['inicio']), max_value=999999999, 
                step=1, key=f"in_{idx}", label_visibility="collapsed"
            )
            
            item['final'] = nuevo_final
            galones = item["final"] - item["inicio"]
            subtotal = galones * PRECIOS[item["producto"]]
            venta_bruta_acumulada += subtotal
            
            if galones > 0:
                st.caption(f"✅ {galones:,.2f} gl | S/ {subtotal:,.2f}")
            else:
                st.caption("—")

    # --- MÓDULO 1 (1 al 8) ---
    st.markdown('<div class="header-modulo">MÓDULO 1: Dispensadores 01 - 08</div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    for i in range(0, 8):
        with [col1, col2, col3, col4][i % 4]:
            render_surtidor(i)

    # --- MÓDULO 2 (9 al 16) ---
    st.markdown('<div class="header-modulo">MÓDULO 2: Dispensadores 09 - 16</div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    for i in range(8, 16):
        with [col1, col2, col3, col4][i % 4]:
            render_surtidor(i)

    # --- MÓDULO 3 (17 al 22) ---
    st.markdown('<div class="header-modulo">MÓDULO 3: Dispensadores 17 - 22</div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    for i in range(16, 22):
        with [col1, col2, col3, col4][i % 4]:
            render_surtidor(i)

# --- PESTAÑA 2: GASTOS ---
with tab2:
    st.subheader("Registro de Gastos")
    with st.form("form_gastos", clear_on_submit=True):
        c1, c2 = st.columns([3, 1])
        desc_g = c1.text_input("Descripción")
        monto_g = c2.number_input("Monto", min_value=0.0, step=0.5)
        if st.form_submit_button("Añadir"):
            if desc_g:
                st.session_state.gastos.append({"Descripción": desc_g, "Monto": monto_g})
                st.rerun()
    if st.session_state.gastos:
        st.table(pd.DataFrame(st.session_state.gastos))
        if st.button("Limpiar Gastos"):
            st.session_state.gastos = []
            st.rerun()

# --- PESTAÑA 3: VALES ---
with tab3:
    st.subheader("Registro de Vales")
    with st.form("form_vales", clear_on_submit=True):
        c1, c2 = st.columns([3, 1])
        cliente_v = c1.text_input("Cliente/Placa")
        monto_v = c2.number_input("Importe", min_value=0.0, step=0.5)
        if st.form_submit_button("Registrar"):
            if cliente_v:
                st.session_state.vales.append({"Cliente": cliente_v, "Monto": monto_v})
                st.rerun()
    if st.session_state.vales:
        st.table(pd.DataFrame(st.session_state.vales))
        if st.button("Limpiar Vales"):
            st.session_state.vales = []
            st.rerun()

# --- PESTAÑA 4: SALDO FINAL ---
with tab4:
    total_g = sum(g["Monto"] for g in st.session_state.gastos)
    total_v = sum(v["Monto"] for v in st.session_state.vales)
    saldo_efectivo = venta_bruta_acumulada - total_g - total_v

    st.markdown(f'<div style="background-color:#e1f5fe; padding:20px; border-radius:10px; border: 2px solid #01579b;">'
                f'<h2 style="margin:0; color:#01579b;">RESUMEN DE CAJA</h2>'
                f'<p style="font-size:1.5rem; margin:10px 0;">Venta Bruta: <b>S/ {venta_bruta_acumulada:,.2f}</b></p>'
                f'<p style="color:red; margin:0;">(-) Gastos: S/ {total_g:,.2f}</p>'
                f'<p style="color:orange; margin:0;">(-) Vales: S/ {total_v:,.2f}</p>'
                f'<hr><h1 style="color:#2e7d32; margin:0;">A DEPOSITAR: S/ {saldo_efectivo:,.2f}</h1>'
                f'</div>', unsafe_allow_html=True)

    if st.button("🚀 FINALIZAR TURNO", use_container_width=True):
        st.balloons()
        st.success("Sincronización completa.")

