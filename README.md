# Detector de Indicadores de Corrupción — Huachicol Fiscal en México

Sistema de lógica proposicional que detecta indicadores de corrupción en redes de huachicol fiscal. Usa **Forward Chaining con cláusulas de Horn** sobre una base de conocimiento (KB) de indicadores observables para propagar banderas de riesgo a través de un grafo de actores.

> **Aviso importante:** El sistema detecta indicadores anómalos, no asigna culpabilidad. Una entidad banderada puede ser cómplice, víctima de extorsión, o tener errores administrativos. El sistema identifica _dónde investigar_, no _a quién culpar_.

---

## Contexto: Causa Penal 325/2025 — Huachicol Fiscal AIFA

El caso real que motiva este sistema involucra un esquema de huachicol fiscal documentado por la FGR en la causa penal 325/2025. La red importó combustible (diesel) triangulando facturas falsas, burlando controles aduanales y operando con empresas creadas específicamente para el esquema. Entre los 14 detenidos hay empresarios, funcionarios aduanales y un vicealmirante. Las fuentes incluyen investigaciones de MCCI, reportes de Pemex ante la SEC y registros públicos del SIGER.

---

## Requisitos

```
Python 3.10+
networkx
matplotlib
```

```bash
pip install networkx matplotlib
```

---

## Cómo ejecutar

### CLI interactiva

```bash
python src/cli.py
```

### Escenarios predefinidos

```bash
python scenarios/scenario_1_fjam.py        # Consistente — Alerta Alta
python scenarios/scenario_2_ecocarburante.py  # Contradictorio — Alerta Alta
python scenarios/scenario_3_vera_ochoa.py  # Incierto — Sin Alerta
```

### Comandos CLI

```
add empresa  <nombre> [flag1 flag2 ...]
add persona  <nombre> [flag1 flag2 ...]
add gas      <nombre> [flag1 flag2 ...]

relate <tipo_orig> <nombre_orig> <tipo_dest> <nombre_dest> <tipo_relacion>
  Tipos:     empresa | persona | gasolinera
  Relaciones: socio_de | familiar_de | otorgo_licencia_a | titular_de

lookup <nombre>       Buscar empresa en CompraNet y activar flags automáticamente
run                   Ejecutar inferencia (Forward Chaining)
ask  <tipo> <nombre>  Consultar alerta de un actor específico
list                  Listar todos los actores con sus alertas y montos CompraNet
graph                 Visualizar grafo de la red (requiere networkx + matplotlib)
load <1|2|3>          Cargar escenario predefinido (incluye auto-discovery CompraNet)
reset                 Limpiar el motor
help                  Ver todos los comandos
exit                  Salir
```

---

## Arquitectura

```
Empresa de Importación <---> Persona <---> Gasolinera
         |                      |               |
    (socios)           (funcionario)        (titulares)
```

Cada actor es un nodo con propiedades booleanas. Las aristas son relaciones (`socio_de`, `familiar_de`, `otorgo_licencia_a`). Las banderas emergen de las propiedades del nodo y sus conexiones.

```
src/
  models.py       # Dataclasses: Empresa, Persona, Gasolinera
  kb.py           # Base de Conocimiento: 12 reglas Horn documentadas
  engine.py       # Motor Forward Chaining con punto fijo
  cli.py          # Interfaz de línea de comandos
  data_loader.py  # Integración con CompraNet (CSV) — auto-discovery de contratos
scenarios/
  scenario_1_fjam.py
  scenario_2_ecocarburante.py
  scenario_3_vera_ochoa.py
data/
  siger/          # PDFs del Registro Público de Comercio
  *.csv           # Expedientes CompraNet 2018–2025
```

---

## Diccionario de Variables Proposicionales

### Empresas de Importación

| Variable | Nivel | Definición |
|----------|-------|------------|
| `socio_senalado` | Hereda nivel del socio | True si la empresa tiene al menos un socio con alerta en el sistema |
| `consiguio_permiso_express` | Media | True si obtuvo licencia de importación en menos tiempo que el promedio del sector (SAT: <10 días hábiles; CRE pre-2019: <21 días; CRE post-2019: <75 días) |
| `tiene_discrepancias_en_importaciones` | Alta | True si hay diferencia material entre lo declarado y lo realmente importado o vendido |
| `tiene_discrepancias_en_ganancias` | Alta | True si las ganancias reportadas no cuadran con los volúmenes y precios declarados |
| `ganancias_desproporcionadas` | Media | True si las ganancias anuales superan significativamente el promedio del sector para empresas de antigüedad similar |
| `empresa_nueva` | Baja | True si la empresa fue incorporada hace menos de 1 año al momento de obtener su licencia |
| `tiene_contratos_gubernamentales` | No genera alerta sola | True si tiene contratos vigentes con dependencias del gobierno federal |
| `contradiccion_legitimidad` | Alta | **Derivada.** True si `tiene_contratos_gubernamentales` ∧ `tiene_discrepancias_en_importaciones` |

