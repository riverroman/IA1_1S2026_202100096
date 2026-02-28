from services.prolog_service import PrologService

class DiagnosticService:

    def __init__(self):
        self.prolog_service = PrologService()

    def existe_enfermedad(self, nombre):
        return self.prolog_service.existe_enfermedad(nombre)

    def obtener_sintomas(self, nombre):
        return self.prolog_service.obtener_sintomas(nombre)

    def calcular_afinidad(self, nombre, sintomas):
        return self.prolog_service.calcular_afinidad(nombre, sintomas)

    def obtener_urgencia(self, nombre, porcentaje):
        return self.prolog_service.obtener_urgencia(nombre, porcentaje)

    def obtener_diagnostico(self, sintomas):
        return self.prolog_service.diagnosticar(sintomas)