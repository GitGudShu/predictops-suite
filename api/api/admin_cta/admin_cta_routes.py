from . import admin_cta_blueprint
from flask import request, jsonify, make_response, current_app
from datetime import datetime, timedelta
from utils.errors_utils import handle_exception
from utils.token_utils import admin_cta_required
from utils.email_utils import send_email, guideline_mail_template
from utils.misc_utils import generate_profile_image, get_initials_from_email, get_color
from pymongo import errors, DESCENDING
import pytz
import secrets
import string
import uuid
   
    
@admin_cta_blueprint.route("/create-active-chain-of-command", methods=["POST"])
@admin_cta_required
def create_active_chain_of_command():
    client = current_app.mongo_client
    collection = client[current_app.config.get('DB_NAME', 'pompier')]["active_cdc"]
    data = request.json
    try:
        # Generate a unique UUID for the card
        new_id = str(uuid.uuid4())

        # Determine the new order value based on the current maximum order
        max_order = collection.find_one(sort=[("order", -1)], projection={"order": 1})
        new_order = (max_order["order"] + 1) if max_order else 1

        # Assign new UUID and order
        data['id'] = new_id
        data['order'] = new_order
        data['editing'] = False

        collection.insert_one(data)
        return jsonify({"success": True, "id": new_id}), 201
    except Exception as e:
        return handle_exception(e)
    
@admin_cta_blueprint.route("/create-special-chain-of-command", methods=["POST"])
@admin_cta_required
def create_special_chain_of_command():
    client = current_app.mongo_client
    collection = client[current_app.config.get('DB_NAME', 'pompier')]["active_cdc"]
    data = request.json
    try:
        # Generate a unique UUID for the special card
        new_id = str(uuid.uuid4())

        # Check if a card is already in the second position
        existing_second_card = collection.find_one({"order": 2})
        if existing_second_card:
            # Shift all cards after the second position
            collection.update_many(
                {"order": {"$gte": 2}},
                {"$inc": {"order": 1}}
            )

        # Assign the special card to the second position
        data['id'] = new_id
        data['order'] = 2
        data['special'] = True

        collection.insert_one(data)
        return jsonify({"success": True, "id": new_id}), 201
    except Exception as e:
        return handle_exception(e)
    
@admin_cta_blueprint.route("/update-active-chain-of-command", methods=["PATCH"])
@admin_cta_required
def update_active_chain_of_command():
    client = current_app.mongo_client
    collection = client[current_app.config.get('DB_NAME', 'pompier')]["active_cdc"]
    data = request.json
    id = data.get("id", None)

    if id is None:
        return jsonify({"error": "ID is missing in the request data."}), 400

    try:
        # Ensure that the update doesn't affect the order field unless specifically modified
        order = data.get("order", None)
        data["editing"] = False
        if order is not None:
            # Check if there's a conflict in the desired order position
            existing_card = collection.find_one({"order": order, "id": {"$ne": id}, "dpt": data["dpt"]})
            if existing_card:
                return jsonify({"error": "Another card already has this order position."}), 409

        result = collection.update_one({"id": id}, {"$set": data})
        if result.matched_count == 0:
            return jsonify({"error": "No card found with the given ID."}), 404
        return jsonify({"success": True}), 200
    except Exception as e:
        return handle_exception(e)
    
@admin_cta_blueprint.route("/delete-active-chain-of-command/<string:card_id>", methods=["DELETE"])
@admin_cta_required
def delete_active_chain_of_command(card_id):
    client = current_app.mongo_client
    collection = client[current_app.config.get('DB_NAME', 'pompier')]["active_cdc"]
    try:
        # Step 1: Find the card to delete
        card_to_delete = collection.find_one({"id": card_id})
        if not card_to_delete:
            return jsonify({"error": "No card found with the given ID."}), 404
        
        # Step 2: Delete the card
        result = collection.delete_one({"id": card_id})
        
        # Step 3: Shift the order of the remaining cards
        collection.update_many(
            {"order": {"$gt": card_to_delete["order"]}},
            {"$inc": {"order": -1}}
        )
        
        return jsonify({"success": True}), 200
    except Exception as e:
        return handle_exception(e)
    
