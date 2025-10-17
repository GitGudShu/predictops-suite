from . import admin_blueprint
from flask import request, jsonify, make_response, current_app
from datetime import datetime, timedelta
from utils.errors_utils import handle_exception
from utils.token_utils import admin_required
from utils.email_utils import send_email, default_mail_template
from utils.misc_utils import (
    check_required_args,
    generate_profile_image,
    get_initials_from_email,
    get_color,
)
from pymongo import errors, DESCENDING, ASCENDING
import pytz
import secrets
import string
import uuid
from bson.objectid import ObjectId


@admin_blueprint.route("/users", methods=["GET"])
@admin_required
def get_users():
    client = current_app.mongo_client
    bcrypt = current_app.bcrypt
    collection = client[current_app.config.get("DB_NAME", "pompier")][
        "predictops_users"
    ]
    try:
        data = request.args
        role = data["role"]
        if role == "maintainer":
            users = list(
                collection.find({}, {"_id": 0, "password": 0}).sort(
                    [("dpt", 1), ("email", 1)]
                )
            )
        else:
            department = data["dpt"]
            roles = ["admin", "user", "admin-cta"]
            users = list(
                collection.find(
                    {"dpt": department, "role": {"$in": roles}},
                    {"_id": 0, "password": 0},
                ).sort([("dpt", 1), ("email", 1)])
            )
        for user in users:
            email = user.get("email", "")
            initials = get_initials_from_email(email)
            profile_image = generate_profile_image(initials)
            user["profile_image"] = profile_image
        return jsonify(users), 200
    except Exception as e:
        return handle_exception(e)


@admin_blueprint.route("/create-user", methods=["POST"])
@admin_required
def create_user():
    client = current_app.mongo_client
    bcrypt = current_app.bcrypt
    collection = client[current_app.config.get("DB_NAME", "pompier")][
        "predictops_users"
    ]
    try:
        alphabet = string.ascii_letters + string.digits
        password = "".join(secrets.choice(alphabet) for i in range(12))
        data = request.json
        email = data["email"]
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        role = data["role"]
        department = data["dpt"]
        initials = get_initials_from_email(email)
        profile_image = generate_profile_image(initials)
        active = True
        doc = dict(
            email=email,
            password=hashed_password,
            role=role,
            active=active,
            dpt=department,
        )
        collection.insert_one(doc)
        formatted_message = default_mail_template.format(
            message=f"Votre administateur a créé votre compte. Voici votre mot de passe personnel, ne le communiquez à personne : {password}. <a href='https://dashboard.predictops.fr/predictops/login'>Cliquez ici pour vous connecter.</a>"
        )
        c = send_email(email, "Votre compte Predictops", formatted_message)
        if c == 200:
            return (
                jsonify(
                    {
                        "message": "Utilisateur crée avec succès.",
                        "user": {
                            "email": email,
                            "role": role,
                            "active": active,
                            "dpt": department,
                            "profile_image": profile_image,
                        },
                    }
                ),
                c,
            )
        else:
            return (
                jsonify(
                    {"message": "Une erreur s'est produite lors de l'envoi du mail."}
                ),
                c,
            )
    except Exception as e:
        if type(e) == errors.DuplicateKeyError:
            return jsonify({"message": "L'utilisateur existe déjà."}), 400
        else:
            return handle_exception(e)


@admin_blueprint.route("/delete-user", methods=["DELETE"])
@admin_required
def delete_user():
    client = current_app.mongo_client
    collection = client[current_app.config.get("DB_NAME", "pompier")][
        "predictops_users"
    ]
    try:
        data = request.json
        email = data["email"]
        collection.delete_one({"email": email})
        return jsonify({"message": "Utilisateur supprimé avec succès."}), 200
    except Exception as e:
        return handle_exception(e)


@admin_blueprint.route("/delete-users", methods=["DELETE"])
@admin_required
def delete_users():
    client = current_app.mongo_client
    collection = client[current_app.config.get("DB_NAME", "pompier")][
        "predictops_users"
    ]
    try:
        data = request.json
        emails = data["emails"]
        collection.delete_many({"email": {"$in": emails}})
        return jsonify({"message": "Utilisateur(s) supprimé(s) avec succès."}), 200
    except Exception as e:
        return handle_exception(e)


