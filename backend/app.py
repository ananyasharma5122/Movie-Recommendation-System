from flask import Flask, jsonify, request
from flask_cors import CORS

from pathlib import Path
import os
import requests
from dotenv import load_dotenv

from recommender import MovieRecommender


# ============================================================
# FLASK APP
# ============================================================

app = Flask(__name__)

CORS(app)


# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

ENV_PATH = BASE_DIR / ".env"

load_dotenv(ENV_PATH, override=True)

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

print("=" * 60)
print("TMDB API key loaded:", bool(TMDB_API_KEY))
print("=" * 60)


# ============================================================
# DATASET PATH
# ============================================================

DATA_PATH = (
    BASE_DIR
    / "data"
    / "tmdb_5000_movies.csv"
)


# ============================================================
# CHECK DATASET
# ============================================================

if not DATA_PATH.exists():

    raise FileNotFoundError(
        f"""
Movie dataset not found!

Expected location:

{DATA_PATH}

Please place tmdb_5000_movies.csv inside:

backend/data/
"""
    )


# ============================================================
# LOAD RECOMMENDER
# ============================================================

print("=" * 60)
print("Starting MovieVerse backend...")
print("=" * 60)

recommender = MovieRecommender(DATA_PATH)


# ============================================================
# TMDB MOVIE DETAILS
# ============================================================

def get_tmdb_movie(movie_id):

    try:

        # ----------------------------------------------------
        # Check API key
        # ----------------------------------------------------

        if not TMDB_API_KEY:

            print("TMDB API key is missing.")

            return {}


        # ----------------------------------------------------
        # TMDB URL
        # ----------------------------------------------------

        url = (
            f"https://api.themoviedb.org/3/movie/"
            f"{movie_id}"
        )


        # ----------------------------------------------------
        # API KEY AUTHENTICATION
        # ----------------------------------------------------

        params = {

            "api_key":
                TMDB_API_KEY

        }


        # ----------------------------------------------------
        # REQUEST
        # ----------------------------------------------------

        response = requests.get(

            url,

            params=params,

            timeout=10

        )


        # ----------------------------------------------------
        # DEBUG
        # ----------------------------------------------------

        print(
            f"TMDB movie {movie_id}: "
            f"{response.status_code}"
        )


        # ----------------------------------------------------
        # ERROR
        # ----------------------------------------------------

        if response.status_code != 200:

            print(
                "TMDB error:",
                response.text
            )

            return {}


        # ----------------------------------------------------
        # JSON DATA
        # ----------------------------------------------------

        data = response.json()


        # ----------------------------------------------------
        # RETURN REQUIRED DATA
        # ----------------------------------------------------

        return {

            "poster_path":
                data.get(
                    "poster_path"
                ),

            "backdrop_path":
                data.get(
                    "backdrop_path"
                ),

            "release_date":
                data.get(
                    "release_date"
                ),

            "overview":
                data.get(
                    "overview"
                ),

            "vote_average":
                data.get(
                    "vote_average"
                )

        }


    except requests.exceptions.RequestException as e:

        print(
            f"TMDB request failed "
            f"for movie {movie_id}:",
            e
        )

        return {}


    except Exception as e:

        print(
            f"Unexpected TMDB error "
            f"for movie {movie_id}:",
            e
        )

        return {}


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return jsonify({

        "message":
            "MovieVerse Flask backend is running!",

        "status":
            "success"

    })


# ============================================================
# TEST
# ============================================================

@app.route("/api/test")
def test():

    return jsonify({

        "status":
            "success",

        "message":
            "React can connect to Flask."

    })


# ============================================================
# GET MOVIES
# ============================================================

@app.route(
    "/api/movies",
    methods=["GET"]
)
def get_movies():

    try:

        # ----------------------------------------------------
        # Get movies from ML dataset
        # ----------------------------------------------------

        movies = recommender.get_movies(
            number=6
        )


        # ----------------------------------------------------
        # Add TMDB information
        # ----------------------------------------------------

        for movie in movies:

            tmdb_data = get_tmdb_movie(
                movie["id"]
            )

            movie.update(
                tmdb_data
            )


        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        return jsonify({

            "status":
                "success",

            "movies":
                movies

        })


    except Exception as e:

        print(
            "Error loading movies:",
            e
        )

        return jsonify({

            "status":
                "error",

            "error":
                str(e)

        }), 500


# ============================================================
# RECOMMEND MOVIES
# ============================================================

@app.route(
    "/api/recommend",
    methods=["POST"]
)
def recommend():

    # --------------------------------------------------------
    # GET JSON DATA
    # --------------------------------------------------------

    data = request.get_json(
        silent=True
    ) or {}


    movie_name = data.get(
        "movie",
        ""
    )


    number = data.get(
        "number",
        6
    )


    # --------------------------------------------------------
    # CLEAN INPUT
    # --------------------------------------------------------

    movie_name = str(
        movie_name
    ).strip()


    try:

        number = int(
            number
        )

    except (
        TypeError,
        ValueError
    ):

        number = 6


    # --------------------------------------------------------
    # LIMIT RESULTS
    # --------------------------------------------------------

    if number <= 0:

        number = 6


    if number > 20:

        number = 20


    # --------------------------------------------------------
    # EMPTY SEARCH
    # --------------------------------------------------------

    if not movie_name:

        return jsonify({

            "status":
                "error",

            "error":
                "Please enter a movie name."

        }), 400


    # --------------------------------------------------------
    # RECOMMENDATION
    # --------------------------------------------------------

    try:

        selected_movie, recommendations = (
            recommender.recommend(

                movie_name,

                number

            )
        )


        # ----------------------------------------------------
        # MOVIE NOT FOUND
        # ----------------------------------------------------

        if selected_movie is None:

            return jsonify({

                "status":
                    "error",

                "error":
                    f"No movie found for "
                    f"'{movie_name}'."

            }), 404


        # ----------------------------------------------------
        # GET TMDB DATA
        # ----------------------------------------------------

        for movie in recommendations:

            tmdb_data = get_tmdb_movie(
                movie["id"]
            )

            movie.update(
                tmdb_data
            )


        # ----------------------------------------------------
        # SUCCESS
        # ----------------------------------------------------

        return jsonify({

            "status":
                "success",

            "selected_movie":
                selected_movie,

            "recommendations":
                recommendations

        })


    except Exception as e:

        print(
            "Recommendation error:",
            e
        )

        return jsonify({

            "status":
                "error",

            "error":
                str(e)

        }), 500


# ============================================================
# RUN SERVER
# ============================================================

if __name__ == "__main__":

    app.run(

        host="127.0.0.1",

        port=5000,

        debug=True

    )