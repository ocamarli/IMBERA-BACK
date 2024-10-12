from flask import Blueprint, jsonify, request, current_app
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask_jwt_extended import jwt_required
firmware_bp = Blueprint('firmwares', __name__, url_prefix='/api/v1/firmware')

# Función para obtener todos los firmwares
@firmware_bp.route('/obtenerFirmwares', methods=['GET'])
@jwt_required()
def obtener_firmwares():
    try:
        mongo = PyMongo(current_app)
        estatus = request.args.get('estatus', None)
        
        # Construye el filtro basado en el valor del parámetro 'estatus'
        filtro = {}
        if estatus is not None:
            estatus_bool = estatus.lower() == 'true'
            filtro['estatus'] = estatus_bool

        firmwares = list(mongo.db.catFirmwares.find(filtro))

        for firmware in firmwares:
            firmware['idFirmware'] = str(firmware.pop('_id'))

        msg = f"{len(firmwares)} firmwares encontradas"
        return jsonify(firmwares=firmwares, msg=msg, status=True), 200

    except Exception as e:
        return jsonify(msg=f"Error al obtener firmwares: {str(e)}"), 500

# Función para obtener un firmware por su ID
@firmware_bp.route('/obtenerFirmware/<string:idFirmware>', methods=['GET'])
@jwt_required()
def obtener_firmware(idFirmware):
    if idFirmware:
        try:
            mongo = PyMongo(current_app)
            firmware = mongo.db.catFirmwares.find_one({"_id": ObjectId(idFirmware)})
            if firmware:
                firmware['idFirmware'] = str(firmware.pop('_id'))
                return jsonify(status=True, firmware=firmware, msg="firmware encontrado"), 200
            else:
                return jsonify(status=False, msg="firmware no encontrado"), 404
        except Exception as e:
            return jsonify(status=False, msg=str(e)), 500
    else:
        return jsonify(status=False, msg="ID de firmware no especificado"), 400    

# Función para actualizar un firmware
@firmware_bp.route("/actualizarFirmware", methods=['POST'])
@jwt_required()
def actualizar_hardware():
    json_data = request.get_json()
    if json_data:
        try:
            mongo = PyMongo(current_app)
            idFirmware = json_data.get("idFirmware")
            nombreFirmwareware = json_data.get("nombre", None)

            if nombreFirmwareware:
                # Verificar si ya existe otro hardware con el mismo nombre
                existing_hardware = mongo.db.catFirmwares.find_one(
                    {"nombre": nombreFirmwareware, "_id": {"$ne": ObjectId(idFirmware)}}
                )
                if existing_hardware:
                    return jsonify(status=False, msg="¡ya existe hardware!"), 200

            nuevos_datos = {key: value for key, value in json_data.items() if key != "idFirmware"}
            print(nuevos_datos)
            res = mongo.db.catFirmwares.update_one(
                {"_id": ObjectId(idFirmware)},
                {"$set": nuevos_datos}
            )
            if res.modified_count > 0:
                return jsonify(status=True, msg="¡Firmware actualizado!"), 200
            else:
                return jsonify(status=False, msg="¡No se realizaron cambios!"), 200
        except Exception as e:
            return jsonify(status=False, msg=f"Error: Firmware no actualizado ({str(e)})"), 500
    else:
        return jsonify(status=False, msg="Error: Datos no proporcionados en formato JSON"), 400 

# Función para crear un nuevo firmware
@firmware_bp.route('/crearFirmware', methods=['POST'])
@jwt_required()
def crear_firmware():
    json_data = request.get_json()
    if json_data:
        try:
            mongo = PyMongo(current_app)
            nombre = json_data.get('nombre')
            idFirmwareInterno = json_data.get('idFirmwareInterno')

            existe_firmware = mongo.db.catFirmwares.find_one({"$or": [{"nombre": nombre}, {"idFirmwareInterno": idFirmwareInterno}]})
            if existe_firmware:
                return jsonify(status=False, msg="¡El Id/Nombre ya existe!"), 200
            else:
                mongo.db.catFirmwares.insert_one(json_data)
                return jsonify(status=True, msg="¡Firmware creado exitosamente!"), 200
        except Exception as e:
            return jsonify(status=False, msg=f"Error al crear firmware: {str(e)}"), 500
    else:
        return jsonify(status=False, msg="Datos no proporcionados en formato JSON"), 400

# Función para actualizar el estatus de todos los firmwares
@firmware_bp.route('/actualizarEstatus', methods=['POST'])
@jwt_required()
def actualizar_estatus():
    try:
        mongo = PyMongo(current_app)
        resultado = mongo.db.catFirmwares.update_many({}, {"$set": {"estatus": True}})
        return jsonify(status=True, msg="Estatus actualizado exitosamente", matched_count=resultado.matched_count, modified_count=resultado.modified_count), 200
    except Exception as e:
        return jsonify(status=False, msg=f"Error al actualizar estatus: {str(e)}"), 500
