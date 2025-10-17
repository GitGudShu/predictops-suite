from . import data_blueprint
from flask import request, jsonify, current_app
import requests
import os
from utils.errors_utils import handle_exception
from utils.misc_utils import *
import pandas as pd
from dotenv import load_dotenv
from sklearn.metrics import mean_absolute_error
from datetime import datetime

load_dotenv()

OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")


@data_blueprint.route("/air-quality", methods=["GET"])
def get_air_quality():
    required_args = ["dpt"]
    args_values, missing_args = check_required_args(request, required_args)
    if missing_args:
        return jsonify({"error": f"Missing arguments: {', '.join(missing_args)}"}), 400

    client = current_app.mongo_client
    dpt = args_values["dpt"]
    collection = client[current_app.config.get("DB_NAME", "pompier")]["indice_air"]
    try:
        data = collection.find({"dpt": dpt}, {"_id": 0})
        return jsonify(list(data)), 200
    except Exception as e:
        return handle_exception(e)


@data_blueprint.route("/alerts", methods=["GET"])
def get_alerts():
    required_args = ["dpt"]
    args_values, missing_args = check_required_args(request, required_args)
    if missing_args:
        return jsonify({"error": f"Missing arguments: {', '.join(missing_args)}"}), 400

    client = current_app.mongo_client
    dpt = args_values["dpt"]
    collection = client[current_app.config.get("DB_NAME", "pompier")]["alertes"]
    try:
        data = collection.find({"dpt": dpt}, {"_id": 0})
        return jsonify(list(data)), 200
    except Exception as e:
        return handle_exception(e)


@data_blueprint.route("/bounds", methods=["GET"])
def get_bounds():
    required_args = ["dpt"]
    args_values, missing_args = check_required_args(request, required_args)
    if missing_args:
        return jsonify({"error": f"Missing arguments: {', '.join(missing_args)}"}), 400

    client = current_app.mongo_client
    dpt = args_values["dpt"]
    collection = client[current_app.config.get("DB_NAME", "pompier")]["bounds"]
    try:
        data = collection.find({"dpt": dpt}, {"_id": 0})
        return jsonify(list(data)), 200
    except Exception as e:
        return handle_exception(e)


@data_blueprint.route("/map-bounds", methods=["GET"])
def get_map_bounds():
    required_args = ["dpt", "type", "code_geom", "horizon"]
    args_values, missing_args = check_required_args(request, required_args)
    if missing_args:
        return jsonify({"error": f"Missing arguments: {', '.join(missing_args)}"}), 400

    client = current_app.mongo_client
    dpt = args_values["dpt"]
    type_interv = args_values["type"]
    code_geoms = args_values["code_geom"].split(",")
    horizons = args_values["horizon"].split(",")
    collection = client[current_app.config.get("DB_NAME", "pompier")]["map_bounds"]
    if code_geoms != [""] and horizons != [""]:
        query = {
            "dpt": str(dpt),
            "type": type_interv,
            "code_geom": {"$in": list(map(int, code_geoms))},
            "$or": [],
        }

        for horizon in horizons:
            if len(horizon) > 2:
                query["$or"].append({"tranche": horizon})
            else:
                query["$or"].append({"horizon": int(horizon)})

        try:
            data = collection.find(query, {"_id": 0})
            return jsonify(list(data)), 200
        except Exception as e:
            return handle_exception(e)
    else:
        return jsonify([]), 200


@data_blueprint.route("/news", methods=["GET"])
def get_news():
    required_args = ["dpt", "page"]
    args_values, missing_args = check_required_args(request, required_args)
    if missing_args:
        return jsonify({"error": f"Missing arguments: {', '.join(missing_args)}"}), 400

    client = current_app.mongo_client
    dpt = args_values["dpt"]
    page = args_values["page"]
    collection = client[current_app.config.get("DB_NAME", "pompier")]["pages_alerts"]
    try:
        data = collection.find_one({"dpt": dpt, "page": page}, {"_id": 0, "news": 1})
        if data and "news" in data:
            news_list = list(filter(None, data["news"]))
        else:
            news_list = []

        return jsonify(news_list), 200
    except Exception as e:
        return handle_exception(e)


