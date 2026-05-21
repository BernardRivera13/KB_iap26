"""
Escenario 1: Francisco Javier Antonio Martínez (FJAM) — Consistente, Alerta Alta.

Fuente SIGER: data/siger/cadena-intanza/
  - int-const.pdf                        FME N-2022034988, constituida 27/04/2022 en Monterrey, NL
  - int-rev-fun.pdf                      Asamblea 22/05/2023 — venta total a Ricardo Ayón y Ramiro Rocha
  - tda-const-2022.pdf                   IMPORTACIONES TDA FME N-2022038889, constituida 18/05/2022
  - tda-as-2024-ayon-admin.pdf           Asamblea abr 2024 — Ayón sustituye a Hernán como Admin Único
  - tda-as-2024-ayon-admin-b.pdf         (mismo instrumento, página 2)
  - tda-as-2024-ayon-admin-c.pdf         (mismo instrumento, página 3)
  - garzapalomares-const-2016.pdf        GRUPO GARZAPALOMARES FME N-2018033156, constituida 28/10/2016
  - garzapalomares-poder-marquez-2022.pdf   Poder a Miguel Ángel Márquez Pozadas (mar 2022)
  - garzapalomares-poder-marquez-2022-b.pdf (mismo instrumento, página 2)

Fuente SIGER: data/siger/cadena-belure/
  - belure-as-2018-rocha-admin.pdf      Asamblea ago 2018 — Rocha Alvarado entra como Admin Único
  - belure-as-2018-transmision.pdf      Transmisión acciones ago 2018 (parte 2, inscrita jul 2019)
  - belure-as-2020-estefania-admin.pdf  Asamblea jul 2020 — Estefanía Garza entra como Admin Única

Hallazgos SIGER de Comercializadora Belure S.A. de C.V. (FME: N-2018055928, RFC: CBS180622QI7):
  - Registrada en Monterrey, Nuevo León
  - Agosto 2018: RAMIRO ROCHA ALVARADO nombrado Administrador Único
  - Julio 2020: ESTEFANÍA GARZA PALOMARES nombrada Administrador Única;
                RAMIRO ROCHA ALVARADO continúa como Apoderado General
  → Rocha y Estefanía estaban vinculados en Belure ANTES de fundar Intanza (abr 2022)
  → La red no fue improvisada — SIGER documenta la estructura preexistente

Hallazgos SIGER de Intanza S.A. de C.V.:
  - Constituida 27/04/2022 — empresa nueva al momento del esquema AIFA (2022)
  - Capital inicial: $50,000 (mínimo legal)
  - Objeto social declarado: productos eléctricos, bebidas alcohólicas — SIN mención
    de combustibles ni hidrocarburos. Operó como importadora de diesel sin que su
    acta constitutiva lo contemple → refuerza tiene_discrepancias_en_importaciones
  - Fundadores originales:
      HERNÁN GUILLERMO FERNÁNDEZ MORÁN  RFC: FEMH890907 — 50% → vendió todo
      ESTEFANÍA GARZA PALOMARES         RFC: GAPE960404 — 50% → vendió todo (YA era Admin de Belure)
  - Cambio de control (mayo-julio 2023, post-esquema):
      RICARDO AYÓN RODRÍGUEZ  RFC: AORR941110PZA — 98%  (señalado causa penal 325/2025)
      RAMIRO ROCHA ALVARADO   RFC: ROAR730115IE0 —  2%  (señalado, Admin Único; YA era apoderado de Belure)

Hallazgos SIGER de IMPORTACIONES TDA S.A. de C.V. (FME N-2022038889):
  - Constituida 18/05/2022 — UN MES después de Intanza (27/04/2022), mismos fundadores
  - Fundadores: Hernán Guillermo Fernández Morán (50%) + Estefanía Garza Palomares (50%)
  - Mismo notario que Intanza: Edgar Gerardo Regis García No. 45, Monterrey NL
  - Objeto social: vinos, bebidas alcohólicas, informática — SIN mención de combustibles
  - Abril 2024: RICARDO AYÓN RODRÍGUEZ nombrado Administrador Único (mismo patrón que Intanza)
    Hernán Guillermo sale; Estefanía permanece como Apoderada Legal
  → Patrón idéntico: empresa nueva → esquema → Ayón toma control post-investigación

Hallazgos SIGER de GRUPO GARZAPALOMARES COMERCIALIZACIÓN Y SERVICIOS S.A. de C.V.
  (FME N-2018033156):
  - Constituida 28/10/2016, notario Everardo Alanis Guerra No. 96, Monterrey NL
  - ESTEFANÍA GARZA PALOMARES: 50%, Administrador Única desde constitución
  - Objeto social EXPLÍCITAMENTE incluye: "compra venta de gasolinas, sus derivados"
  → Estefanía tenía empresa de gasolinas desde 2016 — antes del esquema AIFA
  - Marzo 2022: Poder general a MIGUEL ÁNGEL MÁRQUEZ POZADAS (RFC: MAPM7806161V6)
    mismo mes que Intanza operaba como importadora de diesel

Contexto de FJAM (fuentes periodísticas / FGR):
  Director de Administración y Finanzas de ASIPONA Tampico.
  Socio de los dueños de Intanza a través de Comercializadora Belure (NL).
  Acumuló 18 vehículos de lujo en 2 años. Detenido por la FGR.

Resultado esperado:
  - Comercializadora Belure:     MEDIA (propagación desde Intanza vía socios compartidos)
  - Intanza:                     ALTA
  - Importaciones TDA:           MEDIA (empresa_nueva baja + socio_senalado alta = 2 flags → media)
  - Grupo GarzaPalomares:        MEDIA (hereda de Estefanía ALTA, degradación)
  - Estefanía Garza:             ALTA (Belure + Intanza + TDA → multiples_empresas_recientes + hereda ALTA)
  - Hernán Fernández:            MEDIA (hereda de Intanza/TDA)
  - Ricardo Ayón:                ALTA
  - Ramiro Rocha:                ALTA
  - FJAM:                        ALTA
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models import Empresa, Persona, AlertLevel
from engine import ForwardChainingEngine
from data_loader import CompraNetLoader


def cargar(engine: ForwardChainingEngine):
    # --- Comercializadora Belure S.A. de C.V. ---
    # SIGER: cadena-belure/ — FME N-2018055928, RFC: CBS180622QI7, Monterrey NL
    # Nodo puente: Rocha Alvarado y Estefanía controlaron esta empresa ANTES de Intanza
    # FJAM vinculado a Intanza vía Belure (fuentes periodísticas / FGR)
    belure = Empresa(nombre="Comercializadora Belure S.A. de C.V.")
    engine.agregar_empresa(belure)

    # --- IMPORTACIONES TDA S.A. de C.V. ---
    # SIGER: tda-const-2022.pdf — FME N-2022038889, Monterrey NL
    # Fundada 18/05/2022 por Hernán + Estefanía (mismos fundadores que Intanza, un mes después)
    # Abril 2024: Ayón Rodríguez toma el control como Admin Único — patrón idéntico a Intanza
    tda = Empresa(nombre="Importaciones TDA S.A. de C.V.")
    tda.empresa_nueva = True              # mayo 2022, misma ventana que Intanza
    tda.socio_senalado = True             # Ayón Rodríguez (causa penal 325/2025) toma control abr 2024
    tda.socio_senalado_nivel = AlertLevel.HIGH
    engine.agregar_empresa(tda)

    # --- GRUPO GARZAPALOMARES COMERCIALIZACIÓN Y SERVICIOS S.A. de C.V. ---
    # SIGER: garzapalomares-const-2016.pdf — FME N-2018033156, Monterrey NL
    # Estefanía 50% + Admin Única desde 2016. Objeto social incluye "compra venta de gasolinas"
    # Poder otorgado a Márquez Pozadas en mar 2022, mismo período del esquema Intanza/AIFA
    garzapalomares = Empresa(nombre="Grupo GarzaPalomares Comercialización y Servicios S.A. de C.V.")
    engine.agregar_empresa(garzapalomares)

    # --- Intanza S.A. de C.V. (empresa importadora) ---
    # SIGER: int-const.pdf — constituida 27/04/2022, objeto social SIN mención de combustibles
    intanza = Empresa(nombre="Intanza S.A. de C.V.")
    intanza.empresa_nueva = True               # constituida 27/04/2022
    intanza.socio_senalado = True              # Ricardo Ayón / Ramiro Rocha: causa penal 325/2025
    intanza.socio_senalado_nivel = AlertLevel.HIGH
    intanza.tiene_discrepancias_en_importaciones = True  # 10M litros como "aditivos", 555 facturas
    engine.agregar_empresa(intanza)

    # --- Fundador sin señalamientos propios ---
    # SIGER int-const.pdf: co-fundó Intanza, vendió 100% en mayo 2023
    hernan = Persona(nombre="Hernán Guillermo Fernández Morán")
    # RFC: FEMH890907 — sin señalamientos públicos, relevancia como puente societario
    engine.agregar_persona(hernan)

    # --- Estefanía Garza Palomares ---
    # SIGER int-const.pdf: co-fundadora de Intanza (2022)
    # SIGER belure-as-2020-estefania-admin.pdf: Administrador Única de Belure (jul 2020)
    # → aparece en DOS empresas de la red: Belure + Intanza → multiples_empresas_recientes
    estefania = Persona(nombre="Estefanía Garza Palomares")
    estefania.multiples_empresas_recientes = True  # Belure (2020) + Intanza (2022), SIGER confirmado
    engine.agregar_persona(estefania)

    # --- Accionistas señalados (post-venta julio 2023) ---
    # SIGER int-rev-fun.pdf: compraron 100% de Intanza, Rocha se volvió Admin. Único
    # SIGER belure-as-2018-rocha-admin.pdf: Rocha ya era Admin Único de Belure desde 2018
    ayon = Persona(nombre="Ricardo Ayón Rodríguez")
    ayon.tiene_senalamientos          = True   # RFC: AORR941110PZA, causa penal 325/2025
    ayon.multiples_empresas_recientes = True   # aparece en múltiples empresas recientes
    engine.agregar_persona(ayon)

    rocha = Persona(nombre="Ramiro Rocha Alvarado")
    rocha.tiene_senalamientos          = True  # RFC: ROAR730115IE0, causa penal 325/2025
    rocha.multiples_empresas_recientes = True  # Belure (2018–2020) + Intanza (2023), SIGER confirmado
    engine.agregar_persona(rocha)

    # --- Francisco Javier Antonio Martínez (FJAM) ---
    fjam = Persona(nombre="Francisco Javier Antonio Martínez")
    fjam.tiene_senalamientos    = True         # detenido por FGR (causa penal 325/2025)
    fjam.enriquecimiento_dudoso = True         # 18 vehículos de lujo en 2 años
    fjam.es_funcionario         = True         # Director ASIPONA Tampico
    engine.agregar_persona(fjam)

    # --- Relaciones ---
    # Belure ↔ Estefanía (Admin Única 2020, SIGER belure-as-2020)
    engine.agregar_relacion("empresa", "Comercializadora Belure S.A. de C.V.",
                            "persona", "Estefanía Garza Palomares", "socio_de")
    engine.agregar_relacion("persona", "Estefanía Garza Palomares",
                            "empresa", "Comercializadora Belure S.A. de C.V.", "socio_de")

    # Belure ↔ Rocha (Admin Único 2018, Apoderado 2020, SIGER belure-as-2018 + belure-as-2020)
    engine.agregar_relacion("empresa", "Comercializadora Belure S.A. de C.V.",
                            "persona", "Ramiro Rocha Alvarado", "socio_de")
    engine.agregar_relacion("persona", "Ramiro Rocha Alvarado",
                            "empresa", "Comercializadora Belure S.A. de C.V.", "socio_de")

    # Belure ↔ FJAM (fuentes periodísticas / FGR — conexión documentada, no en SIGER disponible)
    engine.agregar_relacion("empresa", "Comercializadora Belure S.A. de C.V.",
                            "persona", "Francisco Javier Antonio Martínez", "socio_de")

    # Intanza → fundadores (conexión societaria histórica)
    engine.agregar_relacion("empresa", "Intanza S.A. de C.V.",
                            "persona", "Hernán Guillermo Fernández Morán", "socio_de")
    engine.agregar_relacion("empresa", "Intanza S.A. de C.V.",
                            "persona", "Estefanía Garza Palomares", "socio_de")

    # Intanza → accionistas señalados
    engine.agregar_relacion("empresa", "Intanza S.A. de C.V.",
                            "persona", "Ricardo Ayón Rodríguez", "socio_de")
    engine.agregar_relacion("empresa", "Intanza S.A. de C.V.",
                            "persona", "Ramiro Rocha Alvarado", "socio_de")

    # FJAM → Intanza (vía Belure, corroborado por FGR)
    engine.agregar_relacion("empresa", "Intanza S.A. de C.V.",
                            "persona", "Francisco Javier Antonio Martínez", "socio_de")

    # Importaciones TDA → fundadores (mismos que Intanza)
    engine.agregar_relacion("empresa", "Importaciones TDA S.A. de C.V.",
                            "persona", "Hernán Guillermo Fernández Morán", "socio_de")
    engine.agregar_relacion("empresa", "Importaciones TDA S.A. de C.V.",
                            "persona", "Estefanía Garza Palomares", "socio_de")
    engine.agregar_relacion("empresa", "Importaciones TDA S.A. de C.V.",
                            "persona", "Ricardo Ayón Rodríguez", "socio_de")

    # Grupo GarzaPalomares → Estefanía (50%, Admin Única desde 2016)
    engine.agregar_relacion("empresa", "Grupo GarzaPalomares Comercialización y Servicios S.A. de C.V.",
                            "persona", "Estefanía Garza Palomares", "socio_de")
    engine.agregar_relacion("persona", "Estefanía Garza Palomares",
                            "empresa", "Grupo GarzaPalomares Comercialización y Servicios S.A. de C.V.", "socio_de")


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

    print("\n=== Escenario 1: Francisco Javier Antonio Martínez ===")
    print("(Escenario Consistente — Resultado esperado: ALTA en todos)\n")

    orden = ["empresa", "persona", "gasolinera"]
    for info in sorted(resultado.values(), key=lambda x: orden.index(x["tipo"])):
        nivel = info["alerta_general"]
        print(f"[{info['tipo'].upper()}] {info['nombre']}")
        print(f"  Alerta general: {nivel.upper()}")
        print(f"  Flags activas: {[f[0] for f in info['flags']]}")
        if info["tipo"] == "empresa" and info.get("monto_compranet", 0) > 0:
            print(f"  CompraNet: {info['contratos_compranet']} contratos — ${info['monto_compranet']:,.0f} MXN")
        print()
