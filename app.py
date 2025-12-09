# app.py
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import hashlib
from datetime import datetime

# =================================================================
# === CONFIGURACIÓN DE PÁGINA Y ESTADO DE SESIÓN ==================
# =================================================================

st.set_page_config(page_title="Gestión de Grifo", page_icon="⛽", layout="centered")

# Inicializa el estado de la sesión
if 'is_authenticated' not in st.session_state:
    st.session_state.is_authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'user_uid' not in st.session_state:
    st.session_state.user_uid = None


# =================================================================
# === 1. CONEXIÓN A FIREBASE Y UTILIDADES =========================
# =================================================================

# Función para hashear la contraseña (misma función que en Configuraciones)
def hash_password(password):
    """Genera un hash SHA-256 de la contraseña."""
    return hashlib.sha256(password.encode()).hexdigest()

# Inicialización segura de Firebase
if not firebase_admin._apps:
    try:
        # Asegúrate de que tu archivo secrets.toml tenga la sección [firebase] con tus credenciales
        cred_source = st.secrets["firebase"]
        cred_dict = dict(cred_source)
        
        # Solución CRÍTICA para el formato de la private_key en Streamlit Secrets
        if "private_key" in cred_dict:
            cred_dict["private_key"] = cred_dict["private_key"].replace('\\n', '\n')
            
        cred = credentials.Certificate(cred_dict)

        # SOLUCIÓN AL ERROR 404: Inicializar con el projectId explícito
        PROJECT_ID = "streamlit-1320265" # <<< Reemplaza con tu ID de Proyecto si es diferente
        
        firebase_admin.initialize_app(cred, {
            'projectId': PROJECT_ID, 
            'databaseURL': f'https://{PROJECT_ID}.firebaseio.com' 
        })
        
    except Exception as e:
        st.error(f"Error CRÍTICO de Conexión a Firebase. Revisa secrets.toml y el ID del proyecto. Error: {e}")
        st.stop()
        
# Inicializa el cliente de Firestore
db = firestore.client()
employees_ref = db.collection('employees')


# =================================================================
# === 2. LÓGICA DE AUTENTICACIÓN ==================================
# =================================================================

def authenticate_user(dni, password):
    """Verifica credenciales contra Firestore."""
    try:
        doc = employees_ref.document(dni).get()
        if doc.exists:
            user_data = doc.to_dict()
            
            # 1. Verificar que el empleado esté activo
            if user_data.get('is_active') is not True:
                return False, "❌ Cuenta Inactiva. Contacta al administrador."
                
            # 2. Obtener el hash almacenado
            stored_hash = user_data.get('password_hash')
            if not stored_hash:
                return False, "❌ Cuenta sin contraseña asignada. Contacta al administrador."
                
            # 3. Comparar HASH
            if hash_password(password) == stored_hash:
                st.session_state.is_authenticated = True
                st.session_state.user_role = user_data.get('role')
                st.session_state.user_uid = dni
                return True, f"¡Bienvenido, {user_data.get('name')}!"
            else:
                return False, "❌ Contraseña incorrecta."
        else:
            return False, "❌ Usuario (DNI) no encontrado."
            
    except Exception as e:
        # Este error debería ser menos común ahora que corregimos el 404
        return False, f"Ocurrió un error inesperado al autenticar: {e}"

def logout():
    """Cierra la sesión y limpia el estado."""
    st.session_state.is_authenticated = False
    st.session_state.user_role = None
    st.session_state.user_uid = None
    st.rerun()


# =================================================================
# === 3. INTERFAZ DE USUARIO (DASHBOARD o LOGIN) ==================
# =================================================================

if st.session_state.is_authenticated:
    # --- VISTA POST-LOGIN (Dashboard Principal) ---
    
    # 1. Bloqueo de No-Administradores (EXTRA SEGURO)
    if st.session_state.user_role != "Administrador":
        st.error("🚫 Acceso denegado. Este sistema es solo para Administradores.")
        logout()
        st.stop()
    
    # 2. Dashboard de Bienvenida
    st.title("⛽ Dashboard Principal del Grifo")
    st.info(f"Sesión activa como: **{st.session_state.user_role}** (UID: {st.session_state.user_uid})")
    
    # Puedes mostrar aquí un resumen rápido del día usando firestore.client()
    st.header("📈 Resumen Rápido del Día")
    st.metric("Total de Ventas Teóricas Hoy", value="S/. 0.00", delta="0.00")
    st.write("*(Para ver los datos detallados, usa la página **Reportes** del menú lateral.)*")
    
    st.markdown("---")
    st.button("Cerrar Sesión", on_click=logout)

else:
    # --- VISTA PRE-LOGIN (Formulario) ---
    
    st.title("🔐 Acceso al Sistema de Gestión de Grifo")
    st.subheader("Ingresa tus credenciales")
    
    with st.form("login_form"):
        username = st.text_input("Usuario (DNI)", key="login_user")
        password = st.text_input("Contraseña", type="password", key="login_pw")
        
        login_button = st.form_submit_button("Iniciar Sesión")
        
        if login_button:
            success, message = authenticate_user(username, password)
            if success:
                st.success(message)
                st.rerun() # Recarga la página para activar la navegación lateral
            else:
                st.error(message)
