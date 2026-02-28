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
    
    def existe_enfermedad(self, nombre):
        return self.query(f"enfermedad({nombre})")

    def obtener_sintomas(self, nombre):
        return self.query(f"sintoma({nombre}, S)")

    def calcular_afinidad(self, nombre, sintomas):
        lista = "[" + ",".join(sintomas) + "]"
        return self.query(f"afinidad({nombre}, {lista}, P)")

    def obtener_urgencia(self, nombre, porcentaje):
        return self.query(f"nivel_urgencia({nombre}, {porcentaje}, U)")

    def diagnosticar(self, sintomas):
        lista = "[" + ",".join(sintomas) + "]"
        return self.query(f"diagnostico({lista}, E, P, U)")