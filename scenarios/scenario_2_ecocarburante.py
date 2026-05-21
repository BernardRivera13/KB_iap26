"""
Escenario 2: Ecocarburante S.A. de C.V. — Contradictorio, Alerta Alta.

Fuente SIGER: data/siger/cadena-ecocarburante/
  - ec-const.pdf                           FME N-2017077880, constituida 14/09/2017, Guadalajara
  - ec-aumento-capital-fijo.pdf            Asamblea 20/03/2020 — cambio total de accionistas
  - ec-fusion-inc.pdf                      Fusión por absorción de Royal Park Ocotlan (09/11/2022)
  - ec-nombramiento-funcionarios-abril2020.pdf
  - ec-nombramiento-funcionarios-mayo2023.pdf
  - rpo-const.pdf                          Royal Park Ocotlan FME: 82678, constituida 20/05/2014
  - robro-const.pdf                        ROBRO S.A. de C.V. FME: 82686, constituida 14/05/2014

Cadena societaria de Royal Park Ocotlan (empresa inmobiliaria absorbida, rpo-const.pdf):
  JUAN ALEJANDRO RODRÍGUEZ LUNA  25%, Admin Único — domicilio Zapopan, Jalisco
  JOSÉ MARTÍN GONZÁLEZ MÁRQUEZ   25%, Comisario   — domicilio Zapopan, Jalisco
  ROBRO S.A. de C.V.             50%

Cadena societaria de ROBRO S.A. de C.V. (robro-const.pdf):
  JUAN ALEJANDRO RODRÍGUEZ LUNA  50%, Admin Único — mismo domicilio Zapopan
  ENRIQUE ROBLEDO SAHAGÚN        50% — domicilio: Calle Centenario 50, Col. Mascota,
                                        OCOTLÁN, JALISCO → fue alcalde de Ocotlán

Nota: ROBRO y Royal Park fueron constituidas el mismo día (14/05/2014 y 20/05/2014)
por el mismo notario (Carlos Gutiérrez Aceves, No. 115039122, Guadalajara).
Objeto social de ambas: fraccionamientos inmobiliarios — ninguna de combustibles.
La fusión de Royal Park en Ecocarburante (empresa de combustibles) es atípica.

Cadena completa hasta Robledo Sahagún:
  Ecocarburante ← fusión ← Royal Park Ocotlan ← 50% ROBRO ← 50% Enrique Robledo Sahagún
                                                                       (ex-alcalde Ocotlán, Jalisco)

Cadena societaria de Ecocarburante (post-fusión 2022):
  EDGAR MARÍN MEZA MORENO       RFC: MEME850621T95   49%  $537,888,000
  ERIC DANIEL ZAMORA DELGADILLO RFC: ZADE820616DH3   25%  $268,945,000
  GERARDO HERNÁNDEZ CHÁVEZ      RFC: HECG740212F60   25%  $268,945,000
  PETRO ALMACENES DE OCCIDENTE  RFC: PAO191021RQ4     1%       $5,000

Cambio de accionistas (mayo 2023) — Edgar Marín y Zamora Delgadillo salen:
  JESUS ARTURO CARDENAS ESPARZA RFC: CAEJ680807UW6   41%  $441,071,000
  SHAHAB AFSHARIAN CAMPUZANO    RFC: AACS821229RB4   33%  $365,762,000
  GERARDO HERNÁNDEZ CHÁVEZ      RFC: HECG740212F60   25%  $268,945,000

Indicadores observables documentados:
  - tiene_discrepancias_en_importaciones: vinculada a causa penal 325/2025 (FGR)
  - tiene_contratos_gubernamentales: contratos con SEDENA para AIFA (500M+ pesos)
  - ganancias_desproporcionadas: $100,000 (2017) → $1,075,783,000 (2022) = 10,757x
  - contradiccion_legitimidad: DERIVADA automáticamente (contratos_gov ∧ discrepancias)

Resultado esperado:
  - Ecocarburante:              ALTA
  - Royal Park Ocotlan:         MEDIA  (hereda de Ecocarburante, degradación)
  - ROBRO:                      BAJA   (hereda de Royal Park, segunda degradación)
  - Enrique Robledo Sahagún:    MEDIA  (es_funcionario ALTA + es_socio_de_empresa_dudosa BAJA)
  - Rodríguez Luna:             BAJA   (hereda de ROBRO/Royal Park)
  - González Márquez:           BAJA   (hereda de Royal Park)
  - Accionistas Eco (2023+):    MEDIA  (hereda ALTA de Ecocarburante, degradación)
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models import Empresa, Persona
from engine import ForwardChainingEngine
from data_loader import CompraNetLoader


def cargar(engine: ForwardChainingEngine):
    # --- Ecocarburante S.A. de C.V. ---
    # ec-const.pdf, ec-fusion-inc.pdf, ec-nombramiento-*.pdf
    eco = Empresa(nombre="Ecocarburante S.A. de C.V.")
    eco.tiene_discrepancias_en_importaciones = True  # causa penal 325/2025 FGR
    eco.tiene_contratos_gubernamentales      = True  # SEDENA/AIFA, 500M+ pesos
    eco.ganancias_desproporcionadas          = True  # $100K → $1,075M en 5 años (SIGER)
    # contradiccion_legitimidad se deriva automáticamente:
    #   tiene_contratos_gubernamentales ∧ tiene_discrepancias_en_importaciones → True
    engine.agregar_empresa(eco)

    # --- Royal Park Ocotlan S.A. de C.V. --- (rpo-const.pdf)
    # FME: 82678, Guadalajara. Empresa inmobiliaria absorbida por Ecocarburante (nov 2022).
    # Objeto social: fraccionamientos, compraventa de casas — SIN relación con combustibles.
    rpo = Empresa(nombre="Royal Park Ocotlan S.A. de C.V.")
    engine.agregar_empresa(rpo)

    # --- ROBRO S.A. de C.V. --- (robro-const.pdf)
    # FME: 82686, Guadalajara. 50% accionista de Royal Park Ocotlan.
    # Constituida el mismo día y por el mismo notario que Royal Park.
    robro = Empresa(nombre="ROBRO S.A. de C.V.")
    engine.agregar_empresa(robro)

    # --- Accionistas activos de Ecocarburante (post-mayo 2023) ---
    gerardo = Persona(nombre="Gerardo Hernández Chávez")
    # RFC: HECG740212F60 — 25%, único accionista que permaneció desde 2022
    engine.agregar_persona(gerardo)

    cardenas = Persona(nombre="Jesús Arturo Cárdenas Esparza")
    # RFC: CAEJ680807UW6 — 41%, entró mayo 2023
    engine.agregar_persona(cardenas)

    shahab = Persona(nombre="Shahab Afsharian Campuzano")
    # RFC: AACS821229RB4 — 33%, entró mayo 2023
    engine.agregar_persona(shahab)

    # --- Accionistas de Royal Park Ocotlan --- (rpo-const.pdf)
    rodriguez = Persona(nombre="Juan Alejandro Rodríguez Luna")
    # 25% de Royal Park + 50% de ROBRO + Admin Único de ambas — nodo de enlace
    engine.agregar_persona(rodriguez)

    gonzalez = Persona(nombre="José Martín González Márquez")
    # 25% de Royal Park, Comisario de ROBRO
    engine.agregar_persona(gonzalez)

    # --- Enrique Robledo Sahagún --- (robro-const.pdf)
    # 50% accionista de ROBRO. Domicilio: Calle Centenario 50, Col. Mascota, Ocotlán, Jalisco.
    # Fue alcalde de Ocotlán, Jalisco → es_funcionario = True
    robledo = Persona(nombre="Enrique Robledo Sahagún")
    robledo.es_funcionario = True  # alcalde de Ocotlán, Jalisco (cargo público)
    engine.agregar_persona(robledo)

    # --- Relaciones ---
    # Ecocarburante → accionistas directos
    engine.agregar_relacion("empresa", "Ecocarburante S.A. de C.V.",
                             "persona", "Gerardo Hernández Chávez", "socio_de")
    engine.agregar_relacion("empresa", "Ecocarburante S.A. de C.V.",
                             "persona", "Jesús Arturo Cárdenas Esparza", "socio_de")
    engine.agregar_relacion("empresa", "Ecocarburante S.A. de C.V.",
                             "persona", "Shahab Afsharian Campuzano", "socio_de")

    # Ecocarburante → Royal Park (fusión por absorción nov 2022)
    engine.agregar_relacion("empresa", "Ecocarburante S.A. de C.V.",
                             "empresa", "Royal Park Ocotlan S.A. de C.V.", "socio_de")

    # Royal Park → sus accionistas directos
    engine.agregar_relacion("empresa", "Royal Park Ocotlan S.A. de C.V.",
                             "persona", "Juan Alejandro Rodríguez Luna", "socio_de")
    engine.agregar_relacion("empresa", "Royal Park Ocotlan S.A. de C.V.",
                             "persona", "José Martín González Márquez", "socio_de")

    # Royal Park → ROBRO (50% accionista de RPO)
    engine.agregar_relacion("empresa", "Royal Park Ocotlan S.A. de C.V.",
                             "empresa", "ROBRO S.A. de C.V.", "socio_de")

    # ROBRO → sus accionistas
    engine.agregar_relacion("empresa", "ROBRO S.A. de C.V.",
                             "persona", "Juan Alejandro Rodríguez Luna", "socio_de")
    engine.agregar_relacion("empresa", "ROBRO S.A. de C.V.",
                             "persona", "Enrique Robledo Sahagún", "socio_de")


if __name__ == "__main__":
    engine = ForwardChainingEngine()
    cargar(engine)

    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
    loader = CompraNetLoader(data_dir=os.path.abspath(base_dir))
    print("\n[CompraNet] Buscando empresas en registros de contratos gubernamentales...")
    descubrimientos = loader.enriquecer_engine(engine, verbose=True)
    if not descubrimientos:
        print("  No se encontraron contratos para los actores de este escenario.")

    resultado = engine.run()

    print("\n=== Escenario 2: Ecocarburante S.A. de C.V. ===")
    print("(Escenario Contradictorio — Resultado esperado: empresa ALTA, accionistas MEDIA)\n")

    orden = ["empresa", "persona", "gasolinera"]
    for info in sorted(resultado.values(), key=lambda x: orden.index(x["tipo"])):
        nivel = info["alerta_general"]
        print(f"[{info['tipo'].upper()}] {info['nombre']}")
        print(f"  Alerta general: {nivel.upper()}")
        print(f"  Flags activas: {[f[0] for f in info['flags']]}")
        if info["tipo"] == "empresa" and info.get("monto_compranet", 0) > 0:
            print(f"  CompraNet: {info['contratos_compranet']} contratos — ${info['monto_compranet']:,.0f} MXN")
        print()
