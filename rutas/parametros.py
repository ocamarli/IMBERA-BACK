import json
import os
import random
from bson import ObjectId
from flask import Blueprint, jsonify, request,current_app
from flask_pymongo import PyMongo
from flask_jwt_extended import jwt_required
parametro_bp = Blueprint('parametros', __name__, url_prefix='/api/v1/parametro')

@parametro_bp.route('/crearParametro', methods=['POST'])
def crearParametro():
    json = request.get_json()
    if json != None:
        try:
            print("json",json)
            mongo = PyMongo(current_app)
            idParametroInterno = json.get('idParametroInterno')
            print("idParametroInterno",idParametroInterno)
            existe_parametro = mongo.db.parameters.find_one({"idParametroInterno": idParametroInterno})
            if existe_parametro:
                 return jsonify(status=False, msg="El Id ya existe"), 200
            else:
                mongo.db.parameters.insert_one(json)
                return jsonify(status=True, msg="¡Parámetro creado exitosamente!"), 200
        except:
            return jsonify(status=False, msg="Error: parametro no agregado (201)"), 200
    else:
        return jsonify(status=False, msg="Error: parametro no agregado (200)"), 200

@parametro_bp.route("/actualizarParametro", methods=['POST'])
def actualizar_parametro():
    json_data = request.get_json()
    if json_data:
        try:
            mongo = PyMongo(current_app)
            idParametro = json_data.get("idParametro")
            nuevos_datos = {key: value for key, value in json_data.items() if key != "idParametro"}
            res = mongo.db.parameters.update_one(
                {"_id": ObjectId(idParametro)},
                {"$set": nuevos_datos}
            )
            if res.modified_count > 0:
                return jsonify(status=True, msg="¡parámetro actualizado!"), 200
            else:
                return jsonify(status=False, msg="¡No se realizaron cambios!"), 200
        except Exception as e:
            return jsonify(status=False, msg=f"Error: parámetro no actualizado ({str(e)})"), 500
    else:
        return jsonify(status=False, msg="Error: Datos no proporcionados en formato JSON"), 400    

# Función para obtener un parametro por su ID
@parametro_bp.route('/obtenerParametro/<string:idParametro>', methods=['GET'])
def obtener_parametro(idParametro):
    if idParametro:
        try:
            mongo = PyMongo(current_app)
            parametro = mongo.db.parameters.find_one({"_id": ObjectId(idParametro)})
            if parametro:
                parametro['idParametro'] = str(parametro.pop('_id'))
                return jsonify(status=True, parametro=parametro, msg="parámetro encontrado"), 200
            else:
                return jsonify(status=False, msg="parámetro no encontrado"), 404
        except Exception as e:
            return jsonify(status=False, msg=str(e)), 500
    else:
        return jsonify(status=False, msg="ID de parámetro no especificado"), 400   



@parametro_bp.route('/obtenerParametros', methods=['GET'])
def obtener_parametros():
    try:
        mongo = PyMongo(current_app)
        estatus = request.args.get('estatus', None)
        
        # Construye el filtro basado en el valor del parámetro 'estatus'
        filtro = {}
        if estatus is not None:
            estatus_bool = estatus.lower() == 'true'
            filtro['estatus'] = estatus_bool

        # Consulta los documentos de la colección 'catParametro' basados en el filtro
        parametros = list(mongo.db.parameters.find(filtro))

        for parametro in parametros:
            parametro['idParametro'] = str(parametro.pop('_id'))

        msg = f"{len(parametros)} parametros encontradas"
        return jsonify(parametros=parametros, msg=msg, status=True), 200

    except Exception as e:
        # Maneja cualquier error que pueda ocurrir al interactuar con la base de datos
        return jsonify(msg=f"Error al obtener parametros: {str(e)}"), 500

