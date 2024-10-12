from flask import Blueprint, jsonify, request,current_app
from flask_pymongo import PyMongo
from flask_jwt_extended import jwt_required
from bson.objectid import ObjectId
from datetime import datetime, timezone
import pytz

timezone_mx = pytz.timezone('America/Mexico_City')
plantilla_bp = Blueprint('plantillas', __name__, url_prefix='/api/v1/plantilla')

@plantilla_bp.route('/obtenerPlantilla/<string:idPlantilla>', methods=['GET'])
@jwt_required()
def obtener_plantilla(idPlantilla):
    if idPlantilla is not None:
        try:
            mongo = PyMongo(current_app)
            print(idPlantilla)
            plantilla = mongo.db.plantillas.find_one({"_id": ObjectId(str(idPlantilla))})
            
            if plantilla:
                # Recorrer los parámetros generales de la plantilla
                for parametro in plantilla['parametrosGenerales']:
                    # Obtener el objeto completo del parámetro
                    print(parametro)
                    parametro_completo = mongo.db.parameters.find_one({"idParametroInterno": parametro["idParametroInterno"]},{"_id":0})
                    # Agregar la información completa al parámetro en la plantilla
                    parametro.update(parametro_completo)

                # Recorrer las programaciones de la plantilla
                for programacion in plantilla['programaciones']:
                    # Recorrer los parámetros de cada programación
                    for parametro in programacion['parametros']:
                        # Obtener el objeto completo del parámetro
                        parametro_completo = mongo.db.parameters.find_one({"idParametroInterno": parametro["idParametroInterno"]},{"_id":0})
                        # Agregar la información completa al parámetro en la programación
                        parametro.update(parametro_completo)

                plantilla['idPlantilla'] = str(plantilla.pop('_id'))
                return jsonify(status=True, plantilla=plantilla, msg="Plantilla encontrada"), 200
            else:
                return jsonify(status=False, msg="Plantilla no encontrada"), 404
        except Exception as e:
            return jsonify(status=False, msg=str(e)), 500
        

@plantilla_bp.route('/obtenerPlantillas', methods=['GET'])
@jwt_required()
def obtener_plantillas():
    try:
        mongo = PyMongo(current_app)
        estatus = request.args.get('estatus', None)
        
        # Construye el filtro basado en el valor del parámetro 'estatus'
        filtro = {}
        if estatus is not None:
            estatus_bool = estatus.lower() == 'true'
            filtro['estatus'] = estatus_bool

        # Consulta los documentos de la colección 'catPlantillas' basados en el filtro
        plantillas = list(mongo.db.plantillas.find(filtro))

        for plantilla in plantillas:
            plantilla['idPlantilla'] = str(plantilla.pop('_id'))

        msg = f"{len(plantillas)} plantillas encontradas"
        return jsonify(plantillas=plantillas, msg=msg, status=True), 200

    except Exception as e:
        # Maneja cualquier error que pueda ocurrir al interactuar con la base de datos
        return jsonify(msg=f"Error al obtener plantillas: {str(e)}"), 500


@plantilla_bp.route('/clonarPlantilla', methods=['POST'])
@jwt_required()
def clonarPlantilla():
    json = request.get_json()
    if json:
        try:
            mongo = PyMongo(current_app)
            nuevo_id = ObjectId()
            idPlantilla = json["idPlantilla"]
            nombrePlantilla = json["nombrePlantilla"]
            creadoPor = json["creadoPor"]
            idPlantillaInterno= json["idPlantillaInterno"]

            # Verificar si ya existe una plantilla con el mismo nombre
            plantilla_existente = mongo.db.plantillas.find_one({"$or":[{"nombrePlantilla": nombrePlantilla},{"idPlantillaInterno":idPlantillaInterno}]})
            if plantilla_existente:
                return jsonify(status=False, msg="¡La plantilla ya existe!"), 200

            original_plantilla = mongo.db.plantillas.find_one({"_id": ObjectId(str(idPlantilla))})

            if original_plantilla:
                nuevaPlantilla = original_plantilla.copy()
                nuevaPlantilla['_id'] = nuevo_id
                nuevaPlantilla['nombrePlantilla'] = nombrePlantilla
                nuevaPlantilla['idPlantillaInterno'] = idPlantillaInterno
                nuevaPlantilla['notas']=[{"creadaPor":creadoPor,"nota":"Plantilla clonada","fechaCreada": datetime.now(timezone.utc)}]
                nuevaPlantilla['creadoPor'] = creadoPor

                result = mongo.db.plantillas.insert_one(nuevaPlantilla)

                idPlantilla = str(result.inserted_id)
                return jsonify(status=True, idPlantilla=idPlantilla, msg="¡Plantilla clonada correctamente!"), 200
            else:
                return jsonify(status=False, msg="Plantilla original no encontrada"), 404
        except Exception as e:
            return jsonify(status=False, msg=str(e)), 500
    else:
        return jsonify(status=False, msg="Datos no proporcionados en formato JSON"), 400

