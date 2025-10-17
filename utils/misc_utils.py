import pandas as pd
from astral.sun import sun
from astral import LocationInfo
import pytz
from datetime import datetime, timedelta
from PIL import Image, ImageDraw, ImageFont
import base64
import io
from collections import defaultdict
import json
import copy
import os
from shapely.geometry import shape, mapping
import math


def check_required_args(request, required_args):
    args_values = {arg: request.args.get(arg) for arg in required_args}
    missing_args = [arg for arg, value in args_values.items() if value is None]
    return args_values, missing_args

def combine_date_and_time(date_str, time_str, is_start=True):
    """
    Combine 'dd/mm/yyyy' and 'HH:MM' into a datetime.
      - If time_str is valid, use it.
      - If time_str is None or empty, use either 00:00:00 (if is_start=True)
        or 23:59:59 (if is_start=False).
    Returns a datetime object or None if date_str is invalid.
    """
    if not date_str:
        # No date at all
        return None

    if date_str == "Indéterminée":
        # Some business logic: treat as an extremely distant date
        return datetime.max if not is_start else datetime.min

    try:
        base_date = datetime.strptime(date_str, "%d/%m/%Y")
    except ValueError:
        return None  # or raise an exception

    if time_str:
        # If user provided something like 'HH:MM'
        try:
            hours, minutes = map(int, time_str.split(':'))
            base_date = base_date.replace(hour=hours, minute=minutes, second=0)
        except (ValueError, AttributeError):
            # Time is malformed or not a string, decide how to handle
            pass
    else:
        # No time provided: default to midnight for start, or 23:59:59 for end
        if is_start:
            base_date = base_date.replace(hour=0, minute=0, second=0)
        else:
            base_date = base_date.replace(hour=23, minute=59, second=59)

    return base_date


def get_quality_color(quality, bounds_quality):
    # Extract values from bounds
    green_threshold = int(bounds_quality["vert"]["value"])
    yellow_threshold = int(bounds_quality["jaune"]["value"])
    orange_threshold = int(bounds_quality["orange"]["value"])
    red_threshold = int(bounds_quality["rouge"]["value"])

    # Determine color based on thresholds
    if quality < red_threshold:
        return "red"
    elif red_threshold <= quality < orange_threshold:
        return "orange"
    elif orange_threshold <= quality < yellow_threshold:
        return "yellow"
    elif quality >= green_threshold:
        return "green"
    else:
        return "black"


def transform_alerts(df):
    result = defaultdict(lambda: defaultdict(list))

    # Group by 'indicator' and then by 'date'
    grouped = df.groupby(["indicator", "date"])

    for (indicator, date), group in grouped:
        group = group.sort_values(["time"])
        current_alert = None

        for idx, row in group.iterrows():
            if current_alert is None:
                current_alert = {
                    "danger": row["value"],
                    "start": row["time"],
                    "end": row["time"],
                    "name": indicator,
                }
            else:
                current_hour = int(current_alert["end"].split(":")[0])
                next_hour = int(row["time"].split(":")[0])

                if (
                    next_hour == current_hour + 1
                    and row["value"] == current_alert["danger"]
                ):
                    current_alert["end"] = row["time"]
                else:
                    # Always add one hour to the end time
                    end_time = datetime.strptime(
                        current_alert["end"], "%H:%M"
                    ) + timedelta(hours=1)
                    current_alert["end"] = end_time.strftime("%H:%M")

                    # Append the current_alert to the result
                    result[date][indicator].append(current_alert)

                    # Start a new alert
                    current_alert = {
                        "danger": row["value"],
                        "start": row["time"],
                        "end": row["time"],
                        "name": indicator,
                    }

        if current_alert is not None:
            # Always add one hour to the end time
            end_time = datetime.strptime(current_alert["end"], "%H:%M") + timedelta(
                hours=1
            )
            current_alert["end"] = end_time.strftime("%H:%M")
            result[date][indicator].append(current_alert)

    # Convert the result to a list of objects, maintaining the same structure
    alert_list = []
    for date in sorted(result.keys(), key=lambda x: datetime.strptime(x, "%d/%m")):
        day_alerts = {"date": date, "indicators": []}
        for indicator, alerts in result[date].items():
            day_alerts["indicators"].append({"name": indicator, "alerts": alerts})
        alert_list.append(day_alerts)

    return alert_list