@admin_blueprint.route("/update-role", methods=["PATCH"])
@admin_required
def update_role():
    client = current_app.mongo_client
    collection = client[current_app.config.get("DB_NAME", "pompier")][
        "predictops_users"
    ]
    try:
        data = request.json
        email = data["email"]
        role = data["role"]
        collection.update_one({"email": email}, {"$set": {"role": role}})
        return jsonify({"message": "Rôle mis à jour avec succès."}), 200
    except Exception as e:
        return handle_exception(e)


@admin_blueprint.route("/update-department", methods=["PATCH"])
@admin_required
def update_department():
    client = current_app.mongo_client
    collection = client[current_app.config.get("DB_NAME", "pompier")][
        "predictops_users"
    ]
    try:
        data = request.json
        email = data["email"]
        dpt = data["dpt"]
        collection.update_one({"email": email}, {"$set": {"dpt": dpt}})
        return jsonify({"message": "Département mis à jour avec succès."}), 200
    except Exception as e:
        return handle_exception(e)


@admin_blueprint.route("/toggle-user-active", methods=["PATCH"])
@admin_required
def toggle_user_active():
    client = current_app.mongo_client
    collection = client[current_app.config.get("DB_NAME", "pompier")][
        "predictops_users"
    ]
    try:
        data = request.json
        email = data["email"]
        active = data["active"]
        collection.update_one({"email": email}, {"$set": {"active": active}})
        message = (
            "Utilisateur activé avec succès."
            if active
            else "Utilisateur désactivé avec succès."
        )
        return jsonify({"message": message}), 200
    except Exception as e:
        return handle_exception(e)


@admin_blueprint.route("/popups", methods=["GET"])
def get_popups():
    client = current_app.mongo_client
    collection = client[current_app.config.get("DB_NAME", "pompier")]["popup"]
    popups = collection.find()
    return jsonify(list(popups)), 200


@admin_blueprint.route("/create-popup", methods=["POST"])
@admin_required
def create_popup():
    client = current_app.mongo_client
    collection = client[current_app.config.get("DB_NAME", "pompier")]["popup"]
    try:
        data = request.json
        _id = str(uuid.uuid4())
        type = data["type"]
        message = data["message"]
        visible = data["visible"]
        date = datetime.now(pytz.timezone("Europe/Paris")).strftime("%d/%m/%Y %H:%M:%S")
        timestamp = datetime.now()
        dpts = data["dpts"]
        doc = dict(
            _id=_id,
            type=type,
            message=message,
            visible=visible,
            date=date,
            dpts=dpts,
            timestamp=timestamp,
        )
        collection.insert_one(doc)
        return jsonify({"message": "Popup crée avec succès.", "popup": doc}), 200
    except Exception as e:
        return handle_exception(e)


@admin_blueprint.route("/update-popup", methods=["PATCH"])
@admin_required
def update_popup():
    client = current_app.mongo_client
    collection = client[current_app.config.get("DB_NAME", "pompier")]["popup"]
    try:
        data = request.json
        _id = data["_id"]
        type = data["type"]
        message = data["message"]
        visible = data["visible"]
        date = datetime.now(pytz.timezone("Europe/Paris")).strftime("%d/%m/%Y %H:%M:%S")
        timestamp = datetime.now()
        dpts = data["dpts"]
        collection.update_one(
            {"_id": _id},
            {
                "$set": {
                    "type": type,
                    "message": message,
                    "visible": visible,
                    "dpts": dpts,
                    "timestamp": timestamp,
                }
            },
        )

        return (
            jsonify(
                {
                    "message": "Popup mis à jour avec succès.",
                    "popup": {
                        "_id": _id,
                        "type": type,
                        "message": message,
                        "visible": visible,
                        "dpts": dpts,
                        "date": date,
                    },
                }
            ),
            200,
        )
    except Exception as e:
        return handle_exception(e)


