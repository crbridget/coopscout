import { useState, useEffect } from 'react';
import type { Job } from '../lib/types/job';
import JobCard from "../components/JobCard.tsx";
import { jobService } from '../services/jobService';
import { favoriteService } from '../services/favoriteService';
import { supabase } from '../lib/supabaseClient';
import './Home.css';

function Home() {
    const [jobs, setJobs] = useState<Job[]>([]);
    const [loading, setLoading] = useState(true);
    const [favorites, setFavorites] = useState<string[]>([]);
    const [user, setUser] = useState<any>(null);

    useEffect(() => {
        supabase.auth.getSession().then(({ data: { session } }) => {
            setUser(session?.user ?? null);
        });

        const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
            setUser(session?.user ?? null);
        });

        return () => subscription.unsubscribe();
    }, []);

    // Load jobs from Supabase
    useEffect(() => {
        loadJobs();
    }, []);

    // Load favorites when user changes
    useEffect(() => {
        if (user) {
            loadFavorites();
        } else {
            setFavorites([]);
        }
    }, [user]);

    const loadJobs = async () => {
        try {
            const data = await jobService.getAllJobs();
            setJobs(data);
        } catch (error) {
            console.error('Error loading jobs:', error);
        } finally {
            setLoading(false);
        }
    };

    const loadFavorites = async () => {
        if (!user) return;

        try {
            const favs = await favoriteService.getFavorites(user.id);
            setFavorites(favs);
        } catch (error) {
            console.error('Error loading favorites:', error);
        }
    };

    const toggleFavorite = async (jobId: string) => {
        if (!user) {
            alert('Please sign in to save favorites');
            return;
        }

        const isFavorite = favorites.includes(jobId);

        try {
            await favoriteService.toggleFavorite(user.id, jobId, isFavorite);

            // Update local state
            if (isFavorite) {
                setFavorites(favorites.filter(id => id !== jobId));
            } else {
                setFavorites([...favorites, jobId]);
            }
        } catch (error) {
            console.error('Error toggling favorite:', error);
        }
    };

    if (loading) {
        return <div>Loading jobs...</div>;
    }

    return (
        <div className="home-page">
            <h1>CoopScout</h1>
            <p>Found {jobs.length} co-op positions</p>

            <div className="jobs-container">
                {jobs.map((job) => (
                    <JobCard
                        key={job.id}
                        job={job}
                        onToggleFavorite={() => toggleFavorite(job.title)}
                        isFavorite={favorites.includes(job.title)}
                    />
                ))}
            </div>
        </div>
    );
}

export default Home;