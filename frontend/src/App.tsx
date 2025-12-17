import { Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Profile from './pages/Profile';
import Favorites from './pages/Favorites';
import JobDetail from './pages/JobDetail';
import EditProfile from './components/EditProfile';
import NavBar from './components/NavBar';
import './App.css';

function App() {
    return (
        <>
            <NavBar />
            <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/profile" element={<Profile />} />
                <Route path="/edit-profile" element={<EditProfile />} />
                <Route path="/favorites" element={<Favorites />} />
                <Route path="/job/:id" element={<JobDetail />} />
            </Routes>
        </>
    );
}

export default App;