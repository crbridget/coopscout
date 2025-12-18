import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { supabase } from '../lib/supabaseClient.ts';
import { favoriteService } from '../services/favoriteService';
import type { Job } from '../lib/types/job.ts';
import './JobDetail.css';

function JobDetail() {
    const { id } = useParams<{ id: string }>();
    const navigate = useNavigate();
    const [job, setJob] = useState<Job | null>(null);
    const [loading, setLoading] = useState(true);
    const [isFavorite, setIsFavorite] = useState(false);
    const [isTracked, setIsTracked] = useState(false);
    const [applicationStatus, setApplicationStatus] = useState<string | null>(null);
    const [userId, setUserId] = useState<string | null>(null);
    const [checkingFavorite, setCheckingFavorite] = useState(true);

    useEffect(() => {
        if (id) {
            loadJob(id);
            checkAuth(id);
        }
    }, [id]);

    const checkAuth = async (jobId: string) => {
        const { data: { user } } = await supabase.auth.getUser();
        if (user) {
            setUserId(user.id);
            await Promise.all([
                checkIfFavorite(user.id, jobId),
                checkIfTracked(user.id, jobId)
            ]);
        } else {
            setCheckingFavorite(false);
        }
    };

    const checkIfFavorite = async (userId: string, jobId: string) => {
        setCheckingFavorite(true);
        try {
            const favorites = await favoriteService.getFavorites(userId);
            const isFav = favorites.includes(jobId);
            console.log('Checking favorite:', { jobId, favorites, isFav }); // Debug
            setIsFavorite(isFav);
        } catch (error) {
            console.error('Error checking favorite:', error);
            setIsFavorite(false);
        } finally {
            setCheckingFavorite(false);
        }
    };

    const checkIfTracked = async (userId: string, jobId: string) => {
        try {
            const { data } = await supabase
                .from('applications')
                .select('status')
                .eq('user_id', userId)
                .eq('job_id', jobId)
                .single();

            if (data) {
                setIsTracked(true);
                setApplicationStatus(data.status);
            }
        } catch (error) {
            setIsTracked(false);
        }
    };

    const loadJob = async (jobId: string) => {
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

    const toggleFavorite = async () => {
        if (!job) return;

        if (!userId) {
            alert('Please sign in to save favorites');
            navigate('/profile');
            return;
        }

        const previousState = isFavorite;

        setIsFavorite(!isFavorite);

        try {
            await favoriteService.toggleFavorite(userId, job.id, isFavorite);
            console.log('Toggled favorite:', { jobId: job.id, newState: !isFavorite }); // Debug
        } catch (error) {
            console.error('Error toggling favorite:', error);
            setIsFavorite(previousState);
            alert('Failed to update favorite');
        }
    };

    const addToApplications = async (status: string = 'saved') => {
        if (!job || !userId) {
            alert('Please sign in to track applications');
            navigate('/profile');
            return;
        }

        try {
            const { error } = await supabase
                .from('applications')
                .insert({
                    user_id: userId,
                    job_id: job.id,
                    status: status,
                    applied_date: status === 'applied' ? new Date().toISOString() : null
                });

            if (error) throw error;

            setIsTracked(true);
            setApplicationStatus(status);
            alert(`Added to Application Tracker as "${status}"!`);
        } catch (error) {
            console.error('Error adding to applications:', error);
            alert('Failed to add to tracker. Please try again.');
        }
    };

    const goToTracker = () => {
        navigate('/applications');
    };

    if (loading) {
        return <div className="job-detail-page">Loading...</div>;
    }

    if (!job) {
        return (
            <div className="job-detail-page">
                <div className="job-not-found">
                    <p>Job not found</p>
                    <button onClick={() => navigate('/')}>Back to Home</button>
                </div>
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
                        disabled={checkingFavorite}
                    >
                        {isFavorite ? '★' : '☆'}
                    </button>
                </div>

                {isTracked && (
                    <div className="tracking-banner">
                        <span>Currently tracking this job as: <strong>{applicationStatus}</strong></span>
                        <button onClick={goToTracker}>View in Tracker →</button>
                    </div>
                )}

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
                    {!isTracked ? (
                        <>
                            <button className="apply-btn" onClick={() => addToApplications('applied')}>
                                Mark as Applied
                            </button>
                            <button className="save-btn" onClick={() => addToApplications('saved')}>
                                Save to Tracker
                            </button>
                        </>
                    ) : (
                        <button className="tracker-btn" onClick={goToTracker}>
                            Manage in Application Tracker
                        </button>
                    )}
                </div>
            </div>
        </div>
    );
}

export default JobDetail;