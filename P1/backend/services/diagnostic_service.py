from services.prolog_service import PrologService

class DiagnosticService:
    def __init__(self):
        self.prolog_service = PrologService()

    def existe_enfermedad(self, nombre):
        query = f"enfermedad({nombre})"
        print(f"Query: {query}")
        print(f"Result: {self.prolog_service.query(query)}")
        return self.prolog_service.query(query)

    def obtener_sintomas(self, nombre):
        query = f"sintoma({nombre}, S)"
        return self.prolog_service.query(query)

    def calcular_afinidad(self, nombre, sintomas):
        lista = "[" + ",".join(sintomas) + "]"
        query = f"afinidad({nombre}, {lista}, P)"
        return self.prolog_service.query(query)

    def obtener_urgencia(self, nombre, porcentaje):
        query = f"nivel_urgencia({nombre}, {porcentaje}, U)"
        return self.prolog_service.query(query)
    
    def obtener_diagnostico(self, sintomas):
        lista = "[" + ",".join(sintomas) + "]"
        query = f"diagnostico({lista}, E, P, U)"
        return self.prolog_service.query(query) 