### Personas

| Variable | Nivel | Definición |
|----------|-------|------------|
| `es_socio_de_empresa_dudosa` | Hereda nivel de la empresa | True si es socio/accionista de una empresa con alerta en el sistema |
| `tiene_familiar_o_socio_en_poder` | Baja | True si un familiar directo o socio comercial ocupa un cargo público |
| `apoyo_campana_politica` | Baja | True si hay donaciones o apoyo público documentado a un candidato o partido |
| `tiene_senalamientos` | Alta | True si tiene señalamientos previos documentados (investigaciones, procesos penales, sanciones) |
| `enriquecimiento_dudoso` | Media | True si las declaraciones patrimoniales son inconsistentes con el nivel de ingreso |
| `es_funcionario` | Alta | True si ocupa o ocupó un cargo público (amplifica riesgo de conflicto de interés) |
| `multiples_empresas_recientes` | Media | True si la persona aparece como socio o representante en múltiples empresas constituidas recientemente — patrón asociado a testaferrismo o estructuras de evasión. En este proyecto: Estefanía Garza (Belure 2020 + Intanza 2022 + TDA 2022 + GarzaPalomares 2016), Ramiro Rocha (Belure 2018 + Intanza 2023), Ricardo Ayón (Intanza 2023 + TDA 2024) |

### Gasolineras

| Variable | Nivel | Definición |
|----------|-------|------------|
| `licitacion_cercana_al_fraude` | Baja | True si la fecha del permiso de expendio coincide con el periodo del esquema |
| `ganancias_exceden_margen` | Media | True si el margen excede $2/litro para gasolina regular o $28.28/litro para diésel (tope vigente) |
| `socios_abanderados` | Hereda nivel | True si algún socio/titular ya tiene alerta en el sistema |

---

## Base de Conocimiento — 12 Reglas Horn

Todas las reglas están implementadas como funciones puras en `src/kb.py`.

---

### Regla 1 — Contradicción de Legitimidad (regla derivada)

**Lenguaje natural:** Una empresa con contratos gubernamentales Y discrepancias en importaciones activa una bandera especial de alta gravedad, porque implica que pasó los filtros del gobierno pero sigue en irregularidades.

**Lógica formal:**
```
tiene_contratos_gubernamentales(X) ∧ tiene_discrepancias_en_importaciones(X)
  → contradiccion_legitimidad(X)
```

**Justificación:** Es más grave que una empresa desconocida con las mismas discrepancias: indica posible facilitación interna desde el gobierno.

---

### Reglas 2–5 — Alerta General de Empresa

**Lenguaje natural:** La alerta general se calcula combinando las banderas activas de la empresa.

**Lógica formal:**
```
empresa_nueva(X) ∧ ¬(otras_banderas)(X)              → sin_alerta(X)
solo_una_media(X)                                     → alerta_baja(X)
solo_una_alta(X)                                      → alerta_media(X)
2_bajas(X)                                            → alerta_baja(X)
cualquier_combinacion_2mas_no_solo_bajas(X)           → alerta_media(X)
alta(X) ∧ media(X)                                    → alerta_alta(X)
4_o_mas_banderas(X)                                   → alerta_alta(X)
```

---

### Reglas 6–9 — Alerta General de Persona

**Lógica formal:**
```
baja(X) ∧ baja(X)    → alerta_baja(X)
baja(X) ∧ media(X)   → alerta_media(X)
alta(X) ∧ baja(X)    → alerta_media(X)
alta(X) ∧ media(X)   → alerta_alta(X)
solo_una_alta(X)      → alerta_media(X)
solo_una_media(X)     → alerta_baja(X)
```

---

### Reglas 10–12 — Alerta General de Gasolinera

**Lógica formal:**
```
alta(X)              → alerta_alta(X)
media(X) ∧ media(X)  → alerta_media(X)
baja(X) ∧ baja(X)    → alerta_baja(X)
```

