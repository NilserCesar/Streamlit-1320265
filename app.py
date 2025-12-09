# app.py
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import hashlib
from datetime import datetime

# =================================================================
# === 1. CONFIGURACIÓN DE PÁGINA Y OCULTAMIENTO DE MENÚ (CRÍTICO) ===
# =================================================================

# 1. Configuración de la página
st.set_page_config(page_title="Gestión de Grifo", page_icon="⛽", layout="centered")

# 2. CSS para OCULTAR el menú lateral por defecto (Elimina el parpadeo/flash)
# Esto se inyecta y aplica ANTES de que el resto del código se ejecute.
st.markdown(
    """
    <style>
        /* Oculta el contenedor principal de la barra lateral */
        [data-testid="stSidebar"] {
            visibility: hidden;
        }
        /* Oculta el botón expandir/colapsar */
        [data-testid="stSidebarToggleButton"] {
            visibility: hidden;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# 3. Inicializa el estado de la sesión
if 'is_authenticated' not in st.session_state:
    st.session_state.is_authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'user_uid' not in st.session_state:
    st.session_state.user_uid = None


# =================================================================
# === 2. CONEXIÓN A FIREBASE Y LÓGICA DE HASH =======================
# =================================================================

# Función para hashear la contraseña
def hash_password(password):
    """Genera un hash SHA-256 de la contraseña."""
    return hashlib.sha256(password.encode()).hexdigest()

# Inicialización segura de Firebase
if not firebase_admin._apps:
    try:
        cred_source = st.secrets["firebase"]
        cred_dict = dict(cred_source)
        
        # Solución CRÍTICA para el formato de la private_key en Streamlit Secrets
        if "private_key" in cred_dict:
            cred_dict["private_key"] = cred_dict["private_key"].replace('\\n', '\n')
            
        cred = credentials.Certificate(cred_dict)

        # Configuración Explícita para evitar Error 404
        PROJECT_ID = "streamlit-1320265" # <<< ¡REEMPLAZA CON TU ID DE PROYECTO REAL!
        
        firebase_admin.initialize_app(cred, {
            'projectId': PROJECT_ID, 
            'databaseURL': f'https://{PROJECT_ID}.firebaseio.com' 
        })
        
    except Exception as e:
        st.error(f"Error CRÍTICO de Conexión a Firebase. Revisa secrets.toml y el ID del proyecto. Error: {e}")
        st.stop()
        
db = firestore.client()
employees_ref = db.collection('employees')


# =================================================================
# === 3. FUNCIÓN DE AUTENTICACIÓN ===================================
# =================================================================

def authenticate_user(dni, password):
    """Verifica credenciales contra Firestore."""
    try:
        doc = employees_ref.document(dni).get()
        if doc.exists:
            user_data = doc.to_dict()
            stored_hash = user_data.get('password_hash')
            
            if hash_password(password) == stored_hash:
                if user_data.get('is_active') is not True:
                    return False, "❌ Cuenta Inactiva. Contacta al administrador."

                st.session_state.is_authenticated = True
                st.session_state.user_role = user_data.get('role')
                st.session_state.user_uid = dni
                return True, f"¡Bienvenido, {user_data.get('name')}!"
            else:
                return False, "❌ Contraseña incorrecta."
        else:
            return False, "❌ Usuario (DNI) no encontrado."
            
    except Exception as e:
        return False, f"Ocurrió un error inesperado al autenticar: {e}"

def logout():
    """Cierra la sesión y limpia el estado."""
    st.session_state.is_authenticated = False
    st.session_state.user_role = None
    st.session_state.user_uid = None
    st.rerun()


# =================================================================
# === 4. LÓGICA CENTRAL DE REDIRECCIÓN Y LOGIN ======================
# =================================================================

if st.session_state.is_authenticated:
    # --- VISTA POST-LOGIN: REDIRECCIÓN ---
    
    # 1. Bloqueo de No-Administradores
    if st.session_state.user_role != "Administrador":
        st.error("🚫 Acceso denegado. Este sistema es solo para Administradores.")
        logout()
        st.stop()
    
    # 2. REDIRECCIÓN INMEDIATA
    # Al redireccionar, el menú lateral (sidebar) se volverá VISIBLE 
    # automáticamente en la página de Reportes.
    try:
        st.switch_page("pages/1_Reportes.py") 
    except Exception as e:
        st.error(f"Error al intentar cargar la página de Reportes. Verifica que 'pages/1_Reportes.py' exista. Error: {e}")
        st.stop()
    
else:
    # --- VISTA PRE-LOGIN: SOLO FORMULARIO ---
    
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
                st.rerun() # Recarga para activar la redirección
            else:
                st.error(message)
