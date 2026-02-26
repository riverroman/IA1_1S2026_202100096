from pyswip import Prolog
from config import PROLOG_FILE

class PrologService:
    
    def __init__(self):
        self.prolog = Prolog()
        self.prolog.consult(PROLOG_FILE)

    def reload(self):
        self.prolog.consult(PROLOG_FILE)

    def diagnosticar(self, sintomas):
        lista = "[" + ",".join(sintomas) + "]"
        query = f"diagnostico({lista}, E, P, U)"
        result = list(self.prolog.query(query))
        return result

    def medicamentos_seguro(self, enfermedad):
        query = f"medicamento_seguro({enfermedad}, M)"
        result = list(self.prolog.query(query))
        return result