@admin_cta_blueprint.route("/delete-special-chain-of-command/<string:card_id>", methods=["DELETE"])
@admin_cta_required
def delete_special_chain_of_command(card_id):
    client = current_app.mongo_client
    collection = client[current_app.config.get('DB_NAME', 'pompier')]["active_cdc"]
    try:
        # Step 1: Find the special card to delete
        card_to_delete = collection.find_one({"id": card_id, "special": True})
        if not card_to_delete:
            return jsonify({"error": "No special card found with the given ID."}), 404
        
        # Step 2: Delete the special card
        result = collection.delete_one({"id": card_id})
        
        # Step 3: Shift the order of the remaining cards
        collection.update_many(
            {"order": {"$gt": 2}},
            {"$inc": {"order": -1}}
        )
        
        return jsonify({"success": True}), 200
    except Exception as e:
        return handle_exception(e)
    
@admin_cta_blueprint.route("/update-card-order", methods=["PATCH"])
@admin_cta_required
def update_card_order():
    client = current_app.mongo_client
    data = request.json
    page = data.get("page", "cdc")
    collection = client[current_app.config.get('DB_NAME', 'pompier')][f"active_{page}"]

    try:
        for card in data.get("cards", []):
            collection.update_one({"id": card["id"], "dpt": card["dpt"]}, {"$set": {"order": card["order"]}})
        return jsonify({"success": True}), 200
    except Exception as e:
        return handle_exception(e)
    
@admin_cta_blueprint.route("/create-active-duty", methods=["POST"])
@admin_cta_required
def create_active_duty():
    client = current_app.mongo_client
    collection = client[current_app.config.get('DB_NAME', 'pompier')]["active_astreintes"]
    data = request.json
    try:
        # Generate a unique UUID for the card
        new_id = str(uuid.uuid4())

        # Determine the new order value based on the current maximum order
        max_order = collection.find_one(sort=[("order", -1)], projection={"order": 1})
        new_order = (max_order["order"] + 1) if max_order else 1

        # Assign new UUID and order
        data['id'] = new_id
        data['order'] = new_order
        data['editing'] = False

        collection.insert_one(data)
        return jsonify({"success": True, "id": new_id}), 201
    except Exception as e:
        return handle_exception(e)

@admin_cta_blueprint.route("/update-active-duty", methods=["PATCH"])
@admin_cta_required
def update_active_duty():
    client = current_app.mongo_client
    collection = client[current_app.config.get('DB_NAME', 'pompier')]["active_astreintes"]
    data = request.json
    id = data.get("id", None)

    if id is None:
        return jsonify({"error": "ID is missing in the request data."}), 400

    try:
        # Ensure that the update doesn't affect the order field unless specifically modified
        order = data.get("order", None)
        data["editing"] = False
        if order is not None:
            # Check if there's a conflict in the desired order position
            existing_card = collection.find_one({"order": order, "id": {"$ne": id}, "dpt": data["dpt"]})
            if existing_card:
                return jsonify({"error": "Another card already has this order position."}), 409

        result = collection.update_one({"id": id}, {"$set": data})
        if result.matched_count == 0:
            return jsonify({"error": "No card found with the given ID."}), 404
        return jsonify({"success": True}), 200
    except Exception as e:
        return handle_exception(e)

@admin_cta_blueprint.route("/delete-active-duty/<string:card_id>", methods=["DELETE"])
@admin_cta_required
def delete_active_duty(card_id):
    client = current_app.mongo_client
    collection = client[current_app.config.get('DB_NAME', 'pompier')]["active_astreintes"]
    try:
        # Step 1: Find the card to delete
        card_to_delete = collection.find_one({"id": card_id})
        if not card_to_delete:
            return jsonify({"error": "No card found with the given ID."}), 404
        
        # Step 2: Delete the card
        result = collection.delete_one({"id": card_id})
        
        # Step 3: Shift the order of the remaining cards
        collection.update_many(
            {"order": {"$gt": card_to_delete["order"]}},
            {"$inc": {"order": -1}}
        )
        
        return jsonify({"success": True}), 200
    except Exception as e:
        return handle_exception(e)
        
