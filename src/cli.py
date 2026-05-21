"""
CLI para el detector de indicadores de corrupción — Huachicol Fiscal México.

Comandos disponibles:
  add empresa  <nombre> [flags...]
  add persona  <nombre> [flags...]
  add gas      <nombre> [flags...]
  relate       <tipo_origen> <nombre_origen> <tipo_destino> <nombre_destino> <tipo_relacion>
  lookup       <nombre_empresa>   Busca en CompraNet y activa flags automáticamente
  run
  ask          <tipo> <nombre>
  list
  graph
  load         <escenario>   (1=FJAM, 2=Ecocarburante, 3=VeraOchoa)
  reset
  help
  exit
"""

import sys
import os

# Asegurar que src/ esté en el path al correr directamente
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import Empresa, Persona, Gasolinera, AlertLevel
from engine import ForwardChainingEngine
from data_loader import CompraNetLoader

try:
    import networkx as nx
    import matplotlib.pyplot as plt
    GRAPH_AVAILABLE = True
except ImportError:
    GRAPH_AVAILABLE = False


COLORES_ALERTA = {
    AlertLevel.NONE:   "\033[0m",
    AlertLevel.LOW:    "\033[93m",
    AlertLevel.MEDIUM: "\033[33m",
    AlertLevel.HIGH:   "\033[91m",
}
RESET = "\033[0m"
USE_COLOR = sys.stdout.isatty()


def color(nivel: str, texto: str) -> str:
    if not USE_COLOR:
        return texto
    return f"{COLORES_ALERTA.get(nivel, '')}{texto}{RESET}"


def imprimir_resultado(info: dict):
    nivel = info["alerta_general"]
    print(f"\n  [{info['tipo'].upper()}] {info['nombre']}")
    print(f"  Alerta general: {color(nivel, nivel.upper())}")
    if info["flags"]:
        print("  Flags activas:")
        for flag_nombre, flag_nivel in info["flags"]:
            print(f"    - {flag_nombre}: {color(flag_nivel, flag_nivel)}")
    else:
        print("  Flags activas: ninguna")
    if info["tipo"] == "empresa" and info.get("monto_compranet", 0) > 0:
        print(f"  CompraNet: {info['contratos_compranet']} contratos — ${info['monto_compranet']:,.0f} MXN")
    print()


def crear_empresa_desde_args(nombre: str, args: list[str]) -> Empresa:
    e = Empresa(nombre=nombre)
    flags_set = set(args)
    e.socio_senalado                       = "socio_senalado" in flags_set
    e.consiguio_permiso_express            = "consiguio_permiso_express" in flags_set
    e.tiene_discrepancias_en_importaciones = "tiene_discrepancias_en_importaciones" in flags_set
    e.tiene_discrepancias_en_ganancias     = "tiene_discrepancias_en_ganancias" in flags_set
    e.ganancias_desproporcionadas          = "ganancias_desproporcionadas" in flags_set
    e.empresa_nueva                        = "empresa_nueva" in flags_set
    e.tiene_contratos_gubernamentales      = "tiene_contratos_gubernamentales" in flags_set
    return e


def crear_persona_desde_args(nombre: str, args: list[str]) -> Persona:
    p = Persona(nombre=nombre)
    flags_set = set(args)
    p.es_socio_de_empresa_dudosa      = "es_socio_de_empresa_dudosa" in flags_set
    p.tiene_familiar_o_socio_en_poder = "tiene_familiar_o_socio_en_poder" in flags_set
    p.apoyo_campana_politica          = "apoyo_campana_politica" in flags_set
    p.tiene_senalamientos             = "tiene_senalamientos" in flags_set
    p.enriquecimiento_dudoso          = "enriquecimiento_dudoso" in flags_set
    p.es_funcionario                  = "es_funcionario" in flags_set
    p.multiples_empresas_recientes    = "multiples_empresas_recientes" in flags_set
    return p


def crear_gasolinera_desde_args(nombre: str, args: list[str]) -> Gasolinera:
    g = Gasolinera(nombre=nombre)
    flags_set = set(args)
    g.licitacion_cercana_al_fraude = "licitacion_cercana_al_fraude" in flags_set
    g.ganancias_exceden_margen     = "ganancias_exceden_margen" in flags_set
    g.socios_abanderados           = "socios_abanderados" in flags_set
    return g


