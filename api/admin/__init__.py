from flask import Blueprint

admin_blueprint = Blueprint('admin', __name__, url_prefix='/api/admin')

from .admin_routes import *