def transform_alerts_apex(df):
    data = df.copy()
    data = data[data["value"] > 0]

    current_year = datetime.now().year
    data["datetime"] = pd.to_datetime(
        f"{current_year}/" + data["date"] + " " + data["time"], format="%Y/%d/%m %H:%M"
    )
    data = data.sort_values(["indicator", "value", "datetime"])

    def find_time_ranges(group):
        time_ranges = []
        start_time = group.iloc[0]["datetime"]

        for i in range(1, len(group)):
            current_time = group.iloc[i]["datetime"]
            previous_time = group.iloc[i - 1]["datetime"]

            # Check if there is a gap of more than 1 hour
            if current_time > previous_time + timedelta(hours=1):
                time_ranges.append((start_time, previous_time + timedelta(hours=1)))
                start_time = current_time

        time_ranges.append(
            (start_time, group.iloc[-1]["datetime"] + timedelta(hours=1))
        )
        return time_ranges

    apex_series_dict = {}
    for (indicator, value), group in data.groupby(["indicator", "value"]):
        time_ranges = find_time_ranges(group)

        series_entries = []
        for start_time, end_time in time_ranges:
            series_entry = {
                "x": indicator,
                "y": [start_time.isoformat(), end_time.isoformat()],
            }
            series_entries.append(series_entry)

        if str(value) not in apex_series_dict:
            apex_series_dict[str(value)] = {"name": str(value), "data": []}

        apex_series_dict[str(value)]["data"].extend(series_entries)

    # Now we will generate the '0' series with gaps for each indicator separately
    for indicator in data["indicator"].unique():
        gap_series = {"name": "0", "data": []}  # '0' signifies the placeholder series

        # Filter the series data for the specific indicator
        indicator_data = [
            entry
            for series in apex_series_dict.values()
            for entry in series["data"]
            if entry["x"] == indicator
        ]

        if indicator_data:
            # Sort the entries by start time
            indicator_data.sort(key=lambda entry: datetime.fromisoformat(entry["y"][0]))

            previous_end = None
            first_alert_start = datetime.fromisoformat(indicator_data[0]["y"][0])

            current_time = datetime.now()

            # Check if there's a gap between 'now' and the first alert
            if first_alert_start > current_time:
                gap_series["data"].append(
                    {
                        "x": indicator,  # Same indicator
                        "y": [current_time.isoformat(), first_alert_start.isoformat()],
                    }
                )

            # Iterate through the series data and fill gaps between consecutive time ranges
            for entry in indicator_data:
                start_time = datetime.fromisoformat(entry["y"][0])

                if previous_end and start_time > previous_end:
                    # Add a placeholder for the gap
                    gap_series["data"].append(
                        {
                            "x": entry["x"],  # Same indicator
                            "y": [previous_end.isoformat(), start_time.isoformat()],
                        }
                    )

                previous_end = datetime.fromisoformat(entry["y"][1])

        # Append the gap series for this indicator if there are gaps
        if gap_series["data"]:
            if "0" not in apex_series_dict:
                apex_series_dict["0"] = {"name": "0", "data": []}
            apex_series_dict["0"]["data"].extend(gap_series["data"])

    apex_series = list(apex_series_dict.values())
    return apex_series


def get_sunrise_sunset(lat, lon):
    city = LocationInfo()
    city.region = "France"
    city.timezone = "Europe/Paris"
    city.latitude = lat
    city.longitude = lon
    date = datetime.now(pytz.timezone("Europe/Paris")).date()
    s = sun(city.observer, date=date, tzinfo=pytz.timezone("Europe/Paris"))

    sunrise = s["sunrise"].strftime("%H:%M")
    sunset = s["sunset"].strftime("%H:%M")

    return sunrise, sunset


def get_initials_from_email(email):
    parts = email.split("@")[0].split(".")
    if len(parts) == 1:
        initials = parts[0][:2].upper()
    else:
        initials = "".join(part[0].upper() for part in parts[:2])
    return initials