---

### Regla de Propagación — Infección entre Nodos

**Lenguaje natural:** La alerta general de un nodo se propaga como variable heredada al nodo conectado. La señal se degrada naturalmente con la distancia en el grafo.

**Lógica formal:**
```
alerta_alta(X) ∧ socio_de(X, Y)   → es_socio_de_empresa_dudosa(Y) ∧ hereda_alta(Y)
hereda_alta(Y) ∧ ¬otras_banderas(Y) → alerta_media(Y)   -- degradación natural
alerta_media(Y) ∧ socio_de(Y, Z)  → socio_senalado(Z) ∧ hereda_media(Z)
hereda_media(Z) ∧ ¬otras_banderas(Z) → alerta_baja(Z)
```

**Justificación:** La degradación es intencional — evita que una sola alerta alta incendie toda la red. Una empresa con un socio sospechoso merece revisión, no una acusación.

---

## Escenario 1 — Francisco Javier Antonio Martínez (Consistente, Alerta Alta)

**Contexto:** Director de Administración y Finanzas de ASIPONA Tampico. Socio de los dueños de Intanza a través de Comercializadora Belure (Nuevo León). Acumuló 18 vehículos de lujo en 2 años. Detenido por la FGR.

**Hallazgos SIGER — Comercializadora Belure S.A. de C.V. (FME: N-2018055928, RFC: CBS180622QI7):**
- Registrada en Monterrey, Nuevo León
- **Agosto 2018:** Ramiro Rocha Alvarado nombrado Administrador Único (`belure-as-2018-rocha-admin.pdf`)
- **Julio 2020:** Estefanía Garza Palomares nombrada Administrador Única; Rocha permanece como Apoderado General (`belure-as-2020-estefania-admin.pdf`)
- **Conclusión:** Rocha y Estefanía estaban vinculados en Belure **antes** de fundar Intanza (abril 2022) — la red no fue improvisada

**Hallazgos SIGER — Intanza S.A. de C.V. (int-const.pdf, int-rev-fun.pdf):**
- Constituida el **27/04/2022** en Monterrey, NL — empresa nueva al momento del esquema
- Objeto social: productos eléctricos y bebidas alcohólicas — **sin mención de combustibles**, a pesar de operar como importadora de diesel
- Fundadores: Hernán Guillermo Fernández Morán (50%) y **Estefanía Garza Palomares** (50%) — ya era Admin de Belure
- Compradores (mayo-jul 2023): **Ricardo Ayón Rodríguez** (RFC: AORR941110PZA, 98%) y **Ramiro Rocha Alvarado** (RFC: ROAR730115IE0, 2%) — ya era Apoderado de Belure

**Hallazgos SIGER — Importaciones TDA S.A. de C.V. (FME: N-2022038889) — `tda-const-2022.pdf`, `tda-as-2024-ayon-admin.pdf`:**
- Constituida el **18/05/2022** — exactamente un mes después de Intanza, por los **mismos fundadores**: Hernán Fernández Morán y Estefanía Garza Palomares
- Mismo notario que Intanza: Edgar Gerardo Regis García No. 45, Monterrey, NL
- Objeto social: vinos y bebidas alcohólicas — sin mención de combustibles
- **Abril 2024:** Ricardo Ayón Rodríguez nombrado Administrador Único en sustitución de Hernán — patrón idéntico al de Intanza
- Estefanía permanece como Apoderada Legal — único nombre que persiste en ambas empresas durante y después del esquema

**Hallazgos SIGER — Grupo GarzaPalomares Comercialización y Servicios S.A. de C.V. (FME: N-2018033156) — `garzapalomares-const-2016.pdf`:**
- Constituida el **28/10/2016** — Estefanía tenía empresa de gasolinas **desde antes del esquema**
- Estefanía Garza Palomares: 50%, Administrador Única desde la constitución
- Objeto social incluye explícitamente: **"compra venta de gasolinas, sus derivados"**
- **Marzo 2022:** Poder general otorgado a Miguel Ángel Márquez Pozadas (RFC: MAPM7806161V6) — mismo periodo de operación de Intanza en AIFA

