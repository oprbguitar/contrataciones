"""
ingest.py — Obtiene el consolidado de procedimientos de contratación.

  python -m src.ingest --refresh   # descarga de la fuente real (config.FUENTE_URL)
  python -m src.ingest             # modo muestra sintética (offline)

Diseñado para correr de forma programada (GitHub Actions / cron) y refrescar el
dato cuando OECE / PERÚ COMPRAS publican una nueva versión de sus datos abiertos.
"""
import argparse
import sys
from io import StringIO

import pandas as pd
import requests

import config

COLUMNAS = ["id_proceso", "entidad", "tipo_procedimiento", "objeto", "descripcion",
            "estado", "fecha_convocatoria", "fecha_adjudicacion",
            "dias_convocatoria_adjudicacion", "n_postores",
            "monto_referencial", "monto_adjudicado", "proveedor_adjudicado"]


def _normalizar(df):
    df = df.rename(columns={c: c.strip().lower() for c in df.columns})
    faltan = [c for c in COLUMNAS if c not in df.columns]
    if faltan:
        raise ValueError(f"La fuente no trae columnas esperadas: {faltan}. "
                         f"Ajusta el mapeo en ingest._normalizar().")
    return df[COLUMNAS]


def descargar_en_vivo():
    if not config.FUENTE_URL:
        raise RuntimeError("config.FUENTE_URL está vacío.")
    r = requests.get(config.FUENTE_URL, timeout=90)
    r.raise_for_status()
    df = _normalizar(pd.read_csv(StringIO(r.text)))
    df["fuente"] = config.FUENTE_NOMBRE
    return df


def cargar_muestra():
    import os
    if not os.path.exists(config.RUTA_MUESTRA):
        from src.make_sample import generar_muestra
        generar_muestra().to_csv(config.RUTA_MUESTRA, index=False)
    return pd.read_csv(config.RUTA_MUESTRA)


def ingestar(refresh=False):
    if refresh:
        try:
            df = descargar_en_vivo()
            print(f"[ingest] Descarga en vivo OK: {len(df)} procesos.")
        except Exception as e:  # noqa: BLE001
            print(f"[ingest] Sin fuente en vivo ({e}). Uso la muestra sintética.",
                  file=sys.stderr)
            df = cargar_muestra()
    else:
        df = cargar_muestra()
        print(f"[ingest] Modo offline: {len(df)} procesos (muestra sintética).")
    df.to_csv(config.RUTA_CRUDO, index=False)
    print(f"[ingest] Guardado en {config.RUTA_CRUDO}")
    return df


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true")
    ingestar(refresh=ap.parse_args().refresh)
