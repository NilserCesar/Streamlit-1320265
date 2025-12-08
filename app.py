# app.py (SOLUCIÓN FINAL DE CONEXIÓN)
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json 

# --- 1. Inicialización Segura y Creación de COPIA ---

if not firebase_admin._apps:
    try:
        # 1. Lee el diccionario de credenciales desde Streamlit Secrets
        #    (Esto es solo lectura)
        cred_source = st.secrets["firebase"]
        
        # 2. Creamos una COPIA independiente del diccionario
        #    Así podemos modificar la copia sin tocar los secretos originales
        cred_dict = dict(cred_source) 
        
        # 3. Limpieza de la Clave Privada (Solo se hace en la copia)
        #    Aseguramos que los saltos de línea sean correctos para Firebase Admin SDK
        cred_dict["private_key"] = cred_dict["private_key"].replace('\\n', '\n')

        # 4. Inicializa la app de Firebase con la COPIA LIMPIA
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        
        st.success("🎉 ¡Conexión a Firebase exitosa! (Problema de Secretos resuelto)")
        
    except Exception as e:
        st.error(f"Error al conectar con Firebase: {e}")
        st.stop()
        
# --- RESTO DEL CÓDIGO ---
db = firestore.client()
st.title("App de Streamlit Conectada a Firebase")
# ... (El código de lectura de datos va aquí)
