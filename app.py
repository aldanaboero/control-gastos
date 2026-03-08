import streamlit as st
import pandas as pd
from datetime import date

st.title("💰 Control de Gastos")

if "gastos" not in st.session_state:
    st.session_state.gastos = pd.DataFrame(columns=["Fecha","Categoria","Descripcion","Monto"])

st.header("Agregar gasto")

fecha = st.date_input("Fecha", date.today())

categoria = st.selectbox(
    "Categoría",
    ["Comida","Transporte","Entretenimiento","Servicios","Compras","Otros"]
)

descripcion = st.text_input("Descripción")

monto = st.number_input("Monto", min_value=0.0)

if st.button("Agregar gasto"):

    nuevo = pd.DataFrame({
        "Fecha":[fecha],
        "Categoria":[categoria],
        "Descripcion":[descripcion],
        "Monto":[monto]
    })

    st.session_state.gastos = pd.concat([st.session_state.gastos,nuevo], ignore_index=True)

st.dataframe(st.session_state.gastos)

total = st.session_state.gastos["Monto"].sum()

st.metric("Total gastado", f"${total}")