@plantilla_bp.route('/crearPlantilla', methods=['POST'])
@jwt_required()
def crearPlantilla():
    json_data = request.get_json()
    if json_data != None:
        try:
            mongo = PyMongo(current_app)
            # Insertar el documento en la colección de plantillas
            
            idPlantillaInterno = json_data.get('idPlantillaInterno')
            nombrePlantilla =  json_data.get('nombrePlantilla')
            
            existe_plantilla = mongo.db.plantillas.find_one({"$or": [{"idPlantillaInterno": idPlantillaInterno}, {"nombrePlantilla": nombrePlantilla}]})
            if existe_plantilla:
                return jsonify(status=False, msg="¡El Id/nombre ya existe!"), 200
            else:
                
                for nota in json_data['notas']:
                    nota['fechaCreada'] = datetime.now(timezone.utc)

                result = mongo.db.plantillas.insert_one(json_data)
                return jsonify(status=True, msg="¡plantilla creada exitosamente!"), 200
            # Obtener el _id generado por MongoDB
            idPlantilla = str(result.inserted_id)
        except Exception as e:
            return jsonify(status=False, msg=f"Error al crear plantilla: {str(e)}"), 500
    else:
        return jsonify(status=False, msg="Parametros faltantes en la petición (200)"), 200
# Función para actualizar un GAE
@plantilla_bp.route("/actualizarPlantilla", methods=['POST'])
@jwt_required()
def actualizar_plantilla():
    json_data = request.get_json()
    if json_data:
        try:
            mongo = PyMongo(current_app)
            idPlantilla = json_data.get("idPlantilla")
            print(json_data)
            nuevos_datos = {key: value for key, value in json_data.items() if key != "idPlantilla" and key != "notas"}
            nueva_nota = json_data.get("notas")
            print("nueva_nota",nueva_nota)
            update_query = {"$set": nuevos_datos}
            if nueva_nota:
                print("siNuevaNota")
                update_query = { "$push": {"notas": { **nueva_nota, "fechaCreada": datetime.now(timezone.utc)}}}
                print("update_query",update_query)
            res = mongo.db.plantillas.update_one(
                {"_id": ObjectId(idPlantilla)},
                update_query
            )

            if res.modified_count > 0:
                return jsonify(status=True, msg="¡Plantilla actualizada!"), 200
            else:
                return jsonify(status=False, msg="¡No se realizaron cambios!"), 200
        except Exception as e:
            print("error",e)
            return jsonify(status=False, msg=f"¡Error: Plantilla no actualizada ({str(e)})!"), 500
    else:
        return jsonify(status=False, msg="Error: Datos no proporcionados en formato JSON"), 400   
    
@plantilla_bp.route('/actualizarParametro', methods=['POST'])
@jwt_required()
def actulizarParametroPlantilla():
    json = request.get_json()
    print("dataUpdate",json)
    if json is not None:
        try:
            mongo = PyMongo(current_app)
            idPlantilla=json["data"]["idPlantilla"]
            idParametro=json["data"]["idParametro"]
            valor=json["data"]["valor"]
            noProgramacion=json["data"]["noProgramacion"]
            estatus=json["data"]["estatus"]
            if(noProgramacion==0):
                result = mongo.db.plantillas.update_one({"_id": ObjectId(str(idPlantilla)), 'parametrosGenerales.idParametroInterno': idParametro},
                                                    {'$set': {'parametrosGenerales.$.valor': valor,'parametrosGenerales.$.estatus': estatus}})                      
            else:
 
                result = mongo.db.plantillas.update_one(
                    {"_id": ObjectId(str(idPlantilla)), "programaciones.noProgramacion": str(noProgramacion), "programaciones.parametros.idParametroInterno": str(idParametro)},
                    {"$set": {"programaciones.$[outer].parametros.$[inner].valor": str(valor),"programaciones.$[outer].parametros.$[inner].estatus": estatus}},
                    array_filters=[{"outer.noProgramacion": str(noProgramacion)}, {"inner.idParametroInterno": str(idParametro)}]

                   
                )           
            print(result)
            if result.modified_count > 0:
                return jsonify(status=True, msg="parametro actualizado"), 200
            else:
                return jsonify(status=False, msg="Error: plantilla/parametro no encontrado(100)"), 200
        except:
            return jsonify(status=False, msg="Error: parametro no actualizado(200)"), 200
    else:
        return jsonify(status=False, msg="Error: parametro no actualizado(300)"), 400

@plantilla_bp.route('/verificarParametros', methods=['GET'])
def verificarParametros():
    idPlantilla = request.args.get('idPlantilla')
    
    if idPlantilla is not None:
        try:
            mongo = PyMongo(current_app)
            plantilla = mongo.db.plantillas.find_one({"_id": ObjectId(idPlantilla)})

            if not plantilla:
                return jsonify(status=False, msg="Plantilla no encontrada"), 404

            # Obtener los programas habilitados
            programas_habilitados = plantilla.get('programasHabilitados', [])

            # Verificar parametrosGenerales
            parametros_generales_faltantes = [param['idParametroInterno'] for param in plantilla['parametrosGenerales'] if not param['estatus']]
            
            # Verificar programaciones
            programaciones_faltantes = {}
            for programacion in plantilla['programaciones']:
                if programacion['noProgramacion'] in programas_habilitados:
                    parametros_faltantes = [param['idParametroInterno'] for param in programacion['parametros'] if not param['estatus']]
                    if parametros_faltantes:
                        programaciones_faltantes[programacion['noProgramacion']] = parametros_faltantes

            if not parametros_generales_faltantes and not programaciones_faltantes:
                return jsonify(status=True, msg="Parámetros están completos"), 200
            else:
                return jsonify(
                    status=False,
                    msg="¡Parámetros incompletos!",
                    parametros_generales_faltantes=parametros_generales_faltantes,
                    programaciones_faltantes=programaciones_faltantes
                ), 200
        except Exception as e:
            return jsonify(status=False, msg=f"Error: {str(e)}"), 500
    else:
        return jsonify(status=False, msg="ID de plantilla no proporcionado"), 400
    
    