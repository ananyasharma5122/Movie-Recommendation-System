import axios from "axios";

const API_KEY = import.meta.env.VITE_TMDB_API_KEY;
const BASE_URL = "https://api.themoviedb.org/3";

export async function getTrendingMovies() {
  try {
    const response = await axios.get(
      `${BASE_URL}/trending/movie/week?api_key=${API_KEY}`
    );

    return response.data.results;
  } catch (error) {
    console.error("TMDB Error:", error);
    return [];
  }
}

export async function searchMovies(query) {
  try {
    const response = await axios.get(
      `${BASE_URL}/search/movie?api_key=${API_KEY}&query=${encodeURIComponent(query)}`
    );

    return response.data.results;
  } catch (error) {
    console.error("Search Error:", error);
    return [];
  }
}