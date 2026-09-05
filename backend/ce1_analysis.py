import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import ast
import os

# ============================================================
# PATHS
# ============================================================

DATA_PATH = "data/tmdb_5000_movies.csv"
OUTPUT_DIR = "ce1_output"

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 70)
print("MOVIEVERSE - CONTINUOUS EVALUATION 1")
print("Dataset Preparation and Exploratory Data Analysis")
print("=" * 70)


# ============================================================
# 1. LOAD DATASET
# ============================================================

print("\n[1] Loading dataset...")

df = pd.read_csv(DATA_PATH)

print("Original dataset shape:", df.shape)

print("\nOriginal columns:")
print(df.columns.tolist())


# ============================================================
# 2. BEFORE PROCESSING
# ============================================================

print("\n[2] BEFORE PROCESSING")

print("\nFirst 10 rows:")
print(df.head(10))

print("\nDataset information:")
print(df.info())

print("\nDuplicate rows:", df.duplicated().sum())

print("\nMissing values:")
print(df.isnull().sum())


# Save before-processing dataset
df.head(20).to_csv(
    f"{OUTPUT_DIR}/01_before_processing.csv",
    index=False
)


# ============================================================
# 3. CLEAN COLUMN NAMES
# ============================================================

df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

print("\nCleaned column names:")
print(df.columns.tolist())


# ============================================================
# 4. REMOVE DUPLICATES
# ============================================================

duplicates_before = df.duplicated().sum()

df = df.drop_duplicates()

duplicates_after = df.duplicated().sum()

print("\n[3] DUPLICATE REMOVAL")

print("Duplicates before:", duplicates_before)
print("Duplicates after:", duplicates_after)

print("Shape after duplicate removal:", df.shape)


# ============================================================
# 5. HANDLE MISSING VALUES
# ============================================================

print("\n[4] MISSING VALUES BEFORE CLEANING")

missing_before = df.isnull().sum()

print(
    missing_before[
        missing_before > 0
    ].sort_values(ascending=False)
)


# ------------------------------------------------------------
# Missing value graph
# ------------------------------------------------------------

missing = (
    df.isnull()
    .sum()
    .sort_values(ascending=False)
)

missing = missing[missing > 0]

plt.figure(figsize=(12, 6))

missing.plot(
    kind="bar"
)

plt.title("Missing Values by Column")
plt.xlabel("Column")
plt.ylabel("Number of Missing Values")

plt.xticks(rotation=45)

plt.tight_layout()

plt.savefig(
    f"{OUTPUT_DIR}/02_missing_values.png",
    dpi=300
)

plt.show()


# ============================================================
# 6. DROP IRRELEVANT COLUMNS
# ============================================================

# These columns are not required for our content-based
# recommendation model.

columns_to_drop = [
    "homepage",
    "tagline"
]

existing_drop_columns = [
    col for col in columns_to_drop
    if col in df.columns
]

df = df.drop(
    columns=existing_drop_columns
)

print("\nRemoved irrelevant columns:")
print(existing_drop_columns)


# ============================================================
# 7. HANDLE MISSING VALUES
# ============================================================

# Text columns
text_columns = [
    "overview",
    "genres",
    "keywords",
    "production_companies",
    "production_countries",
    "spoken_languages"
]

for column in text_columns:

    if column in df.columns:

        df[column] = (
            df[column]
            .fillna("")
            .astype(str)
        )


# Numeric columns
numeric_columns = [
    "budget",
    "revenue",
    "runtime",
    "vote_average",
    "vote_count",
    "popularity"
]

for column in numeric_columns:

    if column in df.columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        df[column] = df[column].fillna(
            df[column].median()
        )


# Release date
if "release_date" in df.columns:

    df["release_date"] = pd.to_datetime(
        df["release_date"],
        errors="coerce"
    )

    # Fill missing dates with the most common year/date
    df["release_date"] = df["release_date"].fillna(
        df["release_date"].mode()[0]
    )


# Status
if "status" in df.columns:

    df["status"] = (
        df["status"]
        .fillna("Unknown")
        .astype(str)
    )


# Original language
if "original_language" in df.columns:

    df["original_language"] = (
        df["original_language"]
        .fillna("unknown")
        .astype(str)
    )


# ============================================================
# 8. VERIFY MISSING VALUES
# ============================================================

print("\n[5] MISSING VALUES AFTER CLEANING")

missing_after = df.isnull().sum()

print(
    missing_after[
        missing_after > 0
    ]
)

print(
    "\nTotal missing values:",
    df.isnull().sum().sum()
)


# ============================================================
# 9. FEATURE ENGINEERING
# ============================================================

print("\n[6] FEATURE ENGINEERING")


# ------------------------------------------------------------
# Release Year
# ------------------------------------------------------------

