import streamlit as st
import pandas as pd
import random
from datetime import datetime

# =================================================================
# === 1. CONFIGURACIÓN DE PÁGINA (BLOQUEO DE SIDEBAR) =============
# =================================================================
st.set_page_config(page_title="Modo Simulación - SENATI", layout="wide")

st.markdown("""
    <style>
        [data-testid="stSidebar"], [data-testid="stSidebarNav"], button[data-testid="stSidebarToggle"] {
            display: none !important;
        }
        [data-testid="stAppViewContainer"] { margin-left: 0px !important; }
        .firma-autor { text-align: center; color: #1E3A8A; font-size: 16px; font-weight: bold; padding: 10px; border: 2px dashed #1E3A8A; border-radius: 10px; margin-bottom: 20px; }
        .stNumberInput input { font-family: 'Courier New', monospace; font-size: 1.5rem !important; font-weight: bold; text-align: center; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="firma-autor">🛠️ MODO SIMULACIÓN DE ENTREGA FINAL<br>Hecho Nilser Cesar Tuero Mayta - Senati</div>', unsafe_allow_html=True)

# =================================================================
# === 2. GENERACIÓN DE DATOS FAKE (SIN CONEXIÓN) ==================
# =================================================================

# Precios aleatorios simulados
PRECIOS_FAKE = {"90": 15.40, "95": 16.80, "DL": 17.20}

# Generar 22 dispensadores con lecturas iniciales aleatorias
if 'dispensadores' not in st.session_state:
    data = []
    for i in range(1, 23):
        prod = random.choice(["90", "95", "DL"])
        lectura_ini = random.randint(100000, 500000)
        data.append({
            "pump_id": f"LADO-{i:02d}",
            "product_id": prod,
            "initial_reading": lectura_ini,
            "final_reading": lectura_ini # Empezamos con final = inicial
        })
    st.session_state.dispensadores = data

# =================================================================
# === 3. INTERFAZ DE USUARIO (PRUEBA) =============================
# =================================================================

st.title("⛽ Simulador de Control de Contómetros")
st.info("Esta versión utiliza datos aleatorios para demostrar la lógica del sistema sin requerir conexión a Firebase.")

tab1, tab2 = st.tabs(["📝 Registro de Lecturas", "📊 Reporte Generado"])

with tab1:
    st.subheader("Ingreso de Lecturas Finales")
    
    # Creamos un formulario simulado
    total_venta_simulada = 0
    
    col1, col2, col3, col4 = st.columns([1, 1, 2, 1])
    col1.write("**Bomba**")
    col2.write("**Prod.**")
    col3.write("**Lectura Final (9D)**")
    col4.write("**Galones**")
    st.divider()

    for i, pump in enumerate(st.session_state.dispensadores):
        c1, c2, c3, c4 = st.columns([1, 1, 2, 1])
        c1.info(f"**{pump['pump_id']}**")
        c2.write(pump['product_id'])
        
        # Input de lectura final
        nuevo_final = c3.number_input(
            label=f"L_{i}",
            value=int(pump['final_reading']),
            min_value=int(pump['initial_reading']),
            step=1,
            key=f"input_fake_{i}",
            label_visibility="collapsed"
        )
        st.session_state.dispensadores[i]['final_reading'] = nuevo_final
        
        galones = nuevo_final - pump['initial_reading']
        total_venta_simulada += (galones * PRECIOS_FAKE[pump['product_id']])
        
        if galones > 0:
            c4.success(f"{galones:,.2f}")
        else:
            c4.write("0.00")

with tab2:
    st.subheader("Resultado de la Liquidación (Simulado)")
    
    # Simular Gastos y Vales aleatorios
    gasto_f = 150.00
    vale_f = 85.50
    saldo_f = total_venta_simulada - gasto_f - vale_f
    
    res1, res2, res3 = st.columns(3)
    res1.metric("Venta Bruta Total", f"S/ {total_venta_simulada:,.2f}")
    res2.metric("Egresos (Gastos + Vales)", f"S/ {gasto_f + vale_f:,.2f}", delta_color="inverse")
    res3.metric("Saldo Neto a Depositar", f"S/ {saldo_f:,.2f}")
    
    st.divider()
    if st.button("💾 SIMULAR ENVÍO A NUBE"):
        st.balloons()
        st.success("SIMULACIÓN EXITOSA: Los datos fueron procesados localmente. En la versión real, estos datos se sincronizan con Firebase y GitHub.")

# Botón para regresar al login real
st.divider()
if st.button("⬅️ VOLVER AL ACCESO REAL"):
    st.switch_page("app.py")