**Red completa documentada:**
```
Belure (NL) ←── Rocha Alvarado (Admin Único 2018, Apoderado 2020)
             ←── Estefanía Garza (Admin Única 2020)
             ←── FJAM (vínculo FGR/periodístico)

Intanza (NL) ←── Estefanía Garza (co-fundadora abr 2022)   ← misma persona
              ←── Rocha Alvarado (compra 2% + Admin Único 2023)
              ←── Ricardo Ayón (compra 98%)

Importaciones TDA ←── Estefanía Garza (co-fundadora may 2022)  ← misma persona, 1 mes después
                   ←── Ayón Rodríguez (Admin Único abr 2024)   ← mismo patrón

GarzaPalomares ←── Estefanía Garza (50%, fundadora 2016, objeto social: gasolinas)
```

**Resultado del motor:**

```
[EMPRESA] Intanza S.A. de C.V.
  Alerta general: ALTA
  Flags: socio_senalado (ALTA), tiene_discrepancias_en_importaciones (ALTA), empresa_nueva (BAJA)

[EMPRESA] Importaciones TDA S.A. de C.V.
  Alerta general: MEDIA    ← empresa_nueva (BAJA) + socio_senalado heredado Ayón (ALTA)

[EMPRESA] Comercializadora Belure S.A. de C.V.
  Alerta general: MEDIA    ← propagación desde Rocha y Estefanía (ALTA)

[EMPRESA] Grupo GarzaPalomares Comercialización y Servicios S.A. de C.V.
  Alerta general: MEDIA    ← hereda de Estefanía (ALTA), degradación natural

[PERSONA] Estefanía Garza Palomares
  Alerta general: ALTA     ← es_socio_de_empresa_dudosa (ALTA) + multiples_empresas_recientes (MEDIA)
  Aparece en: Belure (2020) + Intanza (2022) + TDA (2022) + GarzaPalomares (2016)

[PERSONA] Hernán Guillermo Fernández Morán
  Alerta general: MEDIA    ← es_socio_de_empresa_dudosa (ALTA heredada de Intanza/TDA)

[PERSONA] Ricardo Ayón Rodríguez
  Alerta general: ALTA
  Flags: es_socio_de_empresa_dudosa (ALTA), tiene_senalamientos (ALTA), multiples_empresas_recientes (MEDIA)

[PERSONA] Ramiro Rocha Alvarado
  Alerta general: ALTA
  Flags: es_socio_de_empresa_dudosa (ALTA), tiene_senalamientos (ALTA), multiples_empresas_recientes (MEDIA)

[PERSONA] Francisco Javier Antonio Martínez
  Alerta general: ALTA
  Flags: es_socio_de_empresa_dudosa (ALTA), tiene_senalamientos (ALTA),
         enriquecimiento_dudoso (MEDIA), es_funcionario (ALTA)
```

**Por qué es consistente:** Todas las banderas apuntan en la misma dirección. SIGER confirma la red preexistente (Belure, 2018–2020) que conecta a los mismos actores antes del esquema, eliminando la posibilidad de coincidencia. La existencia de GarzaPalomares desde 2016 con objeto social de gasolinas demuestra que Estefanía no era una intermediaria improvisada.

---

## Escenario 2 — Ecocarburante S.A. de C.V. (Contradictorio, Alerta Alta)

**Contexto:** Proveedora de diesel a la SEDENA durante la construcción del AIFA (500M+ pesos en contratos oficiales). Vinculada a la causa penal 325/2025 por huachicol fiscal.

**Hallazgos SIGER — Ecocarburante (ec-const.pdf, ec-aumento-capital-fijo.pdf, ec-fusion-inc.pdf, ec-nombramiento-*.pdf):**
- Constituida el **14/09/2017** en Guadalajara, Jalisco
- Capital social: $100,000 (2017) → $10,000,000 (2020) → **$1,075,783,000** (2022 post-fusión) — crecimiento de **10,757x en 5 años**
- En 2022 absorbe a **Royal Park Ocotlan S.A. de C.V.** (empresa inmobiliaria) — fusión atípica para una empresa de combustibles
- Accionistas al momento del escándalo (2022–2023): Edgar Marín Meza Moreno 49%, Gerardo Hernández Chávez 25%, Eric Daniel Zamora Delgadillo 25%
- En mayo 2023, Marín y Zamora salen; entran Jesús Arturo Cárdenas Esparza (41%) y Shahab Afsharian Campuzano (33%)

**Hallazgos SIGER — Cadena societaria absorbida (rpo-const.pdf, robro-const.pdf):**

