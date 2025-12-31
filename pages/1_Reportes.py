import streamlit as st
import pandas as pd
import random
from datetime import datetime, date, timedelta

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Reporte Histórico V&T", layout="wide")

# CSS para mantener la interfaz limpia sin menús laterales
st.markdown("""
    <style>
        [data-testid="stSidebar"], [data-testid="stSidebarNav"], button[data-testid="stSidebarToggle"] { display: none !important; }
        [data-testid="stAppViewContainer"] { margin-left: 0px !important; }
        .main-title { color: #003366; font-size: 28px; font-weight: bold; text-align: center; }
        .stMetric { background-color: #f8f9fa; border: 1px solid #e0e0e0; padding: 10px; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div style="text-align: center; color: gray;">Hecho Nilser Cesar Tuero Mayta - Senati</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">📈 AUDITORÍA CONTABLE: HISTORIAL DE VENTAS</div>', unsafe_allow_html=True)

# --- 2. GENERADOR DE DATOS FAKE (OCTUBRE - DICIEMBRE) ---
@st.cache_data
def generar_data_historica():
    fecha_inicio = date(2025, 10, 1)
    fecha_fin = date(2025, 12, 30)
    delta = (fecha_fin - fecha_inicio).days
    
    lista_resumen = []
    lista_bombas = []
    
    for i in range(delta + 1):
        actual = fecha_inicio + timedelta(days=i)
        # Generar venta diaria entre 5,000 y 20,000
        v_bruta = random.uniform(5000, 20000)
        gastos = v_bruta * random.uniform(0.02, 0.05)
        vales = v_bruta * random.uniform(0.01, 0.04)
        
        lista_resumen.append({
            "Fecha": actual,
            "Venta Bruta": round(v_bruta, 2),
            "Gastos": round(gastos, 2),
            "Vales": round(vales, 2),
            "Saldo Neto": round(v_bruta - gastos - vales, 2)
        })
        
        # Simular detalle de los 22 contómetros para ese día
        for b in range(1, 23):
            lista_bombas.append({
                "Fecha": actual,
                "Bomba": f"LADO-{b:02d}",
                "Producto": random.choice(["90 Oct", "95 Oct", "Diesel"]),
                "Venta Soles": round(v_bruta / 22, 2)
            })
            
    return pd.DataFrame(lista_resumen), pd.DataFrame(lista_bombas)

df_diario, df_bombas = generar_data_historica()

# --- 3. FILTROS DE RANGO DE FECHAS ---
st.write("### 🔍 Filtros de Auditoría")
c1, c2 = st.columns(2)
with c1:
    f_inicio = st.date_input("Desde:", date(2025, 10, 1), min_value=date(2025, 10, 1), max_value=date(2025, 12, 30))
with c2:
    f_fin = st.date_input("Hasta:", date(2025, 12, 30), min_value=date(2025, 10, 1), max_value=date(2025, 12, 30))

# Filtrado de datos
df_filtrado = df_diario[(df_diario['Fecha'] >= f_inicio) & (df_diario['Fecha'] <= f_fin)]

# --- 4. PANEL DE MÉTRICAS ACUMULADAS ---
st.divider()
total_v = df_filtrado['Venta Bruta'].sum()
total_g = df_filtrado['Gastos'].sum()
total_s = df_filtrado['Saldo Neto'].sum()

m1, m2, m3 = st.columns(3)
m1.metric("Venta Bruta Acumulada", f"S/ {total_v:,.2f}")
m2.metric("Total Egresos (Gastos/Vales)", f"S/ {(total_v - total_s):,.2f}", delta_color="inverse")
m3.metric("Saldo Neto en Caja", f"S/ {total_s:,.2f}")

# --- 5. GRÁFICO DE DESEMPEÑO ---
st.subheader("📊 Comportamiento de Ventas Diarias")
st.line_chart(df_filtrado.set_index('Fecha')['Venta Bruta'])


# --- 6. LISTADO DETALLADO ---
t1, t2 = st.tabs(["📅 Resumen por Día", "⛽ Detalle por Dispensador"])

with t1:
    st.dataframe(df_filtrado.sort_values(by="Fecha", ascending=False), use_container_width=True, hide_index=True)

with t2:
    fecha_sel = st.selectbox("Seleccione un día para ver los 22 contómetros:", df_filtrado['Fecha'])
    df_detalle_dia = df_bombas[df_bombas['Fecha'] == fecha_sel]
    st.table(df_detalle_dia[['Bomba', 'Producto', 'Venta Soles']])

# --- 7. CIERRE ---
st.divider()
if st.button("⬅️ Volver al Panel de Prueba"):
    st.switch_page("pages/PRUEBA_DE_LA_APP.py")