@admin_blueprint.route("/delete-popup", methods=["DELETE"])
@admin_required
def delete_popup():
    client = current_app.mongo_client
    collection = client[current_app.config.get("DB_NAME", "pompier")]["popup"]
    try:
        data = request.json
        _id = data["_id"]
        collection.delete_one({"_id": _id})
        return jsonify({"message": "Popup supprimé avec succès."}), 200
    except Exception as e:
        return handle_exception(e)


@admin_blueprint.route("/toggle-popup-visible", methods=["PATCH"])
@admin_required
def toggle_popup_visible():
    client = current_app.mongo_client
    collection = client[current_app.config.get("DB_NAME", "pompier")]["popup"]
    try:
        data = request.json
        _id = data["_id"]
        visible = data["visible"]
        collection.update_one({"_id": _id}, {"$set": {"visible": visible}})
        return jsonify({"message": "Popup visible mis à jour avec succès."}), 200
    except Exception as e:
        return handle_exception(e)


@admin_blueprint.route("/delete-popups", methods=["DELETE"])
@admin_required
def delete_popups():
    client = current_app.mongo_client
    collection = client[current_app.config.get("DB_NAME", "pompier")]["popup"]
    try:
        data = request.json
        _ids = data["_ids"]
        collection.delete_many({"_id": {"$in": _ids}})
        return jsonify({"message": "Popups supprimée(s) avec succès."}), 200
    except Exception as e:
        return handle_exception(e)


@admin_blueprint.route("/health", methods=["GET"])
@admin_required
def health():
    db = current_app.mongo_client[current_app.config.get("DB_NAME", "pompier")]
    collections = db.list_collection_names()
    ignore_collections = [
        "users",
        "predictops_users",
        "doctrinops_users",
        "radioitems",
        "bornes",
        "doctrinops_departments",
        "doctrinops_notifications",
        "new_bornes",
        "popup",
        "config",
        "moyenne_eau",
        "pages",
        "bounds",
        "map_bounds",
        "consignes",
        "active_cdc",
        "active_astreintes",
        "active_specialistes",
    ]
    dpts = ["01", "25", "78"]
    results = {dpt: [] for dpt in dpts}

    local_tz = pytz.timezone("Europe/Paris")

    try:
        for collection_name in collections:
            if collection_name in ignore_collections:
                continue

            collection = db[collection_name]

            for dpt in dpts:
                latest_added_at = None

                if collection_name.startswith("mv_") or collection_name == "quality":
                    latest_doc = list(
                        collection.find({"dpt": dpt}).sort("date", DESCENDING).limit(1)
                    )
                    if len(latest_doc) > 0:
                        latest_doc = latest_doc[0]
                        latest_added_at = latest_doc["date"]
                        if collection_name == "quality":
                            latest_added_at = latest_added_at.astimezone(local_tz)
                else:
                    latest_doc = list(
                        collection.find({"dpt": dpt}).sort("_id", DESCENDING).limit(1)
                    )
                    if len(latest_doc) > 0:
                        try:
                            latest_doc = latest_doc[0]
                            latest_added_at = latest_doc["_id"].generation_time
                            latest_added_at = latest_added_at.astimezone(local_tz)
                        except Exception as e:
                            print(e)
                            continue

                if latest_added_at:
                    color = get_color(latest_added_at)
                    formatted_date = latest_added_at.strftime("%d/%m/%Y %H:%M")
                    results[dpt].append(
                        {
                            "name": collection_name,
                            "latest_added_at": formatted_date,
                            "color": color,
                            "timestamp": latest_added_at,  # Adding this for sorting purposes
                        }
                    )

        # Sort results by timestamp in descending order within each department
        for dpt in dpts:
            results[dpt].sort(
                key=lambda x: x["timestamp"].replace(
                    tzinfo=pytz.timezone("Europe/Paris")
                )
            )
            for result in results[dpt]:
                del result["timestamp"]

        return jsonify(results), 200

    except Exception as e:
        return handle_exception(e)


