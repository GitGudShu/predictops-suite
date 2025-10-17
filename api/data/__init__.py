from flask import Blueprint
from utils.token_utils import token_required
data_blueprint = Blueprint('data', __name__, url_prefix='/api/data')

@data_blueprint.before_request
@token_required
def require_token():
    pass 

from .data_routes import *

