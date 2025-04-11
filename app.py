
import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="App de Cargas - Casino", layout="wide")
st.title("🎰 App de Análisis de Cargas del Casino")

seccion = st.sidebar.radio("Seleccioná una sección:", ["📋 Registro"])

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

# SECCIÓN REGISTRO
if seccion == "📋 Registro":
    st.header("📋 Registro General de Jugadores")
    archivo = st.file_uploader("📁 Subí tu archivo de cargas:", type=["xlsx", "xls", "csv"], key="registro")
    dias_filtrado = st.number_input("📅 Filtrar jugadores inactivos hace al menos X días (opcional):", min_value=0, max_value=365, value=0)

    if archivo:
        df = pd.read_excel(archivo) if archivo.name.endswith((".xlsx", ".xls")) else pd.read_csv(archivo)
        df = preparar_dataframe(df)

        if df is not None:
            df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
            df["Monto"] = pd.to_numeric(df["Monto"], errors="coerce").fillna(0)

            # Procesar la columna de Retiro
            df["Retiro"] = (
                df["Retiro"]
                .astype(str)
                .str.replace(".", "", regex=False)
                .str.replace(",", ".", regex=False)
            )
            df["Retiro"] = pd.to_numeric(df["Retiro"], errors="coerce").fillna(0)

            jugadores = df["Jugador"].dropna().unique()
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
                    cantidad_retiro = retiros["Retiro"].sum()
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

            df_registro.to_csv("registro_jugadores.csv", index=False)
            with open("registro_jugadores.csv", "rb") as f:
                st.download_button("📥 Descargar CSV", f, file_name="registro_jugadores.csv")
        else:
            st.error("❌ El archivo no tiene el formato esperado.")
