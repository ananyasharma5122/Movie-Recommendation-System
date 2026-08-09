import "./Movies.css";
import { useEffect, useState } from "react";

import MovieCard from "../components/MovieCard/MovieCard";
import Footer from "../components/Footer/Footer";

import {
  getTrendingMovies,
  searchMovies
} from "../api/tmdb";

function Movies() {

  const [movies, setMovies] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);


  // =========================
  // LOAD TRENDING MOVIES
  // =========================

  useEffect(() => {

    async function loadMovies() {

      try {

        const data = await getTrendingMovies();

        setMovies(data);

      } catch (error) {

        console.error("Error loading movies:", error);

        setMovies([]);

      } finally {

        setLoading(false);

      }

    }

    loadMovies();

  }, []);


  // =========================
  // SEARCH MOVIES
  // =========================

  async function handleSearch(e) {

    e.preventDefault();

    setLoading(true);

    try {

      // Empty search → trending movies
      if (!search.trim()) {

        const data = await getTrendingMovies();

        setMovies(data);

        return;
      }


      // Search API
      const data = await searchMovies(search);

      setMovies(data);

    } catch (error) {

      console.error("Search error:", error);

      setMovies([]);

    } finally {

      setLoading(false);

    }

  }


  // =========================
  // UI
  // =========================

  return (
    <>

      <main className="movies-page">


        {/* HEADER */}

        <div className="movies-header">

          <h1>🎬 Explore Movies</h1>

          <p>
            Discover trending movies and find something you'll love.
          </p>

        </div>


        {/* SEARCH */}

        <form
          className="movie-search"
          onSubmit={handleSearch}
        >

          <input
            type="text"
            placeholder="Search for a movie..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />

          <button type="submit">
            🔍 Search
          </button>

        </form>


        {/* MOVIES */}

        {loading ? (

          <div className="loading">

            <h2>🍿 Loading movies...</h2>

          </div>

        ) : movies.length === 0 ? (

          <div className="no-results">

            <h2>😔 No movies found</h2>

            <p>
              Try searching for another movie.
            </p>

          </div>

        ) : (

          <div className="movie-container">

            {movies.map((movie) => (

              <MovieCard
                key={movie.id}
                title={movie.title}
                rating={
                  movie.vote_average
                    ? movie.vote_average.toFixed(1)
                    : "N/A"
                }
                poster={movie.poster_path}
              />

            ))}

          </div>

        )}

      </main>


      <Footer />

    </>
  );
}

export default Movies;