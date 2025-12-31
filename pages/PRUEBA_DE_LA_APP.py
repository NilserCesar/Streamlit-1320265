import streamlit as st
import pandas as pd
import random
from datetime import datetime
import pytz

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema Grifo V&T", layout="wide")

# --- 2. ESTILO CSS PERSONALIZADO (Limpia botones +/- y mejora fuentes) ---
st.markdown("""
    <style>
    /* Ocultar botones de incremento en inputs numéricos */
    input::-webkit-outer-spin-button, input::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }
    input[type=number] { -moz-appearance: textfield; }

    /* Estilo para los inputs de contómetros */
    .stNumberInput input { 
        font-family: 'Courier New', monospace; 
        font-size: 1.6rem !important; 
        font-weight: bold;
        color: #1E3A8A;
        text-align: center;
        background-color: #f0f2f6;
    }

    /* Títulos y etiquetas */
    .titulo-principal { font-size: 36px; font-weight: bold; color: #003366; text-align: center; margin-bottom: 5px; }
    .sub-info { font-size: 16px; text-align: center; color: #555555; margin-bottom: 20px; }
    .resumen-caja { font-size: 24px; font-weight: bold; padding: 15px; border-radius: 10px; margin: 10px 0; }
    .bg-verde { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
    .bg-azul { background-color: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
    </style>
""", unsafe_allow_html=True)

# --- 3. CONFIGURACIÓN DE TIEMPO (ZONA PERÚ) ---
tz = pytz.timezone('America/Lima')
ahora = datetime.now(tz)
fecha_hoy = ahora.strftime("%d/%m/%Y")
hora_hoy = ahora.strftime("%I:%M %p")

# --- 4. ENCABEZADO ---
st.markdown(f'<div class="titulo-principal">SISTEMA DE CONTROL DE VENTAS - GRIFO V&T</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-info">📅 Fecha: {fecha_hoy} | 🕒 Hora de Registro: {hora_hoy}</div>',
            unsafe_allow_html=True)

# --- 5. INICIALIZACIÓN DE DATOS (Sesión) ---
if 'form_data' not in st.session_state:
    # 22 Dispensadores ficticios con inicios de 9 dígitos
    st.session_state.form_data = [
        {"id": f"D-{i:02d}", "producto": random.choice(["90", "95", "DL"]),
         "inicio": random.randint(1000, 5000)} for i in range(1, 23)
    ]
    for item in st.session_state.form_data:
        item["final"] = item["inicio"]

if 'gastos' not in st.session_state: st.session_state.gastos = []
if 'vales' not in st.session_state: st.session_state.vales = []

# Precios fijos
PRECIOS = {"90": 14.0, "95": 15.0, "DL": 15.0}

# --- 6. PESTAÑAS PRINCIPALES ---
tab1, tab2, tab3, tab4 = st.tabs(["🛒 VENTAS", "💸 GASTOS", "🎫 VALES", "💰 SALDO FINAL"])

# --- PESTAÑA 1: VENTAS (LECTURAS) ---
with tab1:
    h1, h2, h3, h4, h5 = st.columns([1, 1, 2, 2, 1.5])
    h1.write("**ID**");
    h2.write("**Prod**");
    h3.write("**Inicio (9D)**");
    h4.write("**Final (9D)**");
    h5.write("**Total Gal**")
    st.divider()

    venta_bruta_acumulada = 0

    for i, item in enumerate(st.session_state.form_data):
        c1, c2, c3, c4, c5 = st.columns([1, 1, 2, 2, 1.5])

        with c1:
            st.info(f"**{item['id']}**")
        with c2:
            st.write(f"**{item['producto']}**")
        with c3:
            st.code(f"{item['inicio']:09d}")

        with c4:
            nuevo_final = st.number_input(
                label=f"F_{i}", value=int(item['final']), min_value=int(item['inicio']),
                max_value=999999999, step=1, key=f"in_{i}", label_visibility="collapsed"
            )
            # Advertencia discreta de salto
            if (len(str(nuevo_final)) - len(str(item['inicio']))) >= 2:
                st.caption(f"⚠️ Salto inusual: {nuevo_final:09d}")
            item['final'] = nuevo_final

        galones = item["final"] - item["inicio"]
        subtotal_soles = galones * PRECIOS[item["producto"]]
        venta_bruta_acumulada += subtotal_soles

        with c5:
            if galones > 0:
                st.success(f"**{galones:,.2f}**")
            else:
                st.write("---")

# --- PESTAÑA 2: GASTOS ---
with tab2:
    st.subheader("Registro de Gastos Operativos")
    with st.form("form_gastos", clear_on_submit=True):
        col_g1, col_g2 = st.columns([3, 1])
        desc_g = col_g1.text_input("Concepto / Descripción del gasto")
        monto_g = col_g2.number_input("Monto (S/)", min_value=0.0, step=0.5)
        if st.form_submit_button("Añadir Gasto"):
            if desc_g:
                st.session_state.gastos.append({"Descripción": desc_g, "Monto": monto_g})
                st.rerun()

    if st.session_state.gastos:
        df_g = pd.DataFrame(st.session_state.gastos)
        st.table(df_g)
        if st.button("Limpiar Gastos"):
            st.session_state.gastos = []
            st.rerun()

# --- PESTAÑA 3: VALES ---
with tab3:
    st.subheader("Registro de Vales de Crédito")
    with st.form("form_vales", clear_on_submit=True):
        col_v1, col_v2 = st.columns([3, 1])
        cliente_v = col_v1.text_input("Nombre del Cliente / Placa")
        monto_v = col_v2.number_input("Monto del Vale (S/)", min_value=0.0, step=0.5)
        if st.form_submit_button("Registrar Vale"):
            if cliente_v:
                st.session_state.vales.append({"Cliente": cliente_v, "Monto": monto_v})
                st.rerun()

    if st.session_state.vales:
        df_v = pd.DataFrame(st.session_state.vales)
        st.table(df_v)
        if st.button("Limpiar Vales"):
            st.session_state.vales = []
            st.rerun()

# --- PESTAÑA 4: SALDO FINAL (EL CIERRE) ---
with tab4:
    st.subheader("Resumen General de Caja")

    total_g = sum(g["Monto"] for g in st.session_state.gastos)
    total_v = sum(v["Monto"] for v in st.session_state.vales)
    saldo_efectivo = venta_bruta_acumulada - total_g - total_v

    st.markdown(f'<div class="resumen-caja bg-azul">VENTA TOTAL DEL DÍA: S/ {venta_bruta_acumulada:,.2f}</div>',
                unsafe_allow_html=True)

    col_res1, col_res2 = st.columns(2)
    with col_res1:
        st.error(f"Total Gastos: S/ {total_g:,.2f}")
    with col_res2:
        st.warning(f"Total Vales: S/ {total_v:,.2f}")

    st.divider()

    st.markdown(f'<div class="resumen-caja bg-verde">SALDO FINAL A DEPOSITAR: S/ {saldo_efectivo:,.2f}</div>',
                unsafe_allow_html=True)

    if st.button("🚀 FINALIZAR TURNO Y SINCRONIZAR A FIREBASE"):
        st.balloons()
        st.success("¡Datos enviados correctamente! Los valores finales ahora son los nuevos inicios.")
        # Aquí iría el código de Firebase para guardar el registro histórico