Royal Park Ocotlan (FME: 82678, constituida 20/05/2014) — empresa inmobiliaria con objeto social de fraccionamientos, sin relación con combustibles:
- Juan Alejandro Rodríguez Luna — 25%, Admin Único
- José Martín González Márquez — 25%, Comisario
- **ROBRO S.A. de C.V.** — 50%

ROBRO S.A. de C.V. (FME: 82686, constituida 14/05/2014):
- Juan Alejandro Rodríguez Luna — 50%, Admin Único
- **Enrique Robledo Sahagún** — 50% — domicilio Calle Centenario 50, Col. Mascota, Ocotlán, Jalisco → **ex-alcalde de Ocotlán**

Nota: ROBRO y Royal Park fueron constituidas el mismo día (14–20 mayo 2014) por el mismo notario (Carlos Gutiérrez Aceves No. 115039122, Guadalajara).

**Descubrimiento automático vía CompraNet:**
```
[CompraNet] ROBRO S.A. de C.V.
  → 4 contratos, $664,560 MXN
  → Adjudicación directa detectada
  → tiene_contratos_gubernamentales = True  ← activado automáticamente
```

**Cadena societaria completa hasta el ex-alcalde:**
```
Ecocarburante ← fusión ← Royal Park Ocotlan ← 50% ROBRO ← 50% Enrique Robledo Sahagún
                                                                    (ex-alcalde Ocotlán, Jalisco)
ROBRO ← $664,560 MXN en contratos gubernamentales (CompraNet)
```

**Resultado del motor:**

```
[EMPRESA] Ecocarburante S.A. de C.V.
  Alerta general: ALTA
  Flags: tiene_discrepancias_en_importaciones (ALTA), ganancias_desproporcionadas (MEDIA),
         contradiccion_legitimidad (ALTA)  ← derivada automáticamente

[EMPRESA] Royal Park Ocotlan S.A. de C.V.
  Alerta general: MEDIA    ← socio_senalado hereda ALTA de Ecocarburante, degradación

[EMPRESA] ROBRO S.A. de C.V.
  Alerta general: BAJA     ← socio_senalado hereda MEDIA de Royal Park, segunda degradación
  CompraNet: 4 contratos — $664,560 MXN  ← descubierto automáticamente

[PERSONA] Gerardo Hernández Chávez   → MEDIA  (heredó ALTA de Eco, degradación)
[PERSONA] Jesús Arturo Cárdenas Esparza → MEDIA
[PERSONA] Shahab Afsharian Campuzano    → MEDIA

[PERSONA] Juan Alejandro Rodríguez Luna → BAJA  (hereda de ROBRO/Royal Park)
[PERSONA] José Martín González Márquez  → BAJA  (hereda de Royal Park)

[PERSONA] Enrique Robledo Sahagún
  Alerta general: MEDIA
  Flags: es_socio_de_empresa_dudosa (BAJA heredada de ROBRO) + es_funcionario (ALTA)
```

**Por qué es contradictorio:** La empresa fue validada por el gobierno (contratos con SEDENA/AIFA) pero simultáneamente participa en un esquema ilegal. La `contradiccion_legitimidad` se deriva automáticamente — es inferencia, no un hecho observable. Esto revela un fallo en los procesos de verificación gubernamental y posible facilitación interna. Que la cadena llegue hasta un ex-alcalde (Robledo Sahagún) a través de dos capas de empresas inmobiliarias absorbidas añade complejidad estructural al esquema.

---

## Escenario 3 — Saúl Vera Ochoa / Tampico Terminal Marítima (Incierto, Sin Alerta)

**Contexto:** Apoderado irrevocable de Tampico Terminal Marítima S.A. de C.V. (TTM), concesionaria del muelle fiscal de Tampico. Apoyó públicamente a Adán Augusto López. No aparece como accionista — controla TTM operativamente via poder notarial.

**Red familiar y empresarial Vera Ochoa (documentada en SIGER):**

**CONSTRUCTORA VEASA S.A. de C.V.** — accionista mayoritaria de TTM (46%, Villahermosa, Tabasco):
- Controlada por **Patricia Romana Vera Ochoa** (RFC: VEOP581026) — hermana de Saúl (mismo apellido compuesto, confirmado en 3 documentos SIGER)
- Firma poderes en nombre de VEASA en 2018, 2019 y 2022

