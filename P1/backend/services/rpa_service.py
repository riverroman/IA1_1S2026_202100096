from rpa.loader import procesar_archivo
from services.prolog_service import PrologService

class RPAService:
    def __init__(self):
        self.prolog_service = PrologService()

    def procesar_archivo(self, ruta):
        resultado = procesar_archivo(ruta)

        self.prolog_service.reload()

        return resultado