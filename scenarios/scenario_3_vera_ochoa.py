"""
Escenario 3: Saúl Vera Ochoa / Tampico Terminal Marítima — Incierto, Sin Alerta.

Fuente SIGER: data/siger/cadena-ttm/
  - ttm-const.pdf                  FME N-2020036717, constituida 04/06/2020, Tampico, Tamaulipas
  - ttm-as.pdf                     Asamblea mayo 2023 — Tramitadora del Pacífico sale
  - ttm-op.pdf                     Poder (27/03/2023): TTM → Saúl Vera Ochoa, poder IRREVOCABLE
  - cv-op19042018.pdf              CONSTRUCTORA VEASA otorga poder, firmado por Patricia Vera Ochoa (2018)
  - cv-poder-manuel-alexis-2022.pdf  CONSTRUCTORA VEASA → Manuel Alexis Vera Ramírez (2022)
  - cv-poder-patricia-2019.pdf     CONSTRUCTORA VEASA otorga poder (2019), Patricia Vera Ochoa
  - tps-const-2022.pdf             TAMPICO PORT SOLUTIONS FME N-2022034576, Villahermosa, 18/03/2022
  - vos-poder-2018.pdf             VOS GRUPO CONSTRUCTOR FME 5533, poder ene 2018
  - vos-as-2019-capital.pdf        VOS aumento de capital dic 2019 (María Teresa Pérez + Cruz Hernández)
  - vos-poder-patricia-2012.pdf    VOS otorga poder a Patricia Vera Ochoa, ago 2012
  - vertice-const-2019.pdf         ESTUDIOS ESTRATÉGICOS EL VÉRTICE FME N-2019044231, may 2019
  - ryc-const-2014.pdf             MULTISERVICIOS RYC FME 17970, nov 2014, Villahermosa
  - ryc-poder-2018.pdf             RYC Poder 2018
  - ryc-poder-2019.pdf             RYC Poder 2019
  - ryc-poder-2019-b.pdf           RYC Poder 2019 (parte 2)
  - vaf-const-1997.pdf             VAF CONSTRUCCIONES FME 826, 1997, Villahermosa
  - vaf-const-1997-b.pdf           VAF constitución (duplicado)

Red familiar y empresarial Vera Ochoa documentada (SIGER):

  PATRICIA ROMANA VERA OCHOA (RFC: VEOP581026, nac. 26/10/1958, Tabasco)
    → Representa a CONSTRUCTORA VEASA S.A. de C.V. (FME: 13757)
    → Firma poderes en nombre de VEASA en 2018, 2019 y 2022
    → Apoderada de VOS GRUPO CONSTRUCTOR (FME 5533) desde al menos 2012
    → Apellido compuesto idéntico a Saúl → hermana

  CONSTRUCTORA VEASA S.A. de C.V. (RFC: CVE1005194W1)
    → Accionista mayoritaria de TTM: 460 acciones = 46%
    → Registrada en Villahermosa, Tabasco
    → CompraNet: 9 contratos, $66,241,776 MXN — adjudicación directa detectada

  VOS GRUPO CONSTRUCTOR S.A. de C.V. (FME 5533, Villahermosa)
    → Patricia Vera Ochoa apoderada desde 2012 (vos-poder-patricia-2012.pdf)
    → Asamblea dic 2019: accionistas María Teresa Pérez de la Cruz + Encarnación Cruz Hernández
    → Empresa de construcción — misma notaría (José Andrés Gallegos Torres) que TTM y TPS

  TAMPICO PORT SOLUTIONS S.A. de C.V. (FME N-2022034576)
    → Constituida 18/03/2022 en Villahermosa, Cárdenas, Tabasco
    → Objeto social: asesoría aduanal, navieras, importación/exportación, transporte portuario
    → VERA RAMÍREZ aparece como accionista (mismo apellido → red familiar)
    → Misma notaría: José Andrés Gallegos Torres No. 1, Cárdenas, Tabasco
    → Capital: $1,300,000 — empresa activa en servicios portuarios desde 2022

  MANUEL ALEXIS VERA RAMÍREZ
    → Comisario de TTM (nombrado asamblea 2023, ttm-as.pdf)
    → Apoderado de CONSTRUCTORA VEASA (poder otorgado mar 2022)
    → Accionista de TAMPICO PORT SOLUTIONS (tps-const-2022.pdf)
    → Apellido Vera → miembro de la red familiar

  SAÚL VERA OCHOA (RFC: VEOS56072624A)
    → Apoderado irrevocable de TTM (ttm-op.pdf, mar 2023)
    → No aparece como accionista — controla TTM operativamente

Estructura de control real de TTM:
  Patricia (hermana) → CONSTRUCTORA VEASA (46%) → TTM ← Saúl (apoderado irrevocable)
                    ↓                               TTM ← Manuel Alexis (comisario, de VEASA)
               VOS Grupo Constructor               Manuel Alexis → Tampico Port Solutions

Por qué es incierto:
  El sistema detecta la red familiar pero no activa alertas con la evidencia disponible:
  - TTM: empresa_nueva (baja) + contrato gubernamental (no genera alerta sola) = SIN_ALERTA
  - CONSTRUCTORA VEASA: sin flags propias documentadas = SIN_ALERTA
  - Patricia y Manuel Alexis: sin flags propias documentadas = SIN_ALERTA
  - Saúl Vera Ochoa: apoyo_campana (baja) sola = SIN_ALERTA
  - TTM no propaga porque su alerta_general es SIN_ALERTA

  tiene_familiar_o_socio_en_poder requeriría confirmar que algún miembro de la
  familia Vera Ochoa ocupa un cargo público — no documentado aún en SIGER.

  El sistema identifica dónde investigar — no a quién culpar.

  Si se confirmara que TTM recibió combustible de Intanza directamente, se
  activaría tiene_discrepancias_en_importaciones y el sistema escalaría a ALTA
  por contradiccion_legitimidad (tiene_contratos_gubernamentales ya está activo).

Resultado esperado:
  - CONSTRUCTORA VEASA:         SIN_ALERTA
  - Tampico Terminal Marítima:  SIN_ALERTA
  - Patricia Romana Vera Ochoa: SIN_ALERTA
  - Manuel Alexis Vera Ramírez: SIN_ALERTA
  - Saúl Vera Ochoa:            SIN_ALERTA
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from models import Empresa, Persona
from engine import ForwardChainingEngine
from data_loader import CompraNetLoader


def cargar(engine: ForwardChainingEngine):
    # --- CONSTRUCTORA VEASA S.A. de C.V. ---
    # FME 13757, Villahermosa Tabasco. Accionista mayoritaria de TTM (46%).
    # Controlada por Patricia Romana Vera Ochoa (hermana de Saúl).
    # CompraNet: 9 contratos, $66.2M MXN, adjudicación directa — se descubre automáticamente.
    veasa = Empresa(nombre="Constructora VEASA S.A. de C.V.")
    # Sin flags propias manuales — CompraNet activará tiene_contratos_gubernamentales en auto-discovery
    engine.agregar_empresa(veasa)

    # --- VOS GRUPO CONSTRUCTOR S.A. de C.V. ---
    # FME 5533, Villahermosa. Patricia Vera Ochoa es apoderada desde 2012.
    # Asamblea 2019: aumento de capital, accionistas María Teresa Pérez + Encarnación Cruz.
    vos = Empresa(nombre="VOS Grupo Constructor S.A. de C.V.")
    engine.agregar_empresa(vos)

    # --- TAMPICO PORT SOLUTIONS S.A. de C.V. ---
    # FME N-2022034576, Villahermosa, constituida 18/03/2022.
    # Manuel Alexis Vera Ramírez como accionista — empresa de servicios portuarios.
    # Misma notaría que TTM: José Andrés Gallegos Torres No. 1, Cárdenas Tabasco.
    tps = Empresa(nombre="Tampico Port Solutions S.A. de C.V.")
    tps.empresa_nueva = True  # constituida mar 2022, misma ventana que el esquema AIFA
    engine.agregar_empresa(tps)

    # --- Tampico Terminal Marítima S.A. de C.V. ---
    # ttm-const.pdf — muelle fiscal Tampico, opera Recinto Fiscalizado Estratégico
    ttm = Empresa(nombre="Tampico Terminal Marítima S.A. de C.V.")
    ttm.empresa_nueva               = True  # constituida jun 2020, concesión inmediata
    ttm.tiene_contratos_gubernamentales = True  # concesión ASIPONA Tampico
    # 1 baja sola → sin_alerta. Correcto para escenario incierto.
    # OJO: si se activa tiene_discrepancias_en_importaciones, contradiccion_legitimidad
    # se dispararía automáticamente → alerta ALTA.
    engine.agregar_empresa(ttm)

    # --- Patricia Romana Vera Ochoa ---
    # RFC: VEOP581026, nac. 26/10/1958 — representa CONSTRUCTORA VEASA
    # Hermana de Saúl (mismo apellido compuesto, confirmado en 3 documentos SIGER)
    patricia = Persona(nombre="Patricia Romana Vera Ochoa")
    # Sin flags propias documentadas
    engine.agregar_persona(patricia)

    # --- Manuel Alexis Vera Ramírez ---
    # Comisario de TTM (2023) + apoderado de CONSTRUCTORA VEASA (2022)
    # Nodo de enlace entre VEASA y TTM dentro de la red familiar
    manuel = Persona(nombre="Manuel Alexis Vera Ramírez")
    # Sin flags propias documentadas
    engine.agregar_persona(manuel)

    # --- Saúl Vera Ochoa ---
    # RFC: VEOS56072624A — apoderado irrevocable de TTM (ttm-op.pdf mar 2023)
    vera = Persona(nombre="Saúl Vera Ochoa")
    vera.apoyo_campana_politica = True  # apoyó públicamente a Adán Augusto López
    engine.agregar_persona(vera)

    # --- Relaciones ---
    # VEASA (46%) → TTM
    engine.agregar_relacion("empresa", "Constructora VEASA S.A. de C.V.",
                            "empresa", "Tampico Terminal Marítima S.A. de C.V.", "socio_de")

    # Patricia representa/controla CONSTRUCTORA VEASA
    engine.agregar_relacion("empresa", "Constructora VEASA S.A. de C.V.",
                            "persona", "Patricia Romana Vera Ochoa", "socio_de")

    # Manuel Alexis: apoderado de VEASA y comisario de TTM
    engine.agregar_relacion("empresa", "Constructora VEASA S.A. de C.V.",
                            "persona", "Manuel Alexis Vera Ramírez", "socio_de")
    engine.agregar_relacion("empresa", "Tampico Terminal Marítima S.A. de C.V.",
                            "persona", "Manuel Alexis Vera Ramírez", "socio_de")

    # Saúl: apoderado irrevocable de TTM
    engine.agregar_relacion("empresa", "Tampico Terminal Marítima S.A. de C.V.",
                            "persona", "Saúl Vera Ochoa", "titular_de")

    # Vínculo familiar Patricia ↔ Saúl (apellido compuesto idéntico, SIGER confirma)
    engine.agregar_relacion("persona", "Patricia Romana Vera Ochoa",
                            "persona", "Saúl Vera Ochoa", "familiar_de")

    # Patricia → VOS Grupo Constructor (apoderada desde 2012, vos-poder-patricia-2012.pdf)
    engine.agregar_relacion("empresa", "VOS Grupo Constructor S.A. de C.V.",
                            "persona", "Patricia Romana Vera Ochoa", "socio_de")

    # Manuel Alexis → Tampico Port Solutions (accionista, tps-const-2022.pdf)
    engine.agregar_relacion("empresa", "Tampico Port Solutions S.A. de C.V.",
                            "persona", "Manuel Alexis Vera Ramírez", "socio_de")


if __name__ == "__main__":
    engine = ForwardChainingEngine()
    cargar(engine)

    # Auto-descubrimiento: cruzar actores del motor contra CompraNet
    base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data')
    loader = CompraNetLoader(data_dir=os.path.abspath(base_dir))
    print("\n[CompraNet] Buscando empresas en registros de contratos gubernamentales...")
    descubrimientos = loader.enriquecer_engine(engine, verbose=True)
    if not descubrimientos:
        print("  No se encontraron contratos para los actores de este escenario.")

    resultado = engine.run()

    print("\n=== Escenario 3: Saúl Vera Ochoa / Tampico Terminal Marítima ===")
    print("(Escenario Incierto — Resultado esperado: SIN ALERTA en todos)\n")

    orden = ["empresa", "persona", "gasolinera"]
    for info in sorted(resultado.values(), key=lambda x: orden.index(x["tipo"])):
        nivel = info["alerta_general"]
        print(f"[{info['tipo'].upper()}] {info['nombre']}")
        print(f"  Alerta general: {nivel.upper()}")
        print(f"  Flags activas: {[f[0] for f in info['flags']]}")
        if info["tipo"] == "empresa" and info.get("monto_compranet", 0) > 0:
            print(f"  CompraNet: {info['contratos_compranet']} contratos — ${info['monto_compranet']:,.0f} MXN")
        print()
