import "./SearchBar.css";

function SearchBar() {
    return (
        <div className="search-container">

            <input
                className="search-input"
                type="text"
                placeholder="Search your favourite movie..."
            />

            <button className="search-btn">
                Recommend
            </button>

        </div>
    );
}

export default SearchBar;
