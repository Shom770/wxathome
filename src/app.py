from os import environ

import requests
from certifi import where
from dotenv import load_dotenv
from flask import Flask, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.hash import sha256_crypt
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# Load environment variables
load_dotenv()

# Constants
MONGO_PASSWORD = environ.get("MONGODB_PASSWORD")
WEATHER_API = "https://api.weather.gov"

# Initialize clients for Flask and MongoDB
uri = f"mongodb+srv://shayaanwadkar:{MONGO_PASSWORD}@cluster0.mqvayku.mongodb.net/?retryWrites=true&w=majority"

app = Flask(__name__)
client = MongoClient(
    uri,
    server_api=ServerApi('1'),
    tlsCAFile=where()
)
database = client.get_database("wxathome")

# Configure the Flask app
app.config["SECRET_KEY"] = environ.get("FLASK_HASH")
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "mongodb"
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["SESSION_COOKIE_NAME"] = "wxathome"
app.config["SESSION_MONGODB"] = client
app.config["SESSION_MONGODB_DB"] = "wxathome"
app.config["SESSION_MONGODB_COLLECTION"] = "sessions"

# Start the session to keep the user logged in
Session(app)


def _get_base_params() -> dict[str, str]:
    """Returns the base parameters later utilized by the Flask App."""
    return {
        "color": "#98CCEB",
        "secondary_color": "#0D1117",
        "red_color": "#FFB3B3",
        "green_color": "#B3FFB3",
        "name": session.get("name", "").title(),
        "station_name": session.get("station_code"),
        "logged_in": session.get("logged_in", False)
    }


@app.route("/")
def home():
    return render_template(
        "index.html",
        base=_get_base_params(),
        metric_deltas={"temperature": 1, "dewpoint": -10, "relative_humidity": -40}
    )


@app.route("/login")
def login():
    return render_template("login.html", base=_get_base_params())


@app.route("/signup")
def signup():
    return render_template("signup.html", base=_get_base_params())


@app.route("/process_signup", methods=["POST"])
def process_signup():
    signup_info = request.get_json()

    # Return an error if any of the fields are empty.
    fields_filled = sum(bool(signup_info[field]) for field in ("username", "password", "station_code"))

    if fields_filled < 3:
        return {"action": f"{3 - fields_filled} field(s) are empty."}

    # Make sure the station code provided exists.
    validate_station = requests.get(f"{WEATHER_API}/stations/{signup_info['station_code']}")
    if validate_station.status_code == 404:
        return {"action": "The station code you provided doesn't exist."}

    # Make sure that the username provided isn't already in the database.
    users = database.get_collection("users")
    if users.find_one({"username": signup_info["username"]}):
        return {"action": "The username provided is already in use."}

    # Create the user in the database and return a successful signup.
    hashed_password = sha256_crypt.hash(signup_info["password"])
    users.insert_one({
        "username": signup_info["username"],
        "password": hashed_password,
        "station_code": signup_info["station_code"]
    })

    # Set up the Flask session to keep the user logged in.
    session["name"] = signup_info["username"]
    session["station_code"] = signup_info["station_code"]
    session["logged_in"] = True

    return {"action": "Success"}


@app.route("/process_login", methods=["POST"])
def process_login():
    login_info = request.get_json()

    # Return an error if any of the fields are empty.
    fields_filled = sum(bool(login_info[field]) for field in ("username", "password"))

    if fields_filled < 2:
        return {"action": f"{2 - fields_filled} field(s) are empty."}

    # Make sure that the user exists in the database.
    users = database.get_collection("users")
    if not (user := users.find_one({"username": login_info["username"]})):
        return {"action": "Username or password is incorrect."}

    # Make sure that the password provided is correct
    password_correct = sha256_crypt.verify(login_info["password"], user["password"])
    if not password_correct:
        return {"action": "Username or password is incorrect."}

    # Set up the Flask session to keep the user logged in.
    session["name"] = login_info["username"]
    session["station_code"] = user["station_code"]
    session["logged_in"] = True

    return {"action": "Success"}


@app.route("/logout")
def logout():
    session["name"] = ""
    session["logged_in"] = False
    session["station_code"] = ""

    return redirect(url_for("login"))


if __name__ == '__main__':
    app.run(debug=True)
