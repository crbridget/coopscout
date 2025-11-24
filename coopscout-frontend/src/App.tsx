import { useState, useEffect } from 'react';
import { Job } from './types/job';
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
            <h1>CoopScout</h1>
            <p>Found {jobs.length} co-op position</p>
            {/*Add components here*/}
        </div>
    );
}

export default App;