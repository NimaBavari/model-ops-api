import threading
from typing import Any, Dict, Tuple

from flask import Flask, request, session

from .db import Session, sess
from .helpers import check_password, log_request
from .models import Model, User

app = Flask(__name__)
app.config.from_object("api.settings.DevelopmentConfig")


@app.teardown_appcontext
def teardown_db(resp_or_exc):
    Session.remove()


@app.route("/login/", methods=["POST"])
def login() -> Tuple[Dict[str, Any], int]:
    data = request.json
    log_data = "Endpoint: %s, Method: %s, Data: %s" % (request.endpoint, request.method, data)
    threading.Thread(target=log_request, args=(log_data,)).start()

    try:
        email = data["email"]
        password = data["password"]
    except KeyError:
        return {"message": "Malformed request: no email or password"}, 400

    user = sess.query(User).filter(User.email_address == email).one_or_none()
    if not user or not check_password(password, user.password_hash):
        return {"message": "Wrong credentials."}, 401

    session["current_user"] = user._mapping
    return {"message": "Login successful."}, 200


@app.route("/logout/", methods=["POST"])
def logout() -> Tuple[Dict[str, Any], int]:
    log_data = "Endpoint: %s, Method: %s, Data: %s" % (request.endpoint, request.method, request.json)
    threading.Thread(target=log_request, args=(log_data,)).start()

    if "current_user" in session:
        del session["current_user"]
    return {"message": "Logout successful."}, 200


@app.route("/users/", methods=["GET"])
def list_users() -> Tuple[Dict[str, Any], int]:
    log_data = "Endpoint: %s, Method: %s, Data: %s" % (request.endpoint, request.method, request.json)
    threading.Thread(target=log_request, args=(log_data,)).start()

    curr_user = session.get("current_user", None)
    if not curr_user:
        return {"message": "Not authenticated."}, 401

    all_users = sess.query(User).all()
    return all_users, 200


@app.route("/users/<int:user_id>/", methods=["GET"])
def get_user(user_id: int) -> Tuple[Dict[str, Any], int]:
    log_data = "Endpoint: %s, Method: %s, Data: %s" % (request.endpoint, request.method, request.json)
    threading.Thread(target=log_request, args=(log_data,)).start()

    curr_user = session.get("current_user", None)
    if not curr_user:
        return {"message": "Not authenticated."}, 401

    user = sess.get(User, user_id)
    if not user:
        return {"message": "Not found."}, 404

    return user, 200


@app.route("/users/<int:user_id>/models/", methods=["GET"])
def list_models(user_id: int) -> Tuple[Dict[str, Any], int]:
    log_data = "Endpoint: %s, Method: %s, Data: %s" % (request.endpoint, request.method, request.json)
    threading.Thread(target=log_request, args=(log_data,)).start()

    curr_user = session.get("current_user", None)
    if not curr_user:
        return {"message": "Not authenticated."}, 401

    user = sess.get(User, user_id)
    if not user:
        return {"message": "Not found."}, 404

    if user != curr_user:
        return {"message": "Not authorized."}, 403

    all_models = sess.query(Model).filter(Model.user_id == user_id).all()
    return all_models, 200


@app.route("/users/<int:user_id>/models/<int:model_id>/predict/", methods=["GET"])
def predict_with_model(user_id: int, model_id: int) -> Tuple[Dict[str, Any], int]:
    log_data = "Endpoint: %s, Method: %s, Data: %s" % (request.endpoint, request.method, request.json)
    threading.Thread(target=log_request, args=(log_data,)).start()

    curr_user = session.get("current_user", None)
    if not curr_user:
        return {"message": "Not authenticated."}, 401

    user = sess.get(User, user_id)
    if not user:
        return {"message": "Not found."}, 404

    if user != curr_user:
        return {"message": "Not authorized."}, 403

    model = sess.get(Model, model_id)
    if not model or model.user_id != user_id:
        return {"message": "Not found."}, 404

    try:
        algorithm = eval(model.algorithm)
    except NameError:
        # import the relevant algorithm
        pass

    output = algorithm(model.inputs, model.weights)
    return {"output": output}, 200