@admin_blueprint.route("pages", methods=["GET"])
@admin_required
def get_pages():
    client = current_app.mongo_client
    collection = client[current_app.config.get("DB_NAME", "pompier")]["pages"]
    try:
        data = request.args
        role = data["role"]
        if role == "maintainer":
            pages = collection.find({}, {"_id": 0})
        else:
            dpt = data["dpt"]
            pages = collection.find({"dpt": dpt}, {"_id": 0})
        return jsonify(list(pages)), 200

    except Exception as e:
        return handle_exception(e)


@admin_blueprint.route("/add-page", methods=["POST"])
@admin_required
def add_page():
    client = current_app.mongo_client
    collection = client[current_app.config.get("DB_NAME", "pompier")]["pages"]
    try:
        data = request.json
        dpt = data["dpt"]
        path = data["path"]
        icon = data["icon"]
        name = data["name"]

        # check for duplicates for the field "path"
        existing_page = collection.find_one({"dpt": dpt, "pages.path": path})
        if existing_page:
            return jsonify({"error": "La page existe déjà."}), 400

        page = {"path": path, "icon": icon, "name": name}
        collection.update_one({"dpt": dpt}, {"$push": {"pages": page}})
        return jsonify({"message": "Page ajoutée avec succès."}), 200
    except Exception as e:
        return handle_exception(e)


@admin_blueprint.route("/edit-page", methods=["POST"])
@admin_required
def edit_page():
    client = current_app.mongo_client
    collection = client[current_app.config.get("DB_NAME", "pompier")]["pages"]

    try:
        data = request.json
        dpt = data["dpt"]
        path = data["path"]
        icon = data["icon"]
        name = data["name"]

        # Find the document for the specified department (dpt)
        doc = collection.find_one({"dpt": dpt})

        if not doc:
            return (
                jsonify(
                    {"error": "Le département n'existe pas dans la base de données."}
                ),
                404,
            )

        # Find the specific page within the 'pages' array
        page_found = None
        for page in doc["pages"]:
            if page["path"] == path:
                page_found = page
                break

        if not page_found:
            return jsonify({"error": "La page n'existe pas."}), 404

        # Update the page with new values
        page_found["icon"] = icon
        page_found["name"] = name

        # Save the updated document back to the collection
        collection.update_one({"dpt": dpt}, {"$set": {"pages": doc["pages"]}})

        return (
            jsonify({"data": page_found, "message": "Page modifiée avec succès."}),
            200,
        )

    except Exception as e:
        return handle_exception(e)


@admin_blueprint.route("/delete-page", methods=["DELETE"])
@admin_required
def delete_page():
    client = current_app.mongo_client
    collection = client[current_app.config.get("DB_NAME", "pompier")]["pages"]

    try:
        data = request.json
        dpt = data["dpt"]
        path = data["path"]

        # Find the document for the specified department (dpt)
        doc = collection.find_one({"dpt": dpt})

        if not doc:
            return (
                jsonify(
                    {"error": "Le Departement n'existe pas dans la base de données."}
                ),
                404,
            )

        # Find the specific page within the 'pages' array
        page_found = None
        for page in doc["pages"]:
            if page["path"] == path:
                page_found = page
                break

        if not page_found:
            return jsonify({"error": "La page n'existe pas."}), 404

        # Remove the page from the 'pages' array
        doc["pages"].remove(page_found)

        # Save the updated document back to the collection
        collection.update_one({"dpt": dpt}, {"$set": {"pages": doc["pages"]}})

        return (
            jsonify({"data": page_found, "message": "Page supprimée avec sucees."}),
            200,
        )

    except Exception as e:
        return handle_exception(e)


@admin_blueprint.route("/reorder-pages", methods=["POST"])
@admin_required
def reorder_pages():
    client = current_app.mongo_client
    collection = client[current_app.config.get("DB_NAME", "pompier")]["pages"]

    try:
        data = request.json
        dpt = data["dpt"]
        pages = data["pages"]

        # Find the document for the specified department (dpt)
        doc = collection.find_one({"dpt": dpt})

        if not doc:
            return (
                jsonify(
                    {"error": "Le Departement n'existe pas dans la base de données."}
                ),
                404,
            )

        # Update the 'pages' array with the new order
        doc["pages"] = pages

        # Save the updated document back to the collection
        collection.update_one({"dpt": dpt}, {"$set": {"pages": doc["pages"]}})

        return jsonify({"message": "Pages reordonées avec succès."}), 200

    except Exception as e:
        return handle_exception(e)


