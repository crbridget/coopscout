import { useNavigate } from 'react-router-dom';
import './NavBar.css';

const NavBar = () => {
    const navigate = useNavigate();

    return (
        <div className="navbar-container">
            <div className="navbar-content">
                <div className="navbar-left">
                    <button
                        className="home-icon-btn"
                        onClick={() => navigate('/')}
                        title="Home"
                    >
                        <svg
                            width="20"
                            height="20"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                        >
                            <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
                            <polyline points="9 22 9 12 15 12 15 22"></polyline>
                        </svg>
                    </button>
                    <h1 className="navbar-title" onClick={() => navigate('/')} style={{cursor: 'pointer'}}>
                        Co-op Scout
                    </h1>
                </div>
                <div className="navbar-buttons">
                    <button
                        className="applications-button"
                        onClick={() => navigate('/applications')}
                    >
                        Applications
                    </button>
                    <button
                        className="favorites-button"
                        onClick={() => navigate('/favorites')}
                    >
                        Favorites
                    </button>
                    <button
                        className="profile-button"
                        onClick={() => navigate('/profile')}
                    >
                        Profile
                    </button>
                </div>
            </div>
        </div>
    );
};

export default NavBar;