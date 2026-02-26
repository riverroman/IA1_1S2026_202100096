from services.prolog_service import PrologService

class DiagnosticService:

    def __init__(self):
        self.prolog_service = PrologService()

    def obtener_diagnostico(self, sintomas):
        resultados = self.prolog_service.diagnosticar(sintomas)

        if not resultados:
            return {"message": "No se encontró diagnóstico"}

        return resultados