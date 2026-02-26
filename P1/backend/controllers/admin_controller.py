from flask import Blueprint, request, jsonify
from rpa.loader import procesar_archivo

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/upload", methods=["POST"])
def upload_file():
    file = request.files["file"]
    resultado = procesar_archivo(file)
    return jsonify({"message": "Archivo procesado"})