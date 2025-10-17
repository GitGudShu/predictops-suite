from . import auth_blueprint
from flask import request, jsonify, make_response, current_app
from datetime import datetime, timedelta
from utils.errors_utils import handle_exception
from utils.auth_utils import generate_auth_token, set_auth_cookie
from utils.token_utils import verify_token, token_required
@auth_blueprint.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data["email"]
        password = data["password"]
        keep_session = data["keepSession"]

        client = current_app.mongo_client
        collection = client[current_app.config.get('DB_NAME', 'pompier')]["predictops_users"]
        user = collection.find_one({"email": email})

        if user and current_app.bcrypt.check_password_hash(user['password'], password) and user.get('active') == False:
            return jsonify({"message": "Utilisateur désactivé, veuillez contacter l'administrateur."}), 403

        if user and current_app.bcrypt.check_password_hash(user['password'], password):
            token, expiration_time = generate_auth_token(user, keep_session)
            user_email = user.get('email')
            user_dpt = user.get('dpt')
            user_role = user.get('role')
            user_dict = dict(email=user_email, dpt=user_dpt, role=user_role, token=token)
            collection.update_one({"email": email}, {"$set": {"last_login": datetime.now(), "number_of_logins": user.get('number_of_logins', 0) + 1}})
            response = make_response(jsonify(user_dict))
            set_auth_cookie(response, token, expiration_time, current_app)
            return response
        else:
            return jsonify({"message": "L'authentification a echoué."}), 403

    except Exception as e:
        return handle_exception(e)
    
@auth_blueprint.route('/logout', methods=['POST'])
def logout():
    try:
        response = make_response(jsonify({"message": "Logged out"}))
        response.delete_cookie('authToken', samesite='None', secure=True)
        return response

    except Exception as e:
        return handle_exception(e)

@auth_blueprint.route('/check-auth', methods=['POST'])
@token_required
def check_auth():
    try:
        is_valid, message, role = verify_token()
        if is_valid:
            return jsonify({'isAuthenticated': True}), 200
        else:
            return jsonify({'isAuthenticated': False}), 401

    except Exception as e:
        return handle_exception(e)
        


