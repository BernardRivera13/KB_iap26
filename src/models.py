"""
Modelos de nodos para el detector de indicadores de corrupción.
Cada clase representa un tipo de actor en la red de huachicol fiscal.
"""

from dataclasses import dataclass, field
from typing import Optional


class AlertLevel:
    NONE = "sin_alerta"
    LOW = "baja"
    MEDIUM = "media"
    HIGH = "alta"

    ORDER = {NONE: 0, LOW: 1, MEDIUM: 2, HIGH: 3}

    @classmethod
    def max(cls, a: str, b: str) -> str:
        return a if cls.ORDER.get(a, 0) >= cls.ORDER.get(b, 0) else b

    @classmethod
    def degrade(cls, level: str) -> str:
        """Degrada un nivel de alerta un paso hacia abajo."""
        chain = [cls.NONE, cls.LOW, cls.MEDIUM, cls.HIGH]
        idx = chain.index(level) if level in chain else 0
        return chain[max(0, idx - 1)]


@dataclass
class Empresa:
    nombre: str

    # Hechos observables
    socio_senalado: bool = False
    socio_senalado_nivel: str = AlertLevel.NONE  # nivel heredado del socio
    consiguio_permiso_express: bool = False
    tiene_discrepancias_en_importaciones: bool = False
    tiene_discrepancias_en_ganancias: bool = False
    ganancias_desproporcionadas: bool = False
    empresa_nueva: bool = False
    tiene_contratos_gubernamentales: bool = False

    # Derivadas (calculadas por el motor)
    contradiccion_legitimidad: bool = False
    alerta_general: str = AlertLevel.NONE

    # Metadatos CompraNet (llenados por data_loader)
    monto_compranet: float = 0.0
    contratos_compranet: int = 0

    # Flags activas (para reporte)
    flags: list = field(default_factory=list)

    def __hash__(self):
        return hash(self.nombre)

    def __eq__(self, other):
        return isinstance(other, Empresa) and self.nombre == other.nombre


@dataclass
class Persona:
    nombre: str

    # Hechos observables
    es_socio_de_empresa_dudosa: bool = False
    empresa_dudosa_nivel: str = AlertLevel.NONE  # nivel heredado de la empresa
    tiene_familiar_o_socio_en_poder: bool = False
    apoyo_campana_politica: bool = False
    tiene_senalamientos: bool = False
    enriquecimiento_dudoso: bool = False
    es_funcionario: bool = False
    multiples_empresas_recientes: bool = False

    # Derivadas
    alerta_general: str = AlertLevel.NONE

    # Flags activas (para reporte)
    flags: list = field(default_factory=list)

    def __hash__(self):
        return hash(self.nombre)

    def __eq__(self, other):
        return isinstance(other, Persona) and self.nombre == other.nombre


@dataclass
class Gasolinera:
    nombre: str

    # Hechos observables
    licitacion_cercana_al_fraude: bool = False
    ganancias_exceden_margen: bool = False
    socios_abanderados: bool = False
    socios_abanderados_nivel: str = AlertLevel.NONE  # nivel heredado

    # Derivadas
    alerta_general: str = AlertLevel.NONE

    # Flags activas (para reporte)
    flags: list = field(default_factory=list)

    def __hash__(self):
        return hash(self.nombre)

    def __eq__(self, other):
        return isinstance(other, Gasolinera) and self.nombre == other.nombre
