from pyswip import Prolog
from config import PROLOG_FILE

class PrologService:
    def __init__(self):
        self.prolog = Prolog()
        self.prolog.consult(PROLOG_FILE)

    def reload(self):
        self.prolog.consult(PROLOG_FILE)

    def query(self, consulta):
        return list(self.prolog.query(consulta))
    
    def diagnosticar(self, sintomas):
        lista = "[" + ",".join(sintomas) + "]"
        query = f"diagnostico({lista}, E, P, U)"
        return self.query(query)

    def medicamentos_seguro(self, enfermedad):
        query = f"medicamento_seguro({enfermedad}, M)"
        return self.query(query)