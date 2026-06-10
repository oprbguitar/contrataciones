"""
analyze.py — Capa de decisión de ContrataRadar.

Calcula, a partir del consolidado de procesos:
  1) CONCENTRACIÓN DE PROVEEDORES — Índice Herfindahl-Hirschman (HHI) por entidad
     y a nivel global, más la cuota de los principales proveedores. Señala si un
     mercado está competido, moderado o concentrado.
  2) PROCESOS DESIERTOS — tasa de procesos desiertos por entidad y por tipo, con
     alerta cuando supera el umbral configurable.
  3) TIEMPOS PROMEDIO — días de convocatoria a adjudicación por entidad y tipo,
     con marca de "lento" sobre el umbral.

Exporta un JSON de KPIs (data_processed/kpis.json) y el CSV procesado.
"""
import json

import numpy as np
import pandas as pd

import config


def _to_num(s):
    return pd.to_numeric(s, errors="coerce")


def preparar(df):
    df = df.copy()
    for c in ["monto_referencial", "monto_adjudicado", "n_postores",
              "dias_convocatoria_adjudicacion"]:
        df[c] = _to_num(df[c])
    df["fecha_convocatoria"] = pd.to_datetime(df["fecha_convocatoria"], errors="coerce")
    df["anio"] = df["fecha_convocatoria"].dt.year
    return df


def hhi(series_montos):
    """Índice Herfindahl-Hirschman (0–10000) sobre cuotas de mercado por proveedor."""
    total = series_montos.sum()
    if total <= 0:
        return 0.0
    cuotas = (series_montos / total) * 100
    return float(round((cuotas ** 2).sum(), 1))


def clasificar_hhi(valor):
    if valor >= config.HHI_CONCENTRADO:
        return "Concentrado"
    if valor >= config.HHI_MODERADO:
        return "Moderado"
    return "Competido"


def analizar(df):
    df = preparar(df)
    adjud = df[(df["estado"] == "Adjudicado") & (df["proveedor_adjudicado"] != "")]

    # --- 1) Concentración de proveedores ---
    hhi_global = hhi(adjud_montos := adjud.groupby("proveedor_adjudicado")["monto_adjudicado"].sum())
    top_prov = (adjud.groupby("proveedor_adjudicado")["monto_adjudicado"].sum()
                .sort_values(ascending=False).head(10))
    total_adj = adjud["monto_adjudicado"].sum()
    top_prov_list = [{"proveedor": p, "monto": round(m, 2),
                      "cuota_pct": round(m / total_adj * 100, 1)}
                     for p, m in top_prov.items()]

    hhi_entidad = []
    for ent, g in adjud.groupby("entidad"):
        montos = g.groupby("proveedor_adjudicado")["monto_adjudicado"].sum()
        val = hhi(montos)
        hhi_entidad.append({"entidad": ent, "hhi": val,
                            "clasificacion": clasificar_hhi(val),
                            "n_adjudicados": int(len(g))})
    hhi_entidad = sorted(hhi_entidad, key=lambda x: x["hhi"], reverse=True)

    # --- 2) Procesos desiertos ---
    desiertos = []
    for ent, g in df.groupby("entidad"):
        n = len(g)
        d = int((g["estado"] == "Desierto").sum())
        pct = round(d / n * 100, 1) if n else 0.0
        desiertos.append({"entidad": ent, "total": n, "desiertos": d,
                          "tasa_pct": pct, "alerta": pct >= config.ALERTA_DESIERTOS_PCT})
    desiertos = sorted(desiertos, key=lambda x: x["tasa_pct"], reverse=True)

    desiertos_tipo = []
    for tipo, g in df.groupby("tipo_procedimiento"):
        n = len(g)
        d = int((g["estado"] == "Desierto").sum())
        desiertos_tipo.append({"tipo": tipo, "total": n, "desiertos": d,
                               "tasa_pct": round(d / n * 100, 1) if n else 0.0})
    desiertos_tipo = sorted(desiertos_tipo, key=lambda x: x["tasa_pct"], reverse=True)

    # --- 3) Tiempos promedio (convocatoria -> adjudicación) ---
    t = adjud.dropna(subset=["dias_convocatoria_adjudicacion"])
    tiempos_entidad = []
    for ent, g in t.groupby("entidad"):
        prom = round(float(g["dias_convocatoria_adjudicacion"].mean()), 1)
        tiempos_entidad.append({"entidad": ent, "dias_promedio": prom,
                                "n": int(len(g)), "lento": prom >= config.ALERTA_DIAS_LENTO})
    tiempos_entidad = sorted(tiempos_entidad, key=lambda x: x["dias_promedio"], reverse=True)

    tiempos_tipo = []
    for tipo, g in t.groupby("tipo_procedimiento"):
        tiempos_tipo.append({"tipo": tipo,
                             "dias_promedio": round(float(g["dias_convocatoria_adjudicacion"].mean()), 1),
                             "n": int(len(g))})
    tiempos_tipo = sorted(tiempos_tipo, key=lambda x: x["dias_promedio"], reverse=True)

    # --- Serie anual de montos adjudicados ---
    serie_anual = (adjud.groupby("anio")["monto_adjudicado"].sum().round(0))
    serie_anual = [{"anio": int(a), "monto": float(m)} for a, m in serie_anual.items()
                   if not np.isnan(a)]

    # --- Resumen ejecutivo ---
    resumen = {
        "n_procesos": int(len(df)),
        "n_entidades": int(df["entidad"].nunique()),
        "n_proveedores": int(adjud["proveedor_adjudicado"].nunique()),
        "monto_total_adjudicado": round(float(total_adj), 0),
        "tasa_desiertos_global": round(float((df["estado"] == "Desierto").mean() * 100), 1),
        "dias_promedio_global": round(float(t["dias_convocatoria_adjudicacion"].mean()), 1),
        "hhi_global": hhi_global,
        "hhi_global_clase": clasificar_hhi(hhi_global),
    }

    kpis = {
        "meta": {"fuente": config.FUENTE_NOMBRE,
                 "umbral_desiertos_pct": config.ALERTA_DESIERTOS_PCT,
                 "umbral_dias_lento": config.ALERTA_DIAS_LENTO,
                 "hhi_moderado": config.HHI_MODERADO,
                 "hhi_concentrado": config.HHI_CONCENTRADO},
        "resumen": resumen,
        "top_proveedores": top_prov_list,
        "hhi_entidad": hhi_entidad,
        "desiertos_entidad": desiertos,
        "desiertos_tipo": desiertos_tipo,
        "tiempos_entidad": tiempos_entidad,
        "tiempos_tipo": tiempos_tipo,
        "serie_anual": serie_anual,
    }

    df.to_csv(config.RUTA_PROC, index=False)
    with open(config.RUTA_KPIS, "w", encoding="utf-8") as f:
        json.dump(kpis, f, ensure_ascii=False, indent=2)
    print(f"[analyze] KPIs en {config.RUTA_KPIS} · HHI global {hhi_global} "
          f"({resumen['hhi_global_clase']}) · desiertos {resumen['tasa_desiertos_global']}%")
    return kpis


if __name__ == "__main__":
    crudo = pd.read_csv(config.RUTA_CRUDO)
    analizar(crudo)
