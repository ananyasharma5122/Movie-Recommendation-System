from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash

from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId

import os


# =====================================================
# LOAD ENVIRONMENT VARIABLES
# =====================================================

load_dotenv()


# =====================================================
# FLASK APP
# =====================================================

app = Flask(__name__)


# =====================================================
# CORS
# =====================================================

CORS(
    app,
    origins=["http://localhost:5173"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"]
)


# =====================================================
# JWT CONFIGURATION
# =====================================================

app.config["JWT_SECRET_KEY"] = os.getenv(
    "JWT_SECRET_KEY",
    "movieverse-secret-key"
)

jwt = JWTManager(app)


# =====================================================
# MONGODB CONNECTION
# =====================================================

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb://localhost:27017/"
)

try:

    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000
    )

    # Test MongoDB connection
    client.admin.command("ping")

    print("MongoDB Connected Successfully!")

    # Database
    db = client["MovieVerse"]

    # Users collection
    users_collection = db["users"]

except Exception as e:

    print("MongoDB Connection Failed!")
    print(e)

    client = None
    db = None
    users_collection = None


# =====================================================
# HOME ROUTE
# =====================================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "message": "MovieVerse Backend + MongoDB is running 🎬"
    })


# =====================================================
# MONGODB TEST ROUTE
# =====================================================

@app.route("/api/test-db", methods=["GET"])
def test_db():

    try:

        if client is None:

            return jsonify({
                "message": "MongoDB is not connected"
            }), 500

        client.admin.command("ping")

        return jsonify({
            "message": "MongoDB connected successfully 🎉"
        }), 200

    except Exception as e:

        return jsonify({
            "message": "MongoDB connection failed",
            "error": str(e)
        }), 500


# =====================================================
# SIGNUP
# =====================================================

@app.route("/api/auth/signup", methods=["POST"])
def signup():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "message": "No data received"
            }), 400

        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        if not name or not email or not password:

            return jsonify({
                "message": "All fields are required"
            }), 400

        email = email.lower().strip()

        if users_collection is None:

            return jsonify({
                "message": "Database is not connected"
            }), 500

        # Check existing user
        existing_user = users_collection.find_one({
            "email": email
        })

        if existing_user:

            return jsonify({
                "message": "Email already registered"
            }), 409

        # Hash password
        hashed_password = generate_password_hash(
            password
        )

        # Create user
        user = {

            "name": name.strip(),

            "email": email,

            "password": hashed_password,

            "favorites": [],

            "watchlist": [],

            "ratings": []

        }

        result = users_collection.insert_one(user)

        return jsonify({

            "message": "Account created successfully 🎉",

            "user_id": str(result.inserted_id)

        }), 201

    except Exception as e:

        print("Signup Error:", e)

        return jsonify({

            "message": "Signup failed",

            "error": str(e)

        }), 500


# =====================================================
# LOGIN
# =====================================================

@app.route("/api/auth/login", methods=["POST"])
def login():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "message": "No data received"
            }), 400

        email = data.get("email")
        password = data.get("password")

        if not email or not password:

            return jsonify({
                "message": "Email and password are required"
            }), 400

        email = email.lower().strip()

        if users_collection is None:

            return jsonify({
                "message": "Database is not connected"
            }), 500

        # Find user
        user = users_collection.find_one({
            "email": email
        })

        if not user:

            return jsonify({
                "message": "Invalid email or password"
            }), 401

        # Check password
        if not check_password_hash(
            user["password"],
            password
        ):

            return jsonify({
                "message": "Invalid email or password"
            }), 401

        # Create JWT
        token = create_access_token(
            identity=str(user["_id"])
        )

        return jsonify({

            "message": "Login successful 🎉",

            "token": token,

            "user": {

                "id": str(user["_id"]),

                "name": user["name"],

                "email": user["email"]

            }

        }), 200

    except Exception as e:

        print("Login Error:", e)

        return jsonify({

            "message": "Login failed",

            "error": str(e)

        }), 500


# =====================================================
# PROFILE
# =====================================================

