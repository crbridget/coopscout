import { useState, useEffect } from 'react';
import type { Job } from '../lib/types/job';
import JobCard from "../components/JobCard.tsx";
import { jobService } from '../services/jobService';
import { favoriteService } from '../services/favoriteService';
import { supabase } from '../lib/supabaseClient';
import './Home.css';

const JOBS_PER_PAGE = 21;

function Home() {
    const [jobs, setJobs] = useState<Job[]>([]);
    const [loading, setLoading] = useState(true);
    const [favorites, setFavorites] = useState<string[]>([]);
    const [user, setUser] = useState<any>(null);
    const [currentPage, setCurrentPage] = useState(1);

    useEffect(() => {
        supabase.auth.getSession().then(({ data: { session } }) => {
            setUser(session?.user ?? null);
        });

        const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
            setUser(session?.user ?? null);
        });

        return () => subscription.unsubscribe();
    }, []);

    useEffect(() => {
        loadJobs();
    }, []);

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

            if (isFavorite) {
                setFavorites(favorites.filter(id => id !== jobId));
            } else {
                setFavorites([...favorites, jobId]);
            }
        } catch (error) {
            console.error('Error toggling favorite:', error);
        }
    };

    // Pagination calculations
    const totalPages = Math.ceil(jobs.length / JOBS_PER_PAGE);
    const startIndex = (currentPage - 1) * JOBS_PER_PAGE;
    const endIndex = startIndex + JOBS_PER_PAGE;
    const currentJobs = jobs.slice(startIndex, endIndex);

    const goToPage = (page: number) => {
        setCurrentPage(page);
        window.scrollTo({ top: 0, behavior: 'smooth' });
    };

    const goToNextPage = () => {
        if (currentPage < totalPages) {
            goToPage(currentPage + 1);
        }
    };

    const goToPrevPage = () => {
        if (currentPage > 1) {
            goToPage(currentPage - 1);
        }
    };

    // Generate page numbers to display
    const getPageNumbers = () => {
        const pages = [];
        const maxPagesToShow = 5;

        if (totalPages <= maxPagesToShow) {
            for (let i = 1; i <= totalPages; i++) {
                pages.push(i);
            }
        } else {
            if (currentPage <= 3) {
                for (let i = 1; i <= 4; i++) pages.push(i);
                pages.push('...');
                pages.push(totalPages);
            } else if (currentPage >= totalPages - 2) {
                pages.push(1);
                pages.push('...');
                for (let i = totalPages - 3; i <= totalPages; i++) pages.push(i);
            } else {
                pages.push(1);
                pages.push('...');
                pages.push(currentPage - 1);
                pages.push(currentPage);
                pages.push(currentPage + 1);
                pages.push('...');
                pages.push(totalPages);
            }
        }
        return pages;
    };

    if (loading) {
        return <div className="home-page">Loading jobs...</div>;
    }

    return (
        <div className="home-page">
            <h1>Co-op Scout</h1>
            <p>Found {jobs.length} co-op positions</p>

            <div className="jobs-container">
                {currentJobs.map((job) => (
                    <JobCard
                        key={job.id}
                        job={job}
                        onToggleFavorite={() => toggleFavorite(job.id)}
                        isFavorite={favorites.includes(job.id)}
                    />
                ))}
            </div>

            {totalPages > 1 && (
                <div className="pagination">
                    <button
                        onClick={goToPrevPage}
                        disabled={currentPage === 1}
                        className="pagination-btn"
                    >
                        ← Previous
                    </button>

                    <div className="page-numbers">
                        {getPageNumbers().map((page, index) => (
                            typeof page === 'number' ? (
                                <button
                                    key={index}
                                    onClick={() => goToPage(page)}
                                    className={`page-number ${currentPage === page ? 'active' : ''}`}
                                >
                                    {page}
                                </button>
                            ) : (
                                <span key={index} className="page-ellipsis">...</span>
                            )
                        ))}
                    </div>

                    <button
                        onClick={goToNextPage}
                        disabled={currentPage === totalPages}
                        className="pagination-btn"
                    >
                        Next →
                    </button>
                </div>
            )}
        </div>
    );
}

export default Home;