from flask import Blueprint, jsonify, request,current_app
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from flask_jwt_extended import jwt_required
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")
usuario_bp = Blueprint('usuarios', __name__, url_prefix='/api/v1/usuario')

@usuario_bp.route('/obtenerUsuarios', methods=['GET'])
@jwt_required()
def get_usuarios():
    try:
        mongo = PyMongo(current_app)
        estatus = request.args.get('estatus', None)
        # Consulta todos los documentos de la colección 'catGae'

        # Construye el filtro basado en el valor del parámetro 'estatus'
        filtro = {}
        if estatus is not None:
            estatus_bool = estatus.lower() == 'true'
            filtro['estatus'] = estatus_bool

        usuarios = list(mongo.db.usuarios.find(filtro))

        for usuario in usuarios:
            usuario['idUsuario']=str(usuario.pop('_id'))
            msg = f"{len(usuarios)} usuarios encontradas"
        return jsonify(usuarios=usuarios, msg=msg, status=True), 200

    except Exception as e:
        # Maneja cualquier error que pueda ocurrir al interactuar con la base de datos
        return jsonify(msg=f"Error al obtener usuarios: {str(e)}"), 500


@usuario_bp.route("/actualizarUsuario", methods=['POST'])
@jwt_required()
def actualizarUsuario():
    json = request.get_json()

    if json != None:
        try:
  
            mongo = PyMongo(current_app)
            idUsuario = json["idUsuario"]
            nuevos_datos = {key: value for key, value in json.items() if key != "idUsuario"}
            print(idUsuario)
            print("nuevos_datos")
            print(nuevos_datos)
            res = mongo.db.usuarios.update_one(
                {"_id": ObjectId(idUsuario)},  # Filtro para encontrar el documento
                {"$set": nuevos_datos}  # Actualización de todas las claves excepto "idUsuario"
            )

            print(res)
            if res.modified_count > 0:
                return jsonify(status=True, msg="¡usuario actualizado!"), 200
            else:
                return jsonify(status=False, msg="¡No se realizaron cambios!"), 200
        except:
            return jsonify(status=False, msg="Error: usuario no actualizado (2)"), 200
    else:
        return jsonify(status=False, msg="Error: usuario no agregado (3)"), 200    


@usuario_bp.route("/crearUsuario", methods=['POST'])
@jwt_required()
def crearUsuario():
    json = request.get_json()

    # Verificar si los datos fueron enviados en la solicitud
    if json is None:
        return jsonify(status=False, msg="Error: Datos faltantes"), 400

    # Verificar que el correo y la contraseña existan
    usuario = json.get("correo")
    pwo = json.get("pwo")

    if not usuario or not pwo:
        return jsonify(status=False, msg="Error: Datos incompletos (correo o contraseña faltante)"), 400

    try:
        # Inicializa la conexión a la base de datos
        mongo = PyMongo(current_app)

        # Verificar si el usuario ya existe
        user_found = mongo.db.usuarios.find_one({"correo": str(usuario)})
        if user_found:
            return jsonify(status=False, msg="¡El usuario ya existe!"), 200

        # Insertar el nuevo usuario en la base de datos
        try:
            mongo.db.usuarios.insert_one(json)
            return jsonify(status=True, msg="¡Usuario creado exitosamente!"), 200
        except Exception as e:
            print("Error al insertar el usuario en la base de datos:", str(e))
            return jsonify(status=False, msg="Error al insertar el usuario en la base de datos"), 500

    except Exception as e:
        # Capturar cualquier otro error no controlado
        print("Error general:", str(e))
        return jsonify(status=False, msg=f"Error: Usuario no agregado ({str(e)})"), 500



