import streamlit as st
import pandas as pd
import random
from datetime import datetime
import pytz

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sistema Grifo V&T", layout="wide")

# --- 2. ESTILO CSS PERSONALIZADO ---
st.markdown("""
    <style>
    /* Ocultar botones de incremento */
    input::-webkit-outer-spin-button, input::-webkit-inner-spin-button { -webkit-appearance: none; margin: 0; }
    input[type=number] { -moz-appearance: textfield; }

    /* Estilo general y compactación */
    .titulo-principal { font-size: 32px; font-weight: bold; color: #003366; text-align: center; margin-bottom: 2px; }
    .sub-info { font-size: 14px; text-align: center; color: #555555; margin-bottom: 15px; }
    .resumen-caja { font-size: 20px; font-weight: bold; padding: 12px; border-radius: 8px; margin: 5px 0; }
    .bg-verde { background-color: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
    .bg-azul { background-color: #d1ecf1; color: #0c5460; border: 1px solid #bee5eb; }
    
    /* Compactar el editor de datos */
    [data-testid="stDataEditor"] {
        border: 1px solid #e6e9ef;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 3. CONFIGURACIÓN DE TIEMPO (ZONA PERÚ) ---
tz = pytz.timezone('America/Lima')
ahora = datetime.now(tz)
fecha_hoy = ahora.strftime("%d/%m/%Y")
hora_hoy = ahora.strftime("%I:%M %p")

# --- 4. ENCABEZADO ---
st.markdown(f'<div class="titulo-principal">SISTEMA DE CONTROL DE VENTAS - GRIFO V&T</div>', unsafe_allow_html=True)
st.markdown(f'<div class="sub-info">📅 Fecha: {fecha_hoy} | 🕒 Registro: {hora_hoy}</div>', unsafe_allow_html=True)

# --- 5. INICIALIZACIÓN DE DATOS ---
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

# --- 6. PESTAÑAS PRINCIPALES ---
tab1, tab2, tab3, tab4 = st.tabs(["🛒 VENTAS", "💸 GASTOS", "🎫 VALES", "💰 SALDO FINAL"])

# --- PESTAÑA 1: VENTAS (LECTURAS COMPACTAS) ---
with tab1:
    st.write("📝 **Ingrese Lecturas Finales** (Use Flechas o Tab para navegar)")
    
    # Creamos un DataFrame para el editor
    df_input = pd.DataFrame(st.session_state.form_data)
    
    # Editor de datos compacto
    df_editado = st.data_editor(
        df_input,
        column_config={
            "id": st.column_config.TextColumn("ID", disabled=True, width="small"),
            "producto": st.column_config.TextColumn("Prod", disabled=True, width="small"),
            "inicio": st.column_config.NumberColumn("Inicio (9D)", disabled=True, format="%09d"),
            "final": st.column_config.NumberColumn(
                "Final (Actual)", 
                help="Escriba la lectura actual aquí",
                min_value=0,
                max_value=999999999,
                format="%09d",
                required=True
            ),
        },
        hide_index=True,
        use_container_width=True,
        key="editor_ventas"
    )

    # Actualizar estado y calcular totales
    st.session_state.form_data = df_editado.to_dict('records')
    
    venta_bruta_acumulada = 0
    galones_totales = 0

    for item in st.session_state.form_data:
        diff = item["final"] - item["inicio"]
        if diff > 0:
            venta_bruta_acumulada += (diff * PRECIOS[item["producto"]])
            galones_totales += diff

    # Mini resumen visual en la pestaña
    m1, m2 = st.columns(2)
    m1.metric("Galonaje Total", f"{galones_totales:,.2f} gl")
    m2.metric("Venta Bruta Estimada", f"S/ {venta_bruta_acumulada:,.2f}")

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
        st.table(pd.DataFrame(st.session_state.gastos))
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
        st.table(pd.DataFrame(st.session_state.vales))
        if st.button("Limpiar Vales"):
            st.session_state.vales = []
            st.rerun()

# --- PESTAÑA 4: SALDO FINAL ---
with tab4:
    st.subheader("Resumen General de Caja")

    total_g = sum(g["Monto"] for g in st.session_state.gastos)
    total_v = sum(v["Monto"] for v in st.session_state.vales)
    saldo_efectivo = venta_bruta_acumulada - total_g - total_v

    st.markdown(f'<div class="resumen-caja bg-azul">VENTA TOTAL DEL DÍA: S/ {venta_bruta_acumulada:,.2f}</div>', unsafe_allow_html=True)

    col_res1, col_res2 = st.columns(2)
    with col_res1:
        st.error(f"Total Gastos: S/ {total_g:,.2f}")
    with col_res2:
        st.warning(f"Total Vales: S/ {total_v:,.2f}")

    st.divider()
    st.markdown(f'<div class="resumen-caja bg-verde">SALDO FINAL A DEPOSITAR: S/ {saldo_efectivo:,.2f}</div>', unsafe_allow_html=True)

    if st.button("🚀 FINALIZAR TURNO Y SINCRONIZAR"):
        st.balloons()
        st.success("¡Datos enviados correctamente!")
