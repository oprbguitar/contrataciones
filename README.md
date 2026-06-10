# ContrataRadar – Guía básica de uso local

Este proyecto es una página web de análisis visual sobre contrataciones públicas en Perú.  
No necesitas saber programar para revisarlo localmente. Solo sigue los pasos indicados.

## Opción 1: Ejecutar automáticamente en Windows

1. Busca el archivo `iniciar-proyecto.bat`.
2. Haz doble clic sobre el archivo.
3. Espera a que se abra la ventana del navegador (abrirá en `http://localhost:8000`).
4. Si el navegador no se abre, copia la dirección que aparece en la terminal.

## Opción 2: Ejecutar manualmente

1. Abre una terminal en la carpeta del proyecto.
2. Ejecuta:

```bash
cd docs
python -m http.server 8000
```

3. Abre la dirección local en tu navegador:

```text
http://localhost:8000
```

---

# 📡 ContrataRadar (Detalle Técnico)

**Analítica de contrataciones públicas del Perú: concentración de proveedores, procesos desiertos y tiempos promedio — con generación de plantillas TDR/EETT.**

> Convierte los datos abiertos del Estado en señales de control: ¿el mercado de una entidad está concentrado en pocos proveedores?, ¿qué entidades declaran desierto con demasiada frecuencia?, ¿dónde se demoran las adjudicaciones? Y además, genera borradores de Términos de Referencia y Especificaciones Técnicas prellenados con datos.

