"""
make_sample.py — Genera una MUESTRA SINTÉTICA de procedimientos de contratación
con la misma estructura que tendría un consolidado de datos abiertos del OECE /
PERÚ COMPRAS (un registro por procedimiento).

Los datos NO son reales. Sirven para ejecutar el proyecto sin conexión, producir
el tablero y demostrar la analítica. Para datos reales: ingest.py --refresh.
"""
import numpy as np
import pandas as pd

import config


def generar_muestra(n=1800, semilla=11):
    rng = np.random.default_rng(semilla)

    # Catálogo de proveedores sintéticos.
    proveedores = [f"Proveedor {chr(65 + i // 3)}{i}" for i in range(60)]

    # Para que el análisis de concentración tenga señal realista, algunas
    # entidades operan con un mercado CONCENTRADO (pocos proveedores se llevan
    # casi todo) y otras con un mercado COMPETIDO (reparto amplio).
    entidades_concentradas = {"SEDAPAL", "EsSalud", "Municipalidad de Trujillo"}

    def proveedor_para(entidad):
        """Devuelve un proveedor según el perfil de mercado de la entidad."""
        if entidad in entidades_concentradas:
            # El mercado de esta entidad lo atienden muy pocos proveedores.
            pool = proveedores[:5]
            w = np.array([0.45, 0.27, 0.15, 0.08, 0.05])
            return rng.choice(pool, p=w)
        return rng.choice(proveedores, p=pesos_competido)

    pesos_competido = rng.exponential(1.0, len(proveedores))
    pesos_competido = pesos_competido / pesos_competido.sum()

    fechas_conv = pd.to_datetime("2018-01-01") + pd.to_timedelta(
        rng.integers(0, 365 * 8, n), unit="D")

    filas = []
    for i in range(n):
        tipo = rng.choice(config.TIPOS_PROCEDIMIENTO,
                          p=[0.10, 0.06, 0.34, 0.20, 0.16, 0.08, 0.06])
        objeto = rng.choice(config.OBJETOS, p=[0.46, 0.34, 0.14, 0.06])
        entidad = rng.choice(config.ENTIDADES)
        estado = rng.choice(config.ESTADOS, p=[0.66, 0.16, 0.05, 0.08, 0.05])

        # Monto referencial (soles), dependiente del tipo.
        base = {"Licitación Pública": 2_500_000, "Concurso Público": 1_400_000,
                "Adjudicación Simplificada": 280_000, "Subasta Inversa Electrónica": 190_000,
                "Contratación Directa": 520_000, "Comparación de Precios": 90_000,
                "Selección de Consultores Individuales": 70_000}[tipo]
        monto_ref = float(np.round(base * rng.uniform(0.4, 2.2), 2))

        conv = fechas_conv[i]
        # Tiempo de convocatoria -> adjudicación (días), si llegó a adjudicarse.
        dias = int(np.clip(rng.normal(38, 18), 7, 150))
        adj = conv + pd.Timedelta(days=dias) if estado == "Adjudicado" else pd.NaT

        # Postores y proveedor adjudicado.
        postores = int(np.clip(rng.poisson(2.4) + (estado != "Desierto"), 0, 12))
        if estado == "Adjudicado" and postores > 0:
            prov = proveedor_para(entidad)
            monto_adj = round(monto_ref * rng.uniform(0.82, 1.0), 2)
        else:
            prov = ""
            monto_adj = 0.0

        filas.append({
            "id_proceso": f"PROC-{2018 + i % 8}-{i:05d}",
            "entidad": entidad,
            "tipo_procedimiento": tipo,
            "objeto": objeto,
            "descripcion": f"{objeto} para {entidad.split()[-1]} — paquete {i % 50}",
            "estado": estado,
            "fecha_convocatoria": conv.date().isoformat(),
            "fecha_adjudicacion": adj.date().isoformat() if pd.notna(adj) else "",
            "dias_convocatoria_adjudicacion": dias if estado == "Adjudicado" else "",
            "n_postores": postores,
            "monto_referencial": monto_ref,
            "monto_adjudicado": monto_adj,
            "proveedor_adjudicado": prov,
            "fuente": "MUESTRA SINTÉTICA (no es dato real)",
        })
    return pd.DataFrame(filas)


if __name__ == "__main__":
    df = generar_muestra()
    df.to_csv(config.RUTA_MUESTRA, index=False)
    print(f"Muestra sintética: {config.RUTA_MUESTRA} "
          f"({len(df)} procesos, {df['entidad'].nunique()} entidades)")
