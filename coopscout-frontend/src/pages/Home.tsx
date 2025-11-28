import { useState, useEffect } from 'react';
import type { Job } from '../../public/lib/types/job';
import JobCard from "../components/JobCard.tsx";
import '../App.css';

function Home() {
    const [jobs, setJobs] = useState<Job[]>([]);
    const [loading, setLoading] = useState(true);
    const [favorites, setFavorites] = useState<string[]>([]);

    useEffect(() => {
        fetch('/coopsearch.json')
            .then(response => response.json())
            .then(data => {
                setJobs(data);
                setLoading(false);
            })
            .catch(error => {
                console.error('Error loading jobs: ', error);
                setLoading(false);
            });
    }, []);

    useEffect(() => {
        const savedFavorites = localStorage.getItem('favoriteJobs');
        if (savedFavorites) {
            setFavorites(JSON.parse(savedFavorites));
        }
    }, []);

    useEffect(() => {
        localStorage.setItem('favoriteJobs', JSON.stringify(favorites));
    }, [favorites]);

    const toggleFavorite = (jobTitle: string) => {
        if (favorites.includes(jobTitle)) {
            setFavorites(favorites.filter(title => title !== jobTitle));
        } else {
            setFavorites([...favorites, jobTitle]);
        }
    };

    if (loading) {
        return <div>Loading jobs...</div>;
    }

    return (
        <div className="App">
            <h1>CoopScout</h1>
            <p>Found {jobs.length} co-op positions</p>

            <div className="jobs-container">
                {jobs.map((job, index) => (
                    <JobCard
                        key={index}
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