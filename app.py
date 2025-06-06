import streamlit as st
import pandas as pd
import datetime
import plotly.express as px

st.set_page_config(page_title="PlayerMetrics - Análisis de Cargas", layout="wide")
st.markdown("<h1 style='text-align: center; color:#F44336;'>Player metrics</h1>", unsafe_allow_html=True)

# Establecer la URL de la imagen en GitHub
background_image_url = "https://raw.githubusercontent.com/Emi536/app-casino-completa/main/acab4f05-0a6b-4e3b-bfea-7461d6c6ca81.png"

# Agregar CSS para ocultar el icono de GitHub
st.markdown(
    """
    <style>
    .stApp .header .stGitHub { 
        display: none;
    }
    </style>
    """, unsafe_allow_html=True
)


seccion = st.sidebar.radio("Seleccioná una sección:", ["🔝 Métricas de jugadores", "📋 Registro de actividad de jugadores", "📆 Seguimiento de jugadores inactivos"])

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

# SECCIÓN 1: MÉTRICAS DE JUGADORES
if seccion == "🔝 Métricas de jugadores":
    st.header("🔝 Métricas de jugadores - monto y cantidad de cargas")

        # Filtro para elegir la cantidad de jugadores
    top_n = st.selectbox("Selecciona el número de jugadores a mostrar:", [30, 50, 100, 150, 200], index=0)

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
                .head(top_n)
                .reset_index()
            )

            top_cant = (
                df_cargas.groupby("Jugador")
                .agg(Cantidad_Cargas=("Jugador", "count"), Monto_Total_Cargado=("Monto", "sum"))
                .sort_values(by="Cantidad_Cargas", ascending=False)
                .head(top_n)
                .reset_index()
            )

            # Obtener la última vez que cargó (Última fecha de carga)
            top_monto['Última vez que cargó'] = top_monto['Jugador'].apply(lambda x: df_cargas[df_cargas['Jugador'] == x]['Fecha'].max())
            top_cant['Última vez que cargó'] = top_cant['Jugador'].apply(lambda x: df_cargas[df_cargas['Jugador'] == x]['Fecha'].max())

            st.subheader(f"💰 Top {top_n} por Monto Total Cargado")
            st.dataframe(top_monto)

            st.subheader(f"🔢 Top {top_n} por Cantidad de Cargas")
            st.dataframe(top_cant)

            try:
                with pd.ExcelWriter(f"Top{top_n}_Cargas.xlsx", engine="openpyxl") as writer:
                    top_monto.to_excel(writer, sheet_name="Top Monto", index=False)
                    top_cant.to_excel(writer, sheet_name="Top Cantidad", index=False)

                with open(f"Top{top_n}_Cargas.xlsx", "rb") as f:
                    st.download_button(f"📥 Descargar Excel - Top {top_n} Cargas", f, file_name=f"Top{top_n}_Cargas.xlsx")
            except Exception as e:
                st.error(f"❌ Ocurrió un error al guardar el archivo: {e}")

        else:
            st.error("❌ El archivo no tiene el formato esperado.")

# SECCIÓN 2: REGISTRO
elif seccion == "📋 Registro de actividad de jugadores":
    st.header("📋 Registro general de jugadores")
    archivo = st.file_uploader("📁 Subí tu archivo de cargas:", type=["xlsx", "xls", "csv"], key="registro")
    

    if archivo:
        df = pd.read_excel(archivo) if archivo.name.endswith((".xlsx", ".xls")) else pd.read_csv(archivo)
        df = preparar_dataframe(df)

        if df is not None:
            df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
            df["Monto"] = pd.to_numeric(df["Monto"], errors="coerce").fillna(0)
            df["Retiro"] = df["Retiro"].astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
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

            df_registro = df_registro.sort_values("Días inactivo", ascending=False)

            st.subheader("📄 Registro completo de jugadores")
            st.dataframe(df_registro)

            df_registro.to_excel("registro_jugadores.xlsx", index=False)
            with open("registro_jugadores.xlsx", "rb") as f:
                st.download_button("📥 Descargar Excel", f, file_name="registro_jugadores.xlsx")
        else:
            st.error("❌ El archivo no tiene el formato esperado.")


