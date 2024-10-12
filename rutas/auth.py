from flask import Blueprint, jsonify, request,current_app
from User import User
from flask_pymongo import PyMongo
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager, create_refresh_token
from bson.objectid import ObjectId
import os
import random
import json
from cryptography.fernet import Fernet
from dotenv import load_dotenv
import os
load_dotenv()


auth_bp = Blueprint('auth', __name__, url_prefix='/api/v1')
SECRET_KEY = os.getenv('SALT')

@auth_bp.route('/login', methods=['POST'])
def login():
    json = request.get_json()
    if json is not None:
        usuario = json.get("usuario")
        pwo = json.get("pwo")

        if not usuario or not pwo:
            return jsonify(status=False, msg="Datos incompletos"), 400

        try:
            # Conectar a la base de datos
            mongo = PyMongo(current_app)
            user = mongo.db.usuarios.find_one({"correo": usuario, "estatus": True})

            if user:
                # Comparar el hash enviado con el hash almacenado en la base de datos
                stored_hash = user['pwo']

                if pwo == stored_hash:
                    # Si el hash coincide, generar el access token y el refresh token
                    ity = User(str(user['_id']), user["nombre"], user["correo"], user["permisos"], user["pwo"]).toJSON()
                    access_token = create_access_token(identity=ity)
                    refresh_token = create_refresh_token(identity=ity)

                    return jsonify(access_token=access_token, refresh_token=refresh_token, msg="Access token granted", status=True), 200
                else:
                    return jsonify(status=False, msg='Contraseña/Usuario incorrecto!'), 200
            else:
                return jsonify(status=False, msg='Contraseña/Usuario incorrecto!'), 200

        except Exception as e:
            return jsonify(status=False, msg=f"Error: No se encontró información de [{str(usuario)}], {str(e)}"), 500
    else:
        return jsonify(status=False, msg="No se encontró información del usuario!"), 400
    
@auth_bp.route('/db/crearColecciones', methods=['POST'])
def crear_colecciones():
    try:
        
        mongo = PyMongo(current_app)
        db = mongo.db  
        collections = [
            'catFirmwares',
            'catGae',
            'catHardwares',
            'codigoProgramaciones',
            'codigos',
            'parameters',
            'plantillas',
            'templates',
            'usuarios'
        ]
        created_collections = []
        for collection_name in collections:

            if collection_name not in db.list_collection_names():
                db.create_collection(collection_name)
                created_collections.append(collection_name)

        if created_collections:
            return jsonify(status=True, msg="Colecciones creadas", created_collections=created_collections), 201
        else:
            return jsonify(status=True, msg="Todas las colecciones ya existen"), 200
    except Exception as e:
        return jsonify(status=False, msg=str(e)), 500


@auth_bp.route('usuario/obtenerUsuario/<string:idUsuario>', methods=['GET'])
@jwt_required()
def obtenerUsuario(idUsuario):
    if idUsuario:
        print(idUsuario)
        usuario = ""
        try:
            mongo = PyMongo(current_app)
            usuario = mongo.db.usuarios.find_one({"_id": ObjectId(str(idUsuario))})
            if usuario:
                usuario['idUsuario'] = str(usuario.pop('_id'))
                return jsonify(status=True, usuario=usuario, msg="Usuario encontrado"), 200
            else:
                return jsonify(status=False, msg="Usuario no encontrado"), 404
        except Exception as e:
            return jsonify(status=False, msg=str(e)), 500
    else:
        return jsonify(status=False, msg="ID de usuario no especificado"), 400
    # Lógica para registrar un nuevo usuario
@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token)
    # Lógica para generar un nuevo token de acceso usando un token de actualización

    
@auth_bp.route('/agregarEsValorFijo', methods=['GET'])
@jwt_required()
def agregar_es_valor_fijo():
    try:
        mongo = PyMongo(current_app)
        # Actualiza todos los documentos en la colección 'parametross' agregando 'esValorFijo': true
        resultado = mongo.db.catGae.update_many({}, {"$set": {"estatus": True }})
        
        # Prepara la respuesta JSON con el número de documentos modificados
        return jsonify(status=True, msg="Campo 'esValorFijo' agregado a todos los documentos", matched_count=resultado.matched_count, modified_count=resultado.modified_count), 200

    except Exception as e:
        # Maneja cualquier error que pueda ocurrir al interactuar con la base de datos
        return jsonify(status=False, msg=f"Error al agregar el campo 'esValorFijo': {str(e)}"), 500


