"""
Base de Conocimiento (KB) — Cláusulas de Horn para detección de indicadores de corrupción.

Cada regla está documentada en:
  - Lenguaje natural
  - Lógica formal (cláusula de Horn)
  - Justificación

Las reglas son funciones puras: reciben un nodo y retornan (flag_activada: bool, nivel: str).
"""

from models import Empresa, Persona, Gasolinera, AlertLevel


# ---------------------------------------------------------------------------
# REGLAS DE NIVEL DE FLAG INDIVIDUAL
# ---------------------------------------------------------------------------

NIVEL_FLAGS_EMPRESA = {
    "socio_senalado":                      None,       # hereda del socio
    "consiguio_permiso_express":           AlertLevel.MEDIUM,
    "tiene_discrepancias_en_importaciones": AlertLevel.HIGH,
    "tiene_discrepancias_en_ganancias":    AlertLevel.HIGH,
    "ganancias_desproporcionadas":         AlertLevel.MEDIUM,
    "empresa_nueva":                       AlertLevel.LOW,
    "contradiccion_legitimidad":           AlertLevel.HIGH,
}

NIVEL_FLAGS_PERSONA = {
    "es_socio_de_empresa_dudosa":         None,        # hereda de la empresa
    "tiene_familiar_o_socio_en_poder":    AlertLevel.LOW,
    "apoyo_campana_politica":             AlertLevel.LOW,
    "tiene_senalamientos":                AlertLevel.HIGH,
    "enriquecimiento_dudoso":             AlertLevel.MEDIUM,
    "es_funcionario":                     AlertLevel.HIGH,
    "multiples_empresas_recientes":       AlertLevel.MEDIUM,
}

NIVEL_FLAGS_GASOLINERA = {
    "licitacion_cercana_al_fraude":       AlertLevel.LOW,
    "ganancias_exceden_margen":           AlertLevel.MEDIUM,
    "socios_abanderados":                 None,        # hereda de los socios
}


# ---------------------------------------------------------------------------
# REGLA 1: Contradicción de legitimidad (regla derivada)
#
# Natural: Una empresa con contratos gubernamentales Y discrepancias en
#          importaciones activa una bandera especial de alta gravedad, porque
#          implica que pasó filtros del gobierno pero sigue en irregularidades.
#
# Formal:  tiene_contratos_gubernamentales(X) ∧
#          tiene_discrepancias_en_importaciones(X)
#          → contradiccion_legitimidad(X)
#
# Justificación: Es más grave que una empresa desconocida con las mismas
#          discrepancias — indica posible facilitación interna.
# ---------------------------------------------------------------------------

def regla_contradiccion_legitimidad(empresa: Empresa) -> bool:
    """Retorna True si se activa contradiccion_legitimidad."""
    return (
        empresa.tiene_contratos_gubernamentales
        and empresa.tiene_discrepancias_en_importaciones
    )


# ---------------------------------------------------------------------------
# REGLAS 2–5: Alerta general de Empresa
#
# Natural: La alerta general de una empresa se calcula combinando sus banderas
#          activas según las reglas de combinación definidas en el CLAUDE.md.
#
# Formal (ejemplos):
#   empresa_nueva(X) ∧ ¬(otras_banderas)(X) → sin_alerta(X)
#   (solo_una_media)(X) → alerta_baja(X)
#   (solo_una_alta)(X)  → alerta_media(X)
#   (alta(X) ∧ media(X)) → alerta_alta(X)
#   4+_banderas(X)      → alerta_alta(X)
# ---------------------------------------------------------------------------

def calcular_alerta_empresa(empresa: Empresa) -> tuple[str, list]:
    """
    Retorna (nivel_alerta, lista_de_flags_activas).
    Implementa las reglas de combinación de CLAUDE.md como cláusulas de Horn.
    """
    flags = []

    # Recopilar flags activas con su nivel
    if empresa.socio_senalado:
        flags.append(("socio_senalado", empresa.socio_senalado_nivel))
    if empresa.consiguio_permiso_express:
        flags.append(("consiguio_permiso_express", AlertLevel.MEDIUM))
    if empresa.tiene_discrepancias_en_importaciones:
        flags.append(("tiene_discrepancias_en_importaciones", AlertLevel.HIGH))
    if empresa.tiene_discrepancias_en_ganancias:
        flags.append(("tiene_discrepancias_en_ganancias", AlertLevel.HIGH))
    if empresa.ganancias_desproporcionadas:
        flags.append(("ganancias_desproporcionadas", AlertLevel.MEDIUM))
    if empresa.empresa_nueva:
        flags.append(("empresa_nueva", AlertLevel.LOW))
    if empresa.contradiccion_legitimidad:
        flags.append(("contradiccion_legitimidad", AlertLevel.HIGH))

    niveles = [n for _, n in flags]
    n_altas  = niveles.count(AlertLevel.HIGH)
    n_medias = niveles.count(AlertLevel.MEDIUM)
    n_bajas  = niveles.count(AlertLevel.LOW)
    total    = len(flags)

    # Cláusulas de Horn para alerta de empresa:

    # R2: 4+ banderas → alta
    if total >= 4:
        return AlertLevel.HIGH, flags

    # R3: 2+ altas → alta
    if n_altas >= 2:
        return AlertLevel.HIGH, flags

    # R3b: 1 alta + 1 media → alta
    if n_altas >= 1 and n_medias >= 1:
        return AlertLevel.HIGH, flags

    # R4: cualquier combinación de 2+ que no sea solo-bajas → media
    if total >= 2 and not (n_bajas == total):
        return AlertLevel.MEDIUM, flags

    # R5: 2 bajas → baja
    if n_bajas >= 2:
        return AlertLevel.LOW, flags

    # R6: 1 alta sola → media
    if n_altas == 1 and total == 1:
        return AlertLevel.MEDIUM, flags

    # R7: 1 media sola → baja
    if n_medias == 1 and total == 1:
        return AlertLevel.LOW, flags

    # R8: 1 baja sola → sin_alerta
    if total == 1 and n_bajas == 1:
        return AlertLevel.NONE, flags

    # Sin banderas → sin_alerta
    return AlertLevel.NONE, flags


