import { FiSearch, FiX } from "react-icons/fi";
import "./SearchBar.css";

function SearchBar({

    value,

    onChange,

    placeholder = "Search...",

    onClear,

    fullWidth = true,

    className = ""

}) {

    return (

        <div
            className={`
                searchbar
                ${fullWidth ? "searchbar-full" : ""}
                ${className}
            `}
        >

            <span className="search-icon">

                <FiSearch />

            </span>

            <input

                type="text"

                value={value}

                onChange={onChange}

                placeholder={placeholder}

            />

            {value && (

                <button

                    type="button"

                    className="clear-btn"

                    onClick={onClear}

                >

                    <FiX />

                </button>

            )}

        </div>

    );

}

export default SearchBar;