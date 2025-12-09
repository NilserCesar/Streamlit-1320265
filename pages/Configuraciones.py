# pages/3_Configuraciones.py
import streamlit as st
from firebase_admin import firestore
from datetime import datetime
import hashlib

# === VERIFICACIÓN DE SEGURIDAD ===
if 'is_authenticated' not in st.session_state or not st.session_state.is_authenticated:
    st.warning("🔒 Debes iniciar sesión para acceder a esta página. Vuelve a la página principal.")
    st.stop()
# ==================================
st.set_page_config(page_title="Configuraciones del Sistema", page_icon="⚙️")
st.title("⚙️ Configuraciones de Administración")

# Inicializamos la conexión a Firestore
try:
    db = firestore.client()
except Exception:
    st.error("Error: Conexión a Firebase no inicializada.")
    st.stop()

# --- PESTAÑAS ---
tab1, tab2 = st.tabs(["Gestión de Cuentas Móviles", "Precios de Productos"])


# =================================================================
# === PESTAÑA 1: GESTIÓN DE CUENTAS MÓVILES ========================
# =================================================================

with tab1:
    st.header("Gestión de Cuentas de Acceso (App Móvil)")
    st.warning("El DNI del empleado será su 'usuario'. Por seguridad, las contraseñas se almacenarán encriptadas (hash).")

    # Función para hashear la contraseña
    def hash_password(password):
        """Genera un hash SHA-256 de la contraseña."""
        return hashlib.sha256(password.encode()).hexdigest()

    # Cargar la lista de empleados para seleccionar
    @st.cache_data(ttl=600)
    def load_employees_for_login():
        """Carga solo DNI y Nombre de empleados activos."""
        query = db.collection('employees').where('is_active', '==', True).stream()
        return {doc.id: f"{doc.to_dict().get('name')} {doc.to_dict().get('last_name')}" for doc in query}

    employee_list = load_employees_for_login()
    employee_options = [f"{dni} - {name}" for dni, name in employee_list.items()]
    
    # ------------------ 1. CREAR / RESTABLECER CUENTA ------------------
    st.subheader("Crear / Restablecer Contraseña")
    
    with st.form("account_form"):
        selected_employee_info = st.selectbox("Selecciona Empleado:", options=employee_options, index=None, placeholder="Selecciona el DNI del empleado...")
        
        if selected_employee_info:
            selected_dni = selected_employee_info.split(' - ')[0]
            new_password = st.text_input("Nueva Contraseña", type="password", help="Esta será la clave de acceso del empleado.")
            
            submitted = st.form_submit_button("Actualizar Contraseña")

            if submitted and new_password:
                hashed_pw = hash_password(new_password)
                try:
                    # Actualiza el documento del empleado con el hash de la contraseña
                    db.collection('employees').document(selected_dni).update({
                        "password_hash": hashed_pw,
                        "last_pw_update": firestore.SERVER_TIMESTAMP,
                        "employee_uid": selected_dni, # Aseguramos que el UID esté presente para el login
                    })
                    st.success(f"✅ Contraseña para {selected_employee_info} actualizada correctamente. Su usuario es: **{selected_dni}**")
                except Exception as e:
                    st.error(f"❌ Error al actualizar la contraseña: {e}")
        else:
            st.info("Selecciona un empleado para asignarle o actualizar su contraseña.")


# =================================================================
# === PESTAÑA 2: PRECIOS DE PRODUCTOS ==============================
# =================================================================

with tab2:
    st.header("Gestión de Precios de Combustible")
    
    # Referencia a la colección de productos
    products_ref = db.collection('products')

    # ------------------ 1. FORMULARIO PARA NUEVO PRECIO ------------------
    st.subheader("Registrar Nuevo Precio de Venta")
    with st.form("price_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            product_id = st.selectbox("Producto", options=["90", "95", "DL"])
            new_price = st.number_input(f"Precio por Galón para {product_id} (S/.)", min_value=0.01, format="%.3f")
            
        with col2:
            valid_from = st.date_input("Fecha de Vigencia (Desde cuándo aplica)", datetime.now().date())
            
        submitted = st.form_submit_button("Guardar Nuevo Precio")

        if submitted:
            try:
                price_data = {
                    "product_id": product_id,
                    "price_per_gallon": float(new_price),
                    "valid_from": datetime.combine(valid_from, datetime.min.time()),
                    "registered_at": firestore.SERVER_TIMESTAMP,
                }
                # Firestore generará un ID único, manteniendo el historial
                products_ref.add(price_data) 
                st.success(f"✅ Nuevo precio de S/. {new_price:.3f} para {product_id} registrado con vigencia desde {valid_from}.")
            except Exception as e:
                st.error(f"❌ Error al registrar precio: {e}")

    # ------------------ 2. HISTORIAL DE PRECIOS ------------------
    st.subheader("Historial de Precios Registrados")

    @st.cache_data(ttl=600)
    def load_price_history():
        """Carga el historial de precios ordenado por fecha de vigencia."""
        query = products_ref.order_by('valid_from', direction=firestore.Query.DESCENDING).stream()
        data = [doc.to_dict() for doc in query]
        
        # Procesar los datos para una mejor visualización
        for item in data:
            if isinstance(item.get('valid_from'), datetime):
                item['valid_from'] = item['valid_from'].strftime
