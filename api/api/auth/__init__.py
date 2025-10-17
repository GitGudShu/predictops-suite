from flask import Blueprint

auth_blueprint = Blueprint('auth', __name__, url_prefix='/api/auth')

from .auth_routes import *