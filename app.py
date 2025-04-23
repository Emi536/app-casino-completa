import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="PlayerMetrics - Análisis de Cargas", layout="wide")
st.markdown("<h1 style='text-align: center; color:#F44336;'>Player metrics</h1>", unsafe_allow_html=True)

# URL de la imagen
background_image_url = "https://raw.githubusercontent.com/Emi536/app-casino-completa/main/acab4f05-0a6b-4e3b-bfea-7461d6c6ca81.png"

# CSS para establecer la imagen de fondo
st.markdown(
    f"""
    <style>
    .reportview-container {{
        background-image: url("{background_image_url}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }}
    .sidebar .sidebar-content {{
        background-color: rgba(0, 0, 0, 0.7);  /* Fondo oscuro para la barra lateral */
    }}
    .st-bd {{
        color: #FFFFFF;  /* Texto blanco */
    }}
    h1 {{
        color: #4CAF50;  /* Título principal en verde brillante */
        text-align: center;
    }}
    .st-header {{
        background-color: #2196F3;  /* Azul para los encabezados */
    }}
    .st-dataframe {{
        background-color: #f8f9fa;  /* Fondo claro para las tablas */
    }}
    .st-button {{
        background-color: #FF9800;  /* Naranja para los botones */
        color: #FFFFFF;  /* Texto blanco en botones */
    }}
    .st-error {{
        color: #F44336;  /* Rojo para los mensajes de error */
    }}
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
elif seccion == "📆 Seguimiento de jugadores inactivos":
    st.header("📆 Jugadores inactivos detectados")

    archivo_agenda = st.file_uploader("📁 Subí tu archivo con dos hojas (Nombre y Reporte General):", type=["xlsx", "xls"], key="agenda")

    if archivo_agenda:
        try:
            df_hoja1 = pd.read_excel(archivo_agenda, sheet_name=0)
            df_hoja2 = pd.read_excel(archivo_agenda, sheet_name=1)

            df_hoja2 = df_hoja2.rename(columns={
                "operación": "Tipo",
                "Depositar": "Monto",
                "Fecha": "Fecha",
                "Al usuario": "Jugador"
            })

            df_hoja2["Jugador"] = df_hoja2["Jugador"].astype(str).str.strip().str.lower()
            df_hoja2["Fecha"] = pd.to_datetime(df_hoja2["Fecha"], errors="coerce")
            df_hoja2["Monto"] = pd.to_numeric(df_hoja2["Monto"], errors="coerce").fillna(0)

            nombres_hoja1 = df_hoja1["Nombre"].dropna().astype(str).str.strip().str.lower().unique()
            df_hoja2["Jugador"] = df_hoja2["Jugador"].astype(str).str.strip().str.lower()
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
                    dias_inactivo = (hoy - ultima_carga).days

                    resumen.append({
                        "Nombre de Usuario": jugador,
                        "Fecha que ingresó": fecha_ingreso,
                        "Veces que cargó": veces_que_cargo,
                        "Suma de las cargas": suma_de_cargas,
                        "Última vez que cargó": ultima_carga,
                        "Días inactivos": dias_inactivo,
                        "Cantidad de retiro": historial[historial["Tipo"] == "out"]["Retirar"].sum()
                    })

            
            
            if resumen:
                df_resultado = pd.DataFrame(resumen).sort_values("Días inactivos", ascending=False)

                df_hoja1["Nombre_normalizado"] = df_hoja1["Nombre"].astype(str).str.strip().str.lower()
                df_hoja1 = df_hoja1[["Nombre_normalizado", "Sesiones"]]
                df_resultado["Nombre_normalizado"] = df_resultado["Nombre de Usuario"].astype(str).str.strip().str.lower()
                df_resultado = df_resultado.merge(df_hoja1, on="Nombre_normalizado", how="left")
                df_resultado.drop(columns=["Nombre_normalizado"], inplace=True)

                sesiones_disponibles = df_resultado["Sesiones"].dropna().unique()
                sesion_filtrada = st.selectbox("🎯 Filtrar por Sesión (opcional):", options=["Todas"] + sorted(sesiones_disponibles.tolist()))
                if sesion_filtrada != "Todas":
                    df_resultado = df_resultado[df_resultado["Sesiones"] == sesion_filtrada]

                st.subheader("📋 Resumen de Actividad de Jugadores Coincidentes")
                st.dataframe(df_resultado)

                df_resultado.to_excel("agenda_inactivos_resumen.xlsx", index=False)
                with open("agenda_inactivos_resumen.xlsx", "rb") as f:
                    st.download_button("📥 Descargar Excel", f, file_name="agenda_inactivos_resumen.xlsx")
            else:
                st.warning("No se encontraron coincidencias entre ambas hojas.")

        except Exception as e:
            st.error(f"❌ Error al procesar el archivo: {e}")
