import "./Navbar.css";
import { NavLink } from "react-router-dom";
import { FaFilm, FaUserCircle } from "react-icons/fa";

function Navbar() {
  return (
    <nav className="navbar">

      <div className="logo">
        <FaFilm />
        <span>MovieVerse</span>
      </div>

      <div className="nav-links">

        <NavLink to="/">
          Home
        </NavLink>

        <NavLink to="/movies">
          Trending
        </NavLink>

        <NavLink to="/movies">
          Genres
        </NavLink>

        <NavLink to="/about">
          About
        </NavLink>

      </div>

      <NavLink to="/profile" className="profile-link">
        <FaUserCircle className="profile-icon" />
      </NavLink>

    </nav>
  );
}

export default Navbar;