@auth_bp.route('/renombrarIdParametro', methods=['GET'])
@jwt_required()
def renombrar_id_parametro():
    try:
        mongo = PyMongo(current_app)
        
        # Utiliza un pipeline de agregación para renombrar el campo `idParametro` a `idParametroInterno`
        pipeline = [
            {
                "$addFields": {
                    "idParametroInterno": "$idParametro"
                }
            },
            {
                "$unset": "idParametro"
            }
        ]

        # Ejecuta el pipeline de agregación para todos los documentos
        mongo.db.parameters.update_many({}, pipeline)
        
        return jsonify(status=True, msg="Campo 'idParametro' renombrado a 'idParametroInterno' en todos los documentos"), 200

    except Exception as e:
        # Maneja cualquier error que pueda ocurrir al interactuar con la base de datos
        return jsonify(status=False, msg=f"Error al renombrar el campo 'idParametro': {str(e)}"), 500
    
@auth_bp.route('/obtenerListaDe', methods=['GET'])
@jwt_required()
def obtener_usuarios():
    try:
        mongo = PyMongo(current_app)

        usuarios = mongo.db.usuarios.find()
        usuarios_list = list(usuarios)
        for usuario in usuarios_list:
            usuario['_id'] = str(usuario['_id']) 
        return jsonify(status=True, usuarios=usuarios_list), 200
    except Exception as e:
        return jsonify(status=False, msg=f"Error al obtener usuarios: {str(e)}"), 500


@auth_bp.route('/actualizarMitadEsValorFijo', methods=['GET'])
@jwt_required()
def actualizar_mitad_es_valor_fijo():
    try:
        mongo = PyMongo(current_app)
        todos_documentos = list(mongo.db.parameters.find({}))
        mitad_total = len(todos_documentos) // 2
        documentos_seleccionados = random.sample(todos_documentos, mitad_total)
        ids_seleccionados = [doc['_id'] for doc in documentos_seleccionados]
        resultado = mongo.db.parameters.update_many(
            {"_id": {"$in": ids_seleccionados}},
            {"$set": {"esValorFijo": False}}
        )
        return jsonify(
            status=True, 
            msg="Campo 'esValorFijo' actualizado a false en la mitad de los documentos", 
            matched_count=resultado.matched_count, 
            modified_count=resultado.modified_count
        ), 200
    except Exception as e:
        return jsonify(status=False, msg=f"Error al actualizar el campo 'esValorFijo': {str(e)}"), 500
@auth_bp.route('/cargarParametrosDesdeArchivo', methods=['GET'])
def cargar_parametros_desde_archivo():
    try:

        archivo_parametros_path = os.path.join(current_app.root_path, 'data/parametros.json')
        with open(archivo_parametros_path, 'r', encoding='utf-8') as archivo_parametros:
            json_parametros_data = json.load(archivo_parametros)

        archivo_usuarios_path = os.path.join(current_app.root_path, 'data/usuarios.json')
        with open(archivo_usuarios_path, 'r', encoding='utf-8') as archivo_parametros:
            json_usuarios_data = json.load(archivo_parametros)            

        archivo_gaes_path = os.path.join(current_app.root_path, 'data/gaes.json')
        with open(archivo_gaes_path, 'r', encoding='utf-8') as archivo_gaes:
            json_gaes_data = json.load(archivo_gaes)

        archivo_codigos_path = os.path.join(current_app.root_path, 'data/codigos.json')
        with open(archivo_codigos_path, 'r', encoding='utf-8') as archivo_codigos:
            json_codigos_data = json.load(archivo_codigos)            

        # Validar que ambos archivos contienen listas
        if json_parametros_data and isinstance(json_parametros_data, list) and json_gaes_data and isinstance(json_gaes_data, list)and json_usuarios_data and isinstance(json_usuarios_data, list) and json_codigos_data and isinstance(json_codigos_data, list):
            mongo = PyMongo(current_app)
            
            # Insertar parámetros en la colección 'parameters'
            mongo.db.parameters.insert_many(json_parametros_data)
            mongo.db.usuarios.insert_many(json_usuarios_data)
            mongo.db.codigos.insert_many(json_codigos_data)
            # Insertar gaes en la colección 'catGae'
            mongo.db.catGae.insert_many(json_gaes_data)
            
            return jsonify(status=True, msg="Parámetros y Gaes agregados correctamente"), 200
        else:
            return jsonify(status=False, msg="Error: datos no proporcionados en formato JSON o no son listas"), 400
    except Exception as e:
        return jsonify(status=False, msg=f"Error: documentos no agregados ({str(e)})"), 500

@auth_bp.route('/eliminarTodosParametros', methods=['GET'])
@jwt_required()
def eliminar_todos_parametros():
    try:
        mongo = PyMongo(current_app)
        resultado = mongo.db.parameters.delete_many({})
        return jsonify(status=True, msg=f"Eliminados {resultado.deleted_count} parámetros correctamente"), 200
    except Exception as e:
        return jsonify(status=False, msg=f"Error: no se pudieron eliminar los parámetros ({str(e)})"), 500    