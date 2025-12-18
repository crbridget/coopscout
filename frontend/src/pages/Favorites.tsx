import { useState, useEffect } from 'react';
import { supabase } from '../lib/supabaseClient';
import { favoriteService } from '../services/favoriteService';
import JobCard from '../components/JobCard';
import type { Job } from '../lib/types/job';
import './Favorites.css';

function Favorites() {
    const [jobs, setJobs] = useState<Job[]>([]);
    const [favorites, setFavorites] = useState<string[]>([]);
    const [loading, setLoading] = useState(true);
    const [user, setUser] = useState<any>(null);

    useEffect(() => {
        checkAuthAndLoadFavorites();
    }, []);

    const checkAuthAndLoadFavorites = async () => {
        const { data: { user } } = await supabase.auth.getUser();

        if (!user) {
            setLoading(false);
            return;
        }

        setUser(user);
        await loadFavorites(user.id);
    };

    const loadFavorites = async (userId: string) => {
        try {
            // Get favorite job IDs
            const favoriteIds = await favoriteService.getFavorites(userId);
            setFavorites(favoriteIds);

            if (favoriteIds.length === 0) {
                setLoading(false);
                return;
            }

            // Load the actual job data for those IDs
            const { data, error } = await supabase
                .from('jobs')
                .select('*')
                .in('id', favoriteIds);

            if (error) throw error;
            setJobs(data || []);
        } catch (error) {
            console.error('Error loading favorites:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleToggleFavorite = async (jobId: string) => {
        if (!user) return;

        const isFavorite = favorites.includes(jobId);

        try {
            await favoriteService.toggleFavorite(user.id, jobId, isFavorite);

            // Update local state
            if (isFavorite) {
                setFavorites(favorites.filter(id => id !== jobId));
                setJobs(jobs.filter(job => job.id !== jobId));
            }
        } catch (error) {
            console.error('Error toggling favorite:', error);
        }
    };

    if (loading) {
        return <div className="favorites-page">Loading your favorites...</div>;
    }

    if (!user) {
        return (
            <div className="favorites-page">
                <div className="no-favorites">
                    <p>Please sign in to view your favorites</p>
                    <button onClick={() => window.location.href = '/profile'}>Sign In</button>
                </div>
            </div>
        );
    }

    return (
        <div className="favorites-page">
            <h1 className="favorites-title">My Favorite Jobs</h1>

            {jobs.length === 0 ? (
                <div className="no-favorites">
                    <p>You haven't saved any jobs yet!</p>
                    <p>Click the star icon on any job to save it here.</p>
                </div>
            ) : (
                <div className="favorites-grid">
                    {jobs.map((job) => (
                        <JobCard
                            key={job.id}
                            job={job}
                            onToggleFavorite={() => handleToggleFavorite(job.id)}
                            isFavorite={true}
                        />
                    ))}
                </div>
            )}
        </div>
    );
}

export default Favorites;