@admin_blueprint.route("/add-subpage", methods=["POST"])
@admin_required
def add_subpage():
    client = current_app.mongo_client
    collection = client[current_app.config.get("DB_NAME", "pompier")]["pages"]

    try:
        data = request.json
        dpt = data["dpt"]
        path = data["path"]
        icon = data["icon"]
        name = data["name"]
        subpage = data["subpage"]

        # Find the document for the specified department (dpt)
        doc = collection.find_one({"dpt": dpt})

        if not doc:
            return (
                jsonify(
                    {"error": "Le département n'existe pas dans la base de données."}
                ),
                404,
            )

        # Search for the page that matches the provided 'path'
        page_found = None
        for page in doc["pages"]:
            if page["path"] == path:
                page_found = page
                break

        if not page_found:
            return jsonify({"error": "La page n'existe pas."}), 404

        # Check if the subpage already exists (duplicate check)
        for existing_subpage in page_found.get("subpages", []):
            if existing_subpage["path"] == subpage:
                return jsonify({"error": "Le sous-chemin existe déjà."}), 400

        # Append new subpage data to the 'subpages' array
        new_subpage = {"path": subpage, "icon": icon, "name": name}

        if "subpages" not in page_found:
            page_found["subpages"] = []

        page_found["subpages"].append(new_subpage)

        # Update the document in the database
        collection.update_one({"dpt": dpt}, {"$set": doc})

        return jsonify({"message": "Sous-chemin ajouté avec succès."}), 200

    except Exception as e:
        return handle_exception(e)


@admin_blueprint.route("/edit-subpage", methods=["POST"])
@admin_required
def edit_subpage():
    client = current_app.mongo_client
    collection = client[current_app.config.get("DB_NAME", "pompier")]["pages"]

    try:
        data = request.json
        dpt = data["dpt"]
        path = data["path"]
        subpage = data["subpage"]
        # new_subpage = data.get("new_subpage")  # If the subpage is being updated
        icon = data["icon"]
        name = data["name"]

        # Find the document for the specified department (dpt)
        doc = collection.find_one({"dpt": dpt})

        if not doc:
            return (
                jsonify(
                    {"error": "Le département n'existe pas dans la base de données."}
                ),
                404,
            )

        # Search for the page that matches the provided 'path'
        page_found = None
        for page in doc["pages"]:
            if page["path"] == path:
                page_found = page
                break

        if not page_found:
            return jsonify({"error": "La page n'existe pas."}), 404

        # Search for the subpage in the page
        subpage_found = None
        for sub in page_found.get("subpages", []):
            if sub["path"] == subpage:
                subpage_found = sub
                break

        if not subpage_found:
            return jsonify({"error": "Le sous-chemin n'existe pas."}), 404

        # # If new_subpage is provided, check for duplicates
        # if new_subpage and new_subpage != subpage:
        #     for existing_subpage in page_found["subpages"]:
        #         if existing_subpage["path"] == new_subpage:
        #             return jsonify({"error": "Le nouveau sous-chemin existe déjà."}), 400
        #     # Update the path if it's being changed
        #     subpage_found["path"] = new_subpage

        # Update the subpage's icon and name
        subpage_found["icon"] = icon
        subpage_found["name"] = name

        # Update the document in the database
        collection.update_one({"dpt": dpt}, {"$set": doc})

        return jsonify({"message": "Sous-chemin mis à jour avec succès."}), 200

    except Exception as e:
        return handle_exception(e)


