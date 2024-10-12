from flask import Blueprint, jsonify, request, current_app
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

hardware_bp = Blueprint('hardwares', __name__, url_prefix='/api/v1/hardware')

# Función para obtener todos los hardwares
@hardware_bp.route('/obtenerHardwares', methods=['GET'])
def obtener_hardwares():
    try:
        mongo = PyMongo(current_app)
        estatus = request.args.get('estatus', None)
        
        # Construye el filtro basado en el valor del parámetro 'estatus'
        filtro = {}
        if estatus is not None:
            estatus_bool = estatus.lower() == 'true'
            filtro['estatus'] = estatus_bool

        # Consulta los documentos de la colección 'catHardwares' basados en el filtro
        hardwares = list(mongo.db.catHardwares.find(filtro))

        for hardware in hardwares:
            hardware['idHardware'] = str(hardware.pop('_id'))

        msg = f"{len(hardwares)} hardwares encontradas"
        return jsonify(hardwares=hardwares, msg=msg, status=True), 200

    except Exception as e:
        # Maneja cualquier error que pueda ocurrir al interactuar con la base de datos
        return jsonify(msg=f"Error al obtener hardwares: {str(e)}"), 500

# Función para obtener un hardware por su ID
@hardware_bp.route('/obtenerHardware/<string:idHardware>', methods=['GET'])
def obtener_hardware(idHardware):
    if idHardware:
        try:
            mongo = PyMongo(current_app)
            hardware = mongo.db.catHardwares.find_one({"_id": ObjectId(idHardware)})
            if hardware:
                hardware['idHardware'] = str(hardware.pop('_id'))
                return jsonify(status=True, hardware=hardware, msg="hardware encontrado"), 200
            else:
                return jsonify(status=False, msg="hardware no encontrado"), 404
        except Exception as e:
            return jsonify(status=False, msg=str(e)), 500
    else:
        return jsonify(status=False, msg="ID de hardware no especificado"), 400    

# Función para actualizar un hardware
@hardware_bp.route("/actualizarHardware", methods=['POST'])
def actualizar_hardware():
    json_data = request.get_json()
    if json_data:
        try:
            mongo = PyMongo(current_app)
            idHardware = json_data.get("idHardware")
            nombreHardware = json_data.get("nombre", None)

            if nombreHardware:
                # Verificar si ya existe otro hardware con el mismo nombre
                existing_hardware = mongo.db.catHardwares.find_one(
                    {"nombre": nombreHardware, "_id": {"$ne": ObjectId(idHardware)}}
                )
                if existing_hardware:
                    return jsonify(status=False, msg="¡ya existe hardware!"), 200

            nuevos_datos = {key: value for key, value in json_data.items() if key != "idHardware"}
            print(nuevos_datos)
            res = mongo.db.catHardwares.update_one(
                {"_id": ObjectId(idHardware)},
                {"$set": nuevos_datos}
            )
            if res.modified_count > 0:
                return jsonify(status=True, msg="¡Hardware actualizado!"), 200
            else:
                return jsonify(status=False, msg="¡No se realizaron cambios!"), 200
        except Exception as e:
            return jsonify(status=False, msg=f"Error: Hardware no actualizado ({str(e)})"), 500
    else:
        return jsonify(status=False, msg="Error: Datos no proporcionados en formato JSON"), 400

# Función para crear un nuevo hardware
@hardware_bp.route('/crearHardware', methods=['POST'])
def crear_hardware():
    json_data = request.get_json()
    if json_data:
        try:
            mongo = PyMongo(current_app)
            nombre = json_data.get('nombre')
            idHardwareInterno = json_data.get('idHardwareInterno')

            existe_hardware = mongo.db.catHardwares.find_one({"$or": [{"nombre": nombre}, {"idHardwareInterno": idHardwareInterno}]})
            if existe_hardware:
                return jsonify(status=False, msg="¡El Id/Nombre ya existe!"), 200
            else:
                mongo.db.catHardwares.insert_one(json_data)
                return jsonify(status=True, msg="¡Hardware creado exitosamente!"), 200
        except Exception as e:
            return jsonify(status=False, msg=f"Error al crear hardware: {str(e)}"), 500
    else:
        return jsonify(status=False, msg="Datos no proporcionados en formato JSON"), 400

# Función para actualizar el estatus de todos los hardwares
@hardware_bp.route('/actualizarEstatus', methods=['POST'])
def actualizar_estatus():
    try:
        mongo = PyMongo(current_app)
        resultado = mongo.db.catHardwares.update_many({}, {"$set": {"estatus": True}})
        return jsonify(status=True, msg="Estatus actualizado exitosamente", matched_count=resultado.matched_count, modified_count=resultado.modified_count), 200
    except Exception as e:
        return jsonify(status=False, msg=f"Error al actualizar estatus: {str(e)}"), 500