df["release_year"] = (
    df["release_date"]
    .dt.year
    .astype(int)
)


# ------------------------------------------------------------
# Genre extraction
# ------------------------------------------------------------

def extract_names(value):

    try:

        data = ast.literal_eval(value)

        if isinstance(data, list):

            return [
                item.get("name", "")
                for item in data
                if isinstance(item, dict)
            ]

    except:

        return []

    return []


if "genres" in df.columns:

    df["genre_list"] = df["genres"].apply(
        extract_names
    )

    df["genre_text"] = (
        df["genre_list"]
        .apply(lambda x: " ".join(x))
    )


# ------------------------------------------------------------
# Keywords extraction
# ------------------------------------------------------------

if "keywords" in df.columns:

    df["keyword_list"] = df["keywords"].apply(
        extract_names
    )

    df["keyword_text"] = (
        df["keyword_list"]
        .apply(lambda x: " ".join(x))
    )


# ------------------------------------------------------------
# Create recommendation content
# ------------------------------------------------------------

df["content"] = (
    df["title"].fillna("").astype(str)
    + " "
    + df["overview"].fillna("").astype(str)
    + " "
    + df.get(
        "genre_text",
        pd.Series("", index=df.index)
    )
    + " "
    + df.get(
        "keyword_text",
        pd.Series("", index=df.index)
    )
)

print("Feature 'release_year' created.")
print("Feature 'genre_text' created.")
print("Feature 'keyword_text' created.")
print("Feature 'content' created.")


# ============================================================
# 10. CATEGORICAL ENCODING
# ============================================================

print("\n[7] CATEGORICAL DATA ENCODING")


# ------------------------------------------------------------
# One-Hot Encoding for genres
# ------------------------------------------------------------

if "genre_list" in df.columns:

    all_genres = sorted(
        set(
            genre
            for genres in df["genre_list"]
            for genre in genres
            if genre
        )
    )

    for genre in all_genres:

        safe_name = (
            genre
            .lower()
            .replace(" ", "_")
            .replace("-", "_")
        )

        df[
            "genre_" + safe_name
        ] = df["genre_list"].apply(
            lambda genres:
                1 if genre in genres else 0
        )

    print(
        "Genre categories encoded:",
        len(all_genres)
    )


# ------------------------------------------------------------
# Label encoding for original language
# ------------------------------------------------------------

if "original_language" in df.columns:

    language_categories = {
        language: index
        for index, language
        in enumerate(
            sorted(
                df["original_language"]
                .unique()
            )
        )
    }

    df["language_encoded"] = (
        df["original_language"]
        .map(language_categories)
    )

    print(
        "Languages encoded:",
        len(language_categories)
    )


# ============================================================
# 11. EDA - VOTE AVERAGE DISTRIBUTION
# ============================================================

print("\n[8] EXPLORATORY DATA ANALYSIS")


plt.figure(figsize=(10, 6))

plt.hist(
    df["vote_average"],
    bins=20
)

plt.title(
    "Distribution of Movie Ratings"
)

plt.xlabel("Vote Average")
plt.ylabel("Number of Movies")

plt.tight_layout()

plt.savefig(
    f"{OUTPUT_DIR}/03_rating_distribution.png",
    dpi=300
)

plt.show()


# ============================================================
# 12. TOP 10 POPULAR MOVIES
# ============================================================

top_popular = (
    df.sort_values(
        "popularity",
        ascending=False
    )
    .head(10)
)

plt.figure(figsize=(12, 6))

plt.barh(
    top_popular["title"],
    top_popular["popularity"]
)

plt.title(
    "Top 10 Movies by Popularity"
)

plt.xlabel("Popularity")

plt.ylabel("Movie")

plt.gca().invert_yaxis()

plt.tight_layout()

plt.savefig(
    f"{OUTPUT_DIR}/04_top_popular_movies.png",
    dpi=300
)

plt.show()


# ============================================================
# 13. MOVIES RELEASED PER YEAR
# ============================================================

movies_per_year = (
    df["release_year"]
    .value_counts()
    .sort_index()
)

plt.figure(figsize=(12, 6))

plt.plot(
    movies_per_year.index,
    movies_per_year.values
)

plt.title(
    "Number of Movies Released by Year"
)

plt.xlabel("Release Year")

plt.ylabel("Number of Movies")

plt.tight_layout()

plt.savefig(
    f"{OUTPUT_DIR}/05_movies_per_year.png",
    dpi=300
)

plt.show()


# ============================================================
# 14. RATING VS POPULARITY
# ============================================================

plt.figure(figsize=(10, 6))

plt.scatter(
    df["vote_average"],
    df["popularity"],
    alpha=0.5
)

plt.title(
    "Movie Rating vs Popularity"
)

plt.xlabel("Vote Average")

