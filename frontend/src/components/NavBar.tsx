import { useNavigate } from 'react-router-dom';
import './NavBar.css';

const NavBar = () => {
    const navigate = useNavigate();

    return (
        <div className="navbar-container">
            <div className="navbar-content">
                <h1 className="navbar-title" onClick={() => navigate('/')} style={{cursor: 'pointer'}}>
                    CoopScout
                </h1>
                <div className="navbar-buttons">
                    <button
                        className="profile-button"
                        onClick={() => navigate('/profile')}
                        >
                        Profile
                    </button>
                    <button
                        className="favorites-button"
                        onClick={() => navigate('/favorites')}
                        >
                        Favorites
                    </button>
                </div>
            </div>
        </div>
    );
};

export default NavBar;