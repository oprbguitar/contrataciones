"""
build_web.py — Empaqueta los KPIs + ejemplos de plantillas en docs/data.json,
único insumo del tablero estático (docs/index.html). Funciona en GitHub Pages
o en local, sin servidor.
"""
import glob
import json
import os

import config


def _leer_ejemplo(prefijo):
    """Lee el primer archivo de plantilla generado con el prefijo dado (TDR/EETT)."""
    archivos = sorted(glob.glob(os.path.join("templates", f"{prefijo}_*.md")))
    if not archivos:
        return ""
    with open(archivos[0], encoding="utf-8") as f:
        return f.read()


def construir():
    with open(config.RUTA_KPIS, encoding="utf-8") as f:
        kpis = json.load(f)

    # Incrustar ejemplos de plantillas para mostrarlas en la página.
    kpis["plantillas_ejemplo"] = {
        "tdr": _leer_ejemplo("TDR"),
        "eett": _leer_ejemplo("EETT"),
    }

    with open(config.RUTA_WEB_JSON, "w", encoding="utf-8") as f:
        json.dump(kpis, f, ensure_ascii=False, indent=2)
    print(f"[build_web] Tablero alimentado: {config.RUTA_WEB_JSON} "
          f"({kpis['resumen']['n_procesos']} procesos, con ejemplos TDR/EETT)")


if __name__ == "__main__":
    construir()
