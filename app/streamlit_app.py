"""
streamlit_app.py — Tablero local interactivo de ContrataRadar.

Ejecutar:
    streamlit run app/streamlit_app.py

Permite explorar concentración (HHI), desiertos y tiempos, filtrar por entidad y
generar una plantilla TDR/EETT para un proceso elegido.
"""
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parents[1]))
import config  # noqa: E402
from src import analyze, templates_tdr  # noqa: E402

st.set_page_config(page_title="ContrataRadar", layout="wide")
st.title("📡 ContrataRadar")
st.caption("Analítica de contrataciones públicas (OECE / SEACE + PERÚ COMPRAS) · "
           "concentración de proveedores, procesos desiertos y tiempos promedio. "
           "Demostración con muestra sintética. Creado por Pierre R. · peru.labs.pe@gmail.com")


@st.cache_data
def cargar():
    df = pd.read_csv(config.RUTA_PROC if Path(config.RUTA_PROC).exists() else config.RUTA_MUESTRA)
    return df


try:
    df = cargar()
except FileNotFoundError:
    st.warning("Ejecuta primero: `python -m src.run_pipeline`")
    st.stop()

kpis = analyze.analizar(df)
r = kpis["resumen"]

c1, c2, c3, c4 = st.columns(4)
c1.metric("Monto adjudicado (S/)", f"{r['monto_total_adjudicado']:,.0f}")
c2.metric("HHI global", f"{r['hhi_global']} · {r['hhi_global_clase']}")
c3.metric("Tasa de desiertos", f"{r['tasa_desiertos_global']} %")
c4.metric("Días prom. adjudicación", f"{r['dias_promedio_global']}")

st.subheader("Concentración de proveedores · HHI por entidad")
st.dataframe(pd.DataFrame(kpis["hhi_entidad"]), use_container_width=True, hide_index=True)

col1, col2 = st.columns(2)
with col1:
    st.subheader("Procesos desiertos · por entidad")
    st.dataframe(pd.DataFrame(kpis["desiertos_entidad"]), use_container_width=True, hide_index=True)
with col2:
    st.subheader("Tiempos promedio · por entidad")
    st.dataframe(pd.DataFrame(kpis["tiempos_entidad"]), use_container_width=True, hide_index=True)

st.subheader("Top proveedores por monto adjudicado")
st.dataframe(pd.DataFrame(kpis["top_proveedores"]), use_container_width=True, hide_index=True)

st.divider()
st.subheader("Generar plantilla TDR / EETT para un proceso")
proc = st.selectbox("Elige un proceso", df["id_proceso"].tolist())
if st.button("Generar plantilla"):
    fila = df[df["id_proceso"] == proc].iloc[0].to_dict()
    ruta = templates_tdr.generar_para_fila(fila)
    with open(ruta, encoding="utf-8") as f:
        contenido = f.read()
    st.success(f"Plantilla generada: {ruta}")
    st.code(contenido, language="markdown")
    st.download_button("Descargar plantilla", contenido,
                       file_name=Path(ruta).name, mime="text/markdown")

st.info("El HHI mide concentración de mercado (0–10000): a mayor valor, menos competido. "
        "Las plantillas son un asistente de estructuración; no reemplazan la revisión legal.")
