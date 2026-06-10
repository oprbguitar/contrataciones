"""
ContrataRadar — Configuración central
======================================
Analítica de contrataciones públicas del Perú: concentración de proveedores,
procesos desiertos y tiempos promedio, a partir de DATOS ABIERTOS.

FUENTES PÚBLICAS (declaradas; se nombran sin necesidad de pegar los enlaces):
  - OECE — Portal de Datos Abiertos del Organismo Especializado para las
    Contrataciones Públicas Eficientes (antes OSCE). Publica, desde 2018:
    Plan Anual de Contrataciones (PAC), procedimientos convocados y adjudicados,
    contratos, proveedores adjudicados, consorcios, entidades contratantes,
    órdenes de compra y de servicio, procedimientos DESIERTOS y con NULIDAD,
    miembros de comités y procesos con pronunciamientos.
  - OECE — Contrataciones Abiertas, mismos datos en estándar OCDS
    (Open Contracting Data Standard).
  - CONOSCE / BI SEACE — Sistema de Inteligencia de Negocios del OECE.
  - PERÚ COMPRAS — Central de Compras Públicas: órdenes de compra y de servicio
    formalizadas en los Catálogos Electrónicos de Acuerdos Marco, publicadas en
    la Plataforma Nacional de Datos Abiertos y en OCDS (actualización diaria/mensual).
  - Marco legal: Ley N.° 32069 (Ley General de Contrataciones Públicas),
    sus modificaciones posteriores y reglamento actualizado; PLADICOP es la
    plataforma digital prevista por el marco normativo.

NOTA DE DATOS: para que el repositorio funcione siempre (incluso sin conexión y
en GitHub Pages), incluye una MUESTRA SINTÉTICA que NO representa cifras reales.
Para datos reales, configura FUENTE_URL con un CSV publicado y usa --refresh.
"""

# ---------------------------------------------------------------------------
# 1) Fuente configurable (CSV de datos abiertos OECE/PERÚ COMPRAS).
# ---------------------------------------------------------------------------
FUENTE_URL = ""  # vacío => modo muestra sintética
FUENTE_NOMBRE = "OECE (Datos Abiertos / OCDS) + PERÚ COMPRAS — demostración con muestra sintética"

# ---------------------------------------------------------------------------
# 2) Catálogos de referencia para la muestra y la normalización.
# ---------------------------------------------------------------------------
TIPOS_PROCEDIMIENTO = [
    "Licitación Pública", "Concurso Público", "Adjudicación Simplificada",
    "Subasta Inversa Electrónica", "Contratación Directa",
    "Comparación de Precios", "Selección de Consultores Individuales",
]

OBJETOS = ["Bien", "Servicio", "Obra", "Consultoría de Obra"]

ENTIDADES = [
    "Gobierno Regional de Lima", "Municipalidad Provincial de Arequipa",
    "Ministerio de Salud", "EsSalud", "Ministerio de Educación",
    "Gobierno Regional de Cusco", "PRONIED", "SEDAPAL",
    "Municipalidad de Trujillo", "Ministerio del Interior",
]

ESTADOS = ["Adjudicado", "Desierto", "Nulo", "En convocatoria", "Cancelado"]

# ---------------------------------------------------------------------------
# 3) Parámetros de análisis (la capa de decisión).
# ---------------------------------------------------------------------------
# Umbrales del Índice Herfindahl-Hirschman (HHI) para concentración de mercado.
# Convención usual: <1500 competido, 1500–2500 moderado, >2500 concentrado.
HHI_MODERADO = 1500
HHI_CONCENTRADO = 2500

# Umbral de alerta para tasa de procesos desiertos (%) por entidad.
ALERTA_DESIERTOS_PCT = 20.0

# Tiempo (días) de convocatoria a adjudicación considerado "lento".
ALERTA_DIAS_LENTO = 60

# ---------------------------------------------------------------------------
# 4) Rutas de salida.
# ---------------------------------------------------------------------------
RUTA_MUESTRA = "data_open/_muestra_sintetica.csv"
RUTA_CRUDO = "data_open/contrataciones.csv"
RUTA_PROC = "data_processed/contrataciones_procesado.csv"
RUTA_KPIS = "data_processed/kpis.json"
RUTA_WEB_JSON = "docs/data.json"