def mostrar_grafo(engine: ForwardChainingEngine):
    if not GRAPH_AVAILABLE:
        print("  networkx y matplotlib no están instalados. Ejecuta: pip install networkx matplotlib")
        return

    G = nx.DiGraph()
    color_map = []
    node_labels = {}

    nivel_a_color = {
        AlertLevel.NONE:   "#aaaaaa",
        AlertLevel.LOW:    "#ffdd57",
        AlertLevel.MEDIUM: "#ff9f43",
        AlertLevel.HIGH:   "#ee5253",
    }

    for nombre, e in engine.empresas.items():
        nid = f"E:{nombre}"
        G.add_node(nid)
        color_map.append(nivel_a_color.get(e.alerta_general, "#aaaaaa"))
        node_labels[nid] = f"Emp\n{nombre}\n{e.alerta_general}"

    for nombre, p in engine.personas.items():
        nid = f"P:{nombre}"
        G.add_node(nid)
        color_map.append(nivel_a_color.get(p.alerta_general, "#aaaaaa"))
        node_labels[nid] = f"Per\n{nombre}\n{p.alerta_general}"

    for nombre, g in engine.gasolineras.items():
        nid = f"G:{nombre}"
        G.add_node(nid)
        color_map.append(nivel_a_color.get(g.alerta_general, "#aaaaaa"))
        node_labels[nid] = f"Gas\n{nombre}\n{g.alerta_general}"

    prefijo = {"empresa": "E", "persona": "P", "gasolinera": "G"}
    for (tipo_o, nom_o), destinos in engine.relaciones.items():
        src = f"{prefijo[tipo_o]}:{nom_o}"
        for tipo_d, nom_d, rel in destinos:
            dst = f"{prefijo[tipo_d]}:{nom_d}"
            G.add_edge(src, dst, label=rel)

    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, seed=42)
    nx.draw_networkx_nodes(G, pos, node_color=color_map, node_size=2000)
    nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=7)
    nx.draw_networkx_edges(G, pos, arrows=True, arrowsize=20)
    edge_labels = nx.get_edge_attributes(G, "label")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=6)
    plt.title("Red de actores — Detector de Huachicol Fiscal")
    plt.axis("off")
    plt.tight_layout()
    plt.savefig("visualizations/grafo.png", dpi=150)
    print("  Grafo guardado en visualizations/grafo.png")
    plt.show()


def cargar_escenario(engine: ForwardChainingEngine, numero: str, loader: CompraNetLoader):
    engine.__init__()
    scenarios_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scenarios")
    mapa = {"1": "scenario_1_fjam", "2": "scenario_2_ecocarburante", "3": "scenario_3_vera_ochoa"}
    if numero not in mapa:
        print("  Escenario no válido. Usa 1, 2 o 3.")
        return
    sys.path.insert(0, os.path.abspath(scenarios_dir))
    mod = __import__(mapa[numero])
    mod.cargar(engine)
    descubrimientos = loader.enriquecer_engine(engine, verbose=False)
    if descubrimientos:
        for d in descubrimientos:
            print(f"  [CompraNet] {d['empresa']}: {d['contratos']} contratos — ${d['monto']:,.0f} MXN")
    print(f"  Escenario {numero} cargado.")


def mostrar_ayuda():
    print("""
  Comandos disponibles:
    add empresa  <nombre> [flag1 flag2 ...]
    add persona  <nombre> [flag1 flag2 ...]
    add gas      <nombre> [flag1 flag2 ...]

    relate <tipo_orig> <nombre_orig> <tipo_dest> <nombre_dest> <tipo_relacion>
      Tipos: empresa | persona | gasolinera
      Relaciones: socio_de | familiar_de | otorgo_licencia_a | titular_de

    lookup <nombre>       Buscar empresa en CompraNet y activar flags
    run                   Ejecutar inferencia (Forward Chaining)
    ask  <tipo> <nombre>  Consultar alerta de un actor
    list                  Listar todos los actores y sus alertas
    graph                 Visualizar grafo de la red
    load <1|2|3>          Cargar escenario predefinido
    reset                 Limpiar todos los actores y relaciones
    help                  Mostrar esta ayuda
    exit                  Salir

  Flags de Empresa:
    socio_senalado | consiguio_permiso_express | tiene_discrepancias_en_importaciones
    tiene_discrepancias_en_ganancias | ganancias_desproporcionadas | empresa_nueva
    tiene_contratos_gubernamentales

  Flags de Persona:
    es_socio_de_empresa_dudosa | tiene_familiar_o_socio_en_poder | apoyo_campana_politica
    tiene_senalamientos | enriquecimiento_dudoso | es_funcionario

  Flags de Gasolinera:
    licitacion_cercana_al_fraude | ganancias_exceden_margen | socios_abanderados
""")