@admin_cta_blueprint.route("/create-active-specialist", methods=["POST"])
@admin_cta_required
def create_active_specialist():
    client = current_app.mongo_client
    collection = client[current_app.config.get('DB_NAME', 'pompier')]["active_specialistes"]
    data = request.json
    try:
        # Generate a unique UUID for the card
        new_id = str(uuid.uuid4())

        # Determine the new order value based on the current maximum order
        max_order = collection.find_one(sort=[("order", -1)], projection={"order": 1})
        new_order = (max_order["order"] + 1) if max_order else 1

        # Assign new UUID and order
        data['id'] = new_id
        data['order'] = new_order
        data['editing'] = False

        collection.insert_one(data)
        return jsonify({"success": True, "id": new_id}), 201
    except Exception as e:
        return handle_exception(e)

@admin_cta_blueprint.route("/update-active-specialist", methods=["PATCH"])
@admin_cta_required
def update_active_specialist():
    client = current_app.mongo_client
    collection = client[current_app.config.get('DB_NAME', 'pompier')]["active_specialistes"]
    data = request.json
    id = data.get("id", None)

    if id is None:
        return jsonify({"error": "ID is missing in the request data."}), 400

    try:
        # Ensure that the update doesn't affect the order field unless specifically modified
        order = data.get("order", None)
        data["editing"] = False
        if order is not None:
            # Check if there's a conflict in the desired order position
            existing_card = collection.find_one({"order": order, "id": {"$ne": id}, "dpt": data["dpt"]})
            if existing_card:
                return jsonify({"error": "Another card already has this order position."}), 409

        result = collection.update_one({"id": id}, {"$set": data})
        if result.matched_count == 0:
            return jsonify({"error": "No card found with the given ID."}), 404
        return jsonify({"success": True}), 200
    except Exception as e:
        return handle_exception(e)

@admin_cta_blueprint.route("/delete-active-specialist/<string:card_id>", methods=["DELETE"])
@admin_cta_required
def delete_active_specialist(card_id):
    client = current_app.mongo_client
    collection = client[current_app.config.get('DB_NAME', 'pompier')]["active_specialistes"]
    try:
        # Step 1: Find the card to delete
        card_to_delete = collection.find_one({"id": card_id})
        if not card_to_delete:
            return jsonify({"error": "No card found with the given ID."}), 404
        
        # Step 2: Delete the card
        result = collection.delete_one({"id": card_id})
        
        # Step 3: Shift the order of the remaining cards
        collection.update_many(
            {"order": {"$gt": card_to_delete["order"]}},
            {"$inc": {"order": -1}}
        )
        
        return jsonify({"success": True}), 200
    except Exception as e:
        return handle_exception(e)
        
@admin_cta_blueprint.route("/create-guideline", methods=["POST"])
@admin_cta_required
def create_guideline():
    client = current_app.mongo_client
    collection = client[current_app.config.get('DB_NAME', 'pompier')]["consignes"]
    data = request.json

    try:
        data = request.json
        _id = str(uuid.uuid4())
        author = data["author"]
        message = data["message"]
        theme = data["theme"]
        active = data["active"]
        start_date = data["start_date"]
        start_time = data["start_time"]
        end_date = data["end_date"]
        end_time = data["end_time"]
        date = datetime.now(pytz.timezone("Europe/Paris")).strftime("%d/%m/%Y %H:%M:%S")
        dpt = data["dpt"]
        doc = dict(
            _id=_id, author=author, theme=theme, message=message, active=active, date=date, dpt=dpt, start_date=start_date, start_time=start_time, end_date=end_date, end_time=end_time
        )
        collection.insert_one(doc)
        return jsonify({"message": "Consigne créée avec succès.", "guideline": doc}), 200
    except Exception as e:
        return handle_exception(e)
    
