import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PROLOG_FILE = os.path.join(BASE_DIR, "prolog", "knowledge_base.pl")
FACTS_FILE = os.path.join(BASE_DIR, "prolog", "facts.pl")

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")

DEBUG = True