**VOS GRUPO CONSTRUCTOR S.A. de C.V.** (FME: 5533, Villahermosa):
- Patricia Vera Ochoa es apoderada desde al menos **agosto 2012** (`vos-poder-patricia-2012.pdf`)
- Asamblea dic 2019: aumento de capital $28.8M — accionistas María Teresa Pérez de la Cruz y Encarnación Cruz Hernández
- Misma notaría que TTM: José Andrés Gallegos Torres No. 1, Cárdenas, Tabasco

**TAMPICO PORT SOLUTIONS S.A. de C.V.** (FME: N-2022034576):
- Constituida **18/03/2022** en Villahermosa — dos meses antes que el buque Challenge Procyon atracara en Tampico
- Objeto social: asesoría aduanal, navieras, importación/exportación, transporte portuario, supervisión y descarga de buques
- **Manuel Alexis Vera Ramírez** aparece como accionista (`tps-const-2022.pdf`)
- Misma notaría que TTM y VOS: José Andrés Gallegos Torres No. 1, Cárdenas, Tabasco

**Manuel Alexis Vera Ramírez** — nodo de enlace de la red:
- Comisario de TTM (nombrado asamblea 2023)
- Apoderado de CONSTRUCTORA VEASA (poder mar 2022)
- Accionista de TAMPICO PORT SOLUTIONS

**Descubrimiento automático vía CompraNet:**
```
[CompraNet] Constructora VEASA S.A. de C.V.
  → 9 contratos de obra pública, $66,241,776 MXN (2014–2018, Tabasco)
  → Adjudicación directa detectada
  → tiene_contratos_gubernamentales = True  ← activado automáticamente

[CompraNet] VOS Grupo Constructor S.A. de C.V.
  → 4 contratos, $25,614,667 MXN
  → Adjudicación directa detectada
  → tiene_contratos_gubernamentales = True  ← activado automáticamente

Total detectado en la red: $91,856,443 MXN en contratos gubernamentales
```

**Estructura de control real de TTM:**
```
Patricia (hermana) → CONSTRUCTORA VEASA (46%) → TTM ←── Saúl Vera Ochoa (apoderado irrevocable)
         ↓                                        TTM ←── Manuel Alexis (comisario)
  VOS Grupo Constructor                           Manuel Alexis → Tampico Port Solutions
  ($25.6M CompraNet)
  CompraNet VEASA: $66.2M
```

**Resultado del motor:**

```
[EMPRESA] Constructora VEASA S.A. de C.V.
  Alerta general: SIN_ALERTA
  CompraNet: 9 contratos — $66,241,776 MXN  [solo tiene_contratos_gubernamentales, no genera alerta]

[EMPRESA] VOS Grupo Constructor S.A. de C.V.
  Alerta general: SIN_ALERTA
  CompraNet: 4 contratos — $25,614,667 MXN

[EMPRESA] Tampico Port Solutions S.A. de C.V.
  Alerta general: SIN_ALERTA
  Flags: empresa_nueva (BAJA)  [1 baja sola = sin alerta]

[EMPRESA] Tampico Terminal Marítima S.A. de C.V.
  Alerta general: SIN_ALERTA
  Flags: empresa_nueva (BAJA)

[PERSONA] Patricia Romana Vera Ochoa   → SIN_ALERTA
[PERSONA] Manuel Alexis Vera Ramírez   → SIN_ALERTA

[PERSONA] Saúl Vera Ochoa
  Alerta general: SIN_ALERTA
  Flags: apoyo_campana_politica (BAJA)  [1 baja sola = sin alerta]
```

**Por qué es incierto — y qué falta para escalar:**

El sistema detecta $91.8M en contratos gubernamentales con adjudicación directa y aun así no genera alerta — porque sin discrepancias documentadas, no hay base para acusar. Este es el resultado correcto:

- `tiene_contratos_gubernamentales` sola no genera alerta (diseño intencional)
- No hay `tiene_discrepancias_en_importaciones` documentadas para TTM, VEASA o VOS

Si se confirmara que TTM recibió o almacenó combustible de Intanza, se activaría `tiene_discrepancias_en_importaciones` en TTM → `contradiccion_legitimidad` se derivaría automáticamente (TTM ya tiene `tiene_contratos_gubernamentales = True`) → alerta **ALTA** instantánea.

**El sistema identifica dónde investigar, no a quién culpar.**

---

## Fuentes de Datos

### SIGER — Registro Público de Comercio

Consultas manuales en `rpc.economia.gob.mx`. Los documentos descargados se encuentran en `data/siger/`.

