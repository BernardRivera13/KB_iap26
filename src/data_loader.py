"""
Loader de datos CompraNet para el detector de corrupción.

Fuentes soportadas:
  - compranet_historico.csv  (2010-2022): tiene columna 'proveedor' — búsqueda por empresa
  - ExpedientesPublicados*.csv (2018-2022): expedientes sin proveedor — solo estadísticas
  - expedientes_compranet_*.csv / expedientes_comprasmx_*.csv (2023-2025): idem

Uso principal:
  loader = CompraNetLoader(data_dir="data/")
  resultado = loader.buscar_empresa("Ecocarburante")
  loader.aplicar_flags(empresa_obj, resultado)
"""

import os
import re
import csv
import glob
from dataclasses import dataclass, field

# Models import — relativo si se corre desde src/, absoluto si se importa
try:
    from models import Empresa, AlertLevel
except ImportError:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from models import Empresa, AlertLevel


# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

# Sufijos legales mexicanos a ignorar en la comparación
_LEGAL_SUFFIXES = re.compile(
    r"\b(s\.?\s*a\.?\s*de\s*c\.?\s*v\.?|s\.?\s*de\s*r\.?\s*l\.?(\s*de\s*c\.?\s*v\.?)?|"
    r"s\.?\s*c\.?|a\.?\s*c\.?|s\.?\s*a\.?\s*p\.?\s*i\.?|"
    r"sa\s+de\s+cv|srl|srlcv|sc)\b\.?",
    re.IGNORECASE,
)

ADJUDICACION_DIRECTA_KEYWORDS = ["adjudicaci", "directa"]

COMBUSTIBLE_KEYWORDS = [
    "combustible", "diesel", "diésel", "gasolina", "hidrocarburo",
    "petróleo", "petroleo", "gas lp", "gas natural", "fuel",
]

SEDENA_KEYWORDS = ["sedena", "secretar", "defensa nacional", "marina", "semar"]


# ---------------------------------------------------------------------------
# Resultado de búsqueda
# ---------------------------------------------------------------------------

@dataclass
class ResultadoBusqueda:
    empresa_buscada: str
    encontrado: bool = False
    total_contratos: int = 0
    monto_total: float = 0.0
    tiene_adjudicacion_directa: bool = False
    tiene_contratos_combustible: bool = False
    tiene_contratos_sedena: bool = False
    contratos: list = field(default_factory=list)   # muestra de hasta 10 filas
    advertencias: list = field(default_factory=list)

    def resumen(self) -> str:
        if not self.encontrado:
            return f"No se encontraron contratos para '{self.empresa_buscada}'."
        lineas = [
            f"Empresa: {self.empresa_buscada}",
            f"Contratos encontrados: {self.total_contratos}",
            f"Monto total: ${self.monto_total:,.0f} MXN",
            f"Adjudicación directa: {'SI' if self.tiene_adjudicacion_directa else 'no'}",
            f"Contratos combustible: {'SI' if self.tiene_contratos_combustible else 'no'}",
            f"Contratos SEDENA/SEMAR: {'SI' if self.tiene_contratos_sedena else 'no'}",
        ]
        if self.advertencias:
            lineas.append("Advertencias: " + "; ".join(self.advertencias))
        return "\n  ".join(lineas)


# ---------------------------------------------------------------------------
# Loader principal
# ---------------------------------------------------------------------------

