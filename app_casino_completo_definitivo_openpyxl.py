
import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="App de Cargas - Casino", layout="wide")
st.title("🎰 App de Análisis de Cargas del Casino")

seccion = st.sidebar.radio("Seleccioná una sección:", ["🔝 Top 10 de Cargas", "📉 Jugadores Inactivos", "📋 Registro"])

# FUNCIONES AUXILIARES
def preparar_dataframe(df):
    df = df.rename(columns={
        "operación": "Tipo",
        "Depositar": "Monto",
        "Retirar": "Retiro",
        "Wager": "?2",
        "Límites": "?3",
        "Balance antes de operación": "Saldo",
        "Fecha": "Fecha",
        "Tiempo": "Hora",
        "Iniciador": "UsuarioSistema",
        "Del usuario": "Plataforma",
        "Sistema": "Admin",
        "Al usuario": "Jugador",
        "IP": "Extra"
    })
    return df

# SECCIÓN 1: TOP 10 DE CARGAS
if seccion == "🔝 Top 10 de Cargas":
    st.header("🔝 Top 10 por Monto y Cantidad de Cargas")
    archivo = st.file_uploader("📁 Subí tu archivo de cargas recientes:", type=["xlsx", "xls", "csv"], key="top10")

    if archivo:
        df = pd.read_excel(archivo) if archivo.name.endswith((".xlsx", ".xls")) else pd.read_csv(archivo)
        df = preparar_dataframe(df)

        if df is not None:
            df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
            df["Monto"] = pd.to_numeric(df["Monto"], errors="coerce").fillna(0)
            df_cargas = df[df["Tipo"] == "in"]

            top_monto = (
                df_cargas.groupby("Jugador")
                .agg(Monto_Total_Cargado=("Monto", "sum"), Cantidad_Cargas=("Jugador", "count"))
                .sort_values(by="Monto_Total_Cargado", ascending=False)
                .head(10)
                .reset_index()
            )

            top_cant = (
                df_cargas.groupby("Jugador")
                .agg(Cantidad_Cargas=("Jugador", "count"), Monto_Total_Cargado=("Monto", "sum"))
                .sort_values(by="Cantidad_Cargas", ascending=False)
                .head(10)
                .reset_index()
            )

            st.subheader("💰 Top 10 por Monto Total Cargado")
            st.dataframe(top_monto)

            st.subheader("🔢 Top 10 por Cantidad de Cargas")
            st.dataframe(top_cant)

            writer = pd.ExcelWriter("Top10_Cargas.xlsx", engine="openpyxl")
            top_monto.to_excel(writer, sheet_name="Top Monto", index=False)
            top_cant.to_excel(writer, sheet_name="Top Cantidad", index=False)
            writer.close()

            with open("Top10_Cargas.xlsx", "rb") as f:
                st.download_button("📥 Descargar Excel", f, file_name="Top10_Cargas.xlsx")
        else:
            st.error("❌ El archivo no tiene el formato esperado.")