@admin_blueprint.route("/delete-subpage", methods=["DELETE"])
@admin_required
def delete_subpage():
    client = current_app.mongo_client
    collection = client[current_app.config.get("DB_NAME", "pompier")]["pages"]

    try:
        data = request.json
        dpt = data["dpt"]
        path = data["path"]
        subpage = data["subpage"]

        # Find the document for the specified department (dpt)
        doc = collection.find_one({"dpt": dpt})

        if not doc:
            return (
                jsonify(
                    {"error": "Le departement n'existe pas dans la base de données."}
                ),
                404,
            )

        # Search for the page that matches the provided 'path'
        page_found = None
        for page in doc["pages"]:
            if page["path"] == path:
                page_found = page
                break

        if not page_found:
            return jsonify({"error": "La page n'existe pas."}), 404

        # Search for the subpage in the page
        subpage_found = None
        for sub in page_found.get("subpages", []):
            if sub["path"] == subpage:
                subpage_found = sub
                break

        if not subpage_found:
            return jsonify({"error": "Le sous-chemin n'existe pas."}), 404

        # Remove the subpage from the 'subpages' array
        page_found["subpages"].remove(subpage_found)

        # Update the document in the database
        collection.update_one({"dpt": dpt}, {"$set": doc})

        return jsonify({"message": "Sous-chemin supprimé avec succès."}), 200

    except Exception as e:
        return handle_exception(e)


@admin_blueprint.route("/reorder-subpages", methods=["POST"])
@admin_required
def reorder_subpages():
    client = current_app.mongo_client
    collection = client[current_app.config.get("DB_NAME", "pompier")]["pages"]

    try:
        data = request.json
        dpt = data["dpt"]
        path = data["path"]
        subpages = data["subpages"]

        # Find the document for the specified department (dpt)
        doc = collection.find_one({"dpt": dpt})

        if not doc:
            return (
                jsonify(
                    {"error": "Le departement n'existe pas dans la base de données."}
                ),
                404,
            )

        # Search for the page that matches the provided 'path'
        page_found = None
        for page in doc["pages"]:
            if page["path"] == path:
                page_found = page
                break

        if not page_found:
            return jsonify({"error": "La page n'existe pas."}), 404

        # Update the subpages array
        page_found["subpages"] = subpages

        # Update the document in the database
        collection.update_one({"dpt": dpt}, {"$set": doc})

        return jsonify({"message": "Sous-chemins mis à jour avec succès."}), 200

    except Exception as e:
        return handle_exception(e)


@admin_blueprint.route("/diffusion-lists", methods=["GET"])
@admin_required
def get_diffusion_lists():
    required_args = ["dpt"]
    args_values, missing_args = check_required_args(request, required_args)
    if missing_args:
        return jsonify({"error": f"Missing arguments: {', '.join(missing_args)}"}), 400

    client = current_app.mongo_client
    collection = client[current_app.config.get("DB_NAME", "pompier")]["diffusion_lists"]
    dpt = args_values["dpt"]
    try:
        lists = collection.find({"dpt": dpt}).sort("created_at", ASCENDING)
        return jsonify(list(lists)), 200
    except Exception as e:
        return handle_exception(e)


@admin_blueprint.route("/create-diffusion-list", methods=["POST"])
@admin_required
def create_diffusion_list():
    client = current_app.mongo_client
    collection = client[current_app.config.get("DB_NAME", "pompier")]["diffusion_lists"]
    try:
        data = request.json
        _id = str(uuid.uuid4())
        dpt = data["dpt"]
        name = data["name"]
        list_type = data["type"]
        limit = 15 if list_type == "email" else 30
        created_at = datetime.now(pytz.timezone("Europe/Paris")).strftime(
            "%d/%m/%Y %H:%M:%S"
        )
        recipients = data["recipients"]
        doc = dict(
            _id=_id,
            dpt=dpt,
            name=name,
            recipients=recipients,
            type=list_type,
            limit=limit,
            created_at=created_at,
        )
        collection.insert_one(doc)
        return (
            jsonify({"message": "Liste de diffusion crée avec succès.", "list": doc}),
            200,
        )
    except Exception as e:
        if type(e) == errors.DuplicateKeyError:
            return jsonify({"message": "Le nom de la liste existe déjà."}), 400
        else:
            return handle_exception(e)


