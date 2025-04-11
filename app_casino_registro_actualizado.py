
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(layout="wide")
st.title("📊 Registro de Jugadores")

def procesar_excel(archivo, dias_inactivos_filtro=None):
    df = pd.read_excel(archivo)

    # Normalizar nombres de columnas
    df.columns = [str(col).strip().lower() for col in df.columns]

    # Identificar columnas relevantes
    columna_jugador = [col for col in df.columns if "jugador" in col][0]
    columna_operacion = [col for col in df.columns if "operacion" in col][0]
    columna_monto = [col for col in df.columns if "monto" in col][0]
    columna_fecha = [col for col in df.columns if "fecha" in col][0]

    # Convertir fechas y montos
    df[columna_fecha] = pd.to_datetime(df[columna_fecha], errors='coerce')
    df[columna_monto] = pd.to_numeric(df[columna_monto], errors='coerce')

    df_cargas = df[df[columna_operacion] == "in"]
    df_retiros = df[df[columna_operacion] == "out"]

    resumen = df_cargas.groupby(columna_jugador).agg(
        fecha_ingreso=(columna_fecha, "min"),
        veces_que_cargo=(columna_monto, "count"),
        suma_de_las_cargas=(columna_monto, "sum"),
        ultima_vez_que_cargo=(columna_fecha, "max")
    ).reset_index()

    # Sumar retiros por jugador
    retiros = df_retiros.groupby(columna_jugador).agg(
        cantidad_de_retiro=(columna_monto, "sum")
    ).reset_index()

    resumen = resumen.merge(retiros, on=columna_jugador, how="left")
    resumen["cantidad_de_retiro"] = resumen["cantidad_de_retiro"].fillna(0)

    # Calcular días inactivo
    resumen["días_inactivo"] = (pd.Timestamp.now().normalize() - resumen["ultima_vez_que_cargo"]).dt.days

    # Renombrar columna de jugador para presentación
    resumen = resumen.rename(columns={columna_jugador: "Nombre de jugador"})
    resumen = resumen[["Nombre de jugador", "fecha_ingreso", "veces_que_cargo", "suma_de_las_cargas",
                       "ultima_vez_que_cargo", "días_inactivo", "cantidad_de_retiro"]]

    if dias_inactivos_filtro is not None:
        resumen = resumen[resumen["días_inactivo"] >= dias_inactivos_filtro]

    return resumen

st.subheader("📥 Cargar archivo de Excel")
archivo_excel = st.file_uploader("Subí el archivo con las operaciones", type=["xlsx"])

dias_filtro = st.number_input("Filtrar por días de inactividad (opcional)", min_value=0, step=1, value=0)
filtro_activo = dias_filtro if dias_filtro > 0 else None

if archivo_excel is not None:
    resumen_df = procesar_excel(archivo_excel, filtro_activo)
    st.dataframe(resumen_df, use_container_width=True)

    nombre_archivo = f"registro_jugadores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    resumen_df.to_excel(nombre_archivo, index=False)
    with open(nombre_archivo, "rb") as f:
        st.download_button("📤 Descargar Excel", f, file_name=nombre_archivo)
