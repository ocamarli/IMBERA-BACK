from datetime import timedelta
from flask import Flask, request
from flask import jsonify
from config import config
from flask_pymongo import PyMongo
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager, create_refresh_token
from flask_cors import CORS
from User import User, FullTemplate
from bson.objectid import ObjectId
from bson.json_util import dumps, loads
from bson import json_util
from pymongo import ReturnDocument
from dotenv import load_dotenv
import os
import json

load_dotenv()

def create_app(env):
    app = Flask(__name__)
    app.config['DEBUG'] = env.DEBUG
    app.config["MONGO_URI"] = env.MONGO_DATABASE_URI
    app.config["JWT_SECRET_KEY"] = env.JWT_SECRET_KEY
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=100)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)
    app.config.from_object(env)

    return app


env = config['docker']
app = create_app(env)
CORS(app)
jwt = JWTManager(app)
mongo = PyMongo(app)

from rutas.gaes import gae_bp
from rutas.firmwares import firmware_bp
from rutas.auth import auth_bp
from rutas.parametros import parametro_bp
from rutas.hardwares import hardware_bp
from rutas.plantillas import plantilla_bp
from rutas.usuarios import usuario_bp
from rutas.codigos import codigo_bp

app.register_blueprint(gae_bp)
app.register_blueprint(usuario_bp)
app.register_blueprint(firmware_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(parametro_bp)
app.register_blueprint(hardware_bp)
app.register_blueprint(plantilla_bp)
app.register_blueprint(codigo_bp)

@jwt.user_identity_loader
def user_identity_lookup(user):
    return user

@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = jwt_data["sub"]
    user_dict = json.loads(identity)
    user_id = user_dict['id']
    user = mongo.db.usuarios.find_one({'_id': ObjectId(user_id)})

    if user:
        return User(str(user['_id']),user['nombre'], user['correo'],user['permisos'],user['pwo']).toJSON()
    else:
        return None


@app.route("/")
def root():
    return "Works!!"


if __name__ == '__main__':
     port = int(os.getenv('RUN_PORT', 5000))
     app.run(host='0.0.0.0', port=port)
