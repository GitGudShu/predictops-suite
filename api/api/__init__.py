from flask import Flask, request
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from dotenv import dotenv_values
from pymongo import MongoClient
import secrets
import datetime
from .auth import auth_blueprint
from .admin import admin_blueprint
from .admin_cta import admin_cta_blueprint
from .data import data_blueprint
from .password import password_blueprint
import os
import pytz

config = dotenv_values(".env")

LOCAL_DB = (config.get('LOCAL_DB', 'False') == 'True')

app_config = {
    'MONGO_URI': config['LOCAL_MONGO_URI'] if LOCAL_DB else config['REMOTE_MONGO_URI'],
    'SECRET_KEY': secrets.token_urlsafe(16),
    'DEBUG': (config.get('DEBUG', 'False') == 'True'),
    'PRODUCTION': (config.get('PRODUCTION', 'False') == 'True'),
    'ALLOW_ORIGIN': config['ALLOW_ORIGIN'],
    'DB_NAME': ('pompier' if config.get('CONTEXT') == 'production' else 'pompier_test'),
}


def create_app():
    basedir = os.path.abspath(os.path.dirname(__file__))
    static_folder = os.path.join(basedir, '../static')
    app = Flask(__name__, static_folder=static_folder)
    CORS(app, supports_credentials=True, origins=app_config['ALLOW_ORIGIN'], methods=["POST", "GET", "OPTIONS", "PATCH", "PUT", "DELETE"], allow_headers=["Content-Type"])
    bcrypt = Bcrypt(app)
    app.config.from_mapping(app_config)
    app.mongo_client = MongoClient(app_config['MONGO_URI'], tz_aware=True)
    app.bcrypt = bcrypt
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(admin_blueprint)
    app.register_blueprint(admin_cta_blueprint)
    app.register_blueprint(data_blueprint)
    app.register_blueprint(password_blueprint)

    @app.route('/api/static/<path:filename>')
    def serve_static(filename):
        return app.send_static_file(filename)

    @app.after_request
    def print_request(response):
        now = datetime.datetime.now(pytz.timezone("Europe/Paris")).strftime('[%d/%b/%Y %H:%M:%S]')
        print(f"{now} \"{request.method} {request.url}\" {response.status_code}")
        return response
    return app


