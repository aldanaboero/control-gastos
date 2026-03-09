import streamlit as st
import pandas as pd
import plotly.express as px
from database import *
from auth import *

create_tables()

st.title("💰 FinanceFlow")

menu = ["Login","Register"]

choice = st.sidebar.selectbox("Menu",menu)

# LOGIN

if choice == "Login":

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        user = login_user(email)

        if user and verify_password(password, user[2]):

            st.session_state.user = user[0]
            st.success("Logged in")

        else:

            st.error("Invalid credentials")

# REGISTER

if choice == "Register":

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Create account"):

        register_user(email,password)

        st.success("User created")

# DASHBOARD

if "user" in st.session_state:

    st.sidebar.title("Accounts")

    account_type = st.sidebar.selectbox(
        "Select account",
        ["Personal","Business"]
    )

    st.header(account_type)

    tabs = st.tabs([
        "Dashboard",
        "Income",
        "Expenses",
        "Suppliers"
    ])

    # DASHBOARD

    with tabs[0]:

        df = pd.read_sql_query(
            "SELECT * FROM expenses",
            conn
        )

        if not df.empty:

            fig = px.pie(
                df,
                names="category",
                values="amount"
            )

            st.plotly_chart(fig,use_container_width=True)

    # INCOME

    with tabs[1]:

        desc = st.text_input("Description")
        amount = st.number_input("Amount")
        method = st.selectbox(
            "Method",
            ["Cash","Mercado Pago","Transfer"]
        )

        if st.button("Add income"):

            cursor.execute(
                "INSERT INTO incomes(account_id,description,amount,method,date) VALUES (?,?,?,?,date('now'))",
                (1,desc,amount,method)
            )

            conn.commit()

            st.success("Income added")

    # EXPENSES

    with tabs[2]:

        category = st.selectbox(
            "Category",
            ["Food","Transport","Shopping","Health","Home"]
        )

        desc = st.text_input("Description")

        amount = st.number_input("Amount")

        method = st.selectbox(
            "Payment method",
            ["Cash","Mercado Pago","Credit Card"]
        )

        installments = 1

        if method == "Credit Card":

            installments = st.selectbox(
                "Installments",
                [1,3,6,12]
            )

        if st.button("Add expense"):

            cursor.execute(
                """INSERT INTO expenses(account_id,category,description,amount,method,installments,date)
                VALUES (?,?,?,?,?,?,date('now'))""",
                (1,category,desc,amount,method,installments)
            )

            conn.commit()

            st.success("Expense added")

    # SUPPLIERS

    with tabs[3]:

        name = st.text_input("Supplier name")

        product = st.text_input("Product")

        amount = st.number_input("Amount")

        status = st.selectbox(
            "Status",
            ["Pending","Paid"]
        )

        if st.button("Add supplier"):

            cursor.execute(
                """INSERT INTO suppliers(account_id,name,product,amount,status)
                VALUES (?,?,?,?,?)""",
                (1,name,product,amount,status)
            )

            conn.commit()

            st.success("Supplier saved")
