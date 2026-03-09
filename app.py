import streamlit as st
import pandas as pd
import plotly.express as px

from database import *
from auth import *

create_tables()

st.set_page_config(page_title="Finance App", layout="wide")

st.title("💰 Control de Gastos")

# SESSION

if "user" not in st.session_state:
    st.session_state.user = None

# LOGIN / REGISTER

if st.session_state.user is None:

    menu = st.sidebar.selectbox(
        "Menu",
        ["Login","Register"]
    )

    if menu == "Register":

        st.subheader("Crear cuenta")

        email = st.text_input("Email", key="reg_email")
        password = st.text_input("Password", type="password", key="reg_pass")

        if st.button("Crear usuario"):

            register_user(email,password)

            st.success("Usuario creado")

    if menu == "Login":

        st.subheader("Login")

        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Entrar"):

            user = login_user(email)

            if user and verify_password(password, user[2]):

                st.session_state.user = user[0]
                st.rerun()

            else:

                st.error("Credenciales incorrectas")

# APP

if st.session_state.user:

    st.sidebar.success("Usuario conectado")

    if st.sidebar.button("Logout"):

        st.session_state.user = None
        st.rerun()

    account = st.sidebar.selectbox(
        "Cuenta",
        ["Personal","Negocio"]
    )

    tabs = st.tabs([
        "Dashboard",
        "Ingresos",
        "Gastos",
        "Proveedores"
    ])

# DASHBOARD

    with tabs[0]:

        expenses = pd.read_sql_query(
            f"SELECT * FROM expenses WHERE user_id={st.session_state.user}",
            conn
        )

        incomes = pd.read_sql_query(
            f"SELECT * FROM incomes WHERE user_id={st.session_state.user}",
            conn
        )

        total_income = incomes["amount"].sum() if not incomes.empty else 0
        total_expenses = expenses["amount"].sum() if not expenses.empty else 0
        balance = total_income - total_expenses

        col1,col2,col3 = st.columns(3)

        col1.metric("Ingresos", total_income)
        col2.metric("Gastos", total_expenses)
        col3.metric("Balance", balance)

        if not expenses.empty:

            fig = px.pie(
                expenses,
                names="category",
                values="amount",
                height=350
            )

            st.plotly_chart(fig, use_container_width=True)

# INGRESOS

    with tabs[1]:

        st.subheader("Agregar ingreso")

        desc = st.text_input("Descripción", key="income_desc")

        amount = st.number_input("Monto", key="income_amount")

        method = st.selectbox(
            "Medio",
            ["Efectivo","Mercado Pago","Transferencia"],
            key="income_method"
        )

        if st.button("Guardar ingreso"):

            cursor.execute(
                """INSERT INTO incomes
                (user_id,account,description,amount,method,date)
                VALUES (?,?,?,?,?,date('now'))""",
                (st.session_state.user,account,desc,amount,method)
            )

            conn.commit()

            st.success("Ingreso guardado")

# GASTOS

    with tabs[2]:

        st.subheader("Agregar gasto")

        category = st.selectbox(
            "Categoría",
            ["Comida","Transporte","Compras","Salud","Casa"],
            key="expense_category"
        )

        desc = st.text_input("Descripción", key="expense_desc")

        amount = st.number_input("Monto", key="expense_amount")

        method = st.selectbox(
            "Medio de pago",
            ["Efectivo","Mercado Pago","Tarjeta"],
            key="expense_method"
        )

        installments = 1

        if method == "Tarjeta":

            installments = st.selectbox(
                "Cuotas",
                [1,3,6,12],
                key="expense_installments"
            )

        if st.button("Guardar gasto"):

            cursor.execute(
                """INSERT INTO expenses
                (user_id,account,category,description,amount,method,installments,date)
                VALUES (?,?,?,?,?,?,?,date('now'))""",
                (st.session_state.user,account,category,desc,amount,method,installments)
            )

            conn.commit()

            st.success("Gasto guardado")

# PROVEEDORES (NEGOCIO)

    with tabs[3]:

        if account == "Negocio":

            st.subheader("Proveedores")

            name = st.text_input("Proveedor", key="supplier_name")

            product = st.text_input("Producto", key="supplier_product")

            amount = st.number_input("Monto", key="supplier_amount")

            status = st.selectbox(
                "Estado",
                ["Pendiente","Pagado"],
                key="supplier_status"
            )

            if st.button("Guardar proveedor"):

                cursor.execute(
                    """INSERT INTO suppliers
                    (user_id,name,product,amount,status)
                    VALUES (?,?,?,?,?)""",
                    (st.session_state.user,name,product,amount,status)
                )

                conn.commit()

                st.success("Proveedor guardado")

        else:

            st.info("Esta sección es solo para cuentas de negocio.")
