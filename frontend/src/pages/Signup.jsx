import "./Auth.css";
import { Link, useNavigate } from "react-router-dom";
import {
  FaFilm,
  FaUser,
  FaEnvelope,
  FaLock
} from "react-icons/fa";
import { useState } from "react";

function Signup() {

  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [loading, setLoading] = useState(false);

  async function handleSignup(e) {

    e.preventDefault();

    console.log("NEW SIGNUP FILE IS RUNNING");

    if (password !== confirmPassword) {
      alert("Passwords do not match!");
      return;
    }

    try {

      setLoading(true);

      console.log("Sending request to Flask...");

      const response = await fetch(
        "http://127.0.0.1:5000/api/auth/signup",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            name,
            email,
            password
          })
        }
      );

      const data = await response.json();

      console.log("FLASK RESPONSE:", data);

      if (!response.ok) {
        alert(data.message || "Signup failed");
        return;
      }

      alert("Account created successfully! 🎉");

      navigate("/login");

    } catch (error) {

      console.error("SIGNUP ERROR:", error);

      alert("Cannot connect to Flask backend.");

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

        <h1>Create Account 🎬</h1>

        <p className="auth-subtitle">
          Join MovieVerse and discover your next favourite movie.
        </p>

        <form onSubmit={handleSignup}>

          <div className="input-group">
            <FaUser />

            <input
              type="text"
              placeholder="Full name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />
          </div>

          <div className="input-group">
            <FaEnvelope />

            <input
              type="email"
              placeholder="Email address"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="input-group">
            <FaLock />

            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <div className="input-group">
            <FaLock />

            <input
              type="password"
              placeholder="Confirm password"
              value={confirmPassword}
              onChange={(e) =>
                setConfirmPassword(e.target.value)
              }
              required
            />
          </div>

          <button
            className="auth-btn"
            type="submit"
            disabled={loading}
          >
            {loading
              ? "Creating Account..."
              : "Create Account"}
          </button>

        </form>

        <p className="switch-auth">
          Already have an account?
          <Link to="/login"> Login</Link>
        </p>

      </div>

    </div>
  );
}

export default Signup;