@admin_blueprint.route("/update-diffusion-list/<_id>", methods=["PUT"])
@admin_required
def update_diffusion_list(_id):
    client = current_app.mongo_client
    collection = client[current_app.config.get("DB_NAME", "pompier")]["diffusion_lists"]
    try:
        data = request.json
        name = data["name"]
        recipients = data["recipients"]
        collection.update_one(
            {"_id": _id}, {"$set": {"name": name, "recipients": recipients}}
        )
        return jsonify({"message": "Liste de diffusion mise à jour avec succès."}), 200
    except Exception as e:
        if type(e) == errors.DuplicateKeyError:
            return jsonify({"message": "Le nom de la liste existe déjà."}), 400
        else:
            return handle_exception(e)


@admin_blueprint.route("/duplicate-diffusion-list/<_id>", methods=["POST"])
@admin_required
def duplicate_diffusion_list(_id):
    client = current_app.mongo_client
    collection = client[current_app.config.get("DB_NAME", "pompier")]["diffusion_lists"]
    try:
        doc = collection.find_one({"_id": _id})
        _id = str(uuid.uuid4())
        doc["name"] = doc["name"] + " (copie)"
        doc["_id"] = _id
        collection.insert_one(doc)
        return (
            jsonify(
                {"message": "Liste de diffusion dupliquée avec succès.", "list": doc}
            ),
            200,
        )
    except errors.DuplicateKeyError:
        while True:
            try:
                doc["name"] = doc["name"] + " (copie)"
                doc["_id"] = str(uuid.uuid4())
                collection.insert_one(doc)
                return (
                    jsonify(
                        {
                            "message": "Liste de diffusion dupliquée avec succès.",
                            "list": doc,
                        }
                    ),
                    200,
                )
            except errors.DuplicateKeyError:
                continue
    except Exception as e:
        return handle_exception(e)


@admin_blueprint.route("/delete-diffusion-list/<_id>", methods=["DELETE"])
@admin_required
def delete_diffusion_list(_id):
    client = current_app.mongo_client
    collection = client[current_app.config.get("DB_NAME", "pompier")]["diffusion_lists"]
    try:
        collection.delete_one({"_id": _id})
        return jsonify({"message": "Liste de diffusion supprimée avec succès."}), 200
    except Exception as e:
        return handle_exception(e)


@admin_blueprint.route("/update/bounds", methods=["PUT"])
@admin_required
def update_bounds():
    client = current_app.mongo_client
    collection = client[current_app.config.get("DB_NAME", "pompier")]["bounds"]
    try:
        data = request.json
        dpt = data["dpt"]
        del data["dpt"]
        doc = dict(dpt=dpt, bounds=data)
        collection.delete_one({"dpt": dpt})
        collection.insert_one(doc)
        return jsonify({"message": "Données mises à jour avec succès"}), 200
    except Exception as e:
        return handle_exception(e)


@admin_blueprint.route("/update/map-bounds", methods=["PUT"])
@admin_required
def update_map_bounds():
    client = current_app.mongo_client
    collection = client[current_app.config.get("DB_NAME", "pompier")]["map_bounds"]
    try:
        data_list = request.json  # Expecting a list of documents
        for data in data_list:
            dpt = data["dpt"]
            code_geom = data["code_geom"]
            name = data["name"]
            horizon = data["horizon"]
            tranche = data["tranche"]
            type = data["type"]
            yellow = data.get("yellow", 0)
            orange = data.get("orange", 0)
            red = data.get("red", 0)

            # Create the document to be inserted or updated
            doc = {
                "dpt": dpt,
                "code_geom": int(code_geom),
                "name": name,
                "horizon": int(horizon),
                "tranche": tranche,
                "type": type,
                "yellow": float(yellow),
                "orange": float(orange),
                "red": float(red),
            }

            # Define the query to find the document
            query = {
                "dpt": dpt,
                "code_geom": int(code_geom),
                "name": name,
                "tranche": tranche,
                "horizon": int(horizon),
                "type": type,
            }

            # Update the document or insert if it does not exist
            collection.update_one(query, {"$set": doc}, upsert=True)

        return jsonify({"message": "Données mises à jour avec succès"}), 200
    except Exception as e:
        return handle_exception(e)
