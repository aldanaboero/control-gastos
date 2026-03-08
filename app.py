import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date

st.set_page_config(page_title="Gestor Financiero Avanzado", layout="wide")

# ========================
# Título y sueldo
# ========================
st.title("💰 Gestor Financiero Avanzado")

sueldo = st.number_input("💵 Ingresos mensuales", min_value=0.0, value=0.0, step=1000)

limite_tarjeta = st.number_input("💳 Límite tarjeta de crédito", min_value=0.0, value=0.0, step=1000)

# ========================
# Base de datos en memoria
# ========================
if "gastos" not in st.session_state:
    st.session_state.gastos = pd.DataFrame(columns=[
        "Fecha","Categoria","Metodo","Descripcion","Monto","Cuotas","Cuota_actual"
    ])

df = st.session_state.gastos

# ========================
# Registrar gasto
# ========================
st.header("➕ Agregar gasto")

col1, col2, col3 = st.columns(3)

with col1:
    fecha = st.date_input("📅 Fecha", date.today())
    categoria = st.selectbox(
        "🏷️ Categoría",
        ["Alquiler","Comida","Transporte","Servicios","Peluquería",
         "Entretenimiento","Compras","Inversiones","Educación","Tarjeta de crédito","Otros"]
    )

with col2:
    metodo = st.selectbox(
        "💳 Método de pago",
        ["Efectivo","Tarjeta de crédito","Transferencia","Débito"]
    )
    monto = st.number_input("💰 Monto", min_value=0.0, step=100.0)

with col3:
    descripcion = st.text_input("📝 Descripción")
    cuotas = 1
    cuota_actual = 1
    if metodo == "Tarjeta de crédito":
        cuotas = st.number_input("Número de cuotas", min_value=1, step=1)
        cuota_actual = st.number_input("Cuota actual", min_value=1, max_value=cuotas, step=1)

if st.button("Agregar gasto"):
    nuevo = pd.DataFrame({
        "Fecha":[fecha],
        "Categoria":[categoria],
        "Metodo":[metodo],
        "Descripcion":[descripcion],
        "Monto":[monto],
        "Cuotas":[cuotas],
        "Cuota_actual":[cuota_actual]
    })
    st.session_state.gastos = pd.concat([df,nuevo], ignore_index=True)
    st.success("Gasto agregado ✅")

# ========================
# Lista de gastos y eliminación
# ========================
st.header("📋 Historial de gastos")
df = st.session_state.gastos
df_display = df.copy()
df_display["Monto por cuota"] = df_display["Monto"]/df_display["Cuotas"]
st.dataframe(df_display, use_container_width=True)

# Eliminar fila
fila_a_borrar = st.number_input("Número de fila para eliminar (comienza en 0)", min_value=0, max_value=len(df)-1, step=1)
if st.button("Eliminar fila"):
    st.session_state.gastos = df.drop(fila_a_borrar).reset_index(drop=True)
    st.success("Fila eliminada ✅")

# ========================
# Cálculos principales
# ========================
total_gastos = df["Monto"].sum()
restante = sueldo - total_gastos

# gastos por método
gastos_metodo = df.groupby("Metodo")["Monto"].sum()
gastos_tarjeta = gastos_metodo.get("Tarjeta de crédito",0)
tarjeta_restante = limite_tarjeta - gastos_tarjeta

col1, col2, col3, col4 = st.columns(4)
col1.metric("💵 Sueldo", f"${sueldo}")
col2.metric("💸 Total gastos", f"${total_gastos}")
col3.metric("🏦 Dinero restante", f"${restante}")
col4.metric("💳 Tarjeta usada", f"${gastos_tarjeta} / {limite_tarjeta}")
st.progress(min(gastos_tarjeta/limite_tarjeta,1) if limite_tarjeta>0 else 0)

# ========================
# Gráficos
# ========================
st.header("📊 Visualización de gastos")

# colores por método
colores_metodo = {
    "Efectivo":"green",
    "Tarjeta de crédito":"blue",
    "Transferencia":"purple",
    "Débito":"orange"
}

# Gastos por categoría
if not df.empty:
    st.subheader("Gastos por categoría")
    cat = df.groupby("Categoria")["Monto"].sum()
    fig1, ax1 = plt.subplots()
    ax1.pie(cat, labels=cat.index, autopct="%1.1f%%")
    st.pyplot(fig1)

# Gastos por método
if not df.empty:
    st.subheader("Gastos por método de pago")
    metodo_g = df.groupby("Metodo")["Monto"].sum()
    fig2, ax2 = plt.subplots()
    ax2.bar(metodo_g.index, metodo_g.values, color=[colores_metodo.get(x,"grey") for x in metodo_g.index])
    st.pyplot(fig2)

# Gastos mensuales
if not df.empty:
    st.subheader("Gastos mensuales")
    df["Mes"] = pd.to_datetime(df["Fecha"]).dt.month
    mensual = df.groupby("Mes")["Monto"].sum()
    fig3, ax3 = plt.subplots()
    ax3.bar(mensual.index, mensual.values, color="teal")
    ax3.set_xticks(mensual.index)
    ax3.set_xticklabels([f"Mes {i}" for i in mensual.index])
    st.pyplot(fig3)

# ========================
# Análisis IA simple
# ========================
st.header("🤖 Análisis automático")

if not df.empty:
    mayor_categoria = df.groupby("Categoria")["Monto"].sum().idxmax()
    porcentaje_sueldo = (total_gastos/sueldo)*100 if sueldo>0 else 0
    st.write("📌 Categoría donde más gastas:", mayor_categoria)
    st.write(f"📊 Has gastado {round(porcentaje_sueldo,1)}% de tu sueldo")
    if porcentaje_sueldo > 80:
        st.warning("⚠️ Estás gastando demasiado de tu sueldo")
    elif porcentaje_sueldo > 50:
        st.info("💡 Podrías intentar ahorrar más")
    else:
        st.success("👍 Tus gastos están bajo control")

# ========================
# Exportar a Excel / CSV
# ========================
st.header("📥 Exportar datos")
df_export = df.copy()
df_export["Monto por cuota"] = df_export["Monto"]/df_export["Cuotas"]
excel = df_export.to_csv(index=False).encode("utf-8")
st.download_button("Descargar CSV", excel, "gastos.csv", "text/csv")
