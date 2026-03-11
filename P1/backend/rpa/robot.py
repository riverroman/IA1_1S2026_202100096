"""
robot.py — RPA MediLogic
Script INDEPENDIENTE que usa PyAutoGUI para llenar automáticamente
el formulario de enfermedades en la app MediLogic.

CÓMO USAR:
    1. Corre la app:  python app.py
    2. Inicia sesión como Admin → ve a pestaña "Enfermedades"
    3. En otra terminal: python rpa/robot.py
    4. Sigue las instrucciones en pantalla

REQUISITOS:
    pip install pyautogui pyperclip
    En macOS: pip install pyobjc-core pyobjc  (para permisos de accesibilidad)
"""

import sys
import os
import time
import subprocess
from datetime import datetime

import pyautogui

# Agregar carpeta raíz al path para importar loader
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from rpa.loader import procesar_archivo
from services.rpa_service import RPAService
from config import EMAIL_CONFIG

# ── Configuración ─────────────────────────────────────────────────────
pyautogui.PAUSE    = 0.5   # pausa entre cada acción PyAutoGUI
pyautogui.FAILSAFE = True  # mover mouse a esquina superior-izquierda para abortar

DELAY_ENTRE_ENFERMEDADES = 2.0   # segundos entre cada enfermedad
RUTA_TXT_DEFAULT = os.path.join(os.path.dirname(__file__), "..", "ArchivoRPA.txt")


# ── Helpers ───────────────────────────────────────────────────────────

def _es_mac():
    return sys.platform == "darwin"


def _pegar_texto(texto):
    """Escribe texto usando clipboard — maneja tildes y caracteres especiales."""
    if _es_mac():
        proc = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
        proc.communicate(texto.encode("utf-8"))
        pyautogui.hotkey("command", "v")
    else:
        import pyperclip
        pyperclip.copy(texto)
        pyautogui.hotkey("ctrl", "v")
    time.sleep(0.3)


def _limpiar_campo():
    """Selecciona todo y borra el campo actual."""
    if _es_mac():
        pyautogui.hotkey("command", "a")
    else:
        pyautogui.hotkey("ctrl", "a")
    time.sleep(0.1)
    pyautogui.press("delete")
    time.sleep(0.1)


def _cerrar_messagebox():
    """Presiona Enter para cerrar el messagebox de confirmación de Tkinter."""
    time.sleep(0.6)
    pyautogui.press("return")
    time.sleep(0.4)


# ── Lógica principal ──────────────────────────────────────────────────

def llenar_enfermedad(enf, pos_nombre):
    """
    Llena el formulario de UNA enfermedad navegando con Tab.
    pos_nombre = (x, y) del campo 'Nombre' en pantalla.
    """
    x, y = pos_nombre

    # 1. Campo Nombre
    pyautogui.click(x, y)
    time.sleep(0.3)
    _limpiar_campo()
    pyautogui.write(enf["nombre"], interval=0.05)

    # 2. Tab → Descripción (usa clipboard por tildes)
    pyautogui.press("tab")
    time.sleep(0.2)
    _limpiar_campo()
    _pegar_texto(enf["descripcion"])

    # 3. Tab → Síntomas
    pyautogui.press("tab")
    time.sleep(0.2)
    _limpiar_campo()
    pyautogui.write(", ".join(enf["sintomas"]), interval=0.04)

    # 4. Tab → Contraindicados
    pyautogui.press("tab")
    time.sleep(0.2)
    _limpiar_campo()
    pyautogui.write(", ".join(enf["contraindicados"]), interval=0.04)

    # 5. Tab → Clasificaciones
    pyautogui.press("tab")
    time.sleep(0.2)
    _limpiar_campo()
    pyautogui.write(", ".join(enf["clasificaciones"]), interval=0.04)

    time.sleep(0.3)