plt.ylabel("Popularity")

plt.tight_layout()

plt.savefig(
    f"{OUTPUT_DIR}/06_rating_vs_popularity.png",
    dpi=300
)

plt.show()


# ============================================================
# 15. RATING VS VOTE COUNT
# ============================================================

plt.figure(figsize=(10, 6))

plt.scatter(
    df["vote_count"],
    df["vote_average"],
    alpha=0.5
)

plt.title(
    "Vote Count vs Movie Rating"
)

plt.xlabel("Vote Count")

plt.ylabel("Vote Average")

plt.tight_layout()

plt.savefig(
    f"{OUTPUT_DIR}/07_vote_count_vs_rating.png",
    dpi=300
)

plt.show()


# ============================================================
# 16. GENRE ANALYSIS
# ============================================================

if "genre_list" in df.columns:

    genre_counts = {}

    for genres in df["genre_list"]:

        for genre in genres:

            genre_counts[genre] = (
                genre_counts.get(
                    genre,
                    0
                ) + 1
            )

    genre_df = (
        pd.DataFrame(
            list(
                genre_counts.items()
            ),
            columns=[
                "Genre",
                "Movie_Count"
            ]
        )
        .sort_values(
            "Movie_Count",
            ascending=False
        )
        .head(10)
    )

    plt.figure(figsize=(12, 6))

    plt.bar(
        genre_df["Genre"],
        genre_df["Movie_Count"]
    )

    plt.title(
        "Top 10 Movie Genres"
    )

    plt.xlabel("Genre")

    plt.ylabel(
        "Number of Movies"
    )

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.savefig(
        f"{OUTPUT_DIR}/08_top_genres.png",
        dpi=300
    )

    plt.show()


# ============================================================
# 17. LANGUAGE ANALYSIS
# ============================================================

language_counts = (
    df["original_language"]
    .value_counts()
    .head(10)
)

plt.figure(figsize=(10, 6))

plt.bar(
    language_counts.index,
    language_counts.values
)

plt.title(
    "Top 10 Original Languages"
)

plt.xlabel("Language")

plt.ylabel("Number of Movies")

plt.tight_layout()

plt.savefig(
    f"{OUTPUT_DIR}/09_top_languages.png",
    dpi=300
)

plt.show()


# ============================================================
# 18. FINAL CLEANED DATASET
# ============================================================

# Remove helper list columns before final export

helper_columns = [
    "genre_list",
    "keyword_list"
]

final_df = df.drop(
    columns=[
        col
        for col in helper_columns
        if col in df.columns
    ]
)


# ============================================================
# 19. SAVE FINAL DATASET
# ============================================================

final_df.to_csv(
    f"{OUTPUT_DIR}/10_final_cleaned_dataset.csv",
    index=False
)

print(
    "\nFinal dataset saved."
)

print(
    "Final dataset shape:",
    final_df.shape
)


# ============================================================
# 20. FINAL DATASET PREVIEW
# ============================================================

print("\n[9] FINAL DATASET")

print(
    final_df.head(10).to_string()
)

print(
    "\nFinal missing values:",
    final_df.isnull().sum().sum()
)

print(
    "\nFinal duplicate rows:",
    final_df.duplicated().sum()
)


# ============================================================
# 21. FEATURE SELECTION
# ============================================================

feature_columns = [
    "title",
    "overview",
    "genre_text",
    "keyword_text",
    "popularity",
    "vote_average",
    "vote_count",
    "release_year",
    "original_language"
]

feature_columns = [
    col
    for col in feature_columns
    if col in final_df.columns
]

X = final_df[
    feature_columns
]

print("\n[10] FEATURE SELECTION")

print("\nX features:")

for feature in X.columns:

    print(
        " -",
        feature
    )


# ============================================================
# 22. X AND Y
# ============================================================

print("\nX shape:", X.shape)

print(
    "\nRecommendation system type:"
)

print(
    "Content-Based / Unsupervised Recommendation"
)

print(
    "\nTarget variable y:"
)

print(
    "Not applicable because recommendations are generated"
    " using content similarity rather than supervised prediction."
)


# ============================================================
# 23. SUMMARY
# ============================================================

print("\n" + "=" * 70)

print("CE-1 DATA PREPARATION COMPLETED")

print("=" * 70)

print(
    "Original rows:",
    4803
)

print(
    "Final rows:",
    len(final_df)
)

print(
    "Original columns:",
    20
)

print(
    "Final columns:",
    len(final_df.columns)
)

print(
    "Duplicates remaining:",
    final_df.duplicated().sum()
)

print(
    "Missing values remaining:",
    final_df.isnull().sum().sum()
)

print(
    "\nAll graphs and datasets saved inside:"
)

print(
    OUTPUT_DIR
)

print("=" * 70)