class CompraNetLoader:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self._historico_path = os.path.join(data_dir, "compranet_historico.csv")
        self._expedientes_paths = sorted(
            glob.glob(os.path.join(data_dir, "Expedientes*.csv")) +
            glob.glob(os.path.join(data_dir, "expedientes_*.csv"))
        )

    # ------------------------------------------------------------------
    # Búsqueda principal
    # ------------------------------------------------------------------

    @staticmethod
    def _normalizar_nombre(nombre: str) -> str:
        """Elimina sufijos legales para mejorar la coincidencia."""
        n = _LEGAL_SUFFIXES.sub("", nombre)
        n = re.sub(r"\s+", " ", n).strip(" ,.")
        return n

    def buscar_empresa(self, nombre: str) -> ResultadoBusqueda:
        """
        Busca una empresa por nombre en compranet_historico.csv.
        La búsqueda es insensible a mayúsculas, acepta coincidencia parcial,
        e ignora sufijos legales (S.A. de C.V., etc.) para mejorar el match.
        """
        resultado = ResultadoBusqueda(empresa_buscada=nombre)
        termino = self._normalizar_nombre(nombre)
        patron = re.compile(re.escape(termino), re.IGNORECASE)

        if not os.path.exists(self._historico_path):
            resultado.advertencias.append(
                f"No se encontró {self._historico_path}. Coloca el CSV en la carpeta data/."
            )
            return resultado

        filas_match = []
        monto_total = 0.0
        proveedor_col = None

        try:
            with open(self._historico_path, encoding="utf-8", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if proveedor_col is None:
                        proveedor_col = "proveedor" if "proveedor" in reader.fieldnames else None
                        if proveedor_col is None:
                            resultado.advertencias.append("Columna 'proveedor' no encontrada en el histórico.")
                            break

                    proveedor = row.get("proveedor", "") or ""
                    if not patron.search(proveedor):
                        continue

                    filas_match.append(row)

                    try:
                        monto_total += float(row.get("importe", 0) or 0)
                    except (ValueError, TypeError):
                        pass

        except Exception as e:
            resultado.advertencias.append(f"Error leyendo histórico: {e}")
            return resultado

        if not filas_match:
            return resultado

        resultado.encontrado = True
        resultado.total_contratos = len(filas_match)
        resultado.monto_total = monto_total

        # Detectar adjudicación directa
        for row in filas_match:
            tipo = (row.get("tipo_expediente", "") or "").lower()
            if any(k in tipo for k in ADJUDICACION_DIRECTA_KEYWORDS):
                resultado.tiene_adjudicacion_directa = True
                break

        # Detectar contratos de combustible
        for row in filas_match:
            texto = " ".join([
                (row.get("titulo_contrato", "") or ""),
                (row.get("descripcion_contrato", "") or ""),
            ]).lower()
            if any(k in texto for k in COMBUSTIBLE_KEYWORDS):
                resultado.tiene_contratos_combustible = True
                break

        # Detectar contratos con SEDENA/SEMAR
        for row in filas_match:
            texto = " ".join([
                (row.get("titulo_contrato", "") or ""),
                (row.get("descripcion_contrato", "") or ""),
            ]).lower()
            if any(k in texto for k in SEDENA_KEYWORDS):
                resultado.tiene_contratos_sedena = True
                break

        # Muestra de hasta 10 contratos para el reporte
        for row in filas_match[:10]:
            resultado.contratos.append({
                k: row.get(k, "")
                for k in ["proveedor", "titulo_contrato", "tipo_expediente",
                           "importe", "fecha_inicio", "fecha_fin"]
            })

        return resultado

    # ------------------------------------------------------------------
    # Aplicar flags al modelo
    # ------------------------------------------------------------------

    def aplicar_flags(self, empresa: Empresa, resultado: ResultadoBusqueda):
        """
        Actualiza las propiedades booleanas de una instancia Empresa
        con base en lo encontrado en CompraNet.
        """
        if not resultado.encontrado:
            return
        if resultado.total_contratos > 0:
            empresa.tiene_contratos_gubernamentales = True
        # contradiccion_legitimidad la calcula el motor (no se asigna aquí)

    # ------------------------------------------------------------------
    # Auto-descubrimiento: busca todos los actores del motor en CompraNet
    # ------------------------------------------------------------------

    def enriquecer_engine(self, engine, verbose: bool = True) -> list[dict]:
        """
        Itera todas las empresas del engine, busca cada una en CompraNet,
        aplica flags automáticamente, y retorna una lista de descubrimientos.

        Esto es el "Forward Chaining externo": el sistema descubre hechos
        nuevos cruzando bases de datos sin que el analista los especifique.
        """
        descubrimientos = []
        for nombre, empresa in engine.empresas.items():
            resultado = self.buscar_empresa(nombre)
            if not resultado.encontrado:
                continue

            cambios = []
            if resultado.total_contratos > 0 and not empresa.tiene_contratos_gubernamentales:
                empresa.tiene_contratos_gubernamentales = True
                cambios.append(f"tiene_contratos_gubernamentales=True ({resultado.total_contratos} contratos, ${resultado.monto_total:,.0f} MXN)")
            # Siempre guardar monto aunque tiene_contratos_gubernamentales ya estuviera activo
            if resultado.total_contratos > 0:
                empresa.monto_compranet = resultado.monto_total
                empresa.contratos_compranet = resultado.total_contratos
            if resultado.tiene_contratos_combustible:
                cambios.append("contratos de combustible detectados")
            if resultado.tiene_adjudicacion_directa:
                cambios.append("adjudicación directa detectada")

            if cambios:
                descubrimiento = {
                    "empresa": nombre,
                    "contratos": resultado.total_contratos,
                    "monto": resultado.monto_total,
                    "cambios": cambios,
                    "muestra": resultado.contratos[:3],
                }
                descubrimientos.append(descubrimiento)
                if verbose:
                    print(f"  [CompraNet] {nombre}")
                    print(f"    → {resultado.total_contratos} contratos, ${resultado.monto_total:,.0f} MXN")
                    for c in cambios:
                        print(f"    → {c}")

        return descubrimientos