def ejecutar_rpa(ruta_txt, pos_nombre, pos_btn_crear, callback=None):
    """
    Ejecuta el robot completo.

    Args:
        ruta_txt:     ruta al ArchivoRPA.txt
        pos_nombre:   (x, y) del campo Nombre en la app
        pos_btn_crear:(x, y) del botón "Crear Enfermedad"
        callback:     función(msg) para reportar progreso (opcional)
    """

    def log(msg):
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"[{ts}] {msg}")
        if callback:
            callback(msg)

    log(f"Leyendo archivo: {ruta_txt}")
    resultado = procesar_archivo(ruta_txt)

    if not resultado["enfermedades"]:
        log("ERROR: El archivo no contiene enfermedades válidas.")
        resultado["cargadas"]    = []
        resultado["fallidas"]    = []
        resultado["total_ok"]    = 0
        resultado["total_error"] = 0
        return resultado

    log(f"Enfermedades encontradas: {resultado['total']}")
    log("Iniciando automatización en 3 segundos... (NO toques el mouse)")
    time.sleep(3)

    cargadas = []
    fallidas = []

    for i, enf in enumerate(resultado["enfermedades"], 1):
        log(f"[{i}/{resultado['total']}] → {enf['nombre']}")
        try:
            llenar_enfermedad(enf, pos_nombre)

            # Clic en botón "Crear Enfermedad"
            pyautogui.click(pos_btn_crear[0], pos_btn_crear[1])
            log(f"  Clic en Crear Enfermedad")

            # Cerrar messagebox de confirmación
            _cerrar_messagebox()

            cargadas.append(enf["nombre"])
            log(f"  ✓ Cargado correctamente")

        except Exception as ex:
            fallidas.append({"nombre": enf["nombre"], "error": str(ex)})
            log(f"  ✗ Error: {ex}")
            # Intentar limpiar y continuar
            try:
                pyautogui.press("escape")
                time.sleep(0.5)
            except Exception:
                pass

        time.sleep(DELAY_ENTRE_ENFERMEDADES)

    resultado["cargadas"]    = cargadas
    resultado["fallidas"]    = fallidas
    resultado["total_ok"]    = len(cargadas)
    resultado["total_error"] = len(fallidas)

    log(f"RPA completado — OK: {len(cargadas)} | Errores: {len(fallidas)}")
    return resultado


def generar_informe(resultado, guardar_en=None):
    """Genera informe de texto plano. Retorna el string y opcionalmente lo guarda."""
    ts = resultado.get("timestamp", datetime.now().isoformat())
    lineas = [
        "=" * 60,
        "  INFORME DE CARGA RPA — MediLogic",
        "=" * 60,
        f"  Fecha y hora   : {ts}",
        f"  Archivo origen : {resultado.get('archivo', 'N/A')}",
        f"  Total en TXT   : {resultado.get('total', 0)}",
        f"  Cargadas OK    : {resultado.get('total_ok', 0)}",
        f"  Con errores    : {resultado.get('total_error', 0)}",
        "=" * 60,
        "",
        "ENFERMEDADES CARGADAS EXITOSAMENTE:",
        "-" * 40,
    ]
    for nombre in resultado.get("cargadas", []):
        lineas.append(f"  [OK]    {nombre}")

    if resultado.get("fallidas"):
        lineas += ["", "ENFERMEDADES CON ERROR:", "-" * 40]
        for item in resultado["fallidas"]:
            lineas.append(f"  [ERROR] {item['nombre']}: {item['error']}")

    if resultado.get("errores"):
        lineas += ["", "ADVERTENCIAS DEL PARSER:", "-" * 40]
        for err in resultado["errores"]:
            lineas.append(f"  [WARN]  {err}")

    lineas += [
        "",
        "=" * 60,
        "  Generado por el Robot RPA de MediLogic",
        "=" * 60,
    ]
    contenido = "\n".join(lineas)

    if guardar_en:
        with open(guardar_en, "w", encoding="utf-8") as f:
            f.write(contenido)
        print(f"[RPA] Informe guardado en: {guardar_en}")

    return contenido


