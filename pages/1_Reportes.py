import streamlit as st
import pandas as pd
import random
from datetime import datetime, date, timedelta

# --- CONFIGURACIÓN Y ESTILO ---
st.set_page_config(page_title="Reporte Histórico V&T", layout="wide")

st.markdown("""
    <style>
        [data-testid="stSidebar"], [data-testid="stSidebarNav"], button[data-testid="stSidebarToggle"] { display: none !important; }
        [data-testid="stAppViewContainer"] { margin-left: 0px !important; }
        .main-title { color: #003366; font-size: 30px; font-weight: bold; text-align: center; }
        .stMetric { background-color: #f0f2f6; padding: 15px; border-radius: 10px; border: 1px solid #d1d5db; }
    </style>
""", unsafe_allow_html=True)

st.markdown(f'<div style="text-align: center; color: gray;">Hecho Nilser Cesar Tuero Mayta - Senati</div>', unsafe_allow_html=True)
st.markdown(f'<div class="main-title">📈 AUDITORÍA DE VENTAS: OCT - DIC 2025</div>', unsafe_allow_html=True)

# --- GENERACIÓN DE DATOS HISTÓRICOS (FAKERS) ---
@st.cache_data
def generar_historial():
    fecha_inicio = date(2025, 10, 1)
    fecha_fin = date(2025, 12, 30)
    delta = (fecha_fin - fecha_inicio).days
    
    registros_diarios = []
    detalles_contometros = []
    
    for i in range(delta + 1):
        actual = fecha_inicio + timedelta(days=i)
        # Venta total del día entre 5k y 20k
        venta_dia = random.uniform(5000, 20000)
        gastos = venta_dia * random.uniform(0.05, 0.1) # 5-10% gastos
        vales = venta_dia * random.uniform(0.02, 0.08)  # 2-8% vales
        
        registros_diarios.append({
            "Fecha": actual,
            "Venta Bruta": venta_dia,
            "Gastos": gastos,
            "Vales": vales,
            "Saldo Neto": venta_dia - gastos - vales
        })
        
        # Simular los 22 contómetros para ese día específico
        for c in range(1, 23):
            detalles_contometros.append({
                "Fecha": actual,
                "Bomba": f"B-{c:02d}",
                "Producto": random.choice(["90", "95", "DL"]),
                "Venta (S/)": venta_dia / 22 # Reparto equitativo aprox.
            })
            
    return pd.DataFrame(registros_diarios), pd.DataFrame(detalles_contometros)

df_resumen, df_detalles = generar_historial()

# --- FILTROS DE FECHA ---
st.sidebar.header("Filtros")
col_f1, col_f2 = st.columns(2)
with col_f1:
    f_inicio = st.date_input("Fecha Inicio", date(2025, 10, 1), min_value=date(2025, 10, 1), max_value=date(2025, 12, 30))
with col_f2:
    f_fin = st.date_input("Fecha Fin", date(2025, 12, 30), min_value=date(2025, 10, 1), max_value=date(2025, 12, 30))

# Filtrar DataFrames
mask = (df_resumen['Fecha'] >= f_inicio) & (df_resumen['Fecha'] <= f_fin)
df_filtrado = df_resumen.loc[mask]

mask_det = (df_detalles['Fecha'] >= f_inicio) & (df_detalles['Fecha'] <= f_fin)
df_det_filtrado = df_detalles.loc[mask_det)

# --- PANEL DE MÉTRICAS TOTALES ---
st.divider()
t_venta = df_filtrado['Venta Bruta'].sum()
t_gastos = df_filtrado['Gastos'].sum()
t_vales = df_filtrado['Vales'].sum()
t_neto = df_filtrado['Saldo Neto'].sum()

m1, m2, m3, m4 = st.columns(4)
m1.metric("Venta Bruta Total", f"S/ {t_venta:,.2f}")
m2.metric("Total Gastos", f"S/ {t_gastos:,.2f}")
m3.metric("Total Vales", f"S/ {t_vales:,.2f}")
m4.metric("Saldo Líquido", f"S/ {t_neto:,.2f}")

# --- GRÁFICO DE TENDENCIA ---
st.subheader("📊 Tendencia de Ventas Diarias")
st.line_chart(df_filtrado.set_index('Fecha')['Venta Bruta'])



# --- TABLAS DE DETALLES ---
col_t1, col_t2 = st.columns([2, 3])

with col_t1:
    st.subheader("📅 Resumen por Día")
    st.dataframe(df_filtrado.sort_values('Fecha', ascending=False), hide_index=True)

with col_t2:
    st.subheader("⛽ Detalle por Contómetro (22)")
    # Selector de fecha específica para ver los 22
    fecha_sel = st.selectbox("Ver detalle de contómetros para:", df_filtrado['Fecha'])
    df_dia_22 = df_det_filtrado[df_det_filtrado['Fecha'] == fecha_sel]
    st.table(df_dia_22[['Bomba', 'Producto', 'Venta (S/)']])

# --- BOTÓN DE SALIDA ---
st.divider()
if st.button("⬅️ Volver al Panel de Prueba"):
    st.switch_page("pages/PRUEBA_DE_LA_APP.py")
