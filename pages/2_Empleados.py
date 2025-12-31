# pages/2_Empleados.py
import streamlit as st
import pandas as pd
from datetime import datetime

# --- 1. CONFIGURACIÓN DE PÁGINA (SIN NAVEGACIÓN LATERAL) ---
st.set_page_config(page_title="Personal V&T", layout="wide")

st.markdown("""
    <style>
        [data-testid="stSidebar"], [data-testid="stSidebarNav"], button[data-testid="stSidebarToggle"] { display: none !important; }
        [data-testid="stAppViewContainer"] { margin-left: 0px !important; }
        .jefe-card { background-color: #1E3A8A; color: white; padding: 25px; border-radius: 15px; text-align: center; box-shadow: 2px 2px 10px rgba(0,0,0,0.1); }
        .grifero-card { background-color: #ffffff; padding: 15px; border-radius: 10px; border-left: 5px solid #10B981; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); margin-bottom: 10px; }
        .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div style="text-align: center; color: gray; font-weight: bold;">Hecho Nilser Cesar Tuero Mayta - Senati</div>', unsafe_allow_html=True)
st.title("👥 Gestión de Personal y Roles de Turno")

# --- 2. LÓGICA DE ROTACIÓN DE JEFES (15 DÍAS) ---
hoy = datetime.now()
dia_del_año = hoy.timetuple().tm_yday
# Alterna cada 15 días: Juan (bloque 0), Jose (bloque 1)
ciclo_15 = (dia_del_año // 15) % 2

if ciclo_15 == 0:
    jefe_en_grifo, jefe_libre = "JUAN", "JOSE"
else:
    jefe_en_grifo, jefe_libre = "JOSE", "JUAN"

# --- 3. SECCIÓN JEFATURA ---
st.subheader("🏁 Jefatura de Personal (Residencia 15 días)")
col_j1, col_j2 = st.columns([2, 1])

with col_j1:
    st.markdown(f"""
    <div class="jefe-card">
        <h1 style='color: white;'>🏠 EN RESIDENCIA: {jefe_en_grifo}</h1>
        <p style='font-size: 18px;'><b>Encargado de Orden y Supervisión de Personal</b></p>
        <hr>
        <p><b>Sueldo Mensual:</b> S/ 1,900.00 | <b>Estado:</b> Viviendo en Grifo</p>
    </div>
    """, unsafe_allow_html=True)

with col_j2:
    st.info(f"**Personal Libre / Relevo:** {jefe_libre}")
    st.write("📌 **Regla de Negocio:**")
    st.write("- Rotación obligatoria cada 15 días.")
    st.write("- El jefe en turno supervisa las 24 horas.")
    st.write(f"📅 **Fecha Actual:** {hoy.strftime('%d/%m/%Y')}")

st.divider()

# --- 4. SECCIÓN GRIFEROS ---
st.subheader("⛽ Griferos Operativos (8 Horas / Viáticos Incluidos)")

griferos = [
    {"nom": "VERONICA", "est": "🟢 Mañana"},
    {"nom": "GUILLERMO", "est": "🟢 Mañana"},
    {"nom": "CESAR", "est": "🟡 Tarde/Noche"},
    {"nom": "GRIMALDA", "est": "🟡 Tarde/Noche"}
]

c1, c2, c3, c4 = st.columns(4)
for i, g in enumerate(griferos):
    with [c1, c2, c3, c4][i]:
        st.markdown(f"""
        <div class="grifero-card">
            <h4 style='margin:0;'>{g['nom']}</h4>
            <p style='color: #10B981; font-weight: bold; margin:0;'>{g['est']}</p>
            <p style='margin:0;'>S/ 1,500.00</p>
        </div>
        """, unsafe_allow_html=True)

# --- 5. CUADRO RESUMEN DE PLANILLA ---
st.subheader("📊 Resumen Económico de Personal")
data = {
    "Empleado": ["JUAN", "JOSE", "VERONICA", "GUILLERMO", "CESAR", "GRIMALDA"],
    "Cargo": ["Jefe Personal", "Jefe Personal", "Grifero", "Grifero", "Grifero", "Grifero"],
    "Sueldo (S/)": [1900, 1900, 1500, 1500, 1500, 1500],
    "Beneficios": ["Residencia + Viáticos", "Residencia + Viáticos", "Viáticos", "Viáticos", "Viáticos", "Viáticos"]
}
df = pd.DataFrame(data)
st.table(df)

total = df["Sueldo (S/)"].sum()
st.metric("Total Planilla Mensual", f"S/ {total:,.2f}")

# --- BOTÓN DE SALIDA ---
st.divider()
if st.button("⬅️ Volver al Panel de Prueba"):
    st.switch_page("pages/PRUEBA_DE_LA_APP.py")
