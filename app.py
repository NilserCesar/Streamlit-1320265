# app.py
import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# [PEGAR EL CÓDIGO DE CONEXIÓN FIREBASE QUE VIMOS ANTES]
# Lo más importante es que contenga: if not firebase_admin._apps: ...
# para inicializar la conexión.

st.title("Mi Primera App con Streamlit y Firebase")
st.write("Estado de la aplicación:") 

# Ejemplo básico para mostrar el estado de la conexión
if firebase_admin._apps:
    st.success("¡La conexión con Firebase está activa!")
else:
    st.error("Error: Conexión a Firebase no inicializada.")