# ── Entry point (ejecución directa desde terminal) ────────────────────
if __name__ == "__main__":
    ruta = sys.argv[1] if len(sys.argv) > 1 else RUTA_TXT_DEFAULT

    print()
    print("=" * 55)
    print("   MediLogic RPA — Carga automática de enfermedades")
    print("=" * 55)
    print(f"   Archivo TXT : {ruta}")
    print()
    print("   PASOS ANTES DE CONTINUAR:")
    print("   1. Abre la app MediLogic (python app.py)")
    print("   2. Inicia sesión como Administrador")
    print("   3. Ve a la pestaña 'Enfermedades'")
    print("   4. Asegúrate de que el formulario esté visible")
    print()
    input("   Presiona Enter cuando estés listo... ")

    print()
    print("   PASO 1/2 — Detectar campo 'Nombre'")
    print("   Mueve el mouse al campo 'Nombre' del formulario")
    print("   Tienes 4 segundos...")
    time.sleep(4)
    pos_nombre = pyautogui.position()
    print(f"   Campo Nombre detectado en: {pos_nombre}")

    print()
    print("   PASO 2/2 — Detectar botón 'Crear Enfermedad'")
    print("   Mueve el mouse al botón '+ Crear Enfermedad'")
    print("   Tienes 4 segundos...")
    time.sleep(4)
    pos_btn = pyautogui.position()
    print(f"   Botón Crear detectado en: {pos_btn}")

    print()
    print("   Todo listo. Iniciando robot en 3 segundos...")
    print("   Para abortar: mueve el mouse a la esquina superior-izquierda")
    print()

    resultado = ejecutar_rpa(
        ruta_txt=ruta,
        pos_nombre=(pos_nombre.x, pos_nombre.y),
        pos_btn_crear=(pos_btn.x, pos_btn.y),
    )

    # Guardar informe
    ts_safe = datetime.now().strftime("%Y%m%d_%H%M%S")
    dir_rpa = os.path.dirname(os.path.abspath(__file__))
    ruta_informe = os.path.join(dir_rpa, f"informe_rpa_{ts_safe}.txt")
    informe = generar_informe(resultado, guardar_en=ruta_informe)

    print()
    print(informe)
    
    svc = RPAService()

    svc.enviar_email_bitacora(
        resultado,
        EMAIL_CONFIG
    )
    
    print("✓ Email enviado con el informe RPA")


# ── Función llamable desde el Admin (botón en UI) ─────────────────────
def ejecutar_desde_admin(ruta_txt, pos_nombre, pos_btn_crear, callback=None):
    """
    Versión para ser llamada desde el Admin.
    Usa PyAutoGUI + persiste al .pl al final via RPAService.
    """
    # 1. Robot llena el formulario con PyAutoGUI
    resultado = ejecutar_rpa(ruta_txt, pos_nombre, pos_btn_crear, callback)

    # 2. Persistir al .pl via RPAService (por si el robot falla en algún messagebox)
    try:
        from services.rpa_service import RPAService
        svc = RPAService()
        # Recargar las que sí cargó el robot
        for enf_nombre in resultado.get("cargadas", []):
            pass  # ya están en memoria Prolog porque el robot llenó el form
        svc._persistir_pl()
        if callback:
            callback("✓ Base de conocimiento (.pl) actualizada correctamente")
    except Exception as ex:
        if callback:
            callback(f"Advertencia al persistir .pl: {ex}")

    # 3. Guardar informe
    from datetime import datetime
    ts_safe = datetime.now().strftime("%Y%m%d_%H%M%S")
    dir_rpa = os.path.dirname(os.path.abspath(__file__))
    ruta_informe = os.path.join(dir_rpa, f"informe_rpa_{ts_safe}.txt")
    generar_informe(resultado, guardar_en=ruta_informe)

    return resultado, ruta_informe