# ---------------------------------------------------------------------------
# REGLAS 6–9: Alerta general de Persona
#
# Formal (ejemplos):
#   baja(X) ∧ baja(X) → alerta_baja(X)
#   baja(X) ∧ media(X) → alerta_media(X)
#   alta(X) ∧ baja(X)  → alerta_media(X)
#   alta(X) ∧ media(X) → alerta_alta(X)
# ---------------------------------------------------------------------------

def calcular_alerta_persona(persona: Persona) -> tuple[str, list]:
    flags = []

    if persona.es_socio_de_empresa_dudosa:
        flags.append(("es_socio_de_empresa_dudosa", persona.empresa_dudosa_nivel))
    if persona.tiene_familiar_o_socio_en_poder:
        flags.append(("tiene_familiar_o_socio_en_poder", AlertLevel.LOW))
    if persona.apoyo_campana_politica:
        flags.append(("apoyo_campana_politica", AlertLevel.LOW))
    if persona.tiene_senalamientos:
        flags.append(("tiene_senalamientos", AlertLevel.HIGH))
    if persona.enriquecimiento_dudoso:
        flags.append(("enriquecimiento_dudoso", AlertLevel.MEDIUM))
    if persona.es_funcionario:
        flags.append(("es_funcionario", AlertLevel.HIGH))
    if persona.multiples_empresas_recientes:
        flags.append(("multiples_empresas_recientes", AlertLevel.MEDIUM))

    niveles = [n for _, n in flags]
    n_altas  = niveles.count(AlertLevel.HIGH)
    n_medias = niveles.count(AlertLevel.MEDIUM)
    n_bajas  = niveles.count(AlertLevel.LOW)
    total    = len(flags)

    # R6: alta + media → alta
    if n_altas >= 1 and n_medias >= 1:
        return AlertLevel.HIGH, flags

    # R7: alta + baja → media
    if n_altas >= 1 and n_bajas >= 1:
        return AlertLevel.MEDIUM, flags

    # R8: baja + media → media
    if n_bajas >= 1 and n_medias >= 1:
        return AlertLevel.MEDIUM, flags

    # R9: baja + baja → baja
    if n_bajas >= 2:
        return AlertLevel.LOW, flags

    # Una sola flag
    if total == 1:
        nivel = niveles[0]
        if nivel == AlertLevel.HIGH:
            return AlertLevel.MEDIUM, flags
        if nivel == AlertLevel.MEDIUM:
            return AlertLevel.LOW, flags
        return AlertLevel.NONE, flags

    # 2+ altas → alta
    if n_altas >= 2:
        return AlertLevel.HIGH, flags

    return AlertLevel.NONE, flags


# ---------------------------------------------------------------------------
# REGLAS 10–12: Alerta general de Gasolinera
#
# Formal:
#   baja(X) ∧ baja(X)   → alerta_baja(X)
#   media(X) ∧ media(X) → alerta_media(X)
#   alta(X)             → alerta_alta(X)
# ---------------------------------------------------------------------------

def calcular_alerta_gasolinera(gasolinera: Gasolinera) -> tuple[str, list]:
    flags = []

    if gasolinera.licitacion_cercana_al_fraude:
        flags.append(("licitacion_cercana_al_fraude", AlertLevel.LOW))
    if gasolinera.ganancias_exceden_margen:
        flags.append(("ganancias_exceden_margen", AlertLevel.MEDIUM))
    if gasolinera.socios_abanderados:
        flags.append(("socios_abanderados", gasolinera.socios_abanderados_nivel))

    niveles = [n for _, n in flags]
    n_altas  = niveles.count(AlertLevel.HIGH)
    n_medias = niveles.count(AlertLevel.MEDIUM)
    n_bajas  = niveles.count(AlertLevel.LOW)
    total    = len(flags)

    # R10: alta → alta
    if n_altas >= 1:
        return AlertLevel.HIGH, flags

    # R11: media + media → media
    if n_medias >= 2:
        return AlertLevel.MEDIUM, flags

    # R12: 2 bajas → baja
    if n_bajas >= 2:
        return AlertLevel.LOW, flags

    # Una sola flag
    if total == 1:
        nivel = niveles[0]
        if nivel == AlertLevel.MEDIUM:
            return AlertLevel.LOW, flags
        if nivel == AlertLevel.LOW:
            return AlertLevel.NONE, flags

    # media + baja → baja (degradación)
    if n_medias >= 1:
        return AlertLevel.LOW, flags

    return AlertLevel.NONE, flags
