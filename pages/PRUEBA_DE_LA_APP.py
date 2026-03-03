import streamlit as st
import pandas as pd
import random
from datetime import datetime
import pytz

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema V&T - Registro", layout="wide")

# --- 2. CSS PARA DISEÑO ULTRA-COMPACTO ---
st.markdown("""
    <style>
    /* Eliminar flechas y reducir altura de inputs */
    input::-webkit-outer-spin-button, input::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }
    input[type=number] { 
        -moz-appearance: textfield; 
        height: 30px !important; 
        padding: 2px 5px !important;
        font-size: 1.1rem !important;
        font-weight: bold !important;
    }

    /* Reducir márgenes de las columnas y contenedores */
    [data-testid="column"] { padding: 0px 5px !important; }
    .stNumberInput { margin-bottom: 0px !important; }
    
    /* Estilo de fila */
    .fila-surtidor {
        display: flex;
        align-items: center;
        border-bottom: 1px solid #eee;
        padding: 2px 0;
    }
    
    .label-id { font-weight: bold; color: #003366; width: 50px; }
    .label-prod { font-weight: bold; color: #d32f2f; width: 40px; font-size: 0.8rem; }
    .label-inicio { font-family: monospace; color: #666; width: 100px; font-size: 0.9rem; }
    
    .header-modulo { 
        background-color: #f0f2f6; 
        color: #003366; 
        padding: 5px 15px; 
        border-radius: 5px; 
        margin-top: 15px; 
        font-weight: bold;
        border-left: 5px solid #003366;
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

if 'gastos' not in st.session_state: st.session_state.gastos = []
if 'vales' not in st.session_state: st.session_state.vales = []

PRECIOS = {"90": 14.0, "95": 15.0, "DL": 15.0}

# --- 5. ENCABEZADO ---
st.title("⛽ Control de Ventas - V&T")
st.caption(f"📅 Fecha: {fecha_hoy} | Zona Horaria: Lima, Perú")

# --- 6. PESTAÑAS ---
tab1, tab2, tab3, tab4 = st.tabs(["🛒 VENTAS", "💸 GASTOS", "🎫 VALES", "💰 SALDO"])

with tab1:
    venta_bruta_acumulada = 0

    def render_fila_compacta(idx):
        global venta_bruta_acumulada
        item = st.session_state.form_data[idx]
        
        # Usamos columnas de Streamlit muy ajustadas
        c1, c2, c3, c4, c5 = st.columns([0.5, 0.5, 1.2, 1.5, 1.2])
        
        with c1: st.markdown(f"**{item['id']}**")
        with c2: st.markdown(f"<span style='color:red'>{item['producto']}</span>", unsafe_allow_html=True)
        with c3: st.markdown(f"`{item['inicio']:09d}`")
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
                st.markdown(f"**{galones:,.2f}** gl")
            else:
                st.write("")

    # --- RENDERIZADO POR MÓDULOS ---
    
    st.markdown('<div class="header-modulo">MÓDULO 1 (Disp. 01 - 08)</div>', unsafe_allow_html=True)
    for i in range(0, 8):
        render_fila_compacta(i)

    st.markdown('<div class="header-modulo">MÓDULO 2 (Disp. 09 - 16)</div>', unsafe_allow_html=True)
    for i in range(8, 16):
        render_fila_compacta(i)

    st.markdown('<div class="header-modulo">MÓDULO 3 (Disp. 17 - 22)</div>', unsafe_allow_html=True)
    for i in range(16, 22):
        render_fila_compacta(i)

    st.divider()
    st.metric("VENTA BRUTA TOTAL", f"S/ {venta_bruta_acumulada:,.2f}")

# --- PESTAÑAS RESTANTES (GASTOS, VALES, SALDO) ---
# (Se mantienen igual para no alterar la lógica funcional)
with tab2:
    st.subheader("Gastos")
    with st.form("g"):
        c1, c2 = st.columns([3,1])
        d = c1.text_input("Descripción")
        m = c2.number_input("S/", min_value=0.0)
        if st.form_submit_button("Añadir"):
            if d: st.session_state.gastos.append({"Descripción": d, "Monto": m}); st.rerun()
    st.table(pd.DataFrame(st.session_state.gastos)) if st.session_state.gastos else None

with tab3:
    st.subheader("Vales")
    with st.form("v"):
        c1, c2 = st.columns([3,1])
        cl = c1.text_input("Cliente")
        v = c2.number_input("S/", min_value=0.0)
        if st.form_submit_button("Registrar"):
            if cl: st.session_state.vales.append({"Cliente": cl, "Monto": v}); st.rerun()
    st.table(pd.DataFrame(st.session_state.vales)) if st.session_state.vales else None

with tab4:
    total_g = sum(g["Monto"] for g in st.session_state.gastos)
    total_v = sum(v["Monto"] for v in st.session_state.vales)
    neto = venta_bruta_acumulada - total_g - total_v
    
    st.success(f"### SALDO FINAL: S/ {neto:,.2f}")
    if st.button("FINALIZAR Y GUARDAR", use_container_width=True):
        st.balloons()