def main():
    engine = ForwardChainingEngine()
    os.makedirs("visualizations", exist_ok=True)

    # Resolver ruta de data/ relativa a la ubicación del script
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    loader = CompraNetLoader(data_dir=data_dir)

    print("\n=== Detector de Indicadores de Corrupción — Huachicol Fiscal México ===")
    print("  Escribe 'help' para ver los comandos disponibles.\n")

    while True:
        try:
            linea = input("kb> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSaliendo.")
            break

        if not linea:
            continue

        partes = linea.split()
        cmd = partes[0].lower()

        if cmd == "exit":
            break

        elif cmd == "help":
            mostrar_ayuda()

        elif cmd == "reset":
            engine.__init__()
            print("  Sistema reiniciado.")

        elif cmd == "add" and len(partes) >= 3:
            tipo   = partes[1].lower()
            nombre = partes[2]
            flags  = partes[3:]
            if tipo == "empresa":
                engine.agregar_empresa(crear_empresa_desde_args(nombre, flags))
                print(f"  Empresa '{nombre}' agregada.")
            elif tipo == "persona":
                engine.agregar_persona(crear_persona_desde_args(nombre, flags))
                print(f"  Persona '{nombre}' agregada.")
            elif tipo in ("gas", "gasolinera"):
                engine.agregar_gasolinera(crear_gasolinera_desde_args(nombre, flags))
                print(f"  Gasolinera '{nombre}' agregada.")
            else:
                print(f"  Tipo desconocido: {tipo}")

        elif cmd == "relate" and len(partes) == 6:
            _, tipo_o, nom_o, tipo_d, nom_d, rel = partes
            engine.agregar_relacion(tipo_o, nom_o, tipo_d, nom_d, rel)
            print(f"  Relación '{rel}' registrada: {tipo_o}/{nom_o} → {tipo_d}/{nom_d}")

        elif cmd == "run":
            resultado = engine.run()
            print(f"\n  Forward Chaining completado. {len(resultado)} actores evaluados.")
            for info in resultado.values():
                imprimir_resultado(info)

        elif cmd == "ask" and len(partes) == 3:
            _, tipo, nombre = partes
            resultado = engine.run()
            key = (tipo, nombre)
            if key in resultado:
                imprimir_resultado(resultado[key])
            else:
                print(f"  Actor '{tipo}/{nombre}' no encontrado.")

        elif cmd == "list":
            resultado = engine.run()
            if not resultado:
                print("  No hay actores en el sistema.")
            for info in resultado.values():
                nivel = info["alerta_general"]
                monto_str = ""
                if info["tipo"] == "empresa" and info.get("monto_compranet", 0) > 0:
                    monto_str = f"  CompraNet: ${info['monto_compranet']:,.0f} MXN"
                print(f"  [{info['tipo'][0].upper()}] {info['nombre']:30s} → {color(nivel, nivel.upper())}{monto_str}")

        elif cmd == "graph":
            engine.run()
            mostrar_grafo(engine)

        elif cmd == "lookup" and len(partes) >= 2:
            nombre_busqueda = " ".join(partes[1:])
            print(f"\n  Buscando '{nombre_busqueda}' en CompraNet... (puede tardar unos segundos)")
            resultado = loader.buscar_empresa(nombre_busqueda)
            print(f"\n  {resultado.resumen()}")

            if resultado.encontrado:
                # Si la empresa ya está en el motor, aplicar flags
                empresa_obj = engine.empresas.get(nombre_busqueda)
                if empresa_obj:
                    loader.aplicar_flags(empresa_obj, resultado)
                    print(f"\n  Flags aplicadas a '{nombre_busqueda}' en el motor.")
                else:
                    print(f"\n  NOTA: '{nombre_busqueda}' no está en el motor aún.")
                    print(f"  Agrega la empresa con 'add empresa {nombre_busqueda}' para usarla.")

                if resultado.contratos:
                    print("\n  Muestra de contratos:")
                    for c in resultado.contratos[:5]:
                        titulo = str(c.get("titulo_contrato", ""))[:60]
                        tipo   = c.get("tipo_expediente", "")
                        monto  = c.get("importe", "")
                        print(f"    - {titulo}  |  {tipo}  |  ${monto}")
            print()

        elif cmd == "load" and len(partes) == 2:
            cargar_escenario(engine, partes[1], loader)

        else:
            print(f"  Comando no reconocido: '{linea}'. Escribe 'help' para ayuda.")


if __name__ == "__main__":
    main()
