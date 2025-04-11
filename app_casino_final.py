
import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="App de Cargas - Casino", layout="wide")
st.title("🎰 App de Análisis de Cargas del Casino")

seccion = st.sidebar.radio("Seleccioná una sección:", ["🔝 Top 10 de Cargas", "📋 Registro"])

# SECCIÓN 1: TOP 10 DE CARGAS
if seccion == "🔝 Top 10 de Cargas":
    st.header("🔝 Top 10 por Monto y Cantidad de Cargas")
    archivo = st.file_uploader("📁 Subí tu archivo de cargas recientes:", type=["xlsx"], key="top10")

    if archivo:
        df = pd.read_excel(archivo, sheet_name="Hoja1")
        df.columns = df.columns.str.strip()
        df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
        df["Depositar"] = pd.to_numeric(df["Depositar"], errors="coerce").fillna(0)
        df["Jugador"] = df["Del usuario"].astype(str).str.strip().str.lower()

        df_cargas = df[df["operación"] == "in"]

        top_monto = (
            df_cargas.groupby("Jugador")
            .agg(Monto_Total_Cargado=("Depositar", "sum"), Cantidad_Cargas=("Jugador", "count"))
            .sort_values(by="Monto_Total_Cargado", ascending=False)
            .head(10)
            .reset_index()
        )

        top_cant = (
            df_cargas.groupby("Jugador")
            .agg(Cantidad_Cargas=("Jugador", "count"), Monto_Total_Cargado=("Depositar", "sum"))
            .sort_values(by="Cantidad_Cargas", ascending=False)
            .head(10)
            .reset_index()
        )

        st.subheader("💰 Top 10 por Monto Total Cargado")
        st.dataframe(top_monto)

        st.subheader("🔢 Top 10 por Cantidad de Cargas")
        st.dataframe(top_cant)

        writer = pd.ExcelWriter("Top10_Cargas.xlsx", engine="xlsxwriter")
        top_monto.to_excel(writer, sheet_name="Top Monto", index=False)
        top_cant.to_excel(writer, sheet_name="Top Cantidad", index=False)
        writer.close()

        with open("Top10_Cargas.xlsx", "rb") as f:
            st.download_button("📥 Descargar Excel", f, file_name="Top10_Cargas.xlsx")

# SECCIÓN 2: REGISTRO GENERAL DE JUGADORES
elif seccion == "📋 Registro":
    st.header("📋 Registro General de Jugadores")
    archivo = st.file_uploader("📁 Subí tu archivo de cargas:", type=["xlsx"], key="registro")
    dias_filtrado = st.number_input("📅 Filtrar jugadores inactivos hace al menos X días (opcional):", min_value=0, max_value=365, value=0)

    if archivo:
        df = pd.read_excel(archivo, sheet_name="Hoja1")
        df.columns = df.columns.str.strip()

        # Normalizar columnas relevantes
        df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
        df["Depositar"] = pd.to_numeric(df["Depositar"], errors="coerce").fillna(0)
        df["Retirar"] = pd.to_numeric(df["Retirar"], errors="coerce").fillna(0)

        df["Jugador"] = df["Del usuario"].astype(str).str.strip().str.lower()
        df["Receptor"] = df["Al usuario"].astype(str).str.strip().str.lower()

        jugadores = df["Jugador"].unique()
        resumen = []

        for jugador in jugadores:
            historial = df[df["Jugador"] == jugador].sort_values("Fecha")
            cargas = historial[historial["operación"] == "in"]
            fecha_ingreso = cargas["Fecha"].min() if not cargas.empty else pd.NaT
            ultima_carga = cargas["Fecha"].max() if not cargas.empty else pd.NaT
            veces_que_cargo = len(cargas)
            suma_de_cargas = cargas["Depositar"].sum()

            # Buscar retiros donde este jugador fue el receptor
            retiros = df[df["Receptor"] == jugador]
            cantidad_retiro = retiros["Retirar"].sum()

            dias_inactivo = (pd.to_datetime(datetime.date.today()) - ultima_carga).days if pd.notnull(ultima_carga) else None

            resumen.append({
                "Nombre de jugador": jugador,
                "Fecha que ingresó": fecha_ingreso,
                "Veces que cargó": veces_que_cargo,
                "Suma de las cargas": suma_de_cargas,
                "Última vez que cargó": ultima_carga,
                "Días inactivo": dias_inactivo,
                "Cantidad de retiro": cantidad_retiro
            })

        df_registro = pd.DataFrame(resumen)
        if dias_filtrado > 0:
            df_registro = df_registro[df_registro["Días inactivo"] >= dias_filtrado]

        df_registro = df_registro.sort_values("Días inactivo", ascending=False, na_position='last')

        st.subheader("📄 Registro completo de jugadores")
        st.dataframe(df_registro)

        df_registro.to_excel("registro_jugadores.xlsx", index=False)
        with open("registro_jugadores.xlsx", "rb") as f:
            st.download_button("📥 Descargar Excel", f, file_name="registro_jugadores.xlsx")
