# app.py
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore

# --- 1. Inicialización Segura (Usando el Secreto) ---

if not firebase_admin._apps:
    try:
        # El código lee automáticamente la sección [firebase] del Secreto TOML
        cred = credentials.Certificate(st.secrets["firebase"])
        firebase_admin.initialize_app(cred)
    except Exception as e:
        st.error(f"Error al conectar con Firebase: {e}")
        st.stop()

# Inicializa la referencia a la base de datos
db = firestore.client()

# --- 2. Título y Estado ---

st.title("App de Streamlit Conectada a Firebase")
st.success(f"Conexión exitosa a Firestore del proyecto: {db.project}")

# --- 3. FUNCIÓN DE LECTURA DE DATOS ---

def get_firestore_data():
    """Lee todos los documentos de la colección 'items'"""
    st.header("🛒 Elementos de Firestore")
    
    # 3.1 Consulta: Obteniendo la colección 'items'
    items_ref = db.collection('items')
    
    # 3.2 Obtención de los documentos
    docs = items_ref.stream()

    data = []
    # 3.3 Iteración y adición a la lista
    for doc in docs:
        data.append(doc.to_dict())
        
    return data

# --- 4. Mostrar los datos ---
items_list = get_firestore_data()

if items_list:
    st.dataframe(items_list) # Muestra los datos en un formato de tabla
    st.write(f"Total de documentos leídos: {len(items_list)}")
else:
    st.warning("No se encontraron documentos en la colección 'items'.")