def generate_profile_image(initials):
    img = Image.new("RGB", (100, 100), color=(24, 22, 50))
    draw = ImageDraw.Draw(img)

    # Use a bold font
    font = ImageFont.truetype("assets/arialdb.ttf", 40)

    # Calculate text width and height using textbbox
    bbox = draw.textbbox((0, 0), initials, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    position = ((img.width - text_width) / 2, (img.height - text_height) / 2 - bbox[1])
    draw.text(position, initials, (255, 255, 255), font=font)

    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str


def get_color(timestamp):
    timestamp = timestamp.replace(tzinfo=pytz.timezone("Europe/Paris"))
    now = datetime.now(pytz.timezone("Europe/Paris"))
    delta = now - timestamp

    if delta <= timedelta(hours=3):
        return "#23a97b"  # Green
    elif delta <= timedelta(hours=6):
        # Interpolate between green and yellow
        total_seconds = delta.total_seconds() - 3 * 60 * 60
        ratio = total_seconds / (3 * 60 * 60)  # 3 hours to yellow
        green = int(169 + (253 - 169) * ratio)
        red = int(35 + (254 - 35) * ratio)
        blue = int(123 + (48 - 123) * ratio)
        return "#{:02X}{:02X}{:02X}".format(red, green, blue)
    elif delta <= timedelta(hours=9):
        # Interpolate between yellow and orange
        total_seconds = delta.total_seconds() - 6 * 60 * 60
        ratio = total_seconds / (3 * 60 * 60)  # 3 hours to orange
        green = int(253 + (146 - 253) * ratio)
        red = int(254 + (237 - 254) * ratio)
        blue = int(48 + (5 - 48) * ratio)
        return "#{:02X}{:02X}{:02X}".format(red, green, blue)
    elif delta <= timedelta(hours=12):
        # Interpolate between orange and red
        total_seconds = delta.total_seconds() - 9 * 60 * 60
        ratio = total_seconds / (3 * 60 * 60)  # 3 hours to red
        green = int(146 + (42 - 146) * ratio)
        red = int(237 + (201 - 237) * ratio)
        blue = int(5 + (42 - 5) * ratio)
        return "#{:02X}{:02X}{:02X}".format(red, green, blue)
    else:
        return "#c92a2a"


def get_delays_data(list, dpt, start_date_str, end_date_str, heatmap=False, bounds_quality=None, horizon="12h"):
    # Parse the dates
    date_format = "%Y-%m-%d"
    try:
        start_date = datetime.strptime(start_date_str, date_format).date()
        end_date = datetime.strptime(end_date_str, date_format).date()
    except ValueError:
        return {"error": f"Invalid date format. Expected format: {date_format}"}, 400

    

    try:
        data = pd.DataFrame(list)

        # Ensure 'start' is datetime
        if not pd.api.types.is_datetime64_any_dtype(data["start"]):
            data["start"] = pd.to_datetime(data["start"])

        # Convert 'start' to date
        data["start_date"] = data["start"].dt.date

        # Filter data
        filtered_data = data[
            (data["start_date"] >= start_date)
            & (data["start_date"] <= end_date)
        ]

        if filtered_data.empty:
            empty_geojson = {
                "type": "FeatureCollection",
                "features": [],
                "quality": [
                    dict(
                        label="Qualité",
                        value="100%",
                        color="green",
                        description="Pourcentage représentant le ratio interventions dans les délais / total.",
                    ),
                    dict(
                        label="Nombre de retards",
                        value=0,
                        color="transparent",
                        description=f"Nombre d'interventions en retard sur la période de {start_date_str} à {end_date_str}.",
                    ),
                    dict(
                        label="Délai d'arrivée moyen",
                        value="0 min.",
                        color="transparent",
                        description="Temps moyen d'arrivée sur les lieux.",
                    ),
                ]
            }
            return empty_geojson, 200

        # Build hex_interventions
        hex_interventions = {}
        for _, row in filtered_data.iterrows():
            hex_id = row["hex_id"]
            delay = row["delay"]
            raison = row.get("raison", "")
            centre = row["centre"]
            time_difference = row["time_difference (min)"]

            if hex_id not in hex_interventions:
                hex_interventions[hex_id] = {
                    "delayed_interventions": 0,
                    "on_time_interventions": 0,
                    "raisons": set(),
                    "centre": centre,
                    "time_difference": 0
                }

            if delay:
                hex_interventions[hex_id]["delayed_interventions"] += 1
            else:
                hex_interventions[hex_id]["on_time_interventions"] += 1

            hex_interventions[hex_id]["time_difference"] += time_difference
            if raison:
                hex_interventions[hex_id]["raisons"].add(raison)

        # Average time difference per hex
        for hex_id, info in hex_interventions.items():
            total_interventions_hex = info["delayed_interventions"] + info["on_time_interventions"]
            if total_interventions_hex > 0:
                info["average_time_difference"] = round(info["time_difference"] / total_interventions_hex, 2)
            else:
                info["average_time_difference"] = 0

        # Compute global indicators
        total_delayed = sum(info["delayed_interventions"] for info in hex_interventions.values())
        total_on_time = sum(info["on_time_interventions"] for info in hex_interventions.values())
        total_interventions_global = total_delayed + total_on_time

        if total_interventions_global > 0:
            quality = int(round((total_on_time / total_interventions_global) * 100, 0))
        else:
            quality = 100

        num_delays = str(total_delayed)

        total_time_diff_all = sum(info["time_difference"] for info in hex_interventions.values())
        if total_interventions_global > 0:
            global_avg_time_diff = round(total_time_diff_all / total_interventions_global, 2)
        else:
            global_avg_time_diff = 0

        average_time_difference = int(round(global_avg_time_diff, 0))

        # Load hexagones template
        template_path = f"static/hexagones/hexagones_{dpt}.geojson"
        if not os.path.exists(template_path):
            return {"error": "Hexagones template file not found."}, 404

        with open(template_path, "r") as geojson_file:
            template_data = json.load(geojson_file)

        # Prepare filtered_features
        filtered_features = []
        for feature in template_data["features"]:
            hex_id = feature["properties"]["hex_id"]
            if hex_id in hex_interventions:
                intervention_info = hex_interventions[hex_id]
                feature_copy = copy.deepcopy(feature)
                feature_copy["properties"].update({
                    "color": ("red" if intervention_info["delayed_interventions"] > 0 else "green"),
                    "centre": intervention_info["centre"],
                    "delayed_interventions": intervention_info["delayed_interventions"],
                    "on_time_interventions": intervention_info["on_time_interventions"],
                    "raison": ", ".join(intervention_info["raisons"]),
                    "average_time_difference": intervention_info["average_time_difference"]
                })
                filtered_features.append(feature_copy)

        data_indicators = [
            dict(
                label="Qualité",
                value=f"{quality}%",
                color=get_quality_color(int(quality), bounds_quality) if bounds_quality else "transparent",
                description="Pourcentage représentant le ratio entre le nombre d'interventions dans les délais par le nombre total d'interventions.",
            ),
            dict(
                label="Nombre de retards",
                value=num_delays,
                color="transparent",
                description=f"Nombre d'interventions en retard sur la période de {start_date_str} à {end_date_str}.",
            ),
            dict(
                label="Délai d'arrivée moyen",
                value=f"{average_time_difference} min.",
                color="transparent",
                description="Temps moyen d'arrivée sur les lieux.",
            ),
        ]

        # If not heatmap, return polygon GeoJSON
        if not heatmap:
            output_geojson = {
                "type": "FeatureCollection",
                "features": filtered_features,
                "quality": data_indicators
            }
            return output_geojson, 200
        else:
            # Heatmap scenario with log normalization
            max_delays = max(f["properties"]["delayed_interventions"] for f in filtered_features) if filtered_features else 0
            if max_delays == 0:
                # No delays at all, weights = 0
                max_delays = 1  # to avoid division by zero

            heatmap_features = []
            for f in filtered_features:
                geom = shape(f["geometry"])
                centroid = geom.centroid
                delayed = f["properties"]["delayed_interventions"]

                # Log scaling
                # weight = log(delayed_interventions + 1) / log(max_delays + 1)
                weight = math.log(delayed + 1, 10) / math.log(max_delays + 1, 10) if max_delays > 0 else 0

                heatmap_features.append({
                    "type": "Feature",
                    "geometry": mapping(centroid),
                    "properties": {"weight": weight},
                })

            heatmap_geojson = {
                "type": "FeatureCollection",
                "features": heatmap_features,
                "quality": data_indicators
            }
            return heatmap_geojson, 200

    except Exception as e:
        return {"error": str(e)}, 500