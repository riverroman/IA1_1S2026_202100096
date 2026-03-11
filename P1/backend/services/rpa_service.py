"""
rpa_service.py — Servicio RPA
Coordina: loader (escribe al .pl) → reload Prolog → informe → email
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from services.email_service import EmailService

from rpa.loader import procesar_archivo
from services.prolog_service import PrologService

class RPAService:

    def __init__(self):
        self.prolog_service = PrologService()

    def procesar_archivo(self, ruta):
        """
        1. loader.py escribe hechos directamente al .pl
        2. Prolog recarga el .pl actualizado
        3. Retorna resultado con estadísticas
        """
        resultado = procesar_archivo(ruta)

        # Recargar Prolog para que reconozca los nuevos hechos
        self.prolog_service.reload()

        return resultado

    def generar_informe(self, resultado, guardar_en=None):
        """Genera informe de texto plano con los resultados de la carga."""
        ts    = resultado.get("timestamp", datetime.now().isoformat())
        ok    = resultado.get("total_ok", 0)
        err   = resultado.get("total_error", 0)
        total = resultado.get("total", 0)

        lineas = [
            "=" * 60,
            "  INFORME DE CARGA RPA — MediLogic",
            "=" * 60,
            f"  Fecha y hora   : {ts}",
            f"  Archivo origen : {resultado.get('archivo', 'N/A')}",
            f"  Total en TXT   : {total}",
            f"  Cargadas OK    : {ok}",
            f"  Con errores    : {err}",
            "=" * 60,
            "",
            "ENFERMEDADES CARGADAS EXITOSAMENTE:",
            "-" * 40,
        ]
        for nombre in resultado.get("cargadas", []):
            lineas.append(f"  [OK]    {nombre}")

        if resultado.get("errores"):
            lineas += ["", "ADVERTENCIAS:", "-" * 40]
            for e in resultado["errores"]:
                lineas.append(f"  [WARN]  {e}")

        lineas += [
            "",
            "=" * 60,
            "  Generado automáticamente por el Robot RPA de MediLogic",
            "=" * 60,
        ]
        contenido = "\n".join(lineas)

        if guardar_en:
            with open(guardar_en, "w", encoding="utf-8") as f:
                f.write(contenido)
            print(f"[RPA] Informe guardado en: {guardar_en}")

        return contenido

    def enviar_email_bitacora(self, resultado, config_email):
        informe = self.generar_informe(resultado)
        
        email_service = EmailService(
            config_email["host"],
            config_email["port"],
            config_email["usuario"],
            config_email["password"]
        )
        asunto = "[MediLogic] Informe de carga RPA"
        email_service.enviar(
            config_email["destinatario"],
            asunto,
            informe
        )
        return {"ok": True}