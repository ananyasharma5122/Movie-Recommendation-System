
import MovieCard from "./MovieCard";
import "./MovieGrid.css";

function MovieGrid({ movies, onMovieClick }) {
  if (!movies || movies.length === 0) {
    return (
      <div className="empty-movies">
        <div className="empty-icon">🎬</div>

        <h3>No movies found</h3>

        <p>
          Try searching for another movie.
        </p>
      </div>
    );
  }

  return (
    <div className="movie-grid">

      {movies.map((movie, index) => (
        <MovieCard
          key={movie.id || index}
          movie={movie}
          onClick={onMovieClick}
        />
      ))}

    </div>
  );
}

export default MovieGrid;