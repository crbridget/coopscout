import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { supabase } from '../lib/supabaseClient';
import type { Job } from '../lib/types/job';
import './JobDetail.css';

function JobDetail() {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const [job, setJob] = useState<Job | null>(null);
    const [loading, setLoading] = useState(true);
    const [isFavorite, setIsFavorite] = useState(false);

    useEffect(() => {
        if (id) {
            loadJob(parseInt(id));
            checkIfFavorite(parseInt(id));
        }
    }, [id]);

    const loadJob = async (jobId: number) => {
        try {
            const { data, error } = await supabase
                .from('jobs')
                .select('*')
                .eq('id', jobId)
                .single();

            if (error) throw error;
            setJob(data);
        } catch (error) {
            console.error('Error loading job:', error);
        } finally {
            setLoading(false);
        }
    };

    const checkIfFavorite = (jobId: number) => {
        const favoritesString = localStorage.getItem('favorites');
        const favorites = favoritesString ? JSON.parse(favoritesString) : [];
        setIsFavorite(favorites.includes(jobId));
    };

    const toggleFavorite = () => {
        if (!job) return;

        const favoritesString = localStorage.getItem('favorites');
        const favorites = favoritesString ? JSON.parse(favoritesString) : [];

        const newFavorites = isFavorite
            ? favorites.filter((id: number) => id !== job.id)
            : [...favorites, job.id];

        localStorage.setItem('favorites', JSON.stringify(newFavorites));
        setIsFavorite(!isFavorite);
    };

    if (loading) {
        return <div className="job-detail-page">Loading...</div>;
    }

    if (!job) {
        return (
            <div className="job-detail-page">
                <p>Job not found</p>
                <button onClick={() => navigate('/')}>Back to Home</button>
            </div>
        );
    }

    return (
        <div className="job-detail-page">
            <button className="back-btn" onClick={() => navigate(-1)}>
                ← Back
            </button>

            <div className="job-detail-container">
                <div className="job-header">
                    <div>
                        <h1>{job.title}</h1>
                        <h2>{job.company}</h2>
                    </div>
                    <button
                        className={`favorite-btn-large ${isFavorite ? 'favorited' : ''}`}
                        onClick={toggleFavorite}
                    >
                        {isFavorite ? '★' : '☆'}
                    </button>
                </div>

                <div className="job-info-grid">
                    <div className="info-item">
                        <strong>Location:</strong>
                        <span>{job.location}</span>
                    </div>
                    <div className="info-item">
                        <strong>Deadline:</strong>
                        <span>{job.deadline}</span>
                    </div>
                    <div className="info-item">
                        <strong>Compensation:</strong>
                        <span>{job.compensation}</span>
                    </div>
                    <div className="info-item">
                        <strong>Targeted Major:</strong>
                        <span>{job.targeted_major}</span>
                    </div>
                    <div className="info-item">
                        <strong>Minimum GPA:</strong>
                        <span>{job.minimum_GPA}</span>
                    </div>
                </div>

                <div className="job-description-section">
                    <h3>Job Description</h3>
                    <p>{job.description}</p>
                </div>

                <div className="action-buttons">
                    <button className="apply-btn">Apply Now</button>
                    <button className="save-btn" onClick={toggleFavorite}>
                        {isFavorite ? 'Saved ✓' : 'Save for Later'}
                    </button>
                </div>
            </div>
        </div>
    );
}

export default JobDetail;