**Cadena Ecocarburante (`data/siger/cadena-ecocarburante/`):**

| Archivo | Empresa | Contenido |
|---------|---------|-----------|
| `ec-const.pdf` | Ecocarburante | Constitución 14/09/2017, fundadores originales |
| `ec-aumento-capital-fijo.pdf` | Ecocarburante | Cambio de accionistas y aumento de capital (mar 2020) |
| `ec-fusion-inc.pdf` | Ecocarburante | Fusión por absorción de Royal Park Ocotlan (nov 2022) |
| `ec-nombramiento-funcionarios-abril2020.pdf` | Ecocarburante | Nuevo administrador: Eric Daniel Zamora Delgadillo |
| `ec-nombramiento-funcionarios-mayo2023.pdf` | Ecocarburante | Nuevos accionistas: Cárdenas Esparza + Afsharian Campuzano |
| `rpo-const.pdf` | Royal Park Ocotlan | Constitución FME 82678 — empresa inmobiliaria fusionada |
| `robro-const.pdf` | ROBRO S.A. de C.V. | Constitución FME 82686 — 50% accionista de Royal Park; Robledo Sahagún (ex-alcalde) aparece |

**Cadena Intanza (`data/siger/cadena-intanza/`):**

| Archivo | Empresa | Contenido |
|---------|---------|-----------|
| `int-const.pdf` | Intanza | Constitución 27/04/2022 — objeto social sin mención de combustibles |
| `int-rev-fun.pdf` | Intanza | Venta a Ricardo Ayón y Ramiro Rocha (mayo-julio 2023) |
| `tda-const-2022.pdf` | Importaciones TDA | Constitución 18/05/2022 — mismos fundadores que Intanza |
| `tda-as-2024-ayon-admin.pdf` | Importaciones TDA | Asamblea abr 2024 — Ayón sustituye a Hernán como Admin Único |
| `tda-as-2024-ayon-admin-b.pdf` | Importaciones TDA | Mismo instrumento (página 2) |
| `tda-as-2024-ayon-admin-c.pdf` | Importaciones TDA | Mismo instrumento (página 3) |
| `garzapalomares-const-2016.pdf` | Grupo GarzaPalomares | Constitución 28/10/2016 — objeto social incluye gasolinas; Estefanía como Admin Única |
| `garzapalomares-poder-marquez-2022.pdf` | Grupo GarzaPalomares | Poder a Márquez Pozadas, mar 2022 |
| `garzapalomares-poder-marquez-2022-b.pdf` | Grupo GarzaPalomares | Mismo instrumento (página 2) |

**Cadena Belure (`data/siger/cadena-belure/`):**

| Archivo | Empresa | Contenido |
|---------|---------|-----------|
| `belure-as-2018-rocha-admin.pdf` | Comercializadora Belure | Asamblea ago 2018 — Ramiro Rocha Alvarado nombrado Administrador Único |
| `belure-as-2018-transmision.pdf` | Comercializadora Belure | Transmisión de acciones ago 2018 (segunda inscripción) |
| `belure-as-2020-estefania-admin.pdf` | Comercializadora Belure | Asamblea jul 2020 — Estefanía Garza Palomares nombrada Admin Única; Rocha permanece como Apoderado |

**Cadena TTM (`data/siger/cadena-ttm/`):**

| Archivo | Empresa | Contenido |
|---------|---------|-----------|
| `ttm-const.pdf` | Tampico Terminal Marítima | Constitución 04/06/2020, muelle fiscal Tampico |
| `ttm-as.pdf` | Tampico Terminal Marítima | Asamblea mayo 2023 — Tramitadora del Pacífico sale, Manuel Alexis Vera Ramírez entra como comisario |
| `ttm-op.pdf` | Tampico Terminal Marítima | Poder irrevocable 27/03/2023 → Saúl Vera Ochoa |
| `cv-op19042018.pdf` | Constructora VEASA | Poder abr 2018 — firmado por Patricia Romana Vera Ochoa |
| `cv-poder-manuel-alexis-2022.pdf` | Constructora VEASA | Poder mar 2022 → Manuel Alexis Vera Ramírez |
| `cv-poder-patricia-2019.pdf` | Constructora VEASA | Poder 2019 — firmado por Patricia Romana Vera Ochoa |
| `tps-const-2022.pdf` | Tampico Port Solutions | Constitución 18/03/2022 — Manuel Alexis Vera Ramírez como accionista |
| `vos-poder-patricia-2012.pdf` | VOS Grupo Constructor | Poder ago 2012 → Patricia Romana Vera Ochoa |
| `vos-poder-2018.pdf` | VOS Grupo Constructor | Poder ene 2018 |
| `vos-as-2019-capital.pdf` | VOS Grupo Constructor | Asamblea dic 2019 — aumento de capital $28.8M |
| `vertice-const-2019.pdf` | Estudios Estratégicos El Vértice | Constitución may 2019, misma notaría |
| `ryc-const-2014.pdf` | Multiservicios RYC | Constitución nov 2014, Villahermosa |
| `ryc-poder-2018.pdf` | Multiservicios RYC | Poder 2018 |
| `ryc-poder-2019.pdf` | Multiservicios RYC | Poder 2019 |
| `ryc-poder-2019-b.pdf` | Multiservicios RYC | Poder 2019 (parte 2) |
| `vaf-const-1997.pdf` | VAF Construcciones | Constitución 1997, Villahermosa — empresa de obra civil |
| `vaf-const-1997-b.pdf` | VAF Construcciones | Constitución (duplicado) |