@app.route("/api/auth/profile", methods=["GET"])
@jwt_required()
def profile():

    try:

        user_id = get_jwt_identity()

        if users_collection is None:

            return jsonify({
                "message": "Database is not connected"
            }), 500

        user = users_collection.find_one({
            "_id": ObjectId(user_id)
        })

        if not user:

            return jsonify({
                "message": "User not found"
            }), 404

        return jsonify({

            "id": str(user["_id"]),

            "name": user["name"],

            "email": user["email"],

            "favorites": user.get(
                "favorites",
                []
            ),

            "watchlist": user.get(
                "watchlist",
                []
            ),

            "ratings": user.get(
                "ratings",
                []
            )

        }), 200

    except Exception as e:

        print("Profile Error:", e)

        return jsonify({

            "message": "Could not fetch profile",

            "error": str(e)

        }), 500


# =====================================================
# LOGOUT
# =====================================================

@app.route("/api/auth/logout", methods=["POST"])
def logout():

    return jsonify({

        "message": "Logout successful"

    }), 200


# =====================================================
# ADD TO FAVORITES
# =====================================================

@app.route("/api/movies/favorite", methods=["POST"])
@jwt_required()
def add_favorite():

    try:

        user_id = get_jwt_identity()

        data = request.get_json()

        if not data:

            return jsonify({
                "message": "No movie data received"
            }), 400

        movie = data.get("movie")

        if not movie:

            return jsonify({
                "message": "Movie data is required"
            }), 400

        if users_collection is None:

            return jsonify({
                "message": "Database is not connected"
            }), 500

        users_collection.update_one(

            {
                "_id": ObjectId(user_id)
            },

            {
                "$addToSet": {
                    "favorites": movie
                }
            }

        )

        return jsonify({

            "message": "Movie added to favorites ❤️"

        }), 200

    except Exception as e:

        print("Favorite Error:", e)

        return jsonify({

            "message": "Could not add favorite",

            "error": str(e)

        }), 500


# =====================================================
# ADD TO WATCHLIST
# =====================================================

@app.route("/api/movies/watchlist", methods=["POST"])
@jwt_required()
def add_watchlist():

    try:

        user_id = get_jwt_identity()

        data = request.get_json()

        if not data:

            return jsonify({
                "message": "No movie data received"
            }), 400

        movie = data.get("movie")

        if not movie:

            return jsonify({
                "message": "Movie data is required"
            }), 400

        if users_collection is None:

            return jsonify({
                "message": "Database is not connected"
            }), 500

        users_collection.update_one(

            {
                "_id": ObjectId(user_id)
            },

            {
                "$addToSet": {
                    "watchlist": movie
                }
            }

        )

        return jsonify({

            "message": "Movie added to watchlist 🔖"

        }), 200

    except Exception as e:

        print("Watchlist Error:", e)

        return jsonify({

            "message": "Could not add watchlist",

            "error": str(e)

        }), 500


# =====================================================
# REMOVE FROM FAVORITES
# =====================================================

@app.route("/api/movies/favorite/<movie_id>", methods=["DELETE"])
@jwt_required()
def remove_favorite(movie_id):

    try:

        user_id = get_jwt_identity()

        result = users_collection.update_one(

            {
                "_id": ObjectId(user_id)
            },

            {
                "$pull": {
                    "favorites": {
                        "id": int(movie_id)
                    }
                }
            }

        )

        return jsonify({

            "message": "Movie removed from favorites"

        }), 200

    except Exception as e:

        print("Remove Favorite Error:", e)

        return jsonify({

            "message": "Could not remove favorite",

            "error": str(e)

        }), 500


# =====================================================
# REMOVE FROM WATCHLIST
# =====================================================

@app.route("/api/movies/watchlist/<movie_id>", methods=["DELETE"])
@jwt_required()
def remove_watchlist(movie_id):

    try:

        user_id = get_jwt_identity()

        users_collection.update_one(

            {
                "_id": ObjectId(user_id)
            },

            {
                "$pull": {
                    "watchlist": {
                        "id": int(movie_id)
                    }
                }
            }

        )

        return jsonify({

            "message": "Movie removed from watchlist"

        }), 200

    except Exception as e:

        print("Remove Watchlist Error:", e)

        return jsonify({

            "message": "Could not remove watchlist",

            "error": str(e)

        }), 500


# =====================================================
# START SERVER
# =====================================================

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )