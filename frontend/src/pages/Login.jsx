import "./Auth.css";
import { Link, useNavigate } from "react-router-dom";
import { FaFilm, FaEnvelope, FaLock } from "react-icons/fa";
import { useState } from "react";

function Login() {

  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);

  async function handleLogin(e) {

    e.preventDefault();

    try {

      setLoading(true);

      console.log("LOGIN: Sending request to Flask...");

      const response = await fetch(
        "http://127.0.0.1:5000/api/auth/login",
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json"
          },

          body: JSON.stringify({
            email,
            password
          })
        }
      );

      const data = await response.json();

      console.log("LOGIN RESPONSE:", data);

      if (!response.ok) {

        alert(data.message || "Login failed");

        return;
      }

      // Save JWT token
      localStorage.setItem(
        "token",
        data.token
      );

      // Save user information
      localStorage.setItem(
        "user",
        JSON.stringify(data.user)
      );

      alert("Login successful! 🎉");

      navigate("/");

    } catch (error) {

      console.error("LOGIN ERROR:", error);

      alert(
        "Cannot connect to backend. Make sure Flask is running."
      );

    } finally {

      setLoading(false);

    }
  }

  return (

    <div className="auth-page">

      <div className="auth-card">

        <div className="auth-logo">

          <FaFilm />

          <span>MovieVerse</span>

        </div>

        <h1>Welcome Back 👋</h1>

        <p className="auth-subtitle">
          Login to discover movies you'll love.
        </p>

        <form onSubmit={handleLogin}>

          <div className="input-group">

            <FaEnvelope />

            <input
              type="email"
              placeholder="Email address"
              value={email}
              onChange={(e) =>
                setEmail(e.target.value)
              }
              required
            />

          </div>

          <div className="input-group">

            <FaLock />

            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) =>
                setPassword(e.target.value)
              }
              required
            />

          </div>

          <div className="forgot">
            <a href="#">
              Forgot Password?
            </a>
          </div>

          <button
            className="auth-btn"
            type="submit"
            disabled={loading}
          >

            {loading
              ? "Logging in..."
              : "Login"}

          </button>

        </form>

        <p className="switch-auth">

          Don't have an account?

          <Link to="/signup">
            {" "}Create Account
          </Link>

        </p>

      </div>

    </div>

  );
}

export default Login;