# pages/1_Reportes.py
import streamlit as st
import pandas as pd
from datetime import datetime
from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter, FieldOperator

ROL_PERMITIDO = "Administrador"
# === VERIFICACIÓN DE SEGURIDAD ===
if 'is_authenticated' not in st.session_state or not st.session_state.is_authenticated:
    # Bloquea si no ha iniciado sesión
    st.warning("🔒 Debes iniciar sesión para acceder a esta página. Vuelve a la página principal.")
    st.stop()
    
if st.session_state.user_role != ROL_PERMITIDO:
    # Bloquea si el rol no es el correcto (ej: si un "Despachador" intenta acceder)
    st.error(f"🚫 Acceso denegado. Tu rol de '{st.session_state.user_role}' no tiene permiso para ver los reportes.")
    st.stop()
# ==================================
st.set_page_config(page_title="Reporte Diario de Contabilidad", page_icon="📈")
st.title("📈 Reporte Diario de Contabilidad")

try:
    db = firestore.client()
except Exception:
    st.error("Error: Conexión a Firebase no inicializada.")
    st.stop()

# --- CONFIGURACIÓN DE FECHA ---
report_date = st.date_input("Selecciona la Fecha del Reporte:", datetime.now().date())
start_of_day = datetime.combine(report_date, datetime.min.time())
end_of_day = datetime.combine(report_date, datetime.max.time())


# --- FUNCIONES DE LECTURA (USAN CACHE) ---

@st.cache_data(ttl=600)
def get_current_prices():
    """Obtiene el precio vigente más reciente para cada producto."""
    prices = {}
    for product_id in ["90", "95", "DL"]:
        query = db.collection('products').where(
            'product_id', '==', product_id
        ).order_by('valid_from', direction=firestore.Query.DESCENDING).limit(1)
        doc = next(query.stream(), None)
        if doc:
            prices[product_id] = doc.to_dict()['price_per_gallon']
        else:
            prices[product_id] = 0.0
    return prices

@st.cache_data(ttl=600)
def get_daily_readings(start_ts, end_ts):
    """Obtiene los registros de contadores del día."""
    query = db.collection('daily_readings').where(
        filter=FieldFilter('reading_date', FieldOperator.GREATER_THAN_OR_EQUAL, start_ts)
    ).where(
        filter=FieldFilter('reading_date', FieldOperator.LESS_THAN_OR_EQUAL, end_ts)
    ).stream()
    return pd.DataFrame([doc.to_dict() for doc in query])

@st.cache_data(ttl=600)
def get_daily_transactions(start_ts, end_ts, transaction_type=None):
    """Obtiene transacciones (Gastos/Vales/Depósitos) del día."""
    query = db.collection('transactions').where(
        filter=FieldFilter('date', FieldOperator.GREATER_THAN_OR_EQUAL, start_ts)
    ).where(
        filter=FieldFilter('date', FieldOperator.LESS_THAN_OR_EQUAL, end_ts)
    )
    if transaction_type:
        query = query.where(filter=FieldFilter('type', FieldOperator.EQUAL, transaction_type))
    
    return pd.DataFrame([doc.to_dict() for doc in query.stream()])

# --- DATOS BASE ---
PRICES = get_current_prices()
df_readings = get_daily_readings(start_of_day, end_of_day)
df_transactions = get_daily_transactions(start_of_day, end_of_day)

# Manejo si no hay datos de lectura para el día
if df_readings.empty:
    st.warning(f"No hay registros de ventas de contómetro cargados para el {report_
