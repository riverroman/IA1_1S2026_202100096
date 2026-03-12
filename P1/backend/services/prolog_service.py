from pyswip import Prolog
from config import PROLOG_FILE

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

    def reload(self):
        self.prolog.consult(PROLOG_FILE)

    def query(self, consulta):
        return list(self.prolog.query(consulta))

    # ── Helpers de formato ────────────────────────────────────────────

    def _lista_prolog(self, items):
        return "[" + ",".join(str(i) for i in items) + "]"

    def _lista_pares_prolog(self, pares):
        items = [f"[{s},{n}]" for s, n in pares]
        return "[" + ",".join(items) + "]"

    # ── Consultas básicas ─────────────────────────────────────────────

    def existe_enfermedad(self, nombre):
        return self.query(f"enfermedad({nombre})")

    def obtener_todas_enfermedades(self):
        resultados = self.query("enfermedad(E)")
        return [r["E"] for r in resultados]

    def obtener_enfermedades_cronicas(self):
        resultados = self.query("clasificacion(E, cronico)")
        vistos = set()
        cronicas = []
        for r in resultados:
            e = r["E"]
            if e not in vistos:
                vistos.add(e)
                cronicas.append(e)
        return sorted(cronicas)

    def obtener_todos_sintomas(self):
        resultados = self.query("sintoma(_, S)")
        vistos = set()
        unicos = []
        for r in resultados:
            s = r["S"]
            if s not in vistos:
                vistos.add(s)
                unicos.append(s)
        return sorted(unicos)

    def obtener_sintomas_enfermedad(self, enfermedad):
        resultados = self.query(f"sintoma({enfermedad}, S)")
        return [r["S"] for r in resultados]

    def obtener_descripcion(self, enfermedad):
        resultados = self.query(f"descripcion({enfermedad}, D)")
        return resultados[0]["D"] if resultados else ""

    def obtener_contraindicados(self, enfermedad):
        resultados = self.query(f"contraindicado({enfermedad}, M)")
        return [r["M"] for r in resultados]

    def obtener_clasificaciones(self, enfermedad):
        resultados = self.query(f"clasificacion({enfermedad}, C)")
        return [r["C"] for r in resultados]

    # ── Diagnóstico base ──────────────────────────────────────────────

    def diagnosticar(self, sintomas):
        lista = self._lista_prolog(sintomas)
        return self.query(f"diagnostico({lista}, E, P, U)")

    def diagnosticar_ponderado(self, pares):
        lista = self._lista_pares_prolog(pares)
        return self.query(f"diagnostico_ponderado({lista}, E, P, U)")

    # ── Diagnóstico completo ──────────────────────────────────────────

    def diagnosticar_completo(self, sintomas):
        s = self._lista_prolog(sintomas)
        return self.query(
            f"diagnostico_completo({s}, E, P, U, Accion, Medicamento, Coinciden)"
        )

    def diagnosticar_completo_ponderado(self, pares, alergias=None, cronicas=None):
        p = self._lista_pares_prolog(pares)
        return self.query(
            f"diagnostico_completo_ponderado({p}, E, P, U, Accion, Medicamento, Coinciden)"
        )

    # ── Medicamentos ──────────────────────────────────────────────────

    def medicamentos_seguros(self, enfermedad):
        resultados = self.query(f"todos_medicamentos_seguros({enfermedad}, Lista)")
        return resultados[0]["Lista"] if resultados else []

    def es_medicamento_seguro(self, enfermedad, medicamento):
        return bool(self.query(f"medicamento_seguro({enfermedad}, {medicamento})"))

    def obtener_todos_medicamentos(self):
        resultados = self.query("trata(M, _)")
        vistos = set()
        meds = []
        for r in resultados:
            m = r["M"]
            if m not in vistos:
                vistos.add(m)
                meds.append(m)
        return sorted(meds)

    # ── assertz / retract (para Admin) ───────────────────────────────

    def agregar_trata(self, medicamento, enfermedad):
        self.prolog.assertz(f"trata({medicamento}, {enfermedad})")

    def eliminar_trata(self, medicamento, enfermedad):
        try:
            self.prolog.retract(f"trata({medicamento}, {enfermedad})")
        except Exception:
            pass

    def agregar_enfermedad(self, nombre, descripcion, sintomas,
                            contraindicados, clasificaciones):
        self.prolog.assertz(f"enfermedad({nombre})")
        self.prolog.assertz(f"descripcion({nombre}, '{descripcion}')")
        for s in sintomas:
            self.prolog.assertz(f"sintoma({nombre}, {s})")
        for c in contraindicados:
            self.prolog.assertz(f"contraindicado({nombre}, {c})")
        for cl in clasificaciones:
            self.prolog.assertz(f"clasificacion({nombre}, {cl})")

    def eliminar_enfermedad(self, nombre):
        try: self.prolog.retract(f"enfermedad({nombre})")
        except Exception: pass
        for hecho in ["descripcion", "sintoma", "contraindicado",
                      "clasificacion", "trata"]:
            try:
                list(self.prolog.query(f"retractall({hecho}({nombre}, _))"))
            except Exception:
                pass

    # ── Urgencia y acción ─────────────────────────────────────────────

    def obtener_urgencia(self, enfermedad, porcentaje):
        return self.query(f"nivel_urgencia({enfermedad}, {porcentaje}, U)")

    def obtener_accion(self, urgencia):
        resultados = self.query(f"accion_urgencia('{urgencia}', A)")
        return resultados[0]["A"] if resultados else ""

    # ── Explicación ───────────────────────────────────────────────────

    def obtener_explicacion(self, enfermedad, sintomas):
        lista = self._lista_prolog(sintomas)
        resultados = self.query(f"explicacion({enfermedad}, {lista}, Coinciden)")
        return resultados[0]["Coinciden"] if resultados else []

    def obtener_sintomas_ausentes(self, enfermedad, sintomas):
        lista = self._lista_prolog(sintomas)
        resultados = self.query(f"sintomas_ausentes({enfermedad}, {lista}, Ausentes)")
        return resultados[0]["Ausentes"] if resultados else []