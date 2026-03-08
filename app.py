import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="Gestor de Finanzas", layout="wide")

st.title("💰 Gestor Inteligente de Finanzas")

# -----------------------
# SIDEBAR CONFIG
# -----------------------

st.sidebar.header("💵 Configuración financiera")

sueldo = st.sidebar.number_input("Sueldo mensual", min_value=0.0)

limite_tarjeta = st.sidebar.number_input("Límite tarjeta de crédito", min_value=0.0)

# -----------------------
# BASE DE DATOS
# -----------------------

if "gastos" not in st.session_state:
    st.session_state.gastos = pd.DataFrame(
        columns=["Fecha","Categoria","Metodo","Descripcion","Monto"]
    )

df = st.session_state.gastos

# -----------------------
# AGREGAR GASTO
# -----------------------

st.header("➕ Registrar gasto")

col1,col2,col3 = st.columns(3)

with col1:

    fecha = st.date_input("Fecha")

    categoria = st.selectbox(
        "Categoría",
        [
        "Alquiler",
        "Comida",
        "Transporte",
        "Servicios",
        "Peluquería",
        "Entretenimiento",
        "Compras",
        "Inversiones",
        "Educación",
        "Otros"
        ]
    )

with col2:

    metodo = st.selectbox(
        "Método de pago",
        [
        "Efectivo",
        "Tarjeta de crédito",
        "Transferencia",
        "Débito"
        ]
    )

with col3:

    monto = st.number_input("Monto", min_value=0.0)

descripcion = st.text_input("Descripción")

if st.button("Agregar gasto"):

    nuevo = pd.DataFrame({
        "Fecha":[fecha],
        "Categoria":[categoria],
        "Metodo":[metodo],
        "Descripcion":[descripcion],
        "Monto":[monto]
    })

    st.session_state.gastos = pd.concat([df,nuevo], ignore_index=True)

# -----------------------
# TABLA DE GASTOS
# -----------------------

st.header("📋 Historial de gastos")

df = st.session_state.gastos

st.dataframe(df, use_container_width=True)

# -----------------------
# CALCULOS
# -----------------------

total_gastos = df["Monto"].sum()

restante = sueldo - total_gastos

# gastos tarjeta

gastos_tarjeta = df[df["Metodo"]=="Tarjeta de crédito"]["Monto"].sum()

tarjeta_restante = limite_tarjeta - gastos_tarjeta

col1,col2,col3,col4 = st.columns(4)

col1.metric("💰 Sueldo", f"${sueldo}")
col2.metric("💸 Total gastos", f"${total_gastos}")
col3.metric("🏦 Dinero restante", f"${restante}")
col4.metric("💳 Tarjeta usada", f"${gastos_tarjeta}")

st.progress(gastos_tarjeta/limite_tarjeta if limite_tarjeta>0 else 0)

st.write("Disponible en tarjeta:", tarjeta_restante)

# -----------------------
# CONTROL MENSUAL
# -----------------------

st.header("📅 Análisis mensual")

if not df.empty:

    df["Mes"] = pd.to_datetime(df["Fecha"]).dt.month

    mensual = df.groupby("Mes")["Monto"].sum()

    fig, ax = plt.subplots()

    ax.bar(mensual.index, mensual.values)

    ax.set_title("Gastos por mes")

    st.pyplot(fig)

# -----------------------
# GRAFICOS
# -----------------------

if not df.empty:

    st.header("📊 Gastos por categoría")

    cat = df.groupby("Categoria")["Monto"].sum()

    fig2, ax2 = plt.subplots()

    ax2.pie(cat, labels=cat.index, autopct="%1.1f%%")

    st.pyplot(fig2)

    st.header("💳 Métodos de pago")

    metodo = df.groupby("Metodo")["Monto"].sum()

    fig3, ax3 = plt.subplots()

    ax3.bar(metodo.index, metodo.values)

    st.pyplot(fig3)

# -----------------------
# IA ANALISIS DE GASTOS
# -----------------------

st.header("🤖 Análisis automático")

if not df.empty:

    mayor_categoria = df.groupby("Categoria")["Monto"].sum().idxmax()

    porcentaje = (total_gastos/sueldo)*100 if sueldo>0 else 0

    st.write("📌 Categoría donde más gastas:", mayor_categoria)

    st.write("📊 Has gastado", round(porcentaje,1), "% de tu sueldo")

    if porcentaje > 80:
        st.warning("⚠️ Estás gastando demasiado de tu sueldo")

    elif porcentaje > 50:
        st.info("💡 Podrías intentar ahorrar más")

    else:
        st.success("👍 Tus gastos están bajo control")

# -----------------------
# EXPORTAR DATOS
# -----------------------

st.header("📥 Exportar datos")

csv = df.to_csv(index=False).encode("utf-8")

st.download_button(
    "Descargar Excel/CSV",
    csv,
    "gastos.csv",
    "text/csv"
)
