"""
Motor de Forward Chaining con cláusulas de Horn.

Algoritmo:
1. Aplica reglas derivadas (contradiccion_legitimidad).
2. Calcula alerta_general de cada nodo.
3. Propaga alertas entre nodos conectados (via propagation.py).
4. Repite hasta punto fijo (ninguna alerta cambia).

Protección contra ciclos: se registra el estado anterior y se detiene
si no hubo cambios en la iteración.
"""

from models import Empresa, Persona, Gasolinera, AlertLevel
from kb import (
    regla_contradiccion_legitimidad,
    calcular_alerta_empresa,
    calcular_alerta_persona,
    calcular_alerta_gasolinera,
)


class ForwardChainingEngine:
    def __init__(self):
        self.empresas: dict[str, Empresa] = {}
        self.personas: dict[str, Persona] = {}
        self.gasolineras: dict[str, Gasolinera] = {}

        # Grafo de relaciones: {(tipo_origen, nombre): [(tipo_destino, nombre, tipo_relacion)]}
        self.relaciones: dict[tuple, list] = {}

    # ------------------------------------------------------------------
    # Registro de actores
    # ------------------------------------------------------------------

    def agregar_empresa(self, empresa: Empresa):
        self.empresas[empresa.nombre] = empresa

    def agregar_persona(self, persona: Persona):
        self.personas[persona.nombre] = persona

    def agregar_gasolinera(self, gasolinera: Gasolinera):
        self.gasolineras[gasolinera.nombre] = gasolinera

    def agregar_relacion(self, tipo_origen: str, nombre_origen: str,
                         tipo_destino: str, nombre_destino: str,
                         tipo_relacion: str):
        """
        Registra una arista en el grafo.
        tipo_relacion: 'socio_de' | 'familiar_de' | 'otorgo_licencia_a' | 'titular_de'
        """
        key = (tipo_origen, nombre_origen)
        if key not in self.relaciones:
            self.relaciones[key] = []
        self.relaciones[key].append((tipo_destino, nombre_destino, tipo_relacion))

    # ------------------------------------------------------------------
    # Motor principal
    # ------------------------------------------------------------------

    def run(self, max_iter: int = 100) -> dict:
        """
        Ejecuta Forward Chaining hasta punto fijo.
        Retorna un dict con el estado final de todos los nodos.
        """
        for iteracion in range(max_iter):
            estado_anterior = self._snapshot()

            # Paso 1: Aplicar reglas derivadas
            self._aplicar_reglas_derivadas()

            # Paso 2: Calcular alertas locales
            self._calcular_alertas_locales()

            # Paso 3: Propagar entre nodos
            self._propagar()

            # Punto fijo: si nada cambió, terminar
            if self._snapshot() == estado_anterior:
                break

        return self._estado_final()

    # ------------------------------------------------------------------
    # Pasos internos
    # ------------------------------------------------------------------

    def _aplicar_reglas_derivadas(self):
        for empresa in self.empresas.values():
            if regla_contradiccion_legitimidad(empresa):
                empresa.contradiccion_legitimidad = True

    def _calcular_alertas_locales(self):
        for empresa in self.empresas.values():
            nivel, flags = calcular_alerta_empresa(empresa)
            empresa.alerta_general = nivel
            empresa.flags = flags

        for persona in self.personas.values():
            nivel, flags = calcular_alerta_persona(persona)
            persona.alerta_general = nivel
            persona.flags = flags

        for gasolinera in self.gasolineras.values():
            nivel, flags = calcular_alerta_gasolinera(gasolinera)
            gasolinera.alerta_general = nivel
            gasolinera.flags = flags

    def _propagar(self):
        """
        Propaga alertas entre nodos conectados.
        La señal se DEGRADA un nivel al cruzar una arista.
        Ej: ALTA en empresa → hereda ALTA, pero si el destino solo tiene esa flag
            y 1 alta sola = alerta MEDIA en el destino (regla de combinación).
        """
        for (tipo_origen, nombre_origen), destinos in self.relaciones.items():
            nodo_origen = self._get_nodo(tipo_origen, nombre_origen)
            if nodo_origen is None:
                continue

            nivel_origen = nodo_origen.alerta_general
            if nivel_origen == AlertLevel.NONE:
                continue

            for tipo_destino, nombre_destino, tipo_relacion in destinos:
                self._aplicar_propagacion(
                    nivel_origen, tipo_destino, nombre_destino, tipo_relacion
                )

    def _aplicar_propagacion(self, nivel_origen: str, tipo_destino: str,
                              nombre_destino: str, tipo_relacion: str):
        nodo = self._get_nodo(tipo_destino, nombre_destino)
        if nodo is None:
            return

        # La señal que llega es el nivel del nodo origen (sin degradar aquí;
        # la degradación ocurre implícitamente porque el nodo destino calcula
        # su alerta_general con sus propias reglas de combinación).
        nivel_heredado = nivel_origen

        if tipo_destino == "empresa":
            # Una empresa hereda el nivel de su socio (si es más alto que el actual)
            if AlertLevel.ORDER.get(nivel_heredado, 0) > AlertLevel.ORDER.get(nodo.socio_senalado_nivel, 0):
                nodo.socio_senalado = True
                nodo.socio_senalado_nivel = nivel_heredado

        elif tipo_destino == "persona":
            # Una persona hereda el nivel de la empresa dudosa
            if AlertLevel.ORDER.get(nivel_heredado, 0) > AlertLevel.ORDER.get(nodo.empresa_dudosa_nivel, 0):
                nodo.es_socio_de_empresa_dudosa = True
                nodo.empresa_dudosa_nivel = nivel_heredado

        elif tipo_destino == "gasolinera":
            if AlertLevel.ORDER.get(nivel_heredado, 0) > AlertLevel.ORDER.get(nodo.socios_abanderados_nivel, 0):
                nodo.socios_abanderados = True
                nodo.socios_abanderados_nivel = nivel_heredado

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------

    def _get_nodo(self, tipo: str, nombre: str):
        if tipo == "empresa":
            return self.empresas.get(nombre)
        if tipo == "persona":
            return self.personas.get(nombre)
        if tipo == "gasolinera":
            return self.gasolineras.get(nombre)
        return None

    def _snapshot(self) -> dict:
        snap = {}
        for nombre, e in self.empresas.items():
            snap[("empresa", nombre)] = (e.alerta_general, e.contradiccion_legitimidad,
                                          e.socio_senalado_nivel)
        for nombre, p in self.personas.items():
            snap[("persona", nombre)] = (p.alerta_general, p.empresa_dudosa_nivel)
        for nombre, g in self.gasolineras.items():
            snap[("gasolinera", nombre)] = (g.alerta_general, g.socios_abanderados_nivel)
        return snap

    def _estado_final(self) -> dict:
        resultado = {}
        for nombre, e in self.empresas.items():
            resultado[("empresa", nombre)] = {
                "tipo": "empresa",
                "nombre": nombre,
                "alerta_general": e.alerta_general,
                "flags": e.flags,
                "monto_compranet": e.monto_compranet,
                "contratos_compranet": e.contratos_compranet,
            }
        for nombre, p in self.personas.items():
            resultado[("persona", nombre)] = {
                "tipo": "persona",
                "nombre": nombre,
                "alerta_general": p.alerta_general,
                "flags": p.flags,
            }
        for nombre, g in self.gasolineras.items():
            resultado[("gasolinera", nombre)] = {
                "tipo": "gasolinera",
                "nombre": nombre,
                "alerta_general": g.alerta_general,
                "flags": g.flags,
            }
        return resultado