@data_blueprint.route("/calls-quality", methods=["GET"])
def get_calls_quality():
    required_args = ["dpt"]
    args_values, missing_args = check_required_args(request, required_args)
    if missing_args:
        return jsonify({"error": f"Missing arguments: {', '.join(missing_args)}"}), 400

    client = current_app.mongo_client
    dpt = args_values["dpt"]
    collection = client[current_app.config.get("DB_NAME", "pompier")]["calls_quality"]
    try:
        data = collection.find({"dpt": dpt}, {"_id": 0})
        return jsonify(list(data)), 200
    except Exception as e:
        return handle_exception(e)


@data_blueprint.route("/chain-of-command", methods=["GET"])
def get_chain_of_command():
    required_args = ["dpt"]
    args_values, missing_args = check_required_args(request, required_args)
    if missing_args:
        return jsonify({"error": f"Missing arguments: {', '.join(missing_args)}"}), 400

    client = current_app.mongo_client
    dpt = args_values["dpt"]
    collection = client[current_app.config.get("DB_NAME", "pompier")]["cdc"]
    try:
        data = collection.find({"dpt": dpt}, {"_id": 0, "dpt": 0})
        df = pd.DataFrame(list(data))
        df.rename(
            {"type_cdc": "fonction"}, errors="ignore", axis="columns", inplace=True
        )
        df.fillna("", inplace=True)
        return jsonify(df.to_dict("records")), 200
    except Exception as e:
        return handle_exception(e)


@data_blueprint.route("/active-chain-of-command", methods=["GET"])
def get_active_chain_of_command():
    required_args = ["dpt"]
    args_values, missing_args = check_required_args(request, required_args)
    if missing_args:
        return jsonify({"error": f"Missing arguments: {', '.join(missing_args)}"}), 400

    client = current_app.mongo_client
    dpt = args_values["dpt"]
    collection = client[current_app.config.get("DB_NAME", "pompier")]["active_cdc"]
    try:
        data = collection.find({"dpt": dpt}, {"_id": 0, "image": 0})
        df = pd.DataFrame(list(data))
        df.fillna("", inplace=True)
        return jsonify(df.to_dict("records")), 200
    except Exception as e:
        return handle_exception(e)


@data_blueprint.route("/active-duty", methods=["GET"])
def get_active_duty():
    required_args = ["dpt"]
    args_values, missing_args = check_required_args(request, required_args)
    if missing_args:
        return jsonify({"error": f"Missing arguments: {', '.join(missing_args)}"}), 400

    client = current_app.mongo_client
    dpt = args_values["dpt"]
    collection = client[current_app.config.get("DB_NAME", "pompier")][
        "active_astreintes"
    ]
    try:
        data = collection.find({"dpt": dpt}, {"_id": 0, "image": 0})
        df = pd.DataFrame(list(data))
        df.fillna("", inplace=True)
        return jsonify(df.to_dict("records")), 200
    except Exception as e:
        return handle_exception(e)


@data_blueprint.route("/active-specialist", methods=["GET"])
def get_active_specialist():
    required_args = ["dpt"]
    args_values, missing_args = check_required_args(request, required_args)
    if missing_args:
        return jsonify({"error": f"Missing arguments: {', '.join(missing_args)}"}), 400

    client = current_app.mongo_client
    dpt = args_values["dpt"]
    collection = client[current_app.config.get("DB_NAME", "pompier")][
        "active_specialistes"
    ]
    try:
        data = collection.find({"dpt": dpt}, {"_id": 0, "image": 0})
        df = pd.DataFrame(list(data))
        df.fillna("", inplace=True)
        return jsonify(df.to_dict("records")), 200
    except Exception as e:
        return handle_exception(e)


@data_blueprint.route("/image/<collection_name>/<id>", methods=["GET"])
def get_image(collection_name, id):
    client = current_app.mongo_client
    valid_collections = ["active_specialistes", "active_astreintes", "active_cdc"]

    # Ensure the collection name is valid
    if collection_name not in valid_collections:
        return jsonify({"error": f"Invalid collection name: {collection_name}"}), 400

    # Access the appropriate collection
    collection = client[current_app.config.get("DB_NAME", "pompier")][collection_name]

    try:
        # Fetch the specific image for the specialist
        specialist = collection.find_one({"id": id}, {"image": 1, "_id": 0})
        if specialist and "image" in specialist:
            return jsonify({"image": specialist["image"]}), 200
        else:
            return jsonify({"error": "Image not found"}), 404
    except Exception as e:
        return handle_exception(e)


