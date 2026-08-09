import "./Home.css";
import { useEffect, useState } from "react";

import Navbar from "../components/NavBar/Navbar";
import Hero from "../components/Hero/Hero";
import SearchBar from "../components/SearchBar/SearchBar";
import MovieCard from "../components/MovieCard/MovieCard";
import Footer from "../components/Footer/Footer";

import { getTrendingMovies } from "../api/tmdb";

function Home() {

  const [movies, setMovies] = useState([]);

  useEffect(() => {

    async function loadMovies() {

      console.log("Loading movies...");

      const data = await getTrendingMovies();

      console.log("Movies received:", data);

      if (data.length > 0) {
        console.log("First Movie:", data[0]);
      }

      setMovies(data);

    }

    loadMovies();

  }, []);

  return (
    <>
      <Navbar />

      <Hero />

      <SearchBar />

      <section className="trending">

        <h2>🔥 Trending Movies</h2>

        <div className="movie-container">

          {movies.map((movie) => (

            <MovieCard
              key={movie.id}
              title={movie.title}
              rating={movie.vote_average.toFixed(1)}
              poster={movie.poster_path || movie.backdrop_path}
            />

          ))}

        </div>

      </section>

      <Footer />
    </>
  );
}

export default Home;