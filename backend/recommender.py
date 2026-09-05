import os
import requests
import pandas as pd

from dotenv import load_dotenv

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


class MovieRecommender:

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(self, csv_path):

        print("=" * 60)
        print("Loading movie dataset...")
        print("=" * 60)

        # ----------------------------------------------------
        # LOAD CSV
        # ----------------------------------------------------

        self.movies = pd.read_csv(csv_path)

        print(f"Movies loaded: {len(self.movies)}")

        # ----------------------------------------------------
        # CLEAN COLUMN NAMES
        # ----------------------------------------------------

        self.movies.columns = (
            self.movies.columns
            .str.strip()
        )

        # ----------------------------------------------------
        # REQUIRED COLUMNS
        # ----------------------------------------------------

        required_columns = [
            "id",
            "title",
            "overview"
        ]

        for column in required_columns:

            if column not in self.movies.columns:

                raise ValueError(
                    f"Required column '{column}' "
                    f"not found in CSV."
                )

        # ----------------------------------------------------
        # CLEAN TITLE
        # ----------------------------------------------------

        self.movies["title"] = (
            self.movies["title"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        # ----------------------------------------------------
        # CLEAN OVERVIEW
        # ----------------------------------------------------

        self.movies["overview"] = (
            self.movies["overview"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        # ----------------------------------------------------
        # TMDB API KEY
        # ----------------------------------------------------

        self.tmdb_api_key = os.getenv(
            "TMDB_API_KEY"
        )

        if self.tmdb_api_key:

            print(
                "TMDB API key loaded successfully."
            )

        else:

            print(
                "WARNING: TMDB_API_KEY not found!"
            )

        # ----------------------------------------------------
        # POSTER CACHE
        # ----------------------------------------------------

        self.poster_cache = {}

        # ----------------------------------------------------
        # CREATE CONTENT FOR ML
        # ----------------------------------------------------

        self.movies["content"] = (
            self.movies["title"]
            + " "
            + self.movies["overview"]
        )

        # ----------------------------------------------------
        # TF-IDF
        # ----------------------------------------------------

        print(
            "Creating TF-IDF matrix..."
        )

        self.vectorizer = TfidfVectorizer(
            stop_words="english"
        )

        self.tfidf_matrix = (
            self.vectorizer.fit_transform(
                self.movies["content"]
            )
        )

        # ----------------------------------------------------
        # COSINE SIMILARITY
        # ----------------------------------------------------

        print(
            "Calculating cosine similarity..."
        )

        self.similarity = cosine_similarity(
            self.tfidf_matrix
        )

        print(
            "Recommendation system ready!"
        )

        print("=" * 60)


    # ========================================================
    # GET POSTER FROM TMDB
    # ========================================================

    def get_poster(self, movie_id, title):

        # ----------------------------------------------------
        # CHECK CACHE
        # ----------------------------------------------------
        # IMPORTANT:
        # If previous request failed and stored None,
        # we DO NOT permanently return None.
        # We try TMDB again.
        # ----------------------------------------------------

        if movie_id in self.poster_cache:

            cached_poster = self.poster_cache[
                movie_id
            ]

            if cached_poster:

                return cached_poster

        # ----------------------------------------------------
        # CHECK API KEY
        # ----------------------------------------------------

        if not self.tmdb_api_key:

            print(
                "TMDB API key is missing."
            )

            return None

        # ====================================================
        # METHOD 1
        # DIRECT TMDB MOVIE ID
        # ====================================================

        try:

            url = (
                "https://api.themoviedb.org/3/movie/"
                f"{movie_id}"
            )

            params = {
                "api_key": self.tmdb_api_key,
                "language": "en-US"
            }

            response = requests.get(
                url,
                params=params,
                timeout=10
            )

            print(
                f"TMDB ID {movie_id} "
                f"({title}) -> "
                f"{response.status_code}"
            )

            # ------------------------------------------------
            # SUCCESS
            # ------------------------------------------------

            if response.status_code == 200:

                data = response.json()

                poster_path = data.get(
                    "poster_path"
                )

                if poster_path:

                    poster_url = (
                        "https://image.tmdb.org/t/p/w500"
                        + poster_path
                    )

                    # Save only successful poster
                    self.poster_cache[
                        movie_id
                    ] = poster_url

                    return poster_url

                print(
                    f"TMDB returned no poster "
                    f"for {title}"
                )

        except Exception as e:

            print(
                f"TMDB ID lookup error "
                f"for {title}: {e}"
            )

        # ====================================================
        # METHOD 2
        # SEARCH USING MOVIE TITLE
        # ====================================================

        try:

            search_url = (
                "https://api.themoviedb.org/3/"
                "search/movie"
            )

            params = {
                "api_key": self.tmdb_api_key,
                "query": title,
                "include_adult": "false",
                "language": "en-US"
            }

            response = requests.get(
                search_url,
                params=params,
                timeout=10
            )

            print(
                f"TMDB title search "
                f"({title}) -> "
                f"{response.status_code}"
            )

            if response.status_code == 200:

                results = (
                    response
                    .json()
                    .get(
                        "results",
                        []
                    )
                )

                # ------------------------------------------------
                # FIRST: EXACT TITLE MATCH
                # ------------------------------------------------

                for result in results:

                    result_title = (
                        str(
                            result.get(
                                "title",
                                ""
                            )
                        )
                        .strip()
                        .lower()
                    )

                    requested_title = (
                        str(title)
                        .strip()
                        .lower()
                    )

                    if (
                        result_title
                        == requested_title
                    ):

                        poster_path = (
                            result.get(
                                "poster_path"
                            )
                        )

                        if poster_path:

                            poster_url = (
                                "https://image.tmdb.org/t/p/w500"
                                + poster_path
                            )

                            self.poster_cache[
                                movie_id
                            ] = poster_url

                            return poster_url

                # ------------------------------------------------
                # SECOND: FIRST RESULT WITH POSTER
                # ------------------------------------------------

                for result in results[:5]:

                    poster_path = (
                        result.get(
                            "poster_path"
                        )
                    )

                    if poster_path:

                        poster_url = (
                            "https://image.tmdb.org/t/p/w500"
                            + poster_path
                        )

                        self.poster_cache[
                            movie_id
                        ] = poster_url

                        return poster_url

        except Exception as e:

            print(
                f"TMDB title search error "
                f"for {title}: {e}"
            )

        # ====================================================
        # NO POSTER FOUND
        # ====================================================

        print(
            f"No poster found for: {title}"
        )

        # IMPORTANT:
        # Do NOT store None in cache.
        # This allows another request to retry TMDB.
        return None


    # ========================================================
    # GET MOVIES
    # ========================================================

    def get_movies(self, number=6):

        # ----------------------------------------------------
        # LIMIT NUMBER
        # ----------------------------------------------------

        if number <= 0:

            number = 6

        if number > 20:

            number = 20

        # ----------------------------------------------------
        # GET FIRST MOVIES
        # ----------------------------------------------------

        result = self.movies.head(
            number
        ).copy()

        # ----------------------------------------------------
        # FORMAT MOVIES
        # ----------------------------------------------------

        return self.format_movies(
            result
        )


    # ========================================================
    # RECOMMEND MOVIES
    # ========================================================

    def recommend(
        self,
        movie_name,
        number=6
    ):

        # ----------------------------------------------------
        # CLEAN SEARCH
        # ----------------------------------------------------

        movie_name = (
            str(movie_name)
            .strip()
            .lower()
        )

        if not movie_name:

            return None, []

        # ----------------------------------------------------
        # NORMALIZED TITLES
        # ----------------------------------------------------

        titles = (
            self.movies["title"]
            .astype(str)
            .str.strip()
            .str.lower()
        )

        # ====================================================
        # EXACT MATCH
        # ====================================================

        matches = self.movies[
            titles == movie_name
        ]

        # ====================================================
        # PARTIAL MATCH
        # ====================================================

        if matches.empty:

            mask = titles.str.contains(
                movie_name,
                na=False,
                regex=False
            )

            matches = self.movies[
                mask
            ]

        # ====================================================
        # MOVIE NOT FOUND
        # ====================================================

        if matches.empty:

            return None, []

        # ====================================================
        # SELECT FIRST MATCH
        # ====================================================

        selected_index = matches.index[0]

        selected_position = (
            self.movies.index.get_loc(
                selected_index
            )
        )

        selected_title = (
            self.movies.loc[
                selected_index,
                "title"
            ]
        )

        # ====================================================
        # GET SIMILARITY SCORES
        # ====================================================

        distances = list(
            enumerate(
                self.similarity[
                    selected_position
                ]
            )
        )

        # ----------------------------------------------------
        # SORT BY SIMILARITY
        # ----------------------------------------------------

        distances.sort(
            key=lambda x: x[1],
            reverse=True
        )

        recommendations = []

        # ====================================================
        # CREATE RECOMMENDATION LIST
        # ====================================================

        for position, score in distances:

            # ------------------------------------------------
            # SKIP SELECTED MOVIE
            # ------------------------------------------------

            if position == selected_position:

                continue

            movie = self.movies.iloc[
                position
            ]

            # ------------------------------------------------
            # MOVIE ID
            # ------------------------------------------------

            movie_id = self.clean_value(
                movie.get("id")
            )

            # ------------------------------------------------
            # MOVIE TITLE
            # ------------------------------------------------

            movie_title = self.clean_value(
                movie.get("title")
            )

            # ------------------------------------------------
            # GET POSTER
            # ------------------------------------------------

            poster_url = self.get_poster(
                movie_id,
                movie_title
            )

            # ------------------------------------------------
            # CREATE MOVIE OBJECT
            # ------------------------------------------------

            movie_data = {

                "id": movie_id,

                "title": movie_title,

                "poster_path": poster_url,

                "vote_average": self.clean_value(
                    movie.get(
                        "vote_average"
                    )
                ),

                "release_date": self.clean_value(
                    movie.get(
                        "release_date"
                    )
                ),

                "similarity": round(
                    float(score),
                    4
                )
            }

            recommendations.append(
                movie_data
            )

            # ------------------------------------------------
            # STOP AFTER REQUIRED NUMBER
            # ------------------------------------------------

            if len(recommendations) >= number:

                break

        return (
            selected_title,
            recommendations
        )


    # ========================================================
    # FORMAT MOVIES
    # ========================================================

    def format_movies(
        self,
        dataframe
    ):

        result = []

        for _, movie in dataframe.iterrows():

            # ------------------------------------------------
            # ID
            # ------------------------------------------------

            movie_id = self.clean_value(
                movie.get("id")
            )

            # ------------------------------------------------
            # TITLE
            # ------------------------------------------------

            movie_title = self.clean_value(
                movie.get("title")
            )

            # ------------------------------------------------
            # POSTER
            # ------------------------------------------------

            poster_url = self.get_poster(
                movie_id,
                movie_title
            )

            # ------------------------------------------------
            # MOVIE OBJECT
            # ------------------------------------------------

            movie_data = {

                "id": movie_id,

                "title": movie_title,

                "poster_path": poster_url,

                "vote_average": self.clean_value(
                    movie.get(
                        "vote_average"
                    )
                ),

                "release_date": self.clean_value(
                    movie.get(
                        "release_date"
                    )
                )
            }

            result.append(
                movie_data
            )

        return result


    # ========================================================
    # CLEAN VALUES
    # ========================================================

    @staticmethod
    def clean_value(value):

        # ----------------------------------------------------
        # HANDLE NaN
        # ----------------------------------------------------

        if pd.isna(value):

            return None

        # ----------------------------------------------------
        # CONVERT NUMPY TYPES
        # ----------------------------------------------------

        if hasattr(
            value,
            "item"
        ):

            try:

                return value.item()

            except Exception:

                pass

        return value