@data_blueprint.route("/last-update", methods=["GET"])
def get_last_update():
    required_args = ["dpt"]
    args_values, missing_args = check_required_args(request, required_args)
    if missing_args:
        return jsonify({"error": f"Missing arguments: {', '.join(missing_args)}"}), 400
    client = current_app.mongo_client
    dpt = args_values["dpt"]
    collection = client[current_app.config.get("DB_NAME", "pompier")]["maj"]
    try:
        data = collection.find_one({"dpt": dpt}, {"_id": 0})
        return (
            jsonify(
                f"Dernière mise à jour : {data.get('timestamp').strftime('%H:%M')}"
            ),
            200,
        )
    except Exception as e:
        return handle_exception(e)


@data_blueprint.route("/config", methods=["GET"])
def get_config():
    required_args = ["dpt"]
    args_values, missing_args = check_required_args(request, required_args)
    if missing_args:
        return jsonify({"error": f"Missing arguments: {', '.join(missing_args)}"}), 400

    client = current_app.mongo_client
    dpt = args_values["dpt"]
    collection = client[current_app.config.get("DB_NAME", "pompier")]["config"]
    try:
        data = collection.find({"dpt": dpt}, {"_id": 0})
        return jsonify(list(data)), 200
    except Exception as e:
        return handle_exception(e)


@data_blueprint.route("/epidemics", methods=["GET"])
def get_epidemics():
    required_args = ["dpt"]
    args_values, missing_args = check_required_args(request, required_args)
    if missing_args:
        return jsonify({"error": f"Missing arguments: {', '.join(missing_args)}"}), 400

    client = current_app.mongo_client
    dpt = args_values["dpt"]
    collection = client[current_app.config.get("DB_NAME", "pompier")]["epidemie"]
    try:
        data = collection.find({"dpt": dpt}, {"_id": 0})
        df = pd.DataFrame(list(data))
        df.fillna(0, inplace=True)
        return jsonify(df.to_dict("records")), 200
    except Exception as e:
        return handle_exception(e)


@data_blueprint.route("/guidelines", methods=["GET"])
def get_guidelines():
    required_args = ["dpt"]
    args_values, missing_args = check_required_args(request, required_args)
    if missing_args:
        return jsonify({"error": f"Missing arguments: {', '.join(missing_args)}"}), 400

    client = current_app.mongo_client
    dpt = args_values["dpt"]
    collection = client[current_app.config.get("DB_NAME", "pompier")]["consignes"]
    try:
        data = list(collection.find({"dpt": dpt}))

        for item in data:
            sdate = item.get("start_date")
            stime = item.get("start_time")  # Could be a string like "09:30" or None
            edate = item.get("end_date")
            etime = item.get("end_time")    # Could be a string like "18:00" or None

            # Combine them into datetimes
            start_dt = combine_date_and_time(sdate, stime, is_start=True)
            end_dt = combine_date_and_time(edate, etime, is_start=False)

            # If old guidelines don't have these fields at all, handle fallback:
            # e.g., if there's no end date/time, treat as indefinite
            if end_dt is None or end_dt == datetime.min:
                end_dt = datetime.max

            # Now decide if it's active
            # Suppose item["active"] is a boolean in the DB, but we also
            # want to update it if end time is past
            if item.get("active", False):
                # It's only truly active if now < end_dt
                item["active"] = datetime.now() <= end_dt

            # You could also check if "start_dt > now" if you only want
            # future guidelines, etc.

        # Sort guidelines: active first, then by start_dt ascending
        data = sorted(
            data,
            key=lambda x: (
                not x.get("active", False),
                combine_date_and_time(x.get("start_date"), x.get("start_time"), True) or datetime.min
            )
        )

        return jsonify(data), 200
    except Exception as e:
        return handle_exception(e)

@data_blueprint.route("/future-predictions", methods=["GET"])
def get_future_predictions():
    # types_map = {
    #     "CIS" : "SAP",
    #     "CIS-INC" : "CIS",
    #     "Tous" : "Tous"
    # }
    required_args = ["dpt"]
    args_values, missing_args = check_required_args(request, required_args)
    if missing_args:
        return jsonify({"error": f"Missing arguments: {', '.join(missing_args)}"}), 400

    client = current_app.mongo_client
    dpt = args_values["dpt"]
    collection = client[current_app.config.get("DB_NAME", "pompier")]["interv_synthese"]
    try:
        data = collection.find({"dpt": dpt}, {"_id": 0})
        return jsonify(list(data)), 200
    except Exception as e:
        return handle_exception(e)


