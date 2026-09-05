function MovieCard({ movie, onClick }) {

  const posterUrl = movie.poster_path
    ? movie.poster_path.startsWith("http")
      ? movie.poster_path
      : `https://image.tmdb.org/t/p/w500${movie.poster_path}`
    : "https://via.placeholder.com/500x750?text=No+Poster";

  return (
    <div
      className="movie-card"
      onClick={() => onClick?.(movie)}
    >

      <img
        src={posterUrl}
        alt={movie.title || "Movie"}
        className="movie-poster"
      />

      {movie.vote_average !== undefined &&
        movie.vote_average !== null && (
          <div className="rating">
            ⭐ {Number(movie.vote_average).toFixed(1)}
          </div>
        )}

      <div className="movie-info">

        <h3>
          {movie.title || "Unknown Movie"}
        </h3>

        {movie.release_date && (
          <p>
            {new Date(
              movie.release_date
            ).getFullYear()}
          </p>
        )}

      </div>

    </div>
  );
}

export default MovieCard;