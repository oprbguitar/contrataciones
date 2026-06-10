"""
templates_tdr.py — Generador de PLANTILLAS de Términos de Referencia (TDR) y
Especificaciones Técnicas (EETT) prellenadas con datos de un procedimiento.

Qué hace:
  - A partir de una fila del consolidado (o de parámetros), arma el ESQUELETO
    estructural de un TDR (servicios/consultoría) o una EETT (bienes), con las
    secciones mínimas que exige la práctica de contratación pública peruana,
    alineado al marco de la Ley N.° 32069 (Nueva Ley General de Contrataciones
    Públicas) y su reglamento.
  - Inserta automáticamente objeto, finalidad, entidad, monto referencial y un
    checklist de consistencia, dejando marcadas [ ] las decisiones que el área
    usuaria debe completar.

IMPORTANTE: es un ASISTENTE DE ESTRUCTURACIÓN documental. No reemplaza la revisión
legal ni el criterio del área usuaria; produce un borrador base para reducir
omisiones y acelerar la primera versión.

Salida: archivos Markdown en templates/ (portables; convertibles a Word/PDF).
"""
import os
import textwrap

import pandas as pd

import config

OUT_DIR = "templates"

CHECKLIST = [
    "Objeto de la contratación claramente delimitado",
    "Finalidad pública sustentada",
    "Alcance y actividades / características técnicas completas",
    "Entregables y cronograma definidos",
    "Plazo de ejecución y lugar de prestación",
    "Perfil del proveedor / requisitos de calificación",
    "Sistema y forma de pago",
    "Conformidad: área responsable y procedimiento",
    "Penalidades (mora y otras) y su forma de cálculo",
    "Anexos y referencias normativas",
]


def _tdr_servicio(d):
    return textwrap.dedent(f"""\
    # TÉRMINOS DE REFERENCIA (TDR)
    ## Contratación de {d['objeto']}

    > Borrador base generado por ContrataRadar. Asistente de estructuración; no
    > reemplaza revisión legal ni criterio del área usuaria. Completar los campos [ ].

    **Entidad contratante:** {d['entidad']}
    **Tipo de procedimiento (referencial):** {d['tipo_procedimiento']}
    **Monto referencial (referencial):** S/ {d['monto_referencial']}
    **Código de referencia:** {d.get('id_proceso', '[ ]')}

    ### 1. Denominación de la contratación
    {d['descripcion']}

    ### 2. Finalidad pública
    [ ] Describir el interés público que se satisface y su vínculo con los
    objetivos institucionales y el PAC.

    ### 3. Antecedentes
    [ ] Necesidad que origina la contratación y referencias previas.

    ### 4. Objetivos
    - **Objetivo general:** [ ]
    - **Objetivos específicos:** [ ]

    ### 5. Alcance y descripción del servicio
    [ ] Detallar actividades, metodología y supuestos. Para consultoría, precisar
    productos por fase.

    ### 6. Entregables y cronograma
    | N° | Entregable | Plazo | % de pago |
    |----|------------|-------|-----------|
    | 1  | [ ]        | [ ]   | [ ]       |
    | 2  | [ ]        | [ ]   | [ ]       |

    ### 7. Plazo de ejecución y lugar
    - **Plazo:** [ ] días calendario.
    - **Lugar de prestación:** [ ]

    ### 8. Perfil del proveedor y requisitos de calificación
    [ ] Formación, experiencia, RNP vigente, no estar impedido de contratar.

    ### 9. Sistema y forma de pago
    [ ] Suma alzada / precios unitarios. Pagos contra conformidad de entregables.

    ### 10. Conformidad
    [ ] Área responsable de otorgar la conformidad y plazo para emitirla.

    ### 11. Penalidades
    [ ] Penalidad por mora y otras penalidades, con fórmula de cálculo.

    ### 12. Anexos y referencias normativas
    - Ley N.° 32069, Ley General de Contrataciones Públicas, y su Reglamento.
    - [ ] Otros anexos técnicos.

    ---
    **Checklist de consistencia (revisar antes de remitir):**
    """) + "\n".join(f"- [ ] {c}" for c in CHECKLIST)


def _eett_bien(d):
    return textwrap.dedent(f"""\
    # ESPECIFICACIONES TÉCNICAS (EETT)
    ## Adquisición de {d['objeto']}

    > Borrador base generado por ContrataRadar. Asistente de estructuración; no
    > reemplaza revisión legal ni criterio del área usuaria. Completar los campos [ ].

    **Entidad contratante:** {d['entidad']}
    **Tipo de procedimiento (referencial):** {d['tipo_procedimiento']}
    **Monto referencial (referencial):** S/ {d['monto_referencial']}
    **Código de referencia:** {d.get('id_proceso', '[ ]')}

    ### 1. Denominación del bien
    {d['descripcion']}

    ### 2. Finalidad pública
    [ ] Vínculo con la necesidad institucional y el PAC.

    ### 3. Características técnicas del bien
    | Característica | Especificación mínima | Unidad |
    |---------------|-----------------------|--------|
    | [ ]           | [ ]                   | [ ]    |

    ### 4. Cantidad y presentación
    [ ] Cantidad, embalaje y unidades de medida.

    ### 5. Plazo y lugar de entrega
    - **Plazo de entrega:** [ ] días calendario.
    - **Lugar de entrega:** [ ]

    ### 6. Garantía
    [ ] Tipo y período de garantía comercial / técnica.

    ### 7. Requisitos del proveedor
    [ ] RNP vigente, no estar impedido, experiencia y documentación.

    ### 8. Forma de pago y conformidad
    [ ] Pago contra conformidad de recepción por el área usuaria.

    ### 9. Penalidades
    [ ] Penalidad por mora y otras, con fórmula de cálculo.

    ### 10. Referencias normativas
    - Ley N.° 32069, Ley General de Contrataciones Públicas, y su Reglamento.

    ---
    **Checklist de consistencia (revisar antes de remitir):**
    """) + "\n".join(f"- [ ] {c}" for c in CHECKLIST)


def generar_para_fila(d):
    objeto = str(d.get("objeto", "Servicio"))
    if objeto.lower().startswith("bien"):
        contenido, sufijo = _eett_bien(d), "EETT"
    else:
        contenido, sufijo = _tdr_servicio(d), "TDR"
    os.makedirs(OUT_DIR, exist_ok=True)
    nombre = f"{sufijo}_{str(d.get('id_proceso', 'ejemplo')).replace('/', '-')}.md"
    ruta = os.path.join(OUT_DIR, nombre)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(contenido)
    return ruta


def generar_ejemplos(n=3):
    """Toma los primeros procesos del consolidado y genera plantillas de ejemplo."""
    df = pd.read_csv(config.RUTA_PROC if os.path.exists(config.RUTA_PROC)
                     else config.RUTA_MUESTRA)
    # Un ejemplo de bien y dos de servicio para mostrar ambos formatos.
    ejemplos = pd.concat([
        df[df["objeto"] == "Bien"].head(1),
        df[df["objeto"] != "Bien"].head(n - 1),
    ])
    rutas = [generar_para_fila(row._asdict()) for row in ejemplos.itertuples()]
    print(f"[templates] {len(rutas)} plantillas generadas en {OUT_DIR}/:")
    for r in rutas:
        print("   -", r)
    return rutas


if __name__ == "__main__":
    generar_ejemplos()