@data_blueprint.route("/time-ranges", methods=["GET"])
def get_time_ranges():
    required_args = ["dpt", "type"]
    args_values, missing_args = check_required_args(request, required_args)
    if missing_args:
        return jsonify({"error": f"Missing arguments: {', '.join(missing_args)}"}), 400

    client = current_app.mongo_client
    collection = client[current_app.config.get("DB_NAME", "pompier")]["tranches"]
    dpt = args_values["dpt"]
    type = args_values["type"]
    try:
        data = collection.find({"dpt": dpt, "type_interv": type}, {"_id": 0}).sort(
            "item", 1
        )
        time_ranges = [item["tranche"] for item in data]

        return jsonify(time_ranges), 200
    except Exception as e:
        return handle_exception(e)


@data_blueprint.route("/history", methods=["GET"])
def get_history():
    required_args = ["dpt"]
    args_values, missing_args = check_required_args(request, required_args)
    if missing_args:
        return jsonify({"error": f"Missing arguments: {', '.join(missing_args)}"}), 400

    client = current_app.mongo_client
    collection = client[current_app.config.get("DB_NAME", "pompier")]["history"]
    dpt = args_values["dpt"]
    try:
        data = collection.find({"dpt": dpt}, {"_id": 0, "dpt": 0}).sort("creneau", 1)

        return jsonify(list(data)), 200
    except Exception as e:
        return handle_exception(e)


@data_blueprint.route("/mv", methods=["GET"])
def get_mv():
    required_args = ["mv"]
    args_values, missing_args = check_required_args(request, required_args)
    if missing_args:
        return jsonify({"error": f"Missing arguments: {', '.join(missing_args)}"}), 400

    client = current_app.mongo_client
    mv = args_values["mv"]
    collection = client[current_app.config.get("DB_NAME", "pompier")][mv]
    try:
        data = collection.find({}, {"_id": 0})
        return jsonify(list(data)), 200
    except Exception as e:
        return handle_exception(e)


@data_blueprint.route("/pages", methods=["GET"])
def get_pages():
    required_args = ["dpt"]
    args_values, missing_args = check_required_args(request, required_args)
    if missing_args:
        return jsonify({"error": f"Missing arguments: {', '.join(missing_args)}"}), 400

    client = current_app.mongo_client
    dpt = args_values["dpt"]
    collection = client[current_app.config.get("DB_NAME", "pompier")]["pages"]
    try:
        data = collection.find({"dpt": dpt}, {"_id": 0})
        return jsonify(list(data)), 200
    except Exception as e:
        return handle_exception(e)


@data_blueprint.route("/pages-alerts", methods=["GET"])
def get_pages_alerts():
    required_args = ["dpt"]
    args_values, missing_args = check_required_args(request, required_args)
    if missing_args:
        return jsonify({"error": f"Missing arguments: {', '.join(missing_args)}"}), 400

    client = current_app.mongo_client
    dpt = args_values["dpt"]
    collection = client[current_app.config.get("DB_NAME", "pompier")]["pages_alerts"]
    try:
        data = collection.find({"dpt": dpt}, {"_id": 0})
        return jsonify(list(data)), 200
    except Exception as e:
        return handle_exception(e)


@data_blueprint.route("/popup", methods=["GET"])
def get_popup():
    required_args = ["dpt"]
    args_values, missing_args = check_required_args(request, required_args)
    if missing_args:
        return jsonify({"error": f"Missing arguments: {', '.join(missing_args)}"}), 400

    client = current_app.mongo_client
    dpt = args_values["dpt"]
    collection = client[current_app.config.get("DB_NAME", "pompier")]["popup"]
    try:
        data = collection.find_one({"dpts": dpt}, sort=[("timestamp", -1)])

        if data:
            return jsonify(data), 200
        else:
            return jsonify({"message": "No popup found for the specified dpt."}), 204
    except Exception as e:
        return handle_exception(e)


