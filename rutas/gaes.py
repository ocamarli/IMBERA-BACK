from flask import Blueprint, jsonify, request, current_app
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask_jwt_extended import jwt_required
gae_bp = Blueprint('gaes', __name__, url_prefix='/api/v1/gae')

# Función para obtener todos los GAEs
@gae_bp.route('/obtenerGaes', methods=['GET'])
@jwt_required()
def obtener_gaes():
    try:
        mongo = PyMongo(current_app)
        estatus = request.args.get('estatus', None)
        
        # Construye el filtro basado en el valor del parámetro 'estatus'
        filtro = {}
        if estatus is not None:
            estatus_bool = estatus.lower() == 'true'
            filtro['estatus'] = estatus_bool

        # Consulta los documentos de la colección 'catGae' basados en el filtro
        gaes = list(mongo.db.catGae.find(filtro))

        for gae in gaes:
            gae['idGae'] = str(gae.pop('_id'))

        msg = f"{len(gaes)} GAEs encontradas"
        return jsonify(gaes=gaes, msg=msg, status=True), 200

    except Exception as e:
        # Maneja cualquier error que pueda ocurrir al interactuar con la base de datos
        return jsonify(msg=f"Error al obtener GAEs: {str(e)}"), 500

# Función para obtener un GAE por su ID
@gae_bp.route('/obtenerGae/<string:idGae>', methods=['GET'])
def obtener_gae(idGae):
    if idGae:
        try:
            mongo = PyMongo(current_app)
            gae = mongo.db.catGae.find_one({"_id": ObjectId(idGae)})
            if gae:
                gae['idGae'] = str(gae.pop('_id'))
                return jsonify(status=True, gae=gae, msg="GAE encontrado"), 200
            else:
                return jsonify(status=False, msg="GAE no encontrado"), 404
        except Exception as e:
            return jsonify(status=False, msg=str(e)), 500
    else:
        return jsonify(status=False, msg="ID de GAE no especificado"), 400    

# Función para actualizar un GAE
@gae_bp.route("/actualizarGae", methods=['POST'])
@jwt_required()
def actualizar_gae():
    json_data = request.get_json()
    if json_data:
        try:
            mongo = PyMongo(current_app)
            idGae = json_data.get("idGae")
            nuevos_datos = {key: value for key, value in json_data.items() if key != "idGae"}
            res = mongo.db.catGae.update_one(
                {"_id": ObjectId(idGae)},
                {"$set": nuevos_datos}
            )
            if res.modified_count > 0:
                return jsonify(status=True, msg="¡GAE actualizado!"), 200
            else:
                return jsonify(status=False, msg="¡No se realizaron cambios!"), 200
        except Exception as e:
            return jsonify(status=False, msg=f"Error: GAE no actualizado ({str(e)})"), 500
    else:
        return jsonify(status=False, msg="Error: Datos no proporcionados en formato JSON"), 400    

# Función para crear un nuevo GAE
@gae_bp.route('/crearGae', methods=['POST'])
@jwt_required()
def crear_gae():
    json_data = request.get_json()
    if json_data:
        try:
            mongo = PyMongo(current_app)
            codigo = json_data.get('codigo')
            idGaeInterno = json_data.get('idGaeInterno')
            nombre = json_data.get('nombre')

            existe_gae = mongo.db.catGae.find_one({"$or": [{"codigo": codigo}, {"idGaeInterno": idGaeInterno}]})
            if existe_gae:
                return jsonify(status=False, msg="¡El Id/Nombre/Código ya existe!"), 200
            else:
                mongo.db.catGae.insert_one(json_data)
                return jsonify(status=True, msg="¡GAE creado exitosamente!"), 200
        except Exception as e:
            return jsonify(status=False, msg=f"Error al crear GAE: {str(e)}"), 500
    else:
        return jsonify(status=False, msg="Datos no proporcionados en formato JSON"), 400

# Función para actualizar el estatus de todos los GAEs
@gae_bp.route('/actualizarEstatus', methods=['POST'])
@jwt_required()
def actualizar_estatus():
    try:
        mongo = PyMongo(current_app)
        resultado = mongo.db.catGae.update_many({}, {"$set": {"estatus": True}})
        return jsonify(status=True, msg="Estatus actualizado exitosamente", matched_count=resultado.matched_count, modified_count=resultado.modified_count), 200
    except Exception as e:
        return jsonify(status=False, msg=f"Error al actualizar estatus: {str(e)}"), 500