# SECCIÓN 3: INACTIVOS AGENDA
# --- SECCIÓN 3: SEGUIMIENTO DE INACTIVOS ---
elif seccion == "📆 Seguimiento de jugadores inactivos":
    st.header("📆 Seguimiento de Jugadores Inactivos Mejorado")
    archivo_agenda = st.file_uploader("📁 Subí tu archivo con dos hojas (Nombre y Reporte General):", type=["xlsx", "xls"], key="agenda")

    if archivo_agenda:
        try:
            df_hoja1 = pd.read_excel(archivo_agenda, sheet_name=0)
            df_hoja2 = pd.read_excel(archivo_agenda, sheet_name=1)

            df_hoja2 = df_hoja2.rename(columns={
                "operación": "Tipo",
                "Depositar": "Monto",
                "Fecha": "Fecha",
                "Al usuario": "Jugador",
                "Retirar": "Retirar"
            })

            df_hoja2["Jugador"] = df_hoja2["Jugador"].astype(str).str.strip().str.lower()
            df_hoja2["Fecha"] = pd.to_datetime(df_hoja2["Fecha"], errors="coerce")
            df_hoja2["Monto"] = pd.to_numeric(df_hoja2["Monto"], errors="coerce").fillna(0)
            df_hoja2["Retirar"] = pd.to_numeric(df_hoja2["Retirar"], errors="coerce").fillna(0)

            nombres_hoja1 = df_hoja1["Nombre"].dropna().astype(str).str.strip().str.lower().unique()
            df_filtrado = df_hoja2[df_hoja2["Jugador"].isin(nombres_hoja1)]

            resumen = []
            hoy = pd.to_datetime(datetime.date.today())

            for jugador in df_filtrado["Jugador"].dropna().unique():
                historial = df_filtrado[df_filtrado["Jugador"] == jugador].sort_values("Fecha")
                cargas = historial[historial["Tipo"] == "in"]

                if not cargas.empty:
                    fecha_ingreso = cargas["Fecha"].min()
                    ultima_carga = cargas["Fecha"].max()
                    veces_que_cargo = len(cargas)
                    suma_de_cargas = cargas["Monto"].sum()
                    promedio_monto = cargas["Monto"].mean()
                    dias_inactivo = (hoy - ultima_carga).days
                    cantidad_retiro = historial[historial["Tipo"] == "out"]["Retirar"].sum()

                    riesgo = min(100, (dias_inactivo * 2) + (10 / (veces_que_cargo + 1)) + (3000 / (promedio_monto + 1)))
                    riesgo = round(riesgo, 2)

                    resumen.append({
                        "Nombre de Usuario": jugador,
                        "Fecha que ingresó": fecha_ingreso,
                        "Última vez que cargó": ultima_carga,
                        "Veces que cargó": veces_que_cargo,
                        "Suma de las cargas": suma_de_cargas,
                        "Monto promedio": promedio_monto,
                        "Días inactivos": dias_inactivo,
                        "Cantidad de retiro": cantidad_retiro,
                        "Riesgo de inactividad": riesgo
                    })

            if resumen:
                df_resultado = pd.DataFrame(resumen).sort_values("Riesgo de inactividad", ascending=False)
                st.dataframe(df_resultado)

                st.subheader("\ud83d\udcc8 Distribución del Score de Riesgo")
                fig_riesgo = px.histogram(df_resultado, x="Riesgo de inactividad", nbins=20, title="Distribución de Riesgos")
                st.plotly_chart(fig_riesgo, use_container_width=True)

                df_resultado.to_excel("jugadores_riesgo_inactividad.xlsx", index=False)
                with open("jugadores_riesgo_inactividad.xlsx", "rb") as f:
                    st.download_button("\ud83d\udcc5 Descargar Excel Riesgo Inactividad", f, file_name="jugadores_riesgo_inactividad.xlsx")

        except Exception as e:
            st.error(f"\u274c Error al procesar el archivo: {e}")
