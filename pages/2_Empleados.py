import streamlit as st
import pandas as pd
from datetime import datetime, date

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Gestión de Personal - V&T", layout="wide")

st.markdown("""
    <style>
        [data-testid="stSidebar"], [data-testid="stSidebarNav"], button[data-testid="stSidebarToggle"] { display: none !important; }
        [data-testid="stAppViewContainer"] { margin-left: 0px !important; }
        .card { background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #003366; }
        .chef-card { background-color: #e3f2fd; padding: 20px; border-radius: 10px; border-left: 5px solid #1976d2; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div style="text-align: center; color: gray;">Hecho Nilser Cesar Tuero Mayta - Senati</div>', unsafe_allow_html=True)
st.title("👥 Control de Personal y Roles de Turno")

# --- 1. BASE DE DATOS DE EMPLEADOS ---
empleados = [
    {"nombre": "Juan", "cargo": "Jefe de Personal", "sueldo": 1900, "tipo": "Administrativo"},
    {"nombre": "Jose", "cargo": "Jefe de Personal (Relevo)", "sueldo": 1900, "tipo": "Administrativo"},
    {"nombre": "Veronica", "cargo": "Grifero", "sueldo": 1500, "tipo": "Operativo"},
    {"nombre": "Guillermo", "cargo": "Grifero", "sueldo": 1500, "tipo": "Operativo"},
    {"nombre": "Cesar", "cargo": "Grifero", "sueldo": 1500, "tipo": "Operativo"},
    {"nombre": "Grimalda", "cargo": "Grifero", "sueldo": 1500, "tipo": "Operativo"},
]

# --- 2. LÓGICA DE ROTACIÓN (JEFE DE PERSONAL) ---
# Juan y Jose rotan cada 15 días
dia_del_año = datetime.now().timetuple().tm_yday
bloque_15 = (dia_del_año // 15) % 2

jefe_activo = "Juan" if bloque_15 == 0 else "Jose"
jefe_saliente = "Jose" if bloque_15 == 0 else "Juan"

# --- 3. INTERFAZ VISUAL ---

# Sección Jefatura
st.subheader("🏠 Residencia y Jefatura (Rotación 15 días)")
c1, c2 = st.columns(2)

with c1:
    st.markdown(f"""
    <div class="chef-card">
        <h3>En Turno (Vive en Grifo): {jefe_activo}</h3>
        <p><b>Cargo:</b> Jefe de Personal / Orden y Mantenimiento</p>
        <p><b>Sueldo:</b> S/ 1,900.00</p>
        <p><b>Estado:</b> Activo - Supervisando Personal</p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.info(f"**Próximo Relevo:** {jefe_saliente} (Libre actualmente)")
    st.write("La rotación se realiza automáticamente cada 15 días según el calendario del sistema.")

st.divider()

# Sección Griferos
st.subheader("⛽ Griferos Operativos (Turno 8h - Rotación Diaria)")
st.write("Se mantienen **2 trabajadores por turno** con viáticos incluidos.")

# Mostrar tabla de sueldos y viáticos
df_griferos = pd.DataFrame(empleados[2:]) # Solo los griferos
df_griferos['Horas'] = 8
df_griferos['Viáticos'] = "Incluido (Desayuno/Almuerzo/Cena)"

st.table(df_griferos)

# Simulación de Turnos de Hoy
st.info("📅 **Turnos del día de hoy:**")
col_t1, col_t2 = st.columns(2)

# Lógica simple de rotación para 2 personas por turno
with col_t1:
    st.success(f"**Turno Mañana/Tarde:**\n1. Veronica\n2. Guillermo")
with col_t2:
    st.success(f"**Turno Tarde/Noche:**\n1. Cesar\n2. Grimalda")

# --- 4. RESUMEN DE PLANILLA ---
st.divider()
st.subheader("💰 Resumen de Planilla Mensual Estimada")
total_planilla = sum([e['sueldo'] for e in empleados])
st.metric("Inversión Total en Personal", f"S/ {total_planilla:,.2f}", "Incluye viáticos")

# Botón de Navegación
if st.button("⬅️ Volver al Panel de Prueba"):
    st.switch_page("pages/PRUEBA_DE_LA_APP.py")