### CompraNet (datos abiertos)

CSVs de expedientes 2018–2025 en `data/`. El sistema cruza automáticamente todos los actores del motor contra CompraNet al cargar un escenario (`enriquecer_engine`). Activaciones detectadas:

| Empresa | Contratos | Monto MXN | Tipo |
|---------|-----------|-----------|------|
| Constructora VEASA S.A. de C.V. | 9 | $66,241,776 | Obra pública Tabasco, adjudicación directa |
| VOS Grupo Constructor S.A. de C.V. | 4 | $25,614,667 | Adjudicación directa |
| ROBRO S.A. de C.V. | 4 | $664,560 | Adjudicación directa |

Búsqueda manual desde la CLI:
```bash
kb> lookup Ecocarburante
```

### Precios CRE

XML de precios diarios (Acuerdo A/041/2018). Alimenta `ganancias_exceden_margen` como contexto de referencia. Umbrales: tope diesel $28.28/litro, margen máximo gasolina regular $2/litro.

---

## Limitaciones

1. **El sistema no distingue entre corrupción y coerción.** Una gasolinera banderada puede ser cómplice o víctima de extorsión — los gasolineros han documentado ser obligados a comprar combustible robado.

2. **Las alertas reflejan información pública disponible.** Si los registros del SIGER están incompletos o desactualizados, las banderas basadas en accionistas pueden ser incorrectas.

3. **La propagación es conservadora por diseño.** La degradación de señal al cruzar aristas evita falsos positivos masivos, pero puede subestimar redes densamente conectadas.

4. **`empresa_nueva` usa el umbral de fecha de constitución,** no necesariamente la fecha de obtención del permiso CRE, por limitaciones de acceso a datos históricos de la CRE.

5. **Los nombres en la CLI distinguen mayúsculas.** `"Intanza S.A. de C.V."` y `"intanza"` son actores diferentes para el motor.

---

## Estructura del Proyecto

```
KB_iap26/
├── README.md
├── CLAUDE.md                          # Instrucciones del proyecto
├── src/
│   ├── models.py                      # Dataclasses: Empresa, Persona, Gasolinera
│   ├── kb.py                          # 12 reglas Horn documentadas
│   ├── engine.py                      # Motor Forward Chaining
│   ├── cli.py                         # Interfaz CLI
│   └── data_loader.py                 # Auto-discovery CompraNet
├── scenarios/
│   ├── scenario_1_fjam.py             # Consistente — ALTA
│   ├── scenario_2_ecocarburante.py    # Contradictorio — ALTA
│   └── scenario_3_vera_ochoa.py       # Incierto — SIN ALERTA
├── visualizations/
│   └── grafo_todos_escenarios.png     # Grafo de los 3 escenarios
└── data/
    ├── siger/
    │   ├── cadena-ecocarburante/      # 7 PDFs: Ecocarburante, Royal Park, ROBRO
    │   ├── cadena-intanza/            # 9 PDFs: Intanza, TDA, GarzaPalomares, Belure
    │   ├── cadena-belure/             # 3 PDFs: Comercializadora Belure NL
    │   └── cadena-ttm/               # 17 PDFs: TTM, VEASA, VOS, TPS, RYC, VAF, Vértice
    └── *.csv                          # Expedientes CompraNet 2018–2025
```
