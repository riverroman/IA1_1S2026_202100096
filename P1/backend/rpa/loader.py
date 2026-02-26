from config import PROLOG_FILE

def append_to_prolog(content):
    with open(PROLOG_FILE, "a") as f:
        f.write("\n")
        f.write(content)
        
def procesar_archivo(file):
    contenido = file.read().decode("utf-8").strip().split("\n")
    lineas = contenido[1:]

    hechos = []
    
    for linea in lineas:
        partes = linea.split(";")

        nombre = partes[0].lower().replace(" ", "_")
        descripcion = partes[1]

        sintomas = partes[2].strip("[]").split(",")
        contra = partes[3].strip("[]").split(",")
        clasif = partes[4].strip("[]").split(",")

        hechos.append(f"enfermedad({nombre}).")
        hechos.append(f"descripcion({nombre},'{descripcion}').")

        for s in sintomas:
            hechos.append(f"sintoma({nombre},{s.strip().replace(' ','_')}).")

        for c in contra:
            hechos.append(f"contraindicado({nombre},{c.strip().replace(' ','_')}).")

        for cl in clasif:
            hechos.append(f"clasificacion({nombre},{cl.strip().replace(' ','_')}).")

    append_to_prolog("\n".join(hechos))

    return {"message": "Base convertida a Prolog correctamente"}