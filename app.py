# app.py
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
import hashlib
from datetime import datetime

st.set_page_config(page_title="Gestión de Grifo - Login", page_icon="⛽", layout="centered")

# --- 1. CONFIGURACIÓN DE CONEXIÓN Y UTILIDADES ---

# Función para hashear la contraseña (debe ser la misma que en Configuración)
def hash_password(password):
    """Genera un hash SHA-256 de la contraseña."""
    return hashlib.sha256(password.encode()).hexdigest()

# Inicialización segura de Firebase
if not firebase_admin._apps:
    try:
        cred_source = st.secrets["firebase"]
        cred_dict = dict(cred_source)
        
        # 1. LIMPIEZA DE LA PRIVATE KEY (CRÍTICO)
        if "private_key" in cred_dict:
            cred_dict["private_key"] = cred_dict["private_key"].replace('\\n', '\n')
            
        cred = credentials.Certificate(cred_dict)

        # 2. INICIALIZACIÓN CON OPCIONES EXPLICITAS (SOLUCIÓN DEL ERROR 404)
        # Asegúrate de que el project_id sea el correcto: streamlit-1320265
        firebase_admin.initialize_app(cred, {
            'projectId': 'streamlit-1320265', 
            'databaseURL': 'https://streamlit-1320265.firebaseio.com' 
        })
        
        # st.success("Conexión a Firebase activa.") 
    except Exception as e:
        st.error(f"Error CRÍTICO de Conexión a Firebase: {e}")
        st.stop()
        
# A partir de aquí, se puede inicializar el cliente de Firestore
db = firestore.client() 
employees_ref = db.collection('employees')

# Inicializa el estado de la sesión
if 'is_authenticated' not in st.session_state:
    st.session_state.is_authenticated = False
if 'user_role' not in st.session_state:
    st.session_state.user_role = None
if 'user_uid' not in st.session_state:
    st.session_state.user_uid = None


# --- 2. FUNCIÓN DE AUTENTICACIÓN ---

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
                
            # 3. Comparar el hash de la contraseña ingresada con el almacenado
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
        st.error(f"Error durante la autenticación: {e}")
        return False, "Ocurrió un error inesperado."

# Función para cerrar sesión
def logout():
    st.session_state.is_authenticated = False
    st.session_state.user_role = None
    st.session_state.user_uid = None
    st.rerun()

# --- 3. INTERFAZ DE LOGIN ---

if st.session_state.is_authenticated:
    # Si está autenticado, simplemente redirigimos y mostramos el contenido
    st.title("⛽ Dashboard Principal del Grifo")
    st.info(f"Sesión activa como: **{st.session_state.user_role}** (UID: {st.session_state.user_uid})")
    st.markdown("---")
    
    st.header("Resumen del Día")
    st.write("Aquí puedes agregar widgets (KPIs) con datos en tiempo real de Firebase.")
    
    st.button("Cerrar Sesión", on_click=logout)

else:
    # No autenticado: Mostrar formulario de login
    
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
                st.rerun() # Recarga la página para mostrar el dashboard
            else:
                st.error(message)
