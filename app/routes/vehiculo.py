from flask import Blueprint, request, jsonify, flash, redirect, url_for
from app import db
from app.models import Vehiculo
from datetime import datetime

vehiculo_bp = Blueprint("vehiculo", __name__, template_folder="templates")

@vehiculo_bp.route("/vehiculo/crear", methods=["POST"])
def crear_vehiculo():
    try:
        marca = request.form.get("marca", "").strip()
        modelo = request.form.get("modelo", "").strip()
        patente = request.form.get("patente", "").strip()
        cliente_id = request.form.get("cliente_id", "").strip()

        # Validar campos obligatorios
        if not all([marca, modelo, patente, cliente_id]):
            return jsonify({"error": "Faltan datos requeridos"}), 400

        # Validar patente única
        existente = Vehiculo.query.filter_by(patente=patente).first()
        if existente:
            return jsonify({"error": "La patente ya está registrada."}), 409

        # Crear vehículo
        vehiculo = Vehiculo(
            marca=marca,
            modelo=modelo,
            patente=patente,
            cliente_id=int(cliente_id),
            fecha_registro=datetime.now(),
        )
        db.session.add(vehiculo)
        db.session.commit()

        # Retornar datos del vehículo creado en JSON para AJAX
        return jsonify(
            {
                "id": vehiculo.id,
                "marca": vehiculo.marca,
                "modelo": vehiculo.modelo,
                "patente": vehiculo.patente,
            }
        )
    except Exception as e:
        # Puedes usar logging para registrar el error real
        print("Error al crear vehículo:", e)
        return jsonify({"error": "Error interno del servidor"}), 500
