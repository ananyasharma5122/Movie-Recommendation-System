import { useEffect, useState } from "react";
import "./App.css";
import MovieGrid from "./components/MovieGrid";

const API_URL = "http://127.0.0.1:5000";

function App() {
  const [movies, setMovies] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  // ==========================================
  // LOAD MOVIES
  // ==========================================

  useEffect(() => {
    const loadMovies = async () => {
      try {
        const response = await fetch(`${API_URL}/api/movies`);
        const data = await response.json();

        console.log("Movies:", data);

        if (Array.isArray(data)) {
          setMovies(data);
        } else if (Array.isArray(data.movies)) {
          setMovies(data.movies);
        }
      } catch (error) {
        console.error("Error loading movies:", error);
        setMessage("Unable to load movies.");
      }
    };

    loadMovies();
  }, []);

  // ==========================================
  // SEARCH / RECOMMENDATION
  // ==========================================

  const handleSearch = async () => {
    if (!search.trim()) {
      setMessage("Please enter a movie name.");
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      const response = await fetch(`${API_URL}/api/recommend`, {
        method: "POST",

        headers: {
          "Content-Type": "application/json",
        },

        body: JSON.stringify({
          movie: search.trim(),
          number: 6,
        }),
      });

      const data = await response.json();

      console.log("Recommendation response:", data);

      if (!response.ok) {
        setMessage(data.error || "Movie not found.");
        setMovies([]);
        return;
      }

      if (Array.isArray(data.recommendations)) {
        setMovies(data.recommendations);
      }

      if (data.selected_movie) {
        setMessage(
          `Recommendations based on "${data.selected_movie}"`
        );
      }
    } catch (error) {
      console.error("Search error:", error);

      setMessage(
        "Unable to connect to the Flask server."
      );
    } finally {
      setLoading(false);
    }
  };

  // ==========================================
  // ENTER KEY
  // ==========================================

  const handleKeyDown = (event) => {
    if (event.key === "Enter") {
      handleSearch();
    }
  };

  // ==========================================
  // MOVIE CLICK
  // ==========================================

  const handleMovieClick = (movie) => {
    console.log("Selected movie:", movie);
  };

  // ==========================================
  // NAVIGATION
  // ==========================================

  const scrollToMovies = () => {
    document
      .getElementById("movies")
      ?.scrollIntoView({
        behavior: "smooth",
      });
  };

  const scrollToRecommendations = () => {
    document
      .getElementById("recommendations")
      ?.scrollIntoView({
        behavior: "smooth",
      });
  };

  return (
    <div className="app">

      {/* ==========================================
          CINEMATIC BACKGROUND VIDEO
      ========================================== */}

      <video
        className="background-video"
        autoPlay
        muted
        loop
        playsInline
      >
        <source
          src="/videos/movie-bg.mp4"
          type="video/mp4"
        />

        Your browser does not support video.
      </video>

      {/* Dark cinematic overlay */}
      <div className="video-overlay"></div>

      {/* ==========================================
          NAVBAR
      ========================================== */}

      <header className="header">

        <div className="logo">
          <div className="logo-box">
            🎬
          </div>

          <div className="logo-text">
            <span className="logo-title">
              MovieVerse
            </span>

            <span className="logo-subtitle">
              AI MOVIE DISCOVERY
            </span>
          </div>
        </div>

        <nav className="nav">

          <button
            className="nav-link active"
            onClick={() =>
              window.scrollTo({
                top: 0,
                behavior: "smooth",
              })
            }
          >
            Home
          </button>

          <button
            className="nav-link"
            onClick={scrollToMovies}
          >
            Movies
          </button>

          <button
            className="nav-link"
            onClick={scrollToRecommendations}
          >
            Recommendations
          </button>

        </nav>

        <button
          className="explore-btn"
          onClick={scrollToMovies}
        >
          Explore
        </button>

      </header>

      {/* ==========================================
          HERO SECTION
      ========================================== */}

      <main>

        <section className="hero">

          <div className="hero-content">

            {/* Small badge */}

            <div className="hero-badge">
              <span>✦</span>
              AI POWERED MOVIE DISCOVERY
            </div>

            {/* Main heading */}

            <h1>
              Find Your Next
              <br />

              <span className="gradient-text">
                Favorite Movie.
              </span>
            </h1>

            {/* Description */}

            <p className="hero-description">
              Discover movies you'll love with
              intelligent recommendations powered
              by machine learning.
            </p>

            {/* ======================================
                SEARCH
            ====================================== */}

            <div className="search-container">

              <span className="search-icon">
                🔍
              </span>

              <input
                type="text"
                placeholder="Search for a movie you love..."
                value={search}
                onChange={(event) =>
                  setSearch(event.target.value)
                }
                onKeyDown={handleKeyDown}
              />

              <button
                className="discover-btn"
                onClick={handleSearch}
                disabled={loading}
              >
                {loading
                  ? "Searching..."
                  : "Discover"}
              </button>

            </div>

            {/* ======================================
                HERO STATS
            ====================================== */}

            <div className="hero-stats">

              <div className="stat">
                <span className="stat-star">
                  ✦
                </span>

                <span>
                  4,800+ Movies
                </span>
              </div>

              <div className="stat">
                <span>
                  ✦
                </span>

                <span>
                  AI Recommendations
                </span>
              </div>

              <div className="stat">
                <span>
                  ✦
                </span>

                <span>
                  Powered by TMDB
                </span>
              </div>

            </div>

          </div>

        </section>

        {/* ==========================================
            MESSAGE
        ========================================== */}

        {message && (
          <div className="result-message">
            <span>✦</span>
            {message}
          </div>
        )}

        {/* ==========================================
            MOVIES SECTION
        ========================================== */}

        <section
          className="movies-section"
          id="movies"
        >

          <div className="section-heading">

            <div>
              <span className="section-label">
                EXPLORE
              </span>

              <h2>
                Popular Movies
              </h2>
            </div>

            <button
              className="view-all"
              onClick={scrollToMovies}
            >
              View all →
            </button>

          </div>

          <MovieGrid
            movies={movies}
            onMovieClick={handleMovieClick}
          />

        </section>

        {/* ==========================================
            AI RECOMMENDATION SECTION
        ========================================== */}

        <section
          className="recommendation-section"
          id="recommendations"
        >

          <div className="recommendation-card">

            <div className="ai-icon">
              ✦
            </div>

            <span className="recommendation-label">
              PERSONALIZED FOR YOU
            </span>

            <h2>
              Let AI Find Your
              <span> Next Watch.</span>
            </h2>

            <p>
              Enter a movie you enjoyed and MovieVerse
              will discover similar movies using
              content-based machine learning.
            </p>

            <button
              className="recommendation-btn"
              onClick={() =>
                document
                  .querySelector(".search-container input")
                  ?.focus()
              }
            >
              ✦ Try AI Recommendations
            </button>

            <div className="algorithm">
              TF-IDF
              <span>×</span>
              Cosine Similarity
            </div>

          </div>

        </section>

        {/* ==========================================
            FOOTER
        ========================================== */}

        <footer className="footer">

          <div className="footer-logo">
            🎬 MovieVerse
          </div>

          <p>
            AI-powered movie discovery system
          </p>

          <span>
            Built with React • Flask • Machine Learning
          </span>

        </footer>

      </main>

    </div>
  );
}

export default App;