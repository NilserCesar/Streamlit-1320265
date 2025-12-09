# pages/2_Empleados.py
import streamlit as st
import pandas as pd
from datetime import datetime
from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter, FieldOperator
# Puedes usar 'hashlib' si quieres hashear contraseñas aquí, pero lo dejaremos simple por ahora.

st.set_page_config(page_title="Gestión de Empleados", page_icon="👥")
st.title("👥 Gestión de Personal y Salarios")

# Inicializamos la conexión a Firestore
try:
    db = firestore.client()
except Exception:
    st.error("Error: Conexión a Firebase no inicializada.")
    st.stop()
    
# Referencias a las colecciones principales
employees_ref = db.collection('employees')
payments_ref = db.collection('employee_payments') # Colección para el historial de pagos


# --- PESTAÑAS ---
tab1, tab2 = st.tabs(["Lista de Empleados", "Salario y Historial de Pagos"])


# =================================================================
# === PESTAÑA 1: LISTA DE EMPLEADOS (CRUD) =========================
# =================================================================

with tab1:
    st.header("Lista y Registro de Personal")
    
    # ------------------ 1. FORMULARIO DE REGISTRO ------------------
    st.subheader("Registrar Nuevo Empleado")
    with st.form("new_employee_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Nombre", key="emp_name")
            dni = st.text_input("DNI (Usado como ID/Usuario)", key="emp_dni")
            role = st.selectbox("Rol", options=["Despachador", "Supervisor", "Administrador", "Gerente"])
            
        with col2:
            last_name = st.text_input("Apellido", key="emp_last_name")
            phone = st.text_input("Teléfono", key="emp_phone")
            hire_date = st.date_input("Fecha de Ingreso", datetime.now().date())
            
        submitted = st.form_submit_button("Guardar Empleado")

        if submitted and dni:
            try:
                # Comprobamos si el DNI ya existe
                if employees_ref.document(dni).get().exists:
                    st.warning("⚠️ Ya existe un empleado con ese DNI. No se guardó.")
                else:
                    employee_data = {
                        "employee_uid": dni, # Usamos el DNI como ID del documento para facilitar la búsqueda
                        "name": name,
                        "last_name": last_name,
                        "dni": dni,
                        "phone": phone,
                        "role": role,
                        "hire_date": datetime.combine(hire_date, datetime.min.time()),
                        "is_active": True,
                        "created_at": firestore.SERVER_TIMESTAMP,
                    }
                    employees_ref.document(dni).set(employee_data)
                    st.success(f"✅ Empleado {name} {last_name} registrado correctamente.")
            except Exception as e:
                st.error(f"❌ Error al registrar empleado: {e}")

    # ------------------ 2. TABLA DE EMPLEADOS ------------------
    st.subheader("Personal Activo")
    
    @st.cache_data(ttl=600)
    def load_employees():
        """Carga la lista de empleados activos."""
        query = employees_ref.where('is_active', '==', True).stream()
        data = [doc.to_dict() for doc in query]
        
        # Convertir timestamp a formato de fecha legible para Streamlit
        for item in data:
            if isinstance(item.get('hire_date'), datetime):
                item['hire_date'] = item['hire_date'].strftime('%Y-%m-%d')
        
        return pd.DataFrame(data).sort_values(by='last_name')

    df_employees = load_employees()
    
    if not df_employees.empty:
        # Mostramos solo los campos relevantes en la tabla
        st.dataframe(
            df_employees[['name', 'last_name', 'dni', 'phone', 'role', 'hire_date']],
            column_order=('name', 'last_name', 'dni', 'role', 'phone', 'hire_date'),
            hide_index=True
        )
    else:
        st.info("No hay empleados activos registrados.")


# =================================================================
# === PESTAÑA 2: SALARIO E HISTORIAL DE PAGOS ======================
# =================================================================

with tab2:
    st.header("Registro de Pagos al Personal")
    
    if 'df_employees' in locals() and not df_employees.empty:
        
        # 1. Selección de Empleado
        employee_names = df_employees['name'] + ' ' + df_employees['last_name']
        selected_employee = st.selectbox("Selecciona Empleado:", options=employee_names)
        
        # Obtenemos el DNI del empleado seleccionado para usarlo como UID
        selected_uid = df_employees.loc[df_employees['name'] + ' ' + df_employees['last_name'] == selected_employee, 'dni'].iloc[0]

        
        # 2. Formulario de Registro de Pago
        st.subheader(f"Registrar Nuevo Pago para {selected_employee}")
        with st.form("payment_form"):
            col1, col2 = st.columns(2)
            with col1:
                payment_amount = st.number_input("Monto del Pago (S/.)", min_value=0.01, format="%.2f")
            with col2:
                payment_date = st.date_input("Fecha del Pago", datetime.now().date())
            
            payment_submitted = st.form_submit_button("Registrar Pago")

            if payment_submitted:
                try:
                    payment_data = {
                        "employee_uid": selected_uid,
                        "payment_date": datetime.combine(payment_date, datetime.min.time()),
                        "amount": float(payment_amount),
                        "description": "Pago de Nómina",
                        "registered_at": firestore.SERVER_TIMESTAMP,
                    }
                    payments_ref.add(payment_data) # El ID del documento se genera automáticamente
                    st.success(f"✅ Pago de S/. {payment_amount:.2f} registrado para {selected_employee}.")
                except Exception as e:
                    st.error(f"❌ Error al registrar pago: {e}")

        st.divider()
        
        # 3. Historial de Pagos
        st.subheader("Historial de Pagos Efectuados")
        
        @st.cache_data(ttl=600)
        def load_payments(uid):
            """Carga el historial de pagos para un empleado específico."""
            query = payments_ref.where('employee_uid', '==', uid).order_by('payment_date', direction=firestore.Query.DESCENDING).stream()
            data = [doc.to_dict() for doc in query]
            
            for item in data:
                if isinstance(item.get('payment_date'), datetime):
                    item['payment_date'] = item['payment_date'].strftime('%Y-%m-%d')
            
            return pd.DataFrame(data)

        df_payments = load_payments(selected_uid)
        
        if not df_payments.empty:
            # Mostramos el historial en orden descendente
            st.dataframe(
                df_payments[['payment_date', 'amount', 'description', 'registered_at']],
                column_order=('payment_date', 'amount', 'description', 'registered_at'),
                hide_index=True
            )
        else:
            st.info(f"No hay historial de pagos registrado para {selected_employee}.")
    else:
        st.warning("Debe registrar empleados en la pestaña anterior para ver el historial de pagos.")
