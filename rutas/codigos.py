from flask import Blueprint, jsonify, request,current_app

from flask_pymongo import PyMongo
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager, create_refresh_token
from bson.objectid import ObjectId

codigo_bp = Blueprint('codigo', __name__, url_prefix='/api/v1/codigo')

@codigo_bp.route("/obtenerCodigos", methods=['GET'])
@jwt_required()
def obtenerCodigos():
    codigos = []
    msg = ""
    status = False
    try:
        mongo = PyMongo(current_app)
        codigos = list(mongo.db.codigos.find({}, {'_id': 0}))
        msg = "".join([str(len(codigos)), ' códigos encontradas'])
        status = True
    except:
        msg = "Error: No se pudo obtener la información de los códigos."
        status = False

    code = 200 if status else 500
    return jsonify(codigos=codigos, msg=msg, status=status), code


@codigo_bp.route("/actualizarCodigo", methods=['POST'])
@jwt_required()
def actualizar_codigo():
    json_data = request.get_json()
    if json_data:
        try:
            mongo = PyMongo(current_app)

            nombreCodigo = json_data.get("tipoCodigo", None)
            valorCodigo = json_data.get("codigo", None)  # Extraemos el valor del código

            if nombreCodigo is None or valorCodigo is None:
                return jsonify(status=False, msg="Error: 'tipoCodigo' y 'codigo' son campos obligatorios."), 400

            res = mongo.db.codigos.update_one(
                {"nombre": nombreCodigo},
                {"$set": {"valor": valorCodigo}}
            )

            if res.modified_count > 0:
                return jsonify(status=True, msg="¡Código actualizado!"), 200
            else:
                return jsonify(status=False, msg="¡No se realizaron cambios!"), 200
        except Exception as e:
            return jsonify(status=False, msg=f"Error: Código no actualizado ({str(e)})"), 500
    else:
        return jsonify(status=False, msg="Error: Datos no proporcionados en formato JSON"), 400