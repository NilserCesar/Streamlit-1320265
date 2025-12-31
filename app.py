# app.py
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import hashlib

# =================================================================
# === 1. CONFIGURACIÓN DE PÁGINA (SIDEBAR ELIMINADO TOTALMENTE) ===
# =================================================================

st.set_page_config(
    page_title="Gestión de Grifo",
    page_icon="⛽",
    layout="centered",
    initial_sidebar_state="collapsed" # Fuerza el cierre inicial
)

# CSS agresivo para eliminar rastro del sidebar, botones de navegación y espacios
st.markdown("""
    <style>
        /* Oculta el sidebar y el botón de colapsar */
        [data-testid="stSidebar"], [data-testid="stSidebarNav"], button[data-testid="stSidebarToggle"] {
            display: none !important;
        }
        
        /* Elimina el margen izquierdo que deja el sidebar */
        [data-testid="stAppViewContainer"] {
            margin-left: -20rem !important; /* Compensa el espacio del sidebar */
        }

        /* Ajusta el contenedor principal para que use todo el ancho */
        .main .block-container {
            max-width: 100%;
            padding-left: 1rem;
            padding-right: 1rem;
            margin-left: auto;
            margin-right: auto;
        }

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

# Encabezado del Autor
st.markdown('<div class="firma-autor">Hecho Nilser Cesar Tuero Mayta - Senati</div>', unsafe_allow_html=True)

# Inicializar session_state
for key, value in {"is_authenticated": False, "user_role": None, "user_uid": None}.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =================================================================
# === 2. FIREBASE & LÓGICA DE ACCESO ===============================
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
        st.error(f"Error Firebase: {e}")
        st.stop()

db = firestore.client()

# --- VALIDACIÓN Y REDIRECCIÓN ---
if st.session_state.is_authenticated:
    if st.session_state.user_role == "Administrador":
        try:
            st.switch_page("pages/1_Reportes.py")
        except:
            st.error("Archivo Reportes no encontrado.")
    else:
        st.error("🚫 Solo administradores.")
        st.session_state.is_authenticated = False
        st.rerun()

else:
    # --- PANTALLA DE LOGIN ---
    st.title("⛽ PRÁCTICAS GRIFO V&T")
    st.subheader("Acceso al Sistema de Gestión")

    with st.form("login_form"):
        dni = st.text_input("Usuario (DNI)")
        password = st.text_input("Contraseña", type="password")
        btn = st.form_submit_button("Iniciar Sesión")

        if btn:
            try:
                doc = db.collection("employees").document(dni).get()
                if doc.exists:
                    user = doc.to_dict()
                    if hash_password(password) == user.get("password_hash") and user.get("is_active"):
                        st.session_state.is_authenticated = True
                        st.session_state.user_role = user.get("role")
                        st.session_state.user_uid = dni
                        st.success(f"Bienvenido {user.get('name')}")
                        st.rerun()
                    else:
                        st.error("Credenciales inválidas o cuenta inactiva.")
                else:
                    st.error("Usuario no encontrado.")
            except Exception as e:
                st.error(f"Error: {e}")

    # --- BOTÓN DE PRUEBA INDEPENDIENTE ---
    st.divider()
    st.info("Laboratorio de Desarrollo")
    if st.button("🚀 ENTRAR A PRUEBA DE LA APP"):
        try:
            st.switch_page("pages/PRUEBA_DE_LA_APP.py")
        except:
            st.error("Verifica que exista 'pages/PRUEBA_DE_LA_APP.py'")
