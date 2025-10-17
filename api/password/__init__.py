from flask import Blueprint

password_blueprint = Blueprint('password', __name__, url_prefix='/api/password')

from .password_routes import *

