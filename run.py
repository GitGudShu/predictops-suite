from waitress import serve
from api import create_app
from dotenv import dotenv_values
from flask import request, current_app
from flask_socketio import SocketIO, disconnect
from datetime import datetime

config = dotenv_values(".env")

app = create_app()

socketio = SocketIO(app, cors_allowed_origins=config["ALLOW_ORIGIN"])

active_connections = {}


@socketio.on("connect")
def on_connect():
    print(f"Client connected: {request.sid}")


# Custom "login" event from the client
@socketio.on("login")
def on_login(email):
    """
    1. User logs in, providing their unique email.
    2. We store sid -> { email, start_time=now() } in memory.
    """
    active_connections[request.sid] = {"email": email, "start_time": datetime.now()}
    print(f"LOGIN event from {request.sid} (email={email})")


@socketio.on("logout")
def on_logout(email):
    """
    1. User logs out, passing their email again.
    2. We compute the time difference and add it to the user's total_activity in `predictops_users`.
    3. We remove them from in-memory dict and disconnect the socket.
    """
    print(f"LOGOUT event from {request.sid} (email={email})")
    user_data = active_connections.pop(request.sid, None)
    if user_data:
        duration = (datetime.now() - user_data["start_time"]).total_seconds()
        _update_user_total_activity(email, duration)
        print(f"User {email} was active for {duration} seconds this session.")

    disconnect()


@socketio.on("disconnect")
def on_disconnect():
    """
    1. Triggered if the user closes the tab, or if we called disconnect() after logout.
    2. If they're still in active_connections (meaning we didn't pop them in logout),
       we compute the duration and update their total_activity in the DB.
    """
    user_data = active_connections.pop(request.sid, None)
    if user_data:
        duration = (datetime.now() - user_data["start_time"]).total_seconds()
        _update_user_total_activity(user_data["email"], duration)
        print(f"User {user_data['email']} disconnected, adding {duration}s to total.")

    print(f"Client disconnected: {request.sid}")


def _update_user_total_activity(email, session_duration):
    """
    Helper function to increment the user's total_activity in the DB.
    """
    client = current_app.mongo_client
    users_collection = client[current_app.config["DB_NAME"]]["predictops_users"]

    # e.g., if user doc: { email: "someone@example.com", total_activity: <someNumber> }
    # we do an $inc with the session_duration
    users_collection.update_one(
        {"email": email}, {"$inc": {"total_activity": session_duration}}
    )


PRODUCTION = config.get("PRODUCTION", "False") == "True"

# if PRODUCTION:
#     serve(app, host="0.0.0.0", port=config["PORT"])
# else:
app.run(host="0.0.0.0", port=config["PORT"], debug=True)
# socketio.run(app, host="0.0.0.0", port=config["PORT"], debug=False, allow_unsafe_werkzeug=True)