@data_blueprint.route("/quality", methods=["GET"])
def get_quality():
    required_args = ["dpt", "horizon"]
    args_values, missing_args = check_required_args(request, required_args)
    if missing_args:
        return jsonify({"error": f"Missing arguments: {', '.join(missing_args)}"}), 400

    client = current_app.mongo_client
    dpt = args_values["dpt"]
    horizon = args_values["horizon"]
    collection = client[current_app.config.get("DB_NAME", "pompier")]["quality"]
    bounds_collection = client[current_app.config.get("DB_NAME", "pompier")]["bounds"]
    try:
        bounds_docs = bounds_collection.find({"dpt": dpt}, {"_id": 0})
        bounds_data = list(bounds_docs)
        bounds = bounds_data[0]["bounds"]["Qualité des interventions"]
        bounds_quality = bounds["Qualité"]

        doc = collection.find_one(
            {"dpt": dpt, "horizon": horizon}, {"_id": 0}
        )
        if doc:

            quality, num_delays, average_time_difference = (
                int(round(doc.get("quality", 0), 0)),
                doc.get("num_delays", 0),
                doc.get("average_time_difference", 0),
            )

            # Prepare the final data structure
            data = [
                dict(
                    label="Qualité",
                    value=f"{quality}%",
                    color=get_quality_color(int(quality), bounds_quality),
                    description="Pourcentage représentant le ratio entre le nombre d'interventions dans les délais par le nombre total d'interventions.",
                ),
                dict(
                    label="Nombre de retards",
                    value=num_delays,
                    # color=get_num_delays_color(int(num_delays), bounds_num_delays),
                    color="transparent",
                    description=f"Nombre d'interventions en retard sur {horizon}.",
                ),
                dict(
                    label="Délai d'arrivée moyen",
                    value=f"{average_time_difference} min.",
                    # color=get_average_difference_time_color(int(average_time_difference), bounds_average_difference_time),
                    color="transparent",
                    description="Temps moyen d'arrivée sur les lieux.",
                ),
            ]
        else:
            data = []
        return jsonify(data), 200
    except Exception as e:
        return handle_exception(e)


@data_blueprint.route("/delays", methods=["GET"])
def get_delays():
    required_args = ["dpt", "start", "stop"]
    args_values, missing_args = check_required_args(request, required_args)
    if missing_args:
        return jsonify({"error": f"Missing arguments: {', '.join(missing_args)}"}), 400

    client = current_app.mongo_client
    dpt = args_values["dpt"]
    start_str = args_values["start"]
    stop_str = args_values["stop"]

    bounds_collection = client[current_app.config.get("DB_NAME", "pompier")]["bounds"]
    # data_collection = client[current_app.config.get("DB_NAME", "pompier")]["intervention_delays"]    
    data_collection = client["pompier"][f"intervention_delays_{dpt}"]    
    # data = list(data_collection.find({"dpt" : dpt}))
    data = list(data_collection.find({}, {"_id": 0}))
    try:
        bounds_docs = bounds_collection.find({"dpt": dpt}, {"_id": 0})
        bounds_data = list(bounds_docs)
        bounds = bounds_data[0]["bounds"]["Qualité des interventions"]
        bounds_quality = bounds["Qualité"]
        geojson, status_code = get_delays_data(data, dpt, start_str, stop_str, True, bounds_quality)
        return jsonify(geojson), status_code
        
    except Exception as e:
        return handle_exception(e)


@data_blueprint.route("/radioitems", methods=["GET"])
def get_radioitems():
    required_args = ["page"]
    args_values, missing_args = check_required_args(request, required_args)
    if missing_args:
        return jsonify({"error": f"Missing arguments: {', '.join(missing_args)}"}), 400

    client = current_app.mongo_client
    page = args_values["page"]
    collection = client[current_app.config.get("DB_NAME", "pompier")]["radioitems"]
    try:
        data = collection.find_one({"page": page}, {"_id": 0})
        return jsonify(data), 200
    except Exception as e:
        return handle_exception(e)


