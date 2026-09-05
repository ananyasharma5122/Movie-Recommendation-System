import pandas as pd
import ast
import pickle
import re

print("🚀 AI/ML Model Training Started...")


# =========================
# LOAD DATASETS
# =========================

movies = pd.read_csv("ml/tmdb_5000_movies.csv")
credits = pd.read_csv("ml/tmdb_5000_credits.csv")

print("✅ Movies dataset loaded:", movies.shape)
print("✅ Credits dataset loaded:", credits.shape)


# =========================
# MERGE DATASETS
# =========================

credits.rename(columns={"movie_id": "id"}, inplace=True)

movies = movies.merge(
    credits[["id", "cast", "crew"]],
    on="id"
)

print("✅ Datasets merged successfully")


# =========================
# SELECT FEATURES
# =========================

movies = movies[
    [
        "id",
        "title",
        "overview",
        "genres",
        "keywords",
        "cast",
        "crew"
    ]
]

movies.dropna(inplace=True)

movies.reset_index(drop=True, inplace=True)

print("✅ Missing values removed")


# =========================
# EXTRACT GENRES / KEYWORDS
# =========================

def extract_names(text):

    try:

        data = ast.literal_eval(text)

        return " ".join(
            item["name"]
            for item in data
        )

    except:

        return ""


movies["genres"] = movies["genres"].apply(
    extract_names
)

movies["keywords"] = movies["keywords"].apply(
    extract_names
)


# =========================
# EXTRACT TOP 3 CAST
# =========================

def extract_cast(text):

    try:

        data = ast.literal_eval(text)

        return " ".join(
            item["name"]
            for item in data[:3]
        )

    except:

        return ""


movies["cast"] = movies["cast"].apply(
    extract_cast
)


# =========================
# EXTRACT DIRECTOR
# =========================

def extract_director(text):

    try:

        data = ast.literal_eval(text)

        for item in data:

            if item["job"] == "Director":

                return item["name"]

        return ""

    except:

        return ""


movies["crew"] = movies["crew"].apply(
    extract_director
)


# =========================
# CLEAN TEXT
# =========================

def clean_text(text):

    if not isinstance(text, str):
        return ""

    text = text.lower()

    text = re.sub(
        r"[^a-zA-Z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


movies["overview"] = movies["overview"].apply(
    clean_text
)

movies["genres"] = movies["genres"].apply(
    clean_text
)

movies["keywords"] = movies["keywords"].apply(
    clean_text
)

movies["cast"] = movies["cast"].apply(
    clean_text
)

movies["crew"] = movies["crew"].apply(
    clean_text
)


# =========================
# CREATE COMBINED FEATURES
# =========================

movies["tags"] = (
    movies["genres"] + " " +
    movies["genres"] + " " +
    movies["keywords"] + " " +
    movies["keywords"] + " " +
    movies["crew"] + " " +
    movies["crew"] + " " +
    movies["cast"] + " " +
    movies["overview"]
)

print("✅ Movie features created")


# =========================
# TF-IDF
# =========================

from sklearn.feature_extraction.text import TfidfVectorizer

print("🧠 Creating TF-IDF vectors...")

vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=10000,
    ngram_range=(1, 2)
)

vectors = vectorizer.fit_transform(
    movies["tags"]
)

print("✅ TF-IDF completed")

print(
    "Vector shape:",
    vectors.shape
)


# =========================
# COSINE SIMILARITY
# =========================

from sklearn.metrics.pairwise import cosine_similarity

print("🧠 Calculating cosine similarity...")

similarity = cosine_similarity(
    vectors
)

print("✅ Similarity matrix created")


# =========================
# SAVE MODEL
# =========================

model_data = {

    "movies": movies[
        [
            "id",
            "title",
            "genres",
            "keywords",
            "cast",
            "crew",
            "overview"
        ]
    ],

    "similarity": similarity,

    "vectorizer": vectorizer
}


with open(
    "ml/movie_model.pkl",
    "wb"
) as file:

    pickle.dump(
        model_data,
        file
    )


print()
print("================================")
print("🎉 AI/ML MODEL TRAINED!")
print("================================")
print("Movies:", len(movies))
print("Model saved as: ml/movie_model.pkl")