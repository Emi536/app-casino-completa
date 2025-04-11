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
        "Retirar": "?1",
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
    columnas_esperadas = [
        "ID", "Tipo", "Monto", "?1", "?2", "?3", "Saldo",
        "Fecha", "Hora", "UsuarioSistema", "Plataforma", "Admin", "Jugador", "Extra"
    ]
    if len(df.columns) == len(columnas_esperadas):
        df.columns = columnas_esperadas
        return df
    else:
        return None

# SECCIÓN 1: TOP 10 DE CARGAS
if seccion == "🔝 Top 10 de Cargas":
    st.header("🔝 Top 10 por Monto y Cantidad de Cargas")
    archivo = st.file_uploader("📁 Subí tu archivo de cargas recientes:", type=["xlsx", "xls", "csv"], key="top10")

    if archivo:
        df = pd.read_excel(archivo) if archivo.name.endswith((".xlsx", ".xls")) else pd.read_csv(archivo)
        df = preparar_dataframe(df)

        if df is not None:
            df_cargas = df[df["Tipo"] == "in"]
            df_cargas["Fecha"] = pd.to_datetime(df_cargas["Fecha"])

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

            writer = pd.ExcelWriter("Top10_Cargas.xlsx", engine="xlsxwriter")
            top_monto.to_excel(writer, sheet_name="Top Monto", index=False)
            top_cant.to_excel(writer, sheet_name="Top Cantidad", index=False)
            writer.close()

            with open("Top10_Cargas.xlsx", "rb") as f:
                st.download_button("📥 Descargar Excel", f, file_name="Top10_Cargas.xlsx")
        else:
            st.error("❌ El archivo no tiene el formato esperado.")

# SECCIÓN NUEVA: REGISTRO
elif seccion == "📋 Registro":
    st.header("📋 Registro General de Jugadores")
    archivo = st.file_uploader("📁 Subí tu archivo de cargas:", type=["xlsx", "xls", "csv"], key="registro")
    dias_filtrado = st.number_input("📅 Filtrar jugadores inactivos hace al menos X días (opcional):", min_value=0, max_value=365, value=0)

    if archivo:
        df = pd.read_excel(archivo) if archivo.name.endswith((".xlsx", ".xls")) else pd.read_csv(archivo)
        df = preparar_dataframe(df)

        if df is not None:
            df["Fecha"] = pd.to_datetime(df["Fecha"])
            jugadores = df["Jugador"].unique()
            resumen = []

            for jugador in jugadores:
                historial = df[df["Jugador"] == jugador].sort_values("Fecha")
                cargas = historial[historial["Tipo"] == "in"]
                retiros = historial[historial["Tipo"] == "out"]

                if not cargas.empty:
                    fecha_ingreso = cargas["Fecha"].min()
                    ultima_carga = cargas["Fecha"].max()
                    veces_que_cargo = len(cargas)
                    suma_de_cargas = cargas["Monto"].sum()
                    cantidad_retiro = retiros["Monto"].sum()
                    dias_inactivo = (pd.to_datetime(datetime.date.today()) - ultima_carga).days

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

            df_registro = df_registro.sort_values("Días inactivo", ascending=False)

            st.subheader("📄 Registro completo de jugadores")
            st.dataframe(df_registro)

            df_registro.to_excel("registro_jugadores.xlsx", index=False)
            with open("registro_jugadores.xlsx", "rb") as f:
                st.download_button("📥 Descargar Excel", f, file_name="registro_jugadores.xlsx")
        else:
            st.error("❌ El archivo no tiene el formato esperado.")
