"""
run_pipeline.py — Flujo completo de ContrataRadar:
    ingesta -> analítica (HHI / desiertos / tiempos) -> tablero web -> plantillas.

    python -m src.run_pipeline             # offline (muestra sintética)
    python -m src.run_pipeline --refresh   # intenta fuente real (OECE / PERÚ COMPRAS)
"""
import argparse

from src import ingest, analyze, build_web, templates_tdr


def main(refresh=False):
    print("=" * 60)
    print("ContrataRadar — pipeline de analítica de contrataciones")
    print("=" * 60)
    crudo = ingest.ingestar(refresh=refresh)
    analyze.analizar(crudo)
    templates_tdr.generar_ejemplos()
    build_web.construir()
    print("\nListo. Abre docs/index.html (o publícalo en GitHub Pages) y/o ejecuta:")
    print("   streamlit run app/streamlit_app.py")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--refresh", action="store_true")
    main(refresh=ap.parse_args().refresh)
