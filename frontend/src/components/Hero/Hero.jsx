import "./Hero.css";
import { Link } from "react-router-dom";

function Hero() {
  return (
    <section className="hero">

      <div className="hero-content">

        <h1>
          Discover Movies
          <br />
          You'll Love 🍿
        </h1>

        <p>
          AI Powered Movie Recommendation System that helps you
          discover trending, top-rated and personalized movies.
        </p>

        <div className="hero-buttons">

          <Link to="/movies" className="explore-btn">
            🎬 Explore Movies
          </Link>

          <button className="learn-btn">
            Learn More
          </button>

        </div>

      </div>

    </section>
  );
}

export default Hero;