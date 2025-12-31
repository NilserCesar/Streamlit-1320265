# pages/1_Reportes.py
import streamlit as st
import pandas as pd
from datetime import datetime
from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter, FieldOperator

# === 1. CONFIGURACIÓN Y SEGURIDAD ===
st.set_page_config(page_title="Reporte Diario de Contabilidad", page_icon="📈", layout="wide")

# CSS para ocultar el menú lateral (Manteniendo consistencia con tu app.py)
st.markdown("""
    <style>
        [data-testid="stSidebar"], [data-testid="stSidebarNav"], button[data-testid="stSidebarToggle"] {
            display: none !important;
        }
        [data-testid="stAppViewContainer"] { margin-left: 0px !important; }
        .firma-autor { text-align: center; color: #555555; font-size: 14px; font-weight: bold; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="firma-autor">Hecho Nilser Cesar Tuero Mayta - Senati</div>', unsafe_allow_html=True)

ROL_PERMITIDO = "Administrador"

if 'is_authenticated' not in st.session_state or not st.session_state.is_authenticated:
    st.warning("🔒 Debes iniciar sesión para acceder. Vuelve a la página principal.")
    if st.button("Ir al Login"):
        st.switch_page("app.py")
    st.stop()
    
if st.session_state.user_role != ROL_PERMITIDO:
    st.error(f"🚫 Acceso denegado. Rol '{st.session_state.user_role}' no autorizado.")
    st.stop()

# === 2. INICIALIZACIÓN DE DB ===
try:
    db = firestore.client()
except Exception:
    st.error("Error: Conexión a Firebase no inicializada.")
    st.stop()

st.title("📈 Reporte Diario de Contabilidad")

# --- CONFIGURACIÓN DE FECHA ---
col_f1, col_f2 = st.columns([2, 1])
with col_f1:
    report_date = st.date_input("Selecciona la Fecha del Reporte:", datetime.now().date())
with col_f2:
    if st.button("🔄 Actualizar Datos"):
        st.cache_data.clear()
        st.rerun()

start_of_day = datetime.combine(report_date, datetime.min.time())
end_of_day = datetime.combine(report_date, datetime.max.time())

# --- 3. FUNCIONES DE LECTURA ---
@st.cache_data(ttl=600)
def get_current_prices():
    prices = {}
    for product_id in ["90", "95", "DL"]:
        query = db.collection('products').where('product_id', '==', product_id).order_by('valid_from', direction=firestore.Query.DESCENDING).limit(1)
        doc = next(query.stream(), None)
        prices[product_id] = doc.to_dict()['price_per_gallon'] if doc else 0.0
    return prices

@st.cache_data(ttl=600)
def get_daily_readings(start_ts, end_ts):
    query = db.collection('daily_readings').where(filter=FieldFilter('reading_date', FieldOperator.GREATER_THAN_OR_EQUAL, start_ts)).where(filter=FieldFilter('reading_date', FieldOperator.LESS_THAN_OR_EQUAL, end_ts)).stream()
    return pd.DataFrame([doc.to_dict() for doc in query])

@st.cache_data(ttl=600)
def get_daily_transactions(start_ts, end_ts):
    query = db.collection('transactions').where(filter=FieldFilter('date', FieldOperator.GREATER_THAN_OR_EQUAL, start_ts)).where(filter=FieldFilter('date', FieldOperator.LESS_THAN_OR_EQUAL, end_ts)).stream()
    return pd.DataFrame([doc.to_dict() for doc in query])

# --- 4. PROCESAMIENTO DE DATOS ---
PRICES = get_current_prices()
df_readings = get_daily_readings(start_of_day, end_of_day)
df_trans = get_daily_transactions(start_of_day, end_of_day)

if df_readings.empty:
    st.warning(f"⚠️ No hay registros de ventas para el {report_date}")
else:
    # Cálculo de Ventas
    df_readings['galones'] = df_readings['final_reading'] - df_readings['initial_reading']
    df_readings['precio'] = df_readings['product_id'].map(PRICES)
    df_readings['subtotal'] = df_readings['galones'] * df_readings['precio']
    
    total_venta_bruta = df_readings['subtotal'].sum()
    
    # Separación de Transacciones
    gastos_total = 0
    vales_total = 0
    if not df_trans.empty:
        gastos_total = df_trans[df_trans['type'] == 'Gasto']['amount'].sum()
        vales_total = df_trans[df_trans['type'] == 'Vale']['amount'].sum()
    
    saldo_neto = total_venta_bruta - gastos_total - vales_total

    # --- 5. VISUALIZACIÓN ---
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Venta Bruta", f"S/ {total_venta_bruta:,.2f}")
    m2.metric("Total Gastos", f"S/ {gastos_total:,.2f}", delta_color="inverse")
    m3.metric("Total Vales", f"S/ {vales_total:,.2f}", delta_color="inverse")
    m4.metric("SALDO NETO", f"S/ {saldo_neto:,.2f}", delta=f"{saldo_neto/total_venta_bruta:.1%}" if total_venta_bruta > 0 else 0)

    st.subheader("Detalle de Contómetros")
    st.dataframe(df_readings[['pump_id', 'product_id', 'initial_reading', 'final_reading', 'galones', 'subtotal']], use_container_width=True)

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.subheader("Detalle de Gastos")
        if not df_trans.empty and 'Gasto' in df_trans['type'].values:
            st.table(df_trans[df_trans['type'] == 'Gasto'][['description', 'amount']])
        else: st.write("No hay gastos.")
        
    with col_t2:
        st.subheader("Detalle de Vales")
        if not df_trans.empty and 'Vale' in df_trans['type'].values:
            st.table(df_trans[df_trans['type'] == 'Vale'][['description', 'amount']])
        else: st.write("No hay vales.")

if st.button("⬅️ Volver / Cerrar Sesión"):
    st.session_state.is_authenticated = False
    st.switch_page("app.py")
