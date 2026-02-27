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

@patient_bp.route("/existe/<nombre>", methods=["GET"])
def existe(nombre):
    resultado = diagnostic_service.existe_enfermedad(nombre)
    return jsonify(resultado)

@patient_bp.route("/sintomas/<nombre>", methods=["GET"])
def sintomas(nombre):
    resultado = diagnostic_service.obtener_sintomas(nombre)
    return jsonify(resultado)

@patient_bp.route("/afinidad", methods=["POST"])
def afinidad():
    data = request.get_json()
    nombre = data["enfermedad"]
    sintomas = data["sintomas"]
    resultado = diagnostic_service.calcular_afinidad(nombre, sintomas)
    return jsonify(resultado)