🔗 **Repositorio:** [github.com/oprbguitar/contrataciones](https://github.com/oprbguitar/contrataciones)

🔗 **Página en vivo (GitHub Pages):** [oprbguitar.github.io/contrataciones](https://oprbguitar.github.io/contrataciones/)

---

## ¿De qué trata?

La contratación pública peruana genera miles de registros abiertos (OECE/SEACE, PERÚ COMPRAS), pero esa información está dispersa y es difícil de leer para decidir. **ContrataRadar** la consolida y la convierte en tres análisis de control, más un generador documental:

1. **Concentración de proveedores (HHI).** Mide con el Índice Herfindahl-Hirschman cuánto se reparte el monto adjudicado entre proveedores, por entidad y a nivel global, y clasifica el mercado en *Competido / Moderado / Concentrado*.
2. **Procesos desiertos.** Calcula la tasa de procesos declarados desiertos por entidad y por tipo, con alerta sobre el umbral.
3. **Tiempos promedio.** Días de convocatoria a adjudicación por entidad y tipo, marcando los procesos lentos.
4. **Plantillas TDR/EETT autogeneradas.** Borradores prellenados con datos del proceso, alineados a la Ley N.° 32069.

## ¿Para qué sirve y para quién?

- **Áreas de abastecimiento y planeamiento:** detectar cuellos de botella y mejorar la formulación del PAC.
- **Control interno / OCI:** ubicar señales de riesgo (mercados concentrados, desiertos recurrentes) para priorizar revisiones.
- **Proveedores:** estudiar el mercado estatal por entidad y rubro.
- **Periodismo de datos y academia:** análisis de transparencia con fuentes oficiales.

## Cómo usarlo (Pipeline en Python)

```bash
pip install -r requirements.txt

# Pipeline completo (modo demostración con muestra sintética)
python -m src.run_pipeline

# Con datos reales: configura FUENTE_URL en config.py y luego
python -m src.run_pipeline --refresh
```

El pipeline ejecuta: **ingesta → análisis (HHI/desiertos/tiempos) → plantillas TDR/EETT → tablero web**. Genera `data_processed/kpis.json`, los borradores en `templates/` y `docs/data.json` (insumo del tablero).

**Publicar la página:** en GitHub, *Settings → Pages → Source: rama `main`, carpeta `/docs`*. Queda en `https://oprbguitar.github.io/contrataciones/`.

El tablero web incluye navegación fija, filtros por entidad y nivel de atención, reinicio de filtros, lectura dinámica del número de entidades visibles, pestañas TDR/EETT y accesos directos a las fuentes oficiales.

## Plantillas autogeneradas (TDR / EETT)

`src/templates_tdr.py` arma el esqueleto de:
- **TDR** (Términos de Referencia) para servicios y consultoría.
- **EETT** (Especificaciones Técnicas) para bienes.

Cada plantilla se prellena con objeto, entidad y monto del proceso, deja marcadas con `[ ]` las decisiones del área usuaria, incluye un **checklist de consistencia** y referencia el marco de la **Ley N.° 32069**. Es un **asistente de estructuración documental**: acelera la primera versión y reduce omisiones, pero **no reemplaza la revisión legal ni el criterio del área usuaria**.

## Fuentes de datos abiertos (declaradas)

Información **pública y oficial**, trabajada de forma **agregada**:

| Fuente | Referencia oficial | Qué aporta |
|--------|-------------------|------------|
| **OECE — Portal de Datos Abiertos (SEACE)** | [Servicio oficial](https://www.gob.pe/14272-acceder-al-portal-de-datos-abiertos-del-osce) | PAC, procedimientos convocados y adjudicados, contratos, proveedores adjudicados, consorcios, entidades, órdenes de compra/servicio, **procesos desiertos y con nulidad**. Datos desde 2018. |
| **OECE — Contrataciones Abiertas** | [Portal OCDS](https://www.gob.pe/52005-acceder-al-portal-de-contrataciones-abiertas-de-la-compra-publica-ocds) | Información y documentos de las etapas de compra pública, tableros, descargas y APIs bajo el estándar **OCDS**. |
| **PERÚ COMPRAS — Catálogos Electrónicos de Acuerdos Marco** | [Datos abiertos oficiales](https://www.gob.pe/10251-acceder-a-los-datos-abiertos-sobre-compras-del-estado-mediante-catalogos-electronicos) | Órdenes de compra y de servicio formalizadas en los Catálogos Electrónicos. |
| **Marco legal — Ley N.° 32069** | [Compendio oficial actualizado](https://www.gob.pe/institucion/osce/colecciones/45029-ley-n-32069-ley-general-de-contrataciones-publicas-y-su-reglamento) | Ley General de Contrataciones Públicas, modificaciones posteriores y reglamento actualizado. Referencia para los TDR/EETT. |

> Las fuentes oficiales se enlazan desde el tablero y se documentan también en `config.py`.

> **Nota de datos:** para funcionar siempre (incluso sin conexión y en GitHub Pages), el repositorio incluye una **muestra sintética** que **no representa cifras reales**. Para análisis reales, configura `FUENTE_URL` y usa `--refresh`.

## Indicadores y umbrales (configurables en `config.py`)

- **HHI:** < 1500 *Competido*, 1500–2500 *Moderado*, ≥ 2500 *Concentrado*.
- **Alerta de desiertos:** tasa ≥ 20 % por entidad.
- **Tiempo lento:** ≥ 60 días de convocatoria a adjudicación.

## Stack

Python (pandas, numpy, requests) · Streamlit · GitHub Actions / Pages · estándar OCDS.

## Limitaciones

- La muestra sintética es solo demostrativa; las cifras no son reales.
- El HHI se calcula sobre el monto adjudicado; conviene complementarlo con número de postores y análisis por rubro.
- Las plantillas son borradores base; la versión final exige revisión técnica y legal.
- Los umbrales son decisiones de política y deben ajustarse al criterio de cada entidad.

## Confidencialidad

Proyecto **demostrativo**. Usa exclusivamente datos **públicos y agregados** y/o **sintéticos**. **No contiene información reservada, confidencial ni de empleadores actuales o anteriores.** Ver `docs/CONFIDENCIALIDAD.md`.

---

**Creado por Pierre R.** — Ingeniero Industrial · analítica institucional, contrataciones y automatización documental.

📧 **Consultas adicionales:** [peru.labs.pe@gmail.com](mailto:peru.labs.pe@gmail.com)
