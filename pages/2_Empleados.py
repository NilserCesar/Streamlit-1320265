import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Personal V&T", layout="wide")

# CSS para ocultar menús y dar estilo a las tarjetas de personal
st.markdown("""
    <style>
        [data-testid="stSidebar"], [data-testid="stSidebarNav"], button[data-testid="stSidebarToggle"] { display: none !important; }
        [data-testid="stAppViewContainer"] { margin-left: 0px !important; }
        .jefe-card { background-color: #1E3A8A; color: white; padding: 20px; border-radius: 15px; text-align: center; }
        .grifero-card { background-color: #F3F4F6; padding: 15px; border-radius: 10px; border-left: 5px solid #10B981; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div style="text-align: center; color: gray;">Hecho Nilser Cesar Tuero Mayta - Senati</div>', unsafe_allow_html=True)
st.title("👥 Gestión de Planilla y Roles de Turno")

# --- 2. LÓGICA DE ROTACIÓN DE JEFES (15 DÍAS) ---
# Usamos el día del año para determinar quién vive en el grifo
hoy = datetime.now()
dia_del_año = hoy.timetuple().tm_yday
# Cada 15 días cambia el turno (0-14, 15-29, etc.)
ciclo_15 = (dia_del_año // 15) % 2

if ciclo_15 == 0:
    jefe_en_grifo = "JUAN"
    jefe_libre = "JOSE"
else:
    jefe_en_grifo = "JOSE"
    jefe_libre = "JUAN"

# --- 3. SECCIÓN JEFATURA DE PERSONAL ---
st.subheader("🏁 Jefatura de Personal (Residencia 15 días)")
col_j1, col_j2 = st.columns(2)

with col_j1:
    st.markdown(f"""
    <div class="jefe-card">
        <h2>🏠 EN RESIDENCIA: {jefe_en_grifo}</h2>
        <p><b>Sueldo:</b> S/ 1,900.00</p>
        <p><b>Función:</b> Encargado de orden y supervisión 24h</p>
        <p><b>Estado:</b> Activo en Grifo</p>
    </div>
    """, unsafe_allow_html=True)

with col_j2:
    st.info(f"**Personal de Relevo:** {jefe_libre}")
    st.write("🔄 **Sistema de Rotación:** Sale libre cada 15 días. El relevo entra a vivir en el grifo para garantizar la supervisión continua.")
    st.write(f"📅 **Fecha de hoy:** {hoy.strftime('%d/%m/%Y')}")

st.divider()

# --- 4. SECCIÓN GRIFEROS OPERATIVOS ---
st.subheader("⛽ Roles de Griferos (S/ 1,500.00)")
st.write("Turnos de 8 horas con viáticos incluidos. Rotación de 2 griferos por turno.")

griferos = ["VERONICA", "GUILLERMO", "CESAR", "GRIMALDA"]

# Simulación de turnos (2 trabajando, 2 descanso/otro turno)
c1, c2, c3, c4 = st.columns(4)
for i, nombre in enumerate(griferos):
    with [c1, c2, c3, c4][i]:
        estado = "🟢 EN TURNO" if i < 2 else "🟡 PRÓX. TURNO"
        st.markdown(f"""
        <div class="grifero-card">
            <h4>{nombre}</h4>
            <p>S/ 1,500.00</p>
            <p>{estado}</p>
            <small>Viáticos: OK</small>
        </div>
        """, unsafe_allow_html=True)

# --- 5. CUADRO DE PLANILLA PARA SENATI ---
st.subheader("📊 Resumen de Costos de Personal")

data_planilla = {
    "Empleado": ["JUAN", "JOSE", "VERONICA", "GUILLERMO", "CESAR", "GRIMALDA"],
    "Cargo": ["Jefe Personal", "Jefe Personal", "Grifero", "Grifero", "Grifero", "Grifero"],
    "Sueldo Base": [1900, 1900, 1500, 1500, 1500, 1500],
    "Viáticos": ["Hospedaje/Alim.", "Hospedaje/Alim.", "Alimentación", "Alimentación", "Alimentación", "Alimentación"]
}

df_planilla = pd.DataFrame(data_planilla)
st.table(df_planilla)

total_mensual = df_planilla["Sueldo Base"].sum()
st.metric("Total Planilla Mensual V&T", f"S/ {total_mensual:,.2f}")

# --- BOTÓN DE REGRESO ---
st.divider()
if st.button("⬅️ Volver al Panel de Prueba"):
    st.switch_page("pages/PRUEBA_DE_LA_APP.py")
