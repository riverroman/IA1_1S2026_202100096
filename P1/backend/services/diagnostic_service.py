from datetime import datetime
from services.prolog_service import PrologService

NIVELES_SEVERIDAD = ["leve", "moderado", "severo"]

class DiagnosticService:

    def __init__(self):
        self.prolog_service = PrologService()
        self._historial = []

    # ── Consultas dinámicas desde Prolog ──────────────────────────────

    def obtener_todos_sintomas(self):
        """Síntomas únicos cargados en el .pl (vienen del RPA)."""
        return self.prolog_service.obtener_todos_sintomas()

    def obtener_cronicas_disponibles(self):
        """
        Enfermedades crónicas disponibles — extraídas dinámicamente
        del .pl consultando clasificacion(E, cronico).
        """
        return self.prolog_service.obtener_enfermedades_cronicas()

    def obtener_todas_enfermedades(self):
        return self.prolog_service.obtener_todas_enfermedades()

    def nombre_legible(self, clave):
        """
        Convierte clave prolog a nombre legible.
        Primero busca descripcion/2 en Prolog, si no existe formatea la clave.
        """
        desc = self.prolog_service.obtener_descripcion(clave)
        if desc:
            # Usar solo el nombre formateado, no la descripción completa
            return clave.replace("_", " ").title()
        return clave.replace("_", " ").title()

    def obtener_diagnostico(self, sintomas):
        """Compatibilidad hacia atrás."""
        return self.prolog_service.diagnosticar(sintomas)

    # ── Diagnóstico completo con severidad ────────────────────────────

    def diagnosticar(self, nombre, pares_sintoma_nivel, alergias=None, cronicas=None):
        """
        Método principal.
          nombre              : str
          pares_sintoma_nivel : [('fiebre','severo'), ...]
          alergias            : ['aspirina', ...] — medicamentos a evitar
          cronicas            : ['diabetes_tipo_2', ...] — enfermedades preexistentes
        """
        alergias = alergias or []
        cronicas = cronicas or []

        # Diagnóstico desde Prolog
        raw = self.prolog_service.diagnosticar_completo_ponderado(pares_sintoma_nivel)

        # Ordenar por porcentaje descendente
        resultados = sorted(raw, key=lambda r: float(r["P"]), reverse=True)

        sintomas_planos = [s for s, _ in pares_sintoma_nivel]
        enriquecidos = []

        for r in resultados:
            enfermedad  = r["E"]
            porcentaje  = float(r["P"])
            urgencia    = r["U"]
            accion      = r["Accion"]
            medicamento = r["Medicamento"]
            coinciden   = r["Coinciden"]

            ausentes   = self.prolog_service.obtener_sintomas_ausentes(
                enfermedad, sintomas_planos
            )
            todos_meds = self.prolog_service.medicamentos_seguros(enfermedad)
            descripcion= self.prolog_service.obtener_descripcion(enfermedad)
            reglas     = self._generar_explicacion_reglas(
                enfermedad, porcentaje, urgencia, coinciden, pares_sintoma_nivel
            )

            enriquecidos.append({
                "enfermedad":  enfermedad,
                "nombre_ui":   self.nombre_legible(enfermedad),
                "descripcion": descripcion,
                "porcentaje":  round(porcentaje, 1),
                "urgencia":    urgencia,
                "accion":      accion,
                "medicamento": medicamento,
                "todos_meds":  todos_meds,
                "coinciden":   coinciden,
                "ausentes":    ausentes,
                "reglas":      reglas,
            })

        paquete = {
            "nombre":     nombre,
            "fecha":      datetime.now().strftime("%d/%m/%Y %H:%M"),
            "sintomas":   pares_sintoma_nivel,
            "alergias":   alergias,
            "cronicas":   cronicas,
            "resultados": enriquecidos,
            "total":      len(enriquecidos),
        }

        self._historial.append(paquete)
        return paquete

    # ── Historial ─────────────────────────────────────────────────────

    def obtener_historial(self):
        return list(reversed(self._historial))

    def limpiar_historial(self):
        self._historial.clear()

    def historial_count(self):
        return len(self._historial)

    # ── Explicación de reglas ─────────────────────────────────────────

    def _generar_explicacion_reglas(self, enfermedad, porcentaje, urgencia,
                                     coinciden, pares):
        reglas = []

        if coinciden:
            sintomas_str = ", ".join(str(s) for s in coinciden)
            reglas.append(
                f"afinidad_ponderada/3 activada: síntomas coincidentes con "
                f"{enfermedad} → {sintomas_str}"
            )

        reglas.append(
            f"diagnostico_ponderado/4: afinidad {porcentaje}% >= 30% "
            f"(umbral mínimo) → enfermedad incluida"
        )

        if urgencia == "Alta":
            reglas.append(
                "nivel_urgencia/3: urgencia Alta → afinidad alta o "
                "clasificación crónica/infecciosa con P>=60%"
            )
        elif urgencia == "Media":
            reglas.append(
                "nivel_urgencia/3: urgencia Media → 40% <= afinidad < 70%"
            )
        else:
            reglas.append(
                "nivel_urgencia/3: urgencia Baja → afinidad < 40%"
            )

        coinciden_str = [str(c) for c in coinciden]
        severos   = [s for s, n in pares if n == "severo"   and s in coinciden_str]
        moderados = [s for s, n in pares if n == "moderado" and s in coinciden_str]
        leves     = [s for s, n in pares if n == "leve"     and s in coinciden_str]

        if severos:
            reglas.append(
                f"peso_severidad/2: síntomas severos "
                f"({', '.join(severos)}) → peso 1.5 aplicado"
            )
        if moderados:
            reglas.append(
                f"peso_severidad/2: síntomas moderados "
                f"({', '.join(moderados)}) → peso 1.0 aplicado"
            )
        if leves:
            reglas.append(
                f"peso_severidad/2: síntomas leves "
                f"({', '.join(leves)}) → peso 0.5 aplicado"
            )

        reglas.append(
            "primer_medicamento_seguro/2: medicamento seleccionado "
            "verificando contraindicaciones por enfermedad"
        )

        return reglas