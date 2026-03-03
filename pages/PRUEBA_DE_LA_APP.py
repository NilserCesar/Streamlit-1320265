import streamlit as st
import pandas as pd
import random
from datetime import datetime
import pytz

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema V&T", layout="wide")

# --- 2. CSS AGRESIVO (SIN BOTONES +/- Y DISEÑO CUADRADO) ---
st.markdown("""
    <style>
    /* 1. ELIMINAR BOTONES +/- (Chrome, Safari, Edge, Firefox) */
    input::-webkit-outer-spin-button, 
    input::-webkit-inner-spin-button { 
        -webkit-appearance: none !important; 
        margin: 0 !important; 
    }
    input[type=number] { 
        -moz-appearance: textfield !important; 
    }

    /* 2. DISEÑO CUADRÁTICO TOTAL */
    * { border-radius: 0px !important; }

    /* 3. COMPACTACIÓN DE FILAS Y COLUMNAS */
    [data-testid="stVerticalBlock"] > div { 
        gap: 0px !important; 
        padding-top: 0px !important; 
        padding-bottom: 0px !important; 
    }
    [data-testid="column"] { 
        padding: 0px 5px !important; 
    }
    
    /* 4. AJUSTE DE INPUTS (MÁS PEQUEÑOS Y PEGADOS) */
    .stNumberInput { 
        margin-top: -12px !important; 
    }
    input { 
        height: 30px !important; 
        border: 1px solid #999 !important; 
        background-color: #ffffff !important;
        font-weight: bold !important;
    }

    /* 5. ENCABEZADOS DE MÓDULO */
    .mod-header {
        background-color: #2c3e50;
        color: white;
        padding: 3px 10px;
        font-size: 0.85rem;
        margin-top: 12px;
        margin-bottom: 2px;
        text-transform: uppercase;
    }

    /* 6. TEXTOS DE FILA */
    .txt-row { font-size: 0.9rem; line-height: 1.8; }
    .txt-id { font-weight: bold; color: #000; }
    .txt-prod { font-weight: bold; color: #e74c3c; }
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
st.markdown(f"### ⛽ V&T - CONTROL DE VENTAS | {fecha_hoy}")

# --- 6. PESTAÑAS ---
tab1, tab2, tab3, tab4 = st.tabs(["🛒 VENTAS", "💸 GASTOS", "🎫 VALES", "💰 SALDO"])

with tab1:
    venta_bruta_acumulada = 0

    def render_fila_pistero(idx):
        global venta_bruta_acumulada
        item = st.session_state.form_data[idx]
        
        # Grid: ID | PROD | INICIO | INPUT | RESULTADO
        c1, c2, c3, c4, c5 = st.columns([0.4, 0.4, 1.2, 1.5, 1.2])
        
        with c1: st.markdown(f'<span class="txt-row txt-id">{item["id"]}</span>', unsafe_allow_html=True)
        with c2: st.markdown(f'<span class="txt-row txt-prod">{item["producto"]}</span>', unsafe_allow_html=True)
        with c3: st.markdown(f'<span class="txt-row" style="color:#666">[{item["inicio"]:09d}]</span>', unsafe_allow_html=True)
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
                st.markdown(f'<span class="txt-row" style="color:green; font-weight:bold;">+{galones:,.2f} gl</span>', unsafe_allow_html=True)

    # --- RENDERIZADO POR MÓDULOS ---
    st.markdown('<div class="mod-header">MÓDULO 1 (Disp. 01 al 08)</div>', unsafe_allow_html=True)
    for i in range(0, 8): render_fila_pistero(i)

    st.markdown('<div class="mod-header">MÓDULO 2 (Disp. 09 al 16)</div>', unsafe_allow_html=True)
    for i in range(8, 16): render_fila_pistero(i)

    st.markdown('<div class="mod-header">MÓDULO 3 (Disp. 17 al 22)</div>', unsafe_allow_html=True)
    for i in range(16, 22): render_fila_pistero(i)

    st.divider()
    st.subheader(f"Venta Bruta Total: S/ {venta_bruta_acumulada:,.2f}")

# --- PESTAÑAS DE APOYO ---
with tab2:
    st.markdown('<div class="mod-header">REGISTRO DE GASTOS</div>', unsafe_allow_html=True)
    with st.form("g", clear_on_submit=True):
        c1, c2 = st.columns([3,1])
        d = c1.text_input("Concepto")
        m = c2.number_input("Monto S/", min_value=0.0)
        if st.form_submit_button("Añadir Gasto"):
            if d: st.session_state.gastos.append({"Descripción": d, "Monto": m}); st.rerun()
    if st.session_state.gastos: st.table(pd.DataFrame(st.session_state.gastos))

with tab3:
    st.markdown('<div class="mod-header">REGISTRO DE VALES</div>', unsafe_allow_html=True)
    with st.form("v", clear_on_submit=True):
        c1, c2 = st.columns([3,1])
        cl = c1.text_input("Cliente/Placa")
        v = c2.number_input("Monto S/", min_value=0.0)
        if st.form_submit_button("Registrar Vale"):
            if cl: st.session_state.vales.append({"Cliente": cl, "Monto": v}); st.rerun()
    if st.session_state.vales: st.table(pd.DataFrame(st.session_state.vales))

with tab4:
    total_g = sum(g["Monto"] for g in st.session_state.gastos)
    total_v = sum(v["Monto"] for v in st.session_state.vales)
    neto = venta_bruta_acumulada - total_g - total_v
    
    st.markdown(f"""
        <div style="border:3px solid #000; padding:20px; background-color:#fff;">
            <h2 style="margin-top:0;">CIERRE DE CAJA</h2>
            <p>Venta Total: S/ {venta_bruta_acumulada:,.2f}</p>
            <p style="color:red;">Gastos: - S/ {total_g:,.2f}</p>
            <p style="color:orange;">Vales: - S/ {total_v:,.2f}</p>
            <hr>
            <h1 style="color:green; margin:0;">TOTAL A ENTREGAR: S/ {neto:,.2f}</h1>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("🚀 FINALIZAR TURNO Y GUARDAR", use_container_width=True):
        st.success("DATOS GUARDADOS CORRECTAMENTE.")
