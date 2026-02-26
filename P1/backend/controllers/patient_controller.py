from flask import Blueprint, request, jsonify
from services.diagnostic_service import DiagnosticService

patient_bp = Blueprint("patient", __name__)
diagnostic_service = DiagnosticService()

@patient_bp.route("/diagnostico", methods=["POST"])
def diagnostico():
    data = request.get_json()
    sintomas = data.get("sintomas", [])
    
    resultado = diagnostic_service.obtener_diagnostico(sintomas)
    
    return jsonify(resultado)