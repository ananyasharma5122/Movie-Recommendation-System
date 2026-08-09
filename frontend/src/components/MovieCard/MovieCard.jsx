import "./MovieCard.css";
import { FaStar, FaHeart } from "react-icons/fa";

function MovieCard({ title, rating, poster }) {

  // =========================
  // MOVIE IMAGE
  // =========================

  const imageUrl = poster
    ? poster.startsWith("http")
      ? poster
      : `https://image.tmdb.org/t/p/w500${poster}`
    : "https://placehold.co/500x750?text=No+Poster";


  // =========================
  // FAVORITE
  // =========================

  const handleFavorite = async () => {

    const token = localStorage.getItem("token");

    if (!token) {
      alert("Please login first 🔐");
      return;
    }

    try {

      const response = await fetch(
        "http://127.0.0.1:5000/api/movies/favorite",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`
          },

          body: JSON.stringify({
            movie: {
              title: title,
              rating: rating,
              poster: poster
            }
          })
        }
      );

      const data = await response.json();

      console.log("FAVORITE RESPONSE:", data);

      if (!response.ok) {

        alert(
          data.message ||
          "Could not add favorite"
        );

        return;
      }

      alert("❤️ Added to Favorites!");

    } catch (error) {

      console.error("Favorite Error:", error);

      alert("Unable to connect to backend");

    }
  };


  // =========================
  // WATCHLIST
  // =========================

  const handleWatchlist = async () => {

    const token = localStorage.getItem("token");

    if (!token) {
      alert("Please login first 🔐");
      return;
    }

    try {

      const response = await fetch(
        "http://127.0.0.1:5000/api/movies/watchlist",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`
          },

          body: JSON.stringify({
            movie: {
              title: title,
              rating: rating,
              poster: poster
            }
          })
        }
      );

      const data = await response.json();

      console.log("WATCHLIST RESPONSE:", data);

      if (!response.ok) {

        alert(
          data.message ||
          "Could not add watchlist"
        );

        return;
      }

      alert("🔖 Added to Watchlist!");

    } catch (error) {

      console.error("Watchlist Error:", error);

      alert("Unable to connect to backend");

    }
  };


  // =========================
  // UI
  // =========================

  return (

    <div className="movie-wrapper">

      <div className="movie-card">

        {/* POSTER */}

        <div className="movie-poster">

          <img
            src={imageUrl}
            alt={title}
            onError={(e) => {

              e.currentTarget.src =
                "https://placehold.co/500x750?text=No+Poster";

            }}
          />

          {/* RATING */}

          <span className="movie-rating">

            <FaStar />

            {rating || "N/A"}

          </span>

        </div>


        {/* MOVIE INFORMATION */}

        <div className="movie-info">

          <h2>
            {title}
          </h2>


          {/* GENRES */}

          <div className="movie-tags">

            <span>
              Sci-Fi
            </span>

            <span>
              Adventure
            </span>

          </div>


          {/* DETAILS + HEART */}

          <div className="movie-actions">

            <button
              className="details-btn"
              type="button"
            >
              View Details
            </button>


            <button
              className="heart-btn"
              type="button"
              onClick={handleFavorite}
            >
              <FaHeart />
            </button>

          </div>


          {/* FAVORITE + WATCHLIST */}

          <div className="extra-actions">

            <button
              className="favorite-btn"
              type="button"
              onClick={handleFavorite}
            >
              ❤️ Favorite
            </button>


            <button
              className="watchlist-btn"
              type="button"
              onClick={handleWatchlist}
            >
              🔖 Watchlist
            </button>

          </div>

        </div>

      </div>

    </div>

  );
}

export default MovieCard;