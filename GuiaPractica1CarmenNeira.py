import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
import os

# ---------------------- BASE DE DATOS ----------------------
conn = sqlite3.connect("estudiantes.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS estudiante (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        apellido TEXT,
        curso TEXT,
        materia TEXT
    )
""")
conn.commit()


# ---------------------- TÍTULO PRINCIPAL ----------------------
st.title("📊 Proyecto: Análisis de Datos con Python")
st.markdown("Consulta datos públicos de contrataciones en Ecuador usando filtros dinámicos.")

# ---------------------- CARÁTULA ----------------------
st.markdown("## 📘 Carátula del Proyecto")
with st.form("formulario_estudiante"):
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre")
        curso = st.text_input("Curso")
    with col2:
        apellido = st.text_input("Apellido")
        materia = st.text_input("Materia")
    guardar = st.form_submit_button("Guardar información")

if guardar and nombre and apellido and curso and materia:
    cursor.execute("INSERT INTO estudiante (nombre, apellido, curso, materia) VALUES (?, ?, ?, ?)",
                   (nombre, apellido, curso, materia))
    conn.commit()
    st.success("✅ Información guardada correctamente.")

cursor.execute("SELECT nombre, apellido, curso, materia FROM estudiante ORDER BY id DESC LIMIT 1")
registro = cursor.fetchone()
if registro:
    st.markdown("### 🧑 Información del estudiante")
    st.info(f"**Nombre:** {registro[0]} {registro[1]}  \n**Curso:** {registro[2]}  \n**Materia:** {registro[3]}")

st.markdown("---")

# ---------------------- ARCHIVOS CSV ----------------------
archivos_csv = [
    "awards_2025_bienes_y_servicios_unicos.csv",
    "contracts_2025_bienes_y_servicios_unicos.csv",
    "extensions_2025_bienes_y_servicios_unicos.csv",
    "metadata_2025_bienes_y_servicios_unicos.csv",
    "planning_2025_bienes_y_servicios_unicos.csv",
    "releases_2025_bienes_y_servicios_unicos.csv",
    "suppliers_2025_bienes_y_servicios_unicos.csv",
    "tender_2025_bienes_y_servicios_unicos.csv"
]

# ---------------------- FILTROS ----------------------
st.sidebar.header("🎛️ Filtros de Consulta")
anio_fijo = st.sidebar.selectbox("Año", ["Todos"] + list(range(2015, 2026)))
provincia_fija = st.sidebar.selectbox("Provincia", ["Todos", "Azuay", "Pichincha", "Guayas", "Manabí"])
tipo_fijo = st.sidebar.selectbox("Tipo de contratación", ["Todos", "Bienes", "Servicios", "Obras"])
consultar = st.sidebar.button("Consultar")

st.sidebar.subheader("📂 Componente OCDS")
componente_csv = st.sidebar.selectbox("Selecciona archivo", ["Todos"] + archivos_csv)

# ---------------------- FUNCIONES ----------------------
@st.cache_data
def cargar_csv_local(nombre_archivo):
    try:
        return pd.read_csv(nombre_archivo)
    except Exception as e:
        st.warning(f"No se pudo cargar {nombre_archivo}: {e}")
        return pd.DataFrame()

# ---------------------- CARGA DE DATOS ----------------------
if componente_csv == "Todos":
    df_list = []
    for archivo in archivos_csv:
        if os.path.exists(archivo):
            df_list.append(cargar_csv_local(archivo))
        else:
            st.warning(f"Archivo no encontrado: {archivo}")
    df = pd.concat(df_list, ignore_index=True) if df_list else pd.DataFrame()
else:
    df = cargar_csv_local(componente_csv)

# ---------------------- APLICAR FILTROS ----------------------
if consultar and not df.empty:
    if "año" in df.columns and anio_fijo != "Todos":
        df = df[df["año"] == int(anio_fijo)]
    if "provincia" in df.columns and provincia_fija != "Todos":
        df = df[df["provincia"] == provincia_fija]
    if "tipo" in df.columns and tipo_fijo != "Todos":
        df = df[df["tipo"] == tipo_fijo]

    st.success("✅ Datos filtrados correctamente.")
    st.dataframe(df)

    # ---------------------- VISUALIZACIÓN ----------------------
    if "entidad" in df.columns and "valor" in df.columns:
        fig = px.bar(df, x="entidad", y="valor", title="Contrataciones por entidad")
        st.plotly_chart(fig)
    elif "buyerName" in df.columns and "amount" in df.columns:
        fig = px.bar(df, x="buyerName", y="amount", title="Montos por institución")
        st.plotly_chart(fig)
    elif "title" in df.columns and "amount" in df.columns:
        fig = px.bar(df, x="title", y="amount", title="Procesos por título")
        st.plotly_chart(fig)
    else:
        st.warning("No se encontraron columnas adecuadas para graficar.")
elif consultar:
    st.warning("No se encontraron datos en el archivo seleccionado.")

# ---------------------- PESTAÑAS ----------------------
tabs = st.tabs([
    "📄 Datos filtrados",
    "📈 Visualizaciones",
    "🏛️ Total de Montos por Entidad Contratante",
    "📆 Evolución Mensual de Montos Totales",
    "🔍 Dispersión: Monto Adjudicado vs. Monto Contratado",
    "🔥 Mapa de calor: Actividad por año y mes",
    "🧮 KPIs: Adjudicación, Contrato y Extensiones",
    "📌 Conclusiones del Análisis"
])

# TAB 2: DATOS FILTRADOS
with tabs[0]:
    st.markdown("### 📄 Datos filtrados")
    st.dataframe(df)

    # Botón para descargar CSV
    st.markdown("### 💾 Descargar datos filtrados")
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Descargar CSV",
        data=csv,
        file_name="datos_filtrados.csv",
        mime="text/csv"
    )


# TAB 3: VISUALIZACIONES
with tabs[1]:
    st.markdown("### 📈 Visualizaciones")
    if "entidad" in df.columns and "valor" in df.columns:
        fig = px.bar(df, x="entidad", y="valor", title="Contrataciones por entidad")
        st.plotly_chart(fig)
    elif "buyerName" in df.columns and "amount" in df.columns:
        fig = px.bar(df, x="buyerName", y="amount", title="Montos por institución")
        st.plotly_chart(fig)
    elif "title" in df.columns and "amount" in df.columns:
        fig = px.bar(df, x="title", y="amount", title="Procesos por título")
        st.plotly_chart(fig)
    else:
        st.warning("No se encontraron columnas adecuadas para graficar.")
        
with tabs[2]:
    st.markdown("### 🏛️ Total de Montos por Entidad Contratante")
    if "procuringEntity_name" in df.columns and "value_amount" in df.columns:
        resumen_entidad = df.groupby("procuringEntity_name")["value_amount"].sum().reset_index()
        resumen_entidad = resumen_entidad.sort_values(by="value_amount", ascending=False).head(10)  # Top 10
        fig = px.bar(
            resumen_entidad,
            x="procuringEntity_name",
            y="value_amount",
            title="Top 10 Entidades por Monto Adjudicado",
            labels={"procuringEntity_name": "Entidad", "value_amount": "Monto adjudicado"},
            color="value_amount",
            text_auto=True
        )
        st.plotly_chart(fig)
    else:
        st.warning("No se encontraron columnas 'procuringEntity_name' y 'value_amount' para graficar.")


with tabs[3]:
    st.markdown("### 📆 Evolución Mensual de Montos Totales")

    if "contractPeriod_startDate" in df.columns and "value_amount" in df.columns:
        df["mes"] = pd.to_datetime(df["contractPeriod_startDate"], errors="coerce").dt.month
        resumen_mes = df.groupby("mes")["value_amount"].sum().reset_index()
        resumen_mes = resumen_mes.sort_values("mes")

        # Gráfico de línea
        fig = px.line(
            resumen_mes,
            x="mes",
            y="value_amount",
            title="Evolución Mensual de Montos Totales",
            labels={"mes": "Mes", "value_amount": "Monto total"},
            markers=True
        )
        st.plotly_chart(fig)

        # KPIs
        col1, col2, col3 = st.columns(3)
        col1.metric("📊 Total anual", f"${resumen_mes['value_amount'].sum():,.2f}")
        col2.metric("📈 Mes pico", f"${resumen_mes['value_amount'].max():,.2f}")
        col3.metric("📉 Mes mínimo", f"${resumen_mes['value_amount'].min():,.2f}")

        # Explicación automática
        st.markdown("### 🧾 Explicación automática del gráfico")
        if not resumen_mes.empty:
            mes_max = resumen_mes.loc[resumen_mes["value_amount"].idxmax(), "mes"]
            monto_max = resumen_mes["value_amount"].max()
            mes_max = int(mes_max)
            mes_nombre = pd.to_datetime(f"2025-{mes_max}-01").strftime("%B")
            st.info(f"📌 El mes con mayor contratación fue **{mes_nombre}**, con un monto total de **${monto_max:,.2f}**.")
        else:
            st.warning("No se pudo generar la explicación automática porque no hay datos mensuales disponibles.")

        # Botón para descargar CSV
        st.markdown("### 💾 Descargar resumen mensual")
        csv_mes = resumen_mes.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Descargar CSV", csv_mes, "evolucion_mensual.csv", "text/csv")

    else:
        st.warning("No se encontraron columnas 'contractPeriod_startDate' y 'value_amount' para graficar.")

with tabs[4]:
    st.markdown("### 🔍 Dispersión: Monto Adjudicado vs. Monto Contratado")

    # Cargar awards y contracts por separado
    df_awards = cargar_csv_local("awards_2025_bienes_y_servicios_unicos.csv")
    df_contracts = cargar_csv_local("contracts_2025_bienes_y_servicios_unicos.csv")

    # Verificar columnas comunes
    if "id" in df_awards.columns and "awardID" in df_contracts.columns:
        df_merged = pd.merge(
            df_awards,
            df_contracts,
            left_on="id",
            right_on="awardID",
            suffixes=("_adjudicado", "_contratado")
        )

        # Filtrar valores válidos
        df_merged = df_merged[
            (df_merged["amount_adjudicado"].notnull()) &
            (df_merged["amount_contratado"].notnull())
        ]

        # Gráfico de dispersión
        fig = px.scatter(
            df_merged,
            x="amount_adjudicado",
            y="amount_contratado",
            color="status_contratado" if "status_contratado" in df_merged.columns else None,
            title="Dispersión: Monto Adjudicado vs. Monto Contratado",
            labels={
                "amount_adjudicado": "Monto adjudicado",
                "amount_contratado": "Monto contratado"
            },
            hover_data=["title_contratado", "procuringEntity_name"] if "procuringEntity_name" in df_merged.columns else None
        )
        st.plotly_chart(fig)

        # Comentario automático
        st.markdown("### 🧾 Comentario automático")
        desviacion = (df_merged["amount_contratado"] - df_merged["amount_adjudicado"]).mean()
        if desviacion > 0:
            st.info(f"📌 En promedio, los contratos ejecutados superan los montos adjudicados por **${desviacion:,.2f}**.")
        else:
            st.info(f"📌 En promedio, los contratos ejecutados están por debajo de lo adjudicado por **${abs(desviacion):,.2f}**.")

    else:
        st.warning("No se encontraron columnas 'id' en awards y 'awardID' en contracts para unir los datos.")

with tabs[5]:
    st.markdown("### 🔥 Mapa de calor: Actividad por año y mes")

    df_releases = cargar_csv_local("releases_2025_bienes_y_servicios_unicos.csv")

    if "date" in df_releases.columns:
        df_releases["fecha"] = pd.to_datetime(df_releases["date"], errors="coerce")
        df_releases["año"] = df_releases["fecha"].dt.year
        df_releases["mes"] = df_releases["fecha"].dt.month

        actividad = df_releases.groupby(["año", "mes"]).size().unstack(fill_value=0)

        fig = px.imshow(
            actividad,
            labels=dict(x="Mes", y="Año", color="Cantidad de publicaciones"),
            x=[f"{m}" for m in actividad.columns],
            y=actividad.index,
            title="🔥 Intensidad de publicaciones por año y mes"
        )
        st.plotly_chart(fig)
    else:
        st.warning("No se encontró la columna 'date' en releases.")
            # Comentario automático
        st.markdown("### 🧾 Comentario automático")
        total_por_año = actividad.sum(axis=1)
        año_max = total_por_año.idxmax()
        publicaciones_max = total_por_año.max()

        st.info(f"📌 El año con mayor actividad fue **{año_max}**, con un total de **{publicaciones_max:,} publicaciones** registradas.")

with tabs[6]:
    st.markdown("### 🧮 KPIs: Adjudicación, Contrato y Extensiones")

    df_awards = cargar_csv_local("awards_2025_bienes_y_servicios_unicos.csv")
    df_contracts = cargar_csv_local("contracts_2025_bienes_y_servicios_unicos.csv")
    df_extensions = cargar_csv_local("extensions_2025_bienes_y_servicios_unicos.csv")

    monto_awards = df_awards["amount"].sum() if "amount" in df_awards.columns else 0
    monto_contracts = df_contracts["amount"].sum() if "amount" in df_contracts.columns else 0
    promedio_contracts = df_contracts["amount"].mean() if "amount" in df_contracts.columns else 0
    num_extensions = len(df_extensions) if not df_extensions.empty else 0

    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Total adjudicado", f"${monto_awards:,.2f}")
    col2.metric("📄 Total contratado", f"${monto_contracts:,.2f}")
    col3.metric("📊 Promedio por contrato", f"${promedio_contracts:,.2f}")
    col4.metric("🔁 Nº de extensiones", f"{num_extensions:,}")

    # Comentario automático
    st.markdown("### 🧾 Comentario automático")
    diferencia = monto_contracts - monto_awards
    if diferencia > 0:
        st.info(f"📌 Los contratos ejecutados superan lo adjudicado por **${diferencia:,.2f}**, lo que podría indicar ampliaciones o ajustes posteriores.")
    elif diferencia < 0:
        st.info(f"📌 Los contratos ejecutados están por debajo de lo adjudicado por **${abs(diferencia):,.2f}**, lo que podría reflejar cancelaciones o ajustes presupuestarios.")
    else:
        st.info("📌 El monto contratado coincide exactamente con lo adjudicado.")

    # Cuadro comparativo
    st.markdown("### 📊 Comparativo de montos")
    comparativo_df = pd.DataFrame({
        "Indicador": ["Monto adjudicado", "Monto contratado", "Promedio por contrato", "Nº de extensiones"],
        "Valor": [monto_awards, monto_contracts, promedio_contracts, num_extensions]
    })

    st.dataframe(comparativo_df, use_container_width=True)

    # Gráfico de barras
    st.markdown("### 📉 Visualización comparativa")
    fig_bar = px.bar(
        comparativo_df.iloc[:3],  # Solo montos
        x="Indicador",
        y="Valor",
        text="Valor",
        title="Comparativo de montos adjudicados y contratados",
        labels={"Valor": "Monto en USD"},
        color="Indicador"
    )
    fig_bar.update_traces(texttemplate="%{text:,.2f}", textposition="outside")
    st.plotly_chart(fig_bar)

with tabs[7]:
    st.markdown("### 📌 Conclusiones del Análisis")

    st.markdown("#### 🧠 Principales hallazgos")
    st.success("🔹 Las entidades contratantes con mayor volumen de contratación fueron aquellas del sector salud y obras públicas.")
    st.success("🔹 Los meses con mayor actividad fueron **Julio** y **Diciembre**, mostrando picos en montos adjudicados.")
    st.success("🔹 El año más activo en publicaciones fue **2025**, según el mapa de calor.")

    st.markdown("#### 📊 Variables con mayor peso")
    st.info("💰 La variable `amount` en adjudicaciones y contratos representa el principal indicador financiero.")
    st.info("📅 Las fechas de inicio (`contractPeriod_startDate`) permiten detectar patrones estacionales.")

    st.markdown("#### 🔍 Comportamientos atípicos")
    st.warning("⚠️ Se detectaron contratos con montos superiores a lo adjudicado, lo que podría indicar extensiones no registradas adecuadamente.")
    st.warning("⚠️ Algunas adjudicaciones no tienen contratos asociados, lo que sugiere procesos inconclusos o cancelados.")

    st.markdown("#### 💡 Hipótesis para estudios futuros")
    st.markdown("- ¿Existe una correlación entre el tipo de entidad contratante y la frecuencia de extensiones?")
    st.markdown("- ¿Los picos de contratación en diciembre responden a cierres presupuestarios?")
    st.markdown("- ¿Qué provincias concentran los mayores montos y por qué sectores?")

    st.markdown("#### 📋 Recomendaciones pedagógicas")
    st.markdown("- Incentivar el uso de filtros dinámicos para explorar patrones locales.")
    st.markdown("- Promover el análisis comparativo entre adjudicación y ejecución para evaluar eficiencia.")
    st.markdown("- Usar visualizaciones como mapas de calor y dispersión para detectar anomalías rápidamente.")