@data_blueprint.route("/reliability-options", methods=["GET"])
def get_reliability_options():
    def generate_labels(horizon_values):
        if not horizon_values:
            return []

        # Sort the unique horizon values
        horizon_values = sorted(set(horizon_values))

        # Determine the step by finding the difference between the first two values
        step = horizon_values[1] - horizon_values[0]

        labels = []
        for value in horizon_values:
            start_hour = value
            end_hour = (value + step) % 24
            label = f"{start_hour:02}h-{end_hour:02}h"
            labels.append({"label": label, "value": value})

        return labels

    required_args = ["dpt"]
    args_values, missing_args = check_required_args(request, required_args)
    if missing_args:
        return jsonify({"error": f"Missing arguments: {', '.join(missing_args)}"}), 400

    client = current_app.mongo_client
    dpt = args_values["dpt"]
    collection = client[current_app.config.get("DB_NAME", "pompier")]["fiabilite"]
    try:
        pipeline = [
            {"$match": {"dpt": dpt}},
            {"$group": {"_id": "$type_interv", "horizons": {"$addToSet": "$horizon"}}},
            {"$project": {"_id": 0, "type_interv": "$_id", "horizons": 1}},
        ]

        results = list(collection.aggregate(pipeline))

        # Transform results to the required structure
        data = []
        for result in results:
            labels = generate_labels(result["horizons"])
            data.append({"type_interv": result["type_interv"], "horizons": labels})
        tous_index = next(
            (i for i, x in enumerate(data) if x["type_interv"] == "Tous"), None
        )
        if tous_index is not None:
            tous = data.pop(tous_index)
            data.insert(0, tous)

        return jsonify(data), 200
    except Exception as e:
        return handle_exception(e)


@data_blueprint.route("/reliability", methods=["GET"])
def get_reliability():
    required_args = ["dpt", "horizon", "type", "decoupe"]
    args_values, missing_args = check_required_args(request, required_args)
    if missing_args:
        return jsonify({"error": f"Missing arguments: {', '.join(missing_args)}"}), 400

    client = current_app.mongo_client
    dpt = args_values["dpt"]
    horizon = args_values["horizon"]
    type_interv = args_values["type"]
    decoupe = args_values["decoupe"]
    if type_interv == "CIS-SAP":
        type_interv = "CIS"
    if type_interv == "CIS-INC":
        type_interv = "CIS_INC"
    if type_interv == "Appels":
        type_interv = "appels"
    collection = client[current_app.config.get("DB_NAME", "pompier")]["fiabilite"]
    try:
        data = list(
            collection.find(
                {
                    "dpt": dpt,
                    "horizon": int(horizon),
                    "type_interv": type_interv,
                    "id_geom": int(decoupe),
                },
                {"_id": 0},
            ).sort("creneau")
        )
        if not data:
            return jsonify({"error": "Aucune donnée."}), 404

        reel_dict = {
            item["creneau"]: item["value"] for item in data if item["cas"] == "reel"
        }
        predit_dict = {
            item["creneau"]: item["mean"] for item in data if item["cas"] == "predit"
        }

        common_dates = set(reel_dict.keys()).intersection(set(predit_dict.keys()))
        reel_values = [reel_dict[date] for date in common_dates]
        predit_values = [predit_dict[date] for date in common_dates]

        if not reel_values or not predit_values:
            return jsonify({"error": "Données manquantes pour calculer la MAE."}), 400

        mae = mean_absolute_error(reel_values, predit_values)

        return jsonify({"data": data, "mae": mae}), 200
    except Exception as e:
        return handle_exception(e)


@data_blueprint.route("/vigicrues", methods=["GET"])
def get_vigicrues():
    required_args = ["dpt"]
    args_values, missing_args = check_required_args(request, required_args)
    if missing_args:
        return jsonify({"error": f"Missing arguments: {', '.join(missing_args)}"}), 400

    client = current_app.mongo_client
    dpt = args_values["dpt"]
    collection = client[current_app.config.get("DB_NAME", "pompier")]["vigicrues"]
    try:
        data = collection.find({"dpt": dpt}, {"_id": 0})
        df = pd.DataFrame(list(data))
        return jsonify(df.to_dict("records")), 200
    except Exception as e:
        return handle_exception(e)


@data_blueprint.route("/water-station-measure", methods=["GET"])
def get_water_station_measure():
    required_args = ["station"]
    args_values, missing_args = check_required_args(request, required_args)
    if missing_args:
        return jsonify({"error": f"Missing arguments: {', '.join(missing_args)}"}), 400

    client = current_app.mongo_client
    station = args_values["station"]
    collection = client[current_app.config.get("DB_NAME", "pompier")]["hauteur_eau"]
    try:
        data = collection.find({"nom": str.title(station)}, {"_id": 0})
        df = pd.DataFrame(list(data))
        df.fillna(0, inplace=True)
        return jsonify(df.to_dict("records")), 200
    except Exception as e:
        return handle_exception(e)


