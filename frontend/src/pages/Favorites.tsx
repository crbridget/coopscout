import { useState, useEffect } from 'react';
import JobCard from '../components/JobCard';
import type { Job } from '../lib/types/job';
import { supabase } from '../lib/supabaseClient';
import './Favorites.css';

function Favorites() {
    const [allJobs, setAllJobs] = useState<Job[]>([]);
    const [favorites, setFavorites] = useState<number[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        try {
            // Load favorites from localStorage
            const favoritesString = localStorage.getItem('favorites');
            const favoriteIds = favoritesString ? JSON.parse(favoritesString) : [];
            setFavorites(favoriteIds);

            // Load all jobs from Supabase
            const { data, error } = await supabase
                .from('jobs')
                .select('*');

            if (error) throw error;
            setAllJobs(data || []);

        } catch (error) {
            console.error('Error loading data:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleToggleFavorite = (jobId: number) => {
        const newFavorites = favorites.includes(jobId)
            ? favorites.filter(id => id !== jobId)
            : [...favorites, jobId];

        setFavorites(newFavorites);
        localStorage.setItem('favorites', JSON.stringify(newFavorites));
    };

    const favoriteJobs = allJobs.filter(job => favorites.includes(job.id as number));

    if (loading) {
        return <div className="favorites-page">Loading your favorites...</div>;
    }

    return (
        <div className="favorites-page">
            <h1 className="favorites-title">My Favorite Jobs</h1>

            {favoriteJobs.length === 0 ? (
                <div className="no-favorites">
                    <p>You haven't saved any jobs yet!</p>
                    <p>Click the heart icon on any job to save it here.</p>
                </div>
            ) : (
                <div className="favorites-grid">
                    {favoriteJobs.map((job) => (
                        <JobCard
                            key={job.id}
                            job={job}
                            onToggleFavorite={() => handleToggleFavorite(job.id as number)}
                            isFavorite={true}
                        />
                    ))}
                </div>
            )}
        </div>
    );
}

export default Favorites;