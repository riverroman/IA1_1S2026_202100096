from datetime import datetime

def _parsear_lista(texto):
    texto = texto.strip()
    if texto.startswith("[") and texto.endswith("]"):
        texto = texto[1:-1]
    return [i.strip().lower().replace(" ", "_") for i in texto.split(",") if i.strip()]

def append_to_prolog(content):
    """Escribe directamente al .pl (append)."""
    from config import PROLOG_FILE
    with open(PROLOG_FILE, "a", encoding="utf-8") as f:
        f.write("\n")
        f.write(content)
        
def procesar_archivo(ruta_archivo):
    """
    Lee el TXT, genera hechos Prolog y los escribe al .pl.
    Retorna dict con enfermedades cargadas, errores y timestamp.
    """
    enfermedades = []
    errores = []

    try:
        with open(ruta_archivo, "r", encoding="utf-8") as f:
            contenido = f.read().strip().split("\n")
    except FileNotFoundError:
        return {
            "enfermedades": [], "errores": [f"Archivo no encontrado: {ruta_archivo}"],
            "timestamp": datetime.now().isoformat(), "archivo": ruta_archivo, "total": 0,
            "cargadas": [], "fallidas": [], "total_ok": 0, "total_error": 0,
            "message": "Archivo no encontrado"
        }

    # Saltar encabezado
    lineas = contenido[1:]
    hechos = []

    for num, linea in enumerate(lineas, start=2):
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            continue

        partes = linea.split(";")
        if len(partes) < 5:
            errores.append(f"Línea {num}: se esperaban 5 campos")
            continue

        try:
            nombre      = partes[0].strip().lower().replace(" ", "_")
            descripcion = partes[1].strip()
            sintomas    = _parsear_lista(partes[2])
            contra      = _parsear_lista(partes[3])
            clasif      = _parsear_lista(partes[4])

            if not nombre:
                errores.append(f"Línea {num}: nombre vacío")
                continue

            # Generar hechos Prolog
            hechos.append(f"enfermedad({nombre}).")
            desc_safe = descripcion.replace("'", "\\'")
            hechos.append(f"descripcion({nombre},'{desc_safe}').")
            for s in sintomas:
                hechos.append(f"sintoma({nombre},{s}).")
            for c in contra:
                hechos.append(f"contraindicado({nombre},{c}).")
            for cl in clasif:
                hechos.append(f"clasificacion({nombre},{cl}).")

            enfermedades.append({
                "nombre": nombre,
                "descripcion": descripcion,
                "sintomas": sintomas,
                "contraindicados": contra,
                "clasificaciones": clasif,
            })

        except Exception as ex:
            errores.append(f"Línea {num}: {ex}")

    # Escribir al .pl
    if hechos:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        bloque = f"\n% === RPA Carga automática — {ts} ===\n" + "\n".join(hechos)
        append_to_prolog(bloque)

    return {
        "enfermedades": enfermedades,
        "errores":      errores,
        "timestamp":    datetime.now().isoformat(),
        "archivo":      ruta_archivo,
        "total":        len(enfermedades),
        "cargadas":     [e["nombre"] for e in enfermedades],
        "fallidas":     [{"nombre": "línea_" + str(i), "error": e} for i, e in enumerate(errores)],
        "total_ok":     len(enfermedades),
        "total_error":  len(errores),
        "message":      "Base convertida a Prolog correctamente"
    }