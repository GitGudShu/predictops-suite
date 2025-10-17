from . import password_blueprint
from flask import request, jsonify, make_response, current_app
import os
from datetime import datetime
from utils.errors_utils import handle_exception
from utils.token_utils import token_required, generate_password_reset_token
from utils.email_utils import send_email, default_mail_template
import pytz

PRODUCTION = os.getenv("PRODUCTION", "False") == "True"

@password_blueprint.route("/update", methods=["POST"])
@token_required
def update_password():
    bcrypt = current_app.bcrypt
    client = current_app.mongo_client
    collection = client[current_app.config.get('DB_NAME', 'pompier')]["predictops_users"]
    try:
        data = request.json
        email = data["email"]
        old_password = data["old_password"]
        new_password = data["new_password"]
        user = collection.find_one({"email" : email})
        if old_password == new_password:
            return jsonify({"message": "Le nouveau mot de passe doit être different du mot de passe actuel."}), 403
        if user and bcrypt.check_password_hash(user['password'], old_password):
            new_password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
            collection.update_one({"email": email}, {"$set": {"password": new_password_hash}})
            return jsonify({"message": "Changement avec succès."}), 200
        else:
            return jsonify({"message": "Mot de passe incorrect."}), 403
    except Exception as e:
        return handle_exception(e)

@password_blueprint.route("/forgotten", methods=["POST"])
def forgotten_password():
    client = current_app.mongo_client
    collection = client[current_app.config.get('DB_NAME', 'pompier')]["predictops_users"]
    try:
        data = request.json
        email = data["email"]
        base_url = "https://dashboard.predictops.fr/predictops" if PRODUCTION else "http://localhost:9000"
        user = collection.find_one({"email" : email})
        if not user:
            return jsonify({"message": "Email introuvable. Assurez-vous d'avoir entré l'email correctement."}), 404
        token, expiration_time = generate_password_reset_token()
        reset_link = f"{base_url}/password/reset?token={token}"
        collection.update_one(
            {"email": email},
            {"$set": {"reset_token": token, "reset_token_expiration": expiration_time}},
        )
        formatted_message = default_mail_template.format(message=f"Veuillez cliquer sur ce lien pour reinitialiser votre mot de passe : <a href=\"{reset_link}\">{reset_link}</a> Si vous n'avez pas fait cette demande, veuillez ignorer cet email. <span style='font-size: 12px; color: #666; margin-top: 20px;'>Ce lien expirera dans 15 minutes.</span>")
        c = send_email(email, "Demande de réinitialisation de mot de passe", formatted_message)
        if c == 200:
            return jsonify({"message": "Mail envoyé. Pensez à regarder vos spams."}), c
        else:
            return jsonify({"message": "Une erreur s'est produite lors de l'envoi du mail."}), c
            
    except Exception as e:
        return handle_exception(e)

@password_blueprint.route("/reset", methods=["POST"])
def reset_password():
    bcrypt = current_app.bcrypt
    client = current_app.mongo_client
    collection = client[current_app.config.get('DB_NAME', 'pompier')]["predictops_users"]
    try:
        data = request.json
        token = data["token"]
        new_password = data["new_password"]

        user = collection.find_one({"reset_token": token, "reset_token_expiration": {"$gte": datetime.now(pytz.timezone('Europe/Paris'))}})
        if not user:
            return jsonify({"message": "Le token n'est plus valide. Veuillez réessayer."}), 403

        existing_password = user.get("password")
        if existing_password and bcrypt.check_password_hash(existing_password, new_password):
            return jsonify({"message": "Le nouveau mot de passe doit être different du mot de passe actuel."}), 403
        
        new_password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
        collection.update_one({"email": user["email"]}, {"$set": {"password": new_password_hash}, "$unset": {"reset_token": "", "reset_token_expiration": ""}})
        formatted_message = default_mail_template.format(message="Votre mot de passe a été réinitialisé avec succès. Si vous n'êtes pas à l'origine de cette requête, veuillez contacter l'administrateur.")
        c = send_email(user["email"], "Réinitialisation du mot de passe", formatted_message)
        if c == 200:
            return jsonify({"message": "Le mot de passe a été reinitialisé avec succes."}), 200
        else:
            return jsonify({"message": "Une erreur s'est produite lors de l'envoi du mail."}), 500
    except Exception as e:
        return handle_exception(e)

@password_blueprint.route("/check-password-reset-token", methods=["POST"])
def check_password_reset_token():
    client = current_app.mongo_client
    collection = client[current_app.config.get('DB_NAME', 'pompier')]["predictops_users"]
    try:
        data = request.json
        token = data["token"]
        if not token:
            return jsonify({"message": "Le token est manquant."}), 400
        
        user = collection.find_one({"reset_token": token, "reset_token_expiration": {"$gte": datetime.now(pytz.timezone('Europe/Paris'))}})
        if user:
            return jsonify({"message": "Le token est valide."}), 200
        else:
            return jsonify({"message": "Le token n'est pas valide ou est expiré."}), 403
    except Exception as e:
        return handle_exception(e)