# app.py
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json # ¡Importa la librería JSON!

# --- 1. Inicialización Segura y Limpieza de Credenciales ---

if not firebase_admin._apps:
    try:
        # Lee el diccionario de credenciales desde Streamlit Secrets
        cred_dict = st.secrets["firebase"]
        
        # --- SOLUCIÓN DEL ERROR AQUÍ: LIMPIEZA DE LA CLAVE PRIVADA ---
        # La clave privada puede tener saltos de línea literales ('\n') o ser leída como un string.
        # Nos aseguramos de que sea un diccionario si Streamlit lo leyó como un string:
        if isinstance(cred_dict, str):
            cred_dict = json.loads(cred_dict)
            
        # El Firebase Admin SDK a veces necesita que la private_key sea un string simple,
        # no un string multilínea, pero con los saltos de línea correctos.
        # Aseguramos que los saltos de línea estén bien codificados:
        cred_dict["private_key"] = cred_dict["private_key"].replace('\\n', '\n')

        # El resto del código se mantiene igual
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        st.success("¡Conexión a Firebase exitosa!")
        
    except Exception as e:
        st.error(f"Error al conectar con Firebase: {e}")
        st.stop()
        
# [RESTO DEL CÓDIGO DE LECTURA DE DATOS...]
db = firestore.client()
st.title("App de Streamlit Conectada a Firebase")
st.success(f"Conexión exitosa a Firestore del proyecto: {db.project}")

# ... (El código de get_firestore_data, etc., va aquí)
