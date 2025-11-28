import { useNavigate } from 'react-router-dom';
import './NavBar.css';

const NavBar = () => {
    const navigate = useNavigate();

    return (
        <div className="navbar-container">
            <div className="navbar-content">
                <h1 className="navbar-title" onClick={() => navigate('/pages/home')} style={{cursor: 'pointer'}}>
                    CoopScout
                </h1>
                <div className="navbar-buttons">
                    <button
                        className="profile-button"
                        onClick={() => navigate('/pages/profile')}
                    >
                        Profile
                    </button>
                </div>
            </div>
        </div>
    );
};

export default NavBar;