@data_blueprint.route("/viginappes", methods=["GET"])
def get_viginappes():
    required_args = ["dpt"]
    args_values, missing_args = check_required_args(request, required_args)
    if missing_args:
        return jsonify({"error": f"Missing arguments: {', '.join(missing_args)}"}), 400

    client = current_app.mongo_client
    dpt = args_values["dpt"]
    collection = client[current_app.config.get("DB_NAME", "pompier")]["viginappes"]
    try:
        data = collection.find({"dpt": dpt}, {"_id": 0})
        df = pd.DataFrame(list(data))
        return jsonify(df.to_dict("records")), 200
    except Exception as e:
        return handle_exception(e)


@data_blueprint.route("/groundwater-measure", methods=["GET"])
def get_groundwater_measure():
    required_args = ["groundwater"]
    args_values, missing_args = check_required_args(request, required_args)
    if missing_args:
        return jsonify({"error": f"Missing arguments: {', '.join(missing_args)}"}), 400

    client = current_app.mongo_client
    groundwater = args_values["groundwater"]
    collection = client[current_app.config.get("DB_NAME", "pompier")]["hauteur_nappes"]
    try:
        data = collection.find({"code_geom": groundwater}, {"_id": 0})
        df = pd.DataFrame(list(data))
        df.fillna(0, inplace=True)
        return jsonify(df.to_dict("records")), 200
    except Exception as e:
        return handle_exception(e)


@data_blueprint.route("/weather-alerts", methods=["GET"])
def get_weather_alerts():
    required_args = ["dpt", "sub-dpt"]
    args_values, missing_args = check_required_args(request, required_args)
    if missing_args:
        return jsonify({"error": f"Missing arguments: {', '.join(missing_args)}"}), 400

    client = current_app.mongo_client
    dpt, sub_dpt = args_values["dpt"], args_values["sub-dpt"]
    collection = client[current_app.config.get("DB_NAME", "pompier")]["meteo"]
    try:
        if sub_dpt != "undefined":
            department_number = sub_dpt[:2]
            docs = collection.find(
                {"department": department_number, "dpt": dpt, "value": {"$gt": 0}},
                {"_id": 0},
            ).sort("time", 1)
            df = pd.DataFrame(list(docs))
            if not df.empty:
                df["date"] = df["date"].dt.strftime("%d/%m")
                alerts = transform_alerts_apex(df)

                return alerts, 200
            else:
                return jsonify([]), 200
        else:
            return jsonify([]), 200
    except Exception as e:
        return handle_exception(e)


@data_blueprint.route("/weather", methods=["GET"])
def get_weather():
    required_args = ["dpt", "sub-dpt"]
    args_values, missing_args = check_required_args(request, required_args)
    if missing_args:
        return jsonify({"error": f"Missing arguments: {', '.join(missing_args)}"}), 400

    client = current_app.mongo_client
    dpt, sub_dpt = args_values["dpt"], args_values["sub-dpt"]
    collection = client[current_app.config.get("DB_NAME", "pompier")]["radioitems"]
    try:
        if sub_dpt != "undefined":
            docs = collection.find({"page": f"var-exp-{dpt}"}, {"_id": 0})
            coordinates = pd.DataFrame(list(docs))["coordinates"].to_list()[0][sub_dpt]
            lat, lon = coordinates[0], coordinates[1]
            url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHERMAP_API_KEY}&units=metric"
            response = requests.get(url)
            data = response.json()
            icon = data["weather"][0]["icon"]
            temp_min = round(data["main"]["temp_min"], 1)
            temp_max = round(data["main"]["temp_max"], 1)
            temp_current = round(data["main"]["temp"], 1)
            humidity = round(data["main"]["humidity"], 1)
            pressure = round(data["main"]["pressure"], 1)
            sunrise, sunset = get_sunrise_sunset(lat, lon)

            return jsonify(
                dict(
                    icon=icon,
                    temp_min=temp_min,
                    temp_max=temp_max,
                    current_temp=temp_current,
                    humidity=humidity,
                    pressure=pressure,
                    sunrise=sunrise,
                    sunset=sunset,
                ),
                200,
            )
        else:
            return jsonify(
                dict(
                    icon="undefined",
                    temp_min="undefined",
                    temp_max="undefined",
                    current_temp="undefined",
                    humidity="undefined",
                    pressure="undefined",
                    sunrise="undefined",
                    sunset="undefined",
                ),
                200,
            )

    except Exception as e:
        return handle_exception(e)
