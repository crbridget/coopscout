import { useState, useEffect } from 'react';
import type { Job } from './types/job';
import JobCard from "./components/JobCard.tsx";
import './App.css';

function App() {
    const [jobs, setJobs] = useState<Job[]>([]);
    const [loading, setLoading] = useState(true);

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

    if (loading) {
        return <div>Loading jobs...</div>;
    }

    return (
        <div className="App">
            <h1 className="title">CoopScout</h1>
            <p>Found {jobs.length} co-op positions</p>
            <div className="jobs-container">
                {jobs.map((job, index) => (
                    <JobCard key={index} job={job} />
                ))}
            </div>
        </div>
    );
}

export default App;