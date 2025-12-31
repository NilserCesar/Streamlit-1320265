# app.py
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import hashlib
from datetime import datetime

# =================================================================
# === 1. CONFIGURACIÓN DE PÁGINA Y OCULTAMIENTO DE SIDEBAR ========
# =================================================================

st.set_page_config(
    page_title="Gestión de Grifo",
    page_icon="⛽",
    layout="centered"
)

# CSS para ocultar sidebar y personalizar estilos de firma
st.markdown("""
    <style>
        section[data-testid="stSidebar"] { display: none !important; }
        button[data-testid="stSidebarToggle"] { display: none !important; }
        div[data-testid="stAppViewContainer"] { margin-left: 0 !important; padding-left: 0 !important; }
        
        .firma-autor {
            text-align: center;
            color: #555555;
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 20px;
            border-bottom: 2px solid #eeeeee;
            padding-bottom: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# Firma del autor arriba del todo [cite: 13, 14]
st.markdown('<div class="firma-autor">Hecho Nilser Cesar Tuero Mayta - Senati</div>', unsafe_allow_html=True)

# Inicializar session_state
for key, value in {
    "is_authenticated": False,
    "user_role": None,
    "user_uid": None
}.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =================================================================
# === 2. FIREBASE & HASH ===========================================
# =================================================================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

if not firebase_admin._apps:
    try:
        cred_source = st.secrets["firebase"]
        cred_dict = dict(cred_source)
        if "private_key" in cred_dict:
            cred_dict["private_key"] = cred_dict["private_key"].replace("\\n", "\n")
        cred = credentials.Certificate(cred_dict)
        PROJECT_ID = "streamlit-1320265"  
        firebase_admin.initialize_app(cred, {
            "projectId": PROJECT_ID,
            "databaseURL": f"https://{PROJECT_ID}.firebaseio.com"
        })
    except Exception as e:
        st.error(f"Error al conectar Firebase: {e}")
        st.stop()

db = firestore.client()
employees_ref = db.collection("employees")

# =================================================================
# === 3. FUNCIONES DE AUTENTICACIÓN ================================
# =================================================================

def authenticate_user(dni, password):
    try:
        doc = employees_ref.document(dni).get()
        if not doc.exists:
            return False, "❌ Usuario no encontrado."
        user = doc.to_dict()
        if hash_password(password) != user.get("password_hash"):
            return False, "❌ Contraseña incorrecta."
        if not user.get("is_active", False):
            return False, "❌ Cuenta inactiva."
        
        st.session_state.is_authenticated = True
        st.session_state.user_role = user.get("role")
        st.session_state.user_uid = dni
        return True, f"Bienvenido, {user.get('name')}"
    except Exception as e:
        return False, f"Error inesperado: {e}"

def logout():
    st.session_state.is_authenticated = False
    st.session_state.user_role = None
    st.session_state.user_uid = None
    st.rerun()

# =================================================================
# === 4. LOGIN / REDIRECCIÓN =======================================
# =================================================================

if st.session_state.is_authenticated:
    if st.session_state.user_role != "Administrador":
        st.error("🚫 Acceso denegado.")
        logout()
        st.stop()
    try:
        st.switch_page("pages/1_Reportes.py")
    except:
        st.error("Error cargando Reportes.")
else:
    st.title("⛽ PRÁCTICAS GRIFO V&T")
    st.subheader("Acceso al Sistema de Gestión")

    with st.form("login_form"):
        dni = st.text_input("Usuario (DNI)")
        password = st.text_input("Contraseña", type="password")
        btn = st.form_submit_button("Iniciar Sesión")

        if btn:
            ok, msg = authenticate_user(dni, password)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    # --- BOTÓN DE ACCESO A PRUEBA (Fuera del formulario) ---
    st.divider()
    st.info("Área de Desarrollo y Pruebas")
    if st.button("🚀 ENTRAR A PRUEBA DE LA APP"):
        try:
            st.switch_page("pages/PRUEBA_DE_LA_APP.py")
        except Exception as e:
            st.error("Asegúrate de que el archivo existe en 'pages/PRUEBA_DE_LA_APP.py'")
