import "./Profile.css";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  FaUserCircle,
  FaEnvelope,
  FaHeart,
  FaBookmark,
  FaStar,
  FaSignOutAlt
} from "react-icons/fa";

function Profile() {

  const navigate = useNavigate();

  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {

    async function fetchProfile() {

      const token = localStorage.getItem("token");

      // User is not logged in
      if (!token) {
        navigate("/login");
        return;
      }

      try {

        const response = await fetch(
          "http://127.0.0.1:5000/api/auth/profile",
          {
            method: "GET",

            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        );

        const data = await response.json();

        console.log("PROFILE RESPONSE:", data);

        if (!response.ok) {

          localStorage.removeItem("token");
          localStorage.removeItem("user");

          navigate("/login");

          return;
        }

        setUser(data);

      } catch (error) {

        console.error("PROFILE ERROR:", error);

      } finally {

        setLoading(false);

      }
    }

    fetchProfile();

  }, [navigate]);


  function handleLogout() {

    localStorage.removeItem("token");
    localStorage.removeItem("user");

    alert("Logged out successfully 👋");

    navigate("/login");
  }


  if (loading) {

    return (
      <div className="profile-page">
        <h2>Loading Profile...</h2>
      </div>
    );

  }


  if (!user) {

    return (
      <div className="profile-page">
        <h2>Unable to load profile</h2>
      </div>
    );

  }


  return (

    <div className="profile-page">

      <div className="profile-card">

        <div className="profile-avatar">
          <FaUserCircle />
        </div>

        <h1>{user.name}</h1>

        <p className="profile-email">
          <FaEnvelope />
          {user.email}
        </p>

        <div className="profile-stats">

          <div className="stat-box">

            <FaHeart />

            <h3>
              {user.favorites?.length || 0}
            </h3>

            <p>Favorites</p>

          </div>


          <div className="stat-box">

            <FaBookmark />

            <h3>
              {user.watchlist?.length || 0}
            </h3>

            <p>Watchlist</p>

          </div>


          <div className="stat-box">

            <FaStar />

            <h3>
              {user.ratings?.length || 0}
            </h3>

            <p>Ratings</p>

          </div>

        </div>

        <button
          className="logout-btn"
          onClick={handleLogout}
        >
          <FaSignOutAlt />
          Logout
        </button>

      </div>

    </div>

  );
}

export default Profile;