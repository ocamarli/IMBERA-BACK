#"MONGO_DATABASE_URI = 'mongodb://localhost:27017/vikkon'"
    #MONGO_USERNAME = ''
    #MONGO_PASSWORD = ''
    #API_JWT_SECRET = ''
#class DevelopmentConfig(Config):
    #DEBUG = False
    #MONGO_DATABASE_URI = 'mongodb+srv://ocamar:xrfmX3Sr1YKv9S4k@vikkon.tdfkmfc.mongodb.net/imbvikkon?retryWrites=true&w=majority'
    #MONGO_USERNAME = 'ocamar'
    #MONGO_PASSWORD = 'xrfmX3Sr1YKv9S4k'
    #API_JWT_SECRET = ''
    #mongodb://host.docker.internal:27017/vikkon

from dotenv import load_dotenv
import os
load_dotenv()

class Config:
    pass

class DevelopmentConfig(Config):
    DEBUG = False
    MONGO_DATABASE_URI = os.getenv('MONGO_DATABASE_URI')
    MONGO_USERNAME = os.getenv('MONGO_USERNAME', '')
    MONGO_PASSWORD = os.getenv('MONGO_PASSWORD', '')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', '')
class LocalConfig(Config):
    DEBUG = True
    MONGO_DATABASE_URI = 'mongodb://localhost:27017/vikkon'
    MONGO_USERNAME = ''
    MONGO_PASSWORD = ''
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', '')
class DockerConfig(Config):
    DEBUG = True
    MONGO_DATABASE_URI = os.getenv('MONGO_DATABASE_URI', 'mongodb://mongodbvikkon:27017/vikkon')
    MONGO_USERNAME = os.getenv('MONGO_USERNAME', '')
    MONGO_PASSWORD = os.getenv('MONGO_PASSWORD', '')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', '')
 

config = {
    'development': DevelopmentConfig,
    'local': LocalConfig,
    'docker': DockerConfig,
}
