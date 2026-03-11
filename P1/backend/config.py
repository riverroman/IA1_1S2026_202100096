import os
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROLOG_FILE = os.path.join(BASE_DIR, "prolog", "knowledge_base.pl")

EMAIL_CONFIG = {
    "host": os.getenv("SMTP_HOST"),
    "port": int(os.getenv("SMTP_PORT")),
    "usuario": os.getenv("SMTP_USER"),
    "password": os.getenv("SMTP_PASS"),
    "destinatario": os.getenv("SMTP_TO")
}

DEBUG = True