@admin_cta_blueprint.route("/update-guideline", methods=["PATCH"])
@admin_cta_required
def update_guideline():
    client = current_app.mongo_client
    collection = client[current_app.config.get('DB_NAME', 'pompier')]["consignes"]
    data = request.json

    try:
        data = request.json
        _id = data["_id"]
        last_updated_by = data["last_updated_by"]
        last_updated_at = datetime.now(pytz.timezone("Europe/Paris")).strftime("%d/%m/%Y %H:%M:%S")
        message = data["message"]
        theme = data["theme"]
        active = data["active"]
        start_date = data["start_date"]
        start_time = data["start_time"]
        end_date = data["end_date"]
        end_time = data["end_time"]
        date = datetime.now(pytz.timezone("Europe/Paris")).strftime("%d/%m/%Y %H:%M:%S")
        collection.update_one({"_id": _id}, {"$set": {"last_updated_by": last_updated_by, "last_updated_at": last_updated_at, "theme": theme, "message": message, "active": active, "date": date, "start_date": start_date, "start_time": start_time, "end_date": end_date, "end_time": end_time,}})
        return jsonify({"message": "Consigne mise à jour avec succès.", "guideline": {**data, "last_updated_at": last_updated_at}}), 200
    except Exception as e:
        return handle_exception(e)
    
@admin_cta_blueprint.route("/delete-guideline", methods=["DELETE"])
@admin_cta_required
def delete_guideline():
    client = current_app.mongo_client
    collection = client[current_app.config.get('DB_NAME', 'pompier')]["consignes"]
    try:
        data = request.json
        _id = data["_id"]
        collection.delete_one({"_id": _id})
        return jsonify({"message": "Consigne supprimée avec succès."}), 200
    except Exception as e:
        return handle_exception(e)
    
@admin_cta_blueprint.route("/toggle-guideline-active", methods=["PATCH"])
@admin_cta_required
def toggle_guideline_active():
    client = current_app.mongo_client
    collection = client[current_app.config.get('DB_NAME', 'pompier')]["consignes"]
    try:
        data = request.json
        _id = data["_id"]
        active = data["active"]
        tomorrow = (datetime.now(pytz.timezone("Europe/Paris")) + timedelta(days=1)).strftime("%d/%m/%Y")
        collection.update_one({"_id": _id}, {"$set": {"active": active, "end_date": tomorrow}})
        return jsonify({"message": "Consigne active mis à jour avec succès."}), 200
    except Exception as e:
        return handle_exception(e)
    
@admin_cta_blueprint.route("/delete-guidelines", methods=["DELETE"])
@admin_cta_required
def delete_guidelines():
    client = current_app.mongo_client
    collection = client[current_app.config.get('DB_NAME', 'pompier')]["consignes"]
    try:
        data = request.json
        _ids = data["_ids"]
        collection.delete_many({"_id": {"$in": _ids}})
        return jsonify({"message": "Consignes supprimée(s) avec succès."}), 200
    except Exception as e:
        return handle_exception(e)
    
@admin_cta_blueprint.route("/diffuse-guideline", methods=["POST"])
@admin_cta_required
def diffuse_guideline():
    client = current_app.mongo_client
    guideline_collection = client[current_app.config.get('DB_NAME', 'pompier')]["consignes"]
    diffusion_lists_collection = client[current_app.config.get('DB_NAME', 'pompier')]["diffusion_lists"]

    try:
        data = request.json
        guideline_id = data["guideline_id"]
        diffusion_list_id = data["diffusion_list_id"]
        dpt = data["dpt"]
        guideline = guideline_collection.find_one({"_id": guideline_id})
        diffusion_list = diffusion_lists_collection.find_one({"_id": diffusion_list_id})
        if not guideline or not diffusion_list:
            return jsonify({"error": "Consigne ou liste de diffusion introuvable."}), 404
        
        diffusion_list_type = diffusion_list["type"]
        if diffusion_list_type == "email":
            emails = diffusion_list["recipients"]
            for email in emails:
                formatted_message = guideline_mail_template.format(start_date=guideline["start_date"], end_date=guideline["end_date"], author=guideline["author"], theme=guideline["theme"], guideline=guideline["message"])
                send_email(email, 'Nouvelle consigne concernant : {theme}'.format(theme=guideline["theme"]), formatted_message)
        elif diffusion_list_type == "sms":
            phone_numbers = diffusion_list["recipients"]
            for phone_number in phone_numbers:
                pass
        elif diffusion_list_type == "hybrid":
            pass
        else:
            return jsonify({"error": "Type de liste de diffusion invalide."}), 400
        
        return jsonify({"message": "Consigne diffusée avec succès."}), 200
    except Exception as e:
        return handle_exception(e)