from flask import Blueprint
from utils.token_utils import admin_cta_required
admin_cta_blueprint = Blueprint('admin_cta', __name__, url_prefix='/api/admin-cta')

from .admin_cta_routes import *