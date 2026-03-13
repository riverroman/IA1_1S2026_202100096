# Manual Técnico — MediLogic
---

|**CARNET**  |      **NOMBRE COMPLETO**          |  
|----------|:-----------------------------------:|
|202100096 |  RIVER ANDERSON - ISMALEJ ROMAN     | 

---

## Tabla de Contenidos

1. [Descripción General del Sistema](#1-descripción-general-del-sistema)
2. [Herramientas y Tecnologías Utilizadas](#2-herramientas-y-tecnologías-utilizadas)
3. [Estructura del Proyecto](#3-estructura-del-proyecto)
4. [Arquitectura del Sistema](#4-arquitectura-del-sistema)
5. [Base de Conocimiento Prolog](#5-base-de-conocimiento-prolog)
6. [Reglas Lógicas Implementadas](#6-reglas-lógicas-implementadas)
7. [Módulos Python — Capa de Servicios](#7-módulos-python--capa-de-servicios)
8. [Módulos Python — Capa de Interfaz (UI)](#8-módulos-python--capa-de-interfaz-ui)
9. [Robot RPA — Configuración y Arquitectura](#9-robot-rpa--configuración-y-arquitectura)
10. [Flujo de Interacción entre Módulos](#10-flujo-de-interacción-entre-módulos)
11. [Decisiones de Diseño](#11-decisiones-de-diseño)
12. [Configuración del Entorno](#12-configuración-del-entorno)

---

## 1. Descripción General del Sistema

**MediLogic** es un sistema experto de escritorio desarrollado con Python/Tkinter como interfaz gráfica y SWI-Prolog como motor de inferencia lógica. Su propósito es asistir en el proceso de diagnóstico médico preliminar a partir de síntomas reportados por el paciente, generando diagnósticos ponderados, niveles de urgencia, y recomendaciones de medicamentos seguros.

El sistema está compuesto por dos módulos principales:

- **Módulo Paciente:** permite al usuario ingresar síntomas con severidad, enfermedades crónicas y alergias para recibir un diagnóstico automatizado.
- **Módulo Administrador:** permite gestionar la base de conocimiento (enfermedades, síntomas, medicamentos) y ejecutar el Robot RPA para carga automatizada de datos.

---

## 2. Herramientas y Tecnologías Utilizadas

| Tecnología | Versión | Uso |
|---|---|---|
| Python | 3.12 | Lenguaje principal del sistema |
| Tkinter | stdlib | Framework de interfaz gráfica de escritorio |
| SWI-Prolog | 9.x | Motor de inferencia lógica (base de conocimiento) |
| pyswip | 0.2.x | Puente Python ↔ SWI-Prolog |
| PyAutoGUI | 0.9.x | Automatización de interfaz gráfica (RPA) |
| ReportLab | 4.x | Generación de reportes en PDF |
| smtplib | stdlib | Envío de correos electrónicos (bitácora RPA) |
| subprocess / pyperclip | stdlib / 1.x | Portapapeles para caracteres especiales en RPA |

### Justificación de elecciones

**Prolog sobre alternativas:** Prolog es el lenguaje natural para sistemas expertos basados en reglas. Su motor de inferencia por backtracking permite evaluar múltiples hipótesis diagnósticas de forma declarativa, algo que sería complejo de implementar en Python puro.

**pyswip:** Es el puente más maduro entre Python y SWI-Prolog, permitiendo ejecutar consultas Prolog directamente desde código Python y recibir resultados como diccionarios nativos.

**Tkinter:** Librería nativa de Python, sin dependencias externas, multiplataforma (macOS, Windows, Linux) y suficiente para los requerimientos de UI del sistema.

---

## 3. Estructura del Proyecto

```
P1/backend/
├── app.py                  # Punto de entrada de la aplicación
├── config.py               # Configuración global (rutas, email SMTP)
├── ArchivoRPA.txt          # Archivo de entrada del Robot RPA
├── requirements.txt        # Dependencias Python
├── run.sh                  # Script de ejecución (macOS/Linux)
├── setup.sh                # Script de instalación del entorno
├── pip.sh                  # Instalación de dependencias pip
│
├── prolog/
│   └── knowledge_base.pl   # Base de conocimiento Prolog (reglas + hechos)
│
├── rpa/
│   ├── loader.py           # Parser del ArchivoRPA.txt + escritura al .pl
│   └── robot.py            # Robot PyAutoGUI — automatización del formulario
│
├── services/
│   ├── prolog_service.py   # Singleton — interfaz Python ↔ Prolog
│   ├── diagnostic_service.py  # Orquestador del proceso diagnóstico
│   ├── rpa_service.py      # Servicios del robot (informe, email)
│   ├── pdf_service.py      # Generación de PDF con ReportLab
│   └── email_service.py    # Envío de correo SMTP
│
└── ui/
    ├── main_window.py      # Ventana principal y router de vistas
    ├── theme.py            # Paleta de colores y tipografías
    ├── login_view.py       # Pantalla de inicio de sesión
    ├── home_view.py        # Pantalla de inicio / selección de módulo
    ├── patient_view.py     # Módulo Paciente (ingreso de síntomas)
    ├── diagnosis_view.py   # Pantalla de resultados del diagnóstico
    └── admin_view.py       # Módulo Administrador (CRUD + RPA)
```

---

## 4. Arquitectura del Sistema

El sistema sigue una arquitectura en **tres capas**:

```
┌─────────────────────────────────────────────┐
│              CAPA DE PRESENTACIÓN            │
│   Tkinter UI  (ui/*.py)                      │
│   PatientView · AdminView · DiagnosisView    │
└──────────────────┬──────────────────────────┘
                   │ llama a
┌──────────────────▼──────────────────────────┐
│              CAPA DE SERVICIOS               │
│   PrologService (Singleton)                  │
│   DiagnosticService · RPAService             │
│   PDFService · EmailService                  │
└──────────────────┬──────────────────────────┘
                   │ consulta / assertz / retract
┌──────────────────▼──────────────────────────┐
│           MOTOR DE CONOCIMIENTO              │
│   SWI-Prolog + knowledge_base.pl             │
│   Reglas · Hechos · Inferencia               │
└─────────────────────────────────────────────┘
```

### Patrón PrologService

El componente más crítico de la arquitectura es el `PrologService`, implementado como **Singleton** global:

```python
_instancia_global = None

class PrologService:
    def __new__(cls, *args, **kwargs):
        global _instancia_global
        if _instancia_global is None:
            _instancia_global = super().__new__(cls)
            _instancia_global._inicializado = False
        return _instancia_global

    def __init__(self):
        if self._inicializado:
            return
        self._inicializado = True
        self.prolog = Prolog()
        self.prolog.consult(PROLOG_FILE)
```

**Razón:** AdminView y PatientView deben compartir la **misma instancia** de Prolog en memoria. Sin el Singleton, los `assertz()` realizados desde Admin (agregar enfermedad/medicamento) no serían visibles en PatientView porque cada instancia tiene su propio espacio de hechos en memoria.

---

## 5. Base de Conocimiento Prolog

### Estructura del archivo `knowledge_base.pl`

El archivo se divide en tres secciones:

```prolog
% ══════════════════════════════════════════════
% SECCIÓN 1: Directivas de compatibilidad
% ══════════════════════════════════════════════
:- discontiguous enfermedad/1.
:- discontiguous sintoma/2.
:- discontiguous contraindicado/2.
:- discontiguous clasificacion/2.
:- discontiguous descripcion/2.
:- discontiguous trata/2.

% ══════════════════════════════════════════════
% SECCIÓN 2: HECHOS (generados/actualizados por Admin y RPA)
% ══════════════════════════════════════════════
enfermedad(gripe).
descripcion(gripe, 'Infección viral del tracto respiratorio').
sintoma(gripe, fiebre).
sintoma(gripe, tos).
sintoma(gripe, dolor_muscular).
clasificacion(gripe, viral).
clasificacion(gripe, respiratorio).
trata(paracetamol, gripe).
trata(ibuprofeno, gripe).
% ... (30 enfermedades base)

% ══════════════════════════════════════════════
% SECCIÓN 3: REGLAS DE INFERENCIA
% ══════════════════════════════════════════════
```

### Predicados de hechos

| Predicado | Aridad | Descripción |
|---|---|---|
| `enfermedad/1` | `enfermedad(Nombre)` | Registra una enfermedad en el sistema |
| `descripcion/2` | `descripcion(Enf, Desc)` | Descripción textual de la enfermedad |
| `sintoma/2` | `sintoma(Enf, Sint)` | Asocia un síntoma a una enfermedad |
| `contraindicado/2` | `contraindicado(Enf, Med)` | Medicamento contraindicado para la enfermedad |
| `clasificacion/2` | `clasificacion(Enf, Tipo)` | Tipo: `viral`, `bacteriano`, `cronico`, `infeccioso`, etc. |
| `trata/2` | `trata(Med, Enf)` | Medicamento que trata una enfermedad |

---

## 6. Reglas Lógicas Implementadas

### 6.1 `afinidad_ponderada/3`

```prolog
afinidad_ponderada(Enfermedad, ParesSintomaSeveridad, Porcentaje) :-
    findall(S, sintoma(Enfermedad, S), TodosSintomas),
    length(TodosSintomas, Total),
    Total > 0,
    calcular_peso(ParesSintomaSeveridad, Enfermedad, PesoObtenido),
    PesoMaximo is Total * 1.5,
    Porcentaje is (PesoObtenido / PesoMaximo) * 100,
    Porcentaje >= 30.
```

**Propósito:** Calcula qué tan compatible es un conjunto de síntomas reportados (con severidad) con una enfermedad específica.

**Ponderación de severidad:**
- `leve` → peso 0.5
- `moderado` → peso 1.0
- `severo` → peso 1.5

**Justificación:** No todos los síntomas tienen el mismo peso diagnóstico. Un síntoma severo es más significativo que uno leve. El umbral del 30% evita diagnósticos con mínima evidencia.

---

### 6.2 `nivel_urgencia/3`

```prolog
nivel_urgencia(Enfermedad, Porcentaje, alta) :-
    (Porcentaje >= 70 ;
     (clasificacion(Enfermedad, cronico), Porcentaje >= 60) ;
     (clasificacion(Enfermedad, infeccioso), Porcentaje >= 70)), !.

nivel_urgencia(_, Porcentaje, media) :-
    Porcentaje >= 40, !.

nivel_urgencia(_, _, baja).
```

**Propósito:** Clasifica la urgencia médica del diagnóstico en tres niveles.

**Justificación de umbrales:**
- **Alta (≥70%):** Alta concordancia sintomática indica necesidad de atención inmediata.
- **Crónico con ≥60%:** Las enfermedades crónicas requieren intervención temprana aunque la afinidad sea moderada.
- **Media (40–70%):** Concordancia moderada, seguimiento recomendado.
- **Baja (<40%):** Posibilidad diagnóstica menor, monitoreo.

---

### 6.3 `medicamento_seguro/2`

```prolog
medicamento_seguro(Enfermedad, Medicamento) :-
    trata(Medicamento, Enfermedad),
    \+ contraindicado(Enfermedad, Medicamento).
```

**Propósito:** Verifica que un medicamento trate la enfermedad **y** no esté contraindicado para ella.

**Justificación:** La negación por falla (`\+`) es el mecanismo estándar de Prolog para verificar ausencia de un hecho. Si no existe `contraindicado(Enf, Med)` en la base, el medicamento se considera seguro.

---

### 6.4 `primer_medicamento_seguro/2`

```prolog
primer_medicamento_seguro(Enfermedad, Medicamento) :-
    medicamento_seguro(Enfermedad, Medicamento), !.

primer_medicamento_seguro(_, ninguno).
```

**Propósito:** Retorna el primer medicamento seguro disponible o el átomo `ninguno` como fallback.

**Justificación:** El corte (`!`) garantiza que solo se retorne un resultado (determinismo). El fallback `ninguno` previene fallos en la UI cuando no hay medicamentos registrados.

---

### 6.5 `todos_medicamentos_seguros/2`

```prolog
todos_medicamentos_seguros(Enfermedad, Lista) :-
    findall(M, medicamento_seguro(Enfermedad, M), Lista).
```

**Propósito:** Recolecta todos los medicamentos seguros para una enfermedad en una lista.

---

### 6.6 `diagnostico_completo_ponderado/7`

```prolog
diagnostico_completo_ponderado(
    ParesSintomaSeveridad,  % entrada: [(sint,sev), ...]
    Enfermedad,             % salida: nombre de la enfermedad
    Porcentaje,             % salida: 0.0–100.0
    Urgencia,               % salida: alta | media | baja
    Descripcion,            % salida: string
    PrimerMed,              % salida: medicamento o 'ninguno'
    TodosMeds               % salida: lista de medicamentos
) :-
    enfermedad(Enfermedad),
    afinidad_ponderada(Enfermedad, ParesSintomaSeveridad, Porcentaje),
    nivel_urgencia(Enfermedad, Porcentaje, Urgencia),
    (descripcion(Enfermedad, Descripcion) -> true ; Descripcion = 'Sin descripción'),
    primer_medicamento_seguro(Enfermedad, PrimerMed),
    todos_medicamentos_seguros(Enfermedad, TodosMeds).
```

**Propósito:** Predicado principal del sistema. Integra todos los sub-predicados en una consulta única que retorna el diagnóstico completo.

**Justificación del uso de `->` (if-then):** La descripción es opcional en la base. El operador `->` actúa como un condicional seguro que proporciona un valor por defecto si el hecho no existe.

---

### 6.7 `sintomas_ausentes/3` y `explicacion/3`

```prolog
sintomas_ausentes(Enfermedad, ParesSintomaSeveridad, Ausentes) :-
    findall(S, (sintoma(Enfermedad, S),
                \+ member((S, _), ParesSintomaSeveridad)), Ausentes).

explicacion(Enfermedad, ParesSintomaSeveridad, Texto) :-
    sintomas_ausentes(Enfermedad, ParesSintomaSeveridad, Ausentes),
    length(Ausentes, N),
    format(atom(Texto),
        'Enfermedad ~w: ~w síntomas coinciden, faltan ~w síntomas.',
        [Enfermedad, _, N]).
```

**Propósito:** Apoyo diagnóstico — identifica qué síntomas de la enfermedad no fueron reportados, mejorando la explicabilidad del sistema.

---

## 7. Módulos Python — Capa de Servicios

### `prolog_service.py` — Interfaz con el motor Prolog

Métodos principales:

| Método | Descripción |
|---|---|
| `obtener_todas_enfermedades()` | `findall(E, enfermedad(E), Lista)` |
| `obtener_sintomas_enfermedad(enf)` | `findall(S, sintoma(Enf, S), Lista)` |
| `obtener_clasificaciones(enf)` | `findall(C, clasificacion(Enf, C), Lista)` |
| `obtener_contraindicados(enf)` | `findall(M, contraindicado(Enf, M), Lista)` |
| `diagnosticar_completo_ponderado(pares)` | Ejecuta `diagnostico_completo_ponderado/7` |
| `agregar_enfermedad(nombre, desc, sint, contra, clasif)` | `assertz` de todos los hechos |
| `eliminar_enfermedad(nombre)` | `retract` de todos los hechos relacionados |
| `agregar_trata(med, enf)` | `assertz(trata(Med, Enf))` |
| `eliminar_trata(med, enf)` | `retract(trata(Med, Enf))` |
| `reload()` | Re-consulta el `.pl` desde disco |

### `diagnostic_service.py` — Orquestador

Coordina el proceso diagnóstico completo:
1. Recibe síntomas con severidad desde PatientView
2. Llama a `PrologService.diagnosticar_completo_ponderado()`
3. Filtra y ordena resultados por porcentaje de afinidad
4. Retorna lista de diagnósticos listos para mostrar en UI

### `rpa_service.py` — Servicios del Robot

- `generar_informe(resultado)` → genera texto plano del informe
- `enviar_email_bitacora(resultado, email_config)` → envía el informe via SMTP

### `pdf_service.py` — Reportes PDF

Genera un PDF descargable del diagnóstico usando ReportLab con:
- Datos del paciente
- Lista de diagnósticos con porcentajes y urgencia
- Medicamentos recomendados
- Síntomas reportados

---

## 8. Módulos Python — Capa de Interfaz (UI)

### `main_window.py` — Router de vistas

Implementa el patrón **Page Container**: mantiene un diccionario de frames y los muestra/oculta con `pack/pack_forget`. El método `show_frame(ViewClass)` gestiona la navegación.

### `theme.py` — Sistema de diseño

Centraliza colores y tipografías como constantes:

```python
COLORS = {
    "bg_dark":        "#0f1117",   # fondo principal
    "bg_card":        "#1a1d2e",   # tarjetas y sidebar
    "bg_input":       "#252840",   # campos de entrada
    "accent":         "#00d4aa",   # color principal (verde teal)
    "accent_hover":   "#00b894",
    "text_primary":   "#e8eaf0",
    "text_secondary": "#9ba3c0",
    "text_muted":     "#6b7394",
    "border":         "#2d3154",
    "danger":         "#e74c3c",
}
```

### `admin_view.py` — Panel Administrador

4 pestañas con navegación lateral:
- **Enfermedades:** CRUD completo con modo edición inline
- **Medicamentos:** Gestión de relaciones `trata/2`
- **Archivo .pl:** Visor, exportador y cargador del `.pl`
- **Robot RPA:** Configuración y ejecución del robot con log en tiempo real

---

## 9. Robot RPA — Configuración y Arquitectura

### Propósito

El Robot RPA automatiza la carga masiva de enfermedades desde un archivo de texto plano (`ArchivoRPA.txt`) hacia la base de conocimiento, simulando la interacción humana con el formulario de la interfaz gráfica mediante PyAutoGUI.

### Configuración del entorno (`config.py`)

Toda la configuración del robot se centraliza en `config.py`:

```python
# ── Rutas ──────────────────────────────────────────
PROLOG_FILE = os.path.join(BASE_DIR, "prolog", "knowledge_base.pl")
RPA_TXT     = os.path.join(BASE_DIR, "ArchivoRPA.txt")

# ── Configuración de Email para bitácora RPA ────────
EMAIL_CONFIG = {
    "smtp_host":    "smtp.gmail.com",
    "smtp_port":    587,
    "usuario":      "tu_correo@gmail.com",
    "password":     "tu_app_password",       # App Password de Google
    "destinatario": "admin@hospital.com",
}
```

> **Nota de seguridad:** Para Gmail se debe usar un **App Password** (contraseña de aplicación), no la contraseña principal de la cuenta. Se genera en: Cuenta de Google → Seguridad → Verificación en dos pasos → Contraseñas de aplicaciones.

### Formato del `ArchivoRPA.txt`

```
NOMBRE;DESCRIPCION;[sint1,sint2,sint3];[contra1,contra2];[clasif1,clasif2]
```

Ejemplo real:
```
neumonia_bacteriana;Infección bacteriana del tejido pulmonar;[fiebre,tos,dificultad_respiratoria,dolor_pecho];[aspirina];[bacteriano,respiratorio,infeccioso]
hepatitis_a;Infección viral hepática de transmisión fecal-oral;[nauseas,ictericia,fatiga,dolor_abdominal];[];[viral,hepatico]
hipertiroidismo;Exceso de hormona tiroidea;[palpitaciones,perdida_peso,ansiedad,sudoracion];[];[endocrino,cronico]
```

**Reglas de formato:**
- Campos separados por `;`
- Listas entre corchetes `[]`, elementos separados por coma sin espacios
- Nombres sin espacios (usar `_`)
- Lista vacía: `[]`

### Arquitectura del robot (`rpa/robot.py`)

```
robot.py
  ├── _es_mac()                    → detecta sistema operativo
  ├── _pegar_texto(texto)          → clipboard para tildes/especiales
  ├── _limpiar_campo()             → Ctrl+A / Cmd+A + Delete
  ├── _cerrar_messagebox()         → Enter para confirmar diálogos
  ├── llenar_enfermedad(enf, pos)  → llena un formulario completo via Tab
  └── ejecutar_rpa(ruta, pos_nombre, pos_btn, callback)
        1. procesar_archivo(ruta_txt)   → loader.py parsea el TXT
        2. Para cada enfermedad:
           a. llenar_enfermedad()       → PyAutoGUI llena campos
           b. click(pos_btn_crear)      → envía el formulario
           c. _cerrar_messagebox()      → cierra el dialog de confirmación
        3. Retorna resultado con cargadas/fallidas/total
```

### Flujo de detección de posiciones (calibración)

El robot no usa coordenadas fijas — las detecta dinámicamente en tiempo de ejecución:

```
Usuario inicia robot
    ↓ 4 segundos
Usuario mueve mouse al campo "Nombre"
    ↓ pyautogui.position() captura (x, y)
    ↓ 4 segundos  
Usuario mueve mouse al botón "Crear Enfermedad"
    ↓ pyautogui.position() captura (x, y)
    ↓ 3 segundos de cuenta regresiva
Robot inicia automatización
```

**Justificación:** El uso de coordenadas dinámicas hace el robot portable — funciona independientemente de la resolución de pantalla, posición de la ventana o sistema operativo.

### Navegación entre campos (Tab Order)

```
Campo Nombre
    → Tab → Campo Descripción   (usa clipboard por tildes)
    → Tab → Campo Síntomas
    → Tab → Campo Contraindicados
    → Tab → Campo Clasificaciones
    → Click en botón "Crear Enfermedad"
    → Enter para cerrar messagebox de confirmación
```

### Configuración de PyAutoGUI

```python
pyautogui.PAUSE    = 0.5   # pausa entre acciones (ms de seguridad)
pyautogui.FAILSAFE = True  # abortar moviendo mouse a esquina superior-izquierda
```

### Integración con la UI (pestaña Robot RPA)

Cuando el robot se lanza desde el Admin, corre en un **hilo separado** (`threading.Thread`) para no bloquear el event loop de Tkinter. El log se actualiza en tiempo real mediante `self.after(0, callback)` que es el mecanismo thread-safe de Tkinter.

```python
hilo = threading.Thread(target=self._hilo_rpa, args=(ruta_txt,), daemon=True)
hilo.start()
```

---

## 10. Flujo de Interacción entre Módulos

### Flujo Diagnóstico (Módulo Paciente)

```
PatientView
    │  síntomas + severidad + alergias + crónicas
    ▼
DiagnosticService.diagnosticar()
    │  [(sint, sev), ...]
    ▼
PrologService.diagnosticar_completo_ponderado()
    │  query: diagnostico_completo_ponderado/7
    ▼
SWI-Prolog (knowledge_base.pl)
    │  afinidad_ponderada → nivel_urgencia → medicamento_seguro
    ▼
PrologService retorna lista de resultados
    │  [{"enfermedad": ..., "porcentaje": ..., "urgencia": ..., ...}]
    ▼
DiagnosisView.mostrar_resultados()
    │  renderiza tarjetas por diagnóstico
    ▼
PDFService.generar_pdf()  ← si usuario descarga informe
```

### Flujo Administración — Agregar Enfermedad

```
AdminView (formulario)
    │  nombre, desc, síntomas, contraindicados, clasificaciones
    ▼
PrologService.agregar_enfermedad()
    │  assertz(enfermedad(X))
    │  assertz(sintoma(X, S)) × n
    │  assertz(clasificacion(X, C)) × n
    │  assertz(contraindicado(X, M)) × n
    ▼
AdminView._persistir_pl()
    │  lee reglas del .pl actual
    │  regenera sección de hechos desde memoria Prolog
    │  sobreescribe el .pl
    ▼
PatientView (siguiente consulta)
    │  los nuevos hechos ya están en memoria compartida (Singleton)
    │  NO necesita reload() — el assertz ya actualizó la memoria
```

### Flujo RPA

```
ArchivoRPA.txt
    ▼
loader.py.procesar_archivo()
    │  parsea líneas NOMBRE;DESC;[sint];[contra];[clasif]
    │  retorna lista de dicts
    ▼
robot.py.ejecutar_rpa()
    │  PyAutoGUI llena formulario Admin
    │  → Admin._crear_enfermedad() es llamado por el botón
    │  → assertz en Prolog (via Singleton)
    ▼
RPAService.prolog_service.reload()
    │  re-consulta el .pl para sincronizar disco ↔ memoria
    ▼
generar_informe() + enviar_email_bitacora()
    │  EMAIL_CONFIG desde config.py
    ▼
Bitácora enviada al administrador
```

---

## 11. Decisiones de Diseño

### Decisión 1: Singleton en PrologService

**Problema:** AdminView y PatientView se instancian por separado en `main_window.py`. Sin control, cada una crearía su propio `Prolog()` con su propia memoria.

**Solución:** Singleton global con variable de módulo `_instancia_global`. El flag `_inicializado` previene la re-inicialización en llamadas subsecuentes a `__init__`.

**Alternativa descartada:** Pasar la instancia como parámetro en el constructor. Se descartó porque aumenta el acoplamiento y requiere modificar `main_window.py` para pasar dependencias.

---

### Decisión 2: PatientView no llama `reload()` al refrescar síntomas

**Problema:** Si PatientView llama `reload()` al mostrarse, re-lee el `.pl` desde disco. Esto pierde los `assertz` del Admin que aún no fueron persistidos al `.pl`.

**Solución:** PatientView solo consulta la memoria Prolog en vivo (`obtener_todas_enfermedades()`, `obtener_todos_sintomas()`). El Singleton garantiza que esos datos son los mismos que el Admin está modificando.

---

### Decisión 3: RPA escribe hechos vía formulario (no directo al .pl)

**Diseño alternativo descartado:** El loader podría escribir directamente al `.pl` y hacer `reload()`. Esto se descartó porque el enunciado requiere que el robot automatice la interfaz gráfica.

**Diseño implementado:** El robot llena el formulario Admin campo por campo, simulando al usuario. El Admin maneja la lógica de `assertz` y `_persistir_pl()` normalmente.

---

### Decisión 4: Coordenadas dinámicas en el robot

**Problema:** Coordenadas hardcodeadas fallarían al cambiar resolución, tamaño de ventana o sistema operativo.

**Solución:** El robot pide al usuario posicionar el mouse en cada control objetivo y captura las coordenadas en tiempo de ejecución con `pyautogui.position()`.

---

### Decisión 5: Ponderación de severidad en el diagnóstico

**Problema:** Un diagnóstico binario (síntoma presente/ausente) no refleja la realidad clínica.

**Solución:** Se implementó un sistema de pesos donde la severidad multiplica la contribución de cada síntoma al diagnóstico. Un síntoma severo tiene 3× el peso de uno leve.

---

## 12. Configuración del Entorno

### Requisitos del sistema

- Python 3.12+
- SWI-Prolog 9.x instalado y en PATH
- macOS, Windows 10+ o Linux (Ubuntu 20+)

### Instalación

```bash
# 1. Clonar el repositorio
git clone https://github.com/[usuario]/IA1_1S2026_202100096.git
cd IA1_1S2026_202100096/P1/backend

# 2. Crear entorno virtual
python3 -m venv venv
source venv/bin/activate   # macOS/Linux
# venv\Scripts\activate    # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar la aplicación
python app.py
```

### `requirements.txt`

```
pyswip>=0.2.10
pyautogui>=0.9.54
reportlab>=4.0.0
pyperclip>=1.8.2
pillow>=10.0.0
```

### Configuración de email (`config.py`)

```python
EMAIL_CONFIG = {
    "smtp_host":    "smtp.gmail.com",
    "smtp_port":    587,
    "usuario":      "correo@gmail.com",
    "password":     "xxxx xxxx xxxx xxxx",  # App Password de 16 caracteres
    "destinatario": "destino@correo.com",
}
```

### Credenciales de acceso por defecto

| Rol | Usuario | Contraseña |
|---|---|---|
| Administrador | `riverroman1415@gmail.com` | `admin` |

---