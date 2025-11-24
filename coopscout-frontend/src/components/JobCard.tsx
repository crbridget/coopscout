import type { Job } from '../types/job';

interface JobCardProps {
    job: Job;
}

function JobCard({ job }: JobCardProps) {
    return (
        <div className="job-card">
            <h2>{job.title}</h2>
            <h3>{job.company}</h3>
            <div className="job-details">
                <p><strong>Location:</strong> {job.location}</p>
                <p><strong>Deadline:</strong> {job.deadline}</p>
                <p><strong>Compensation:</strong> {job.compensation}</p>
                <p><strong>Major:</strong> {job["targeted major"]}</p>
                <p><strong>Min GPA:</strong> {job["minimum GPA"]}</p>
            </div>
            <div className="job-description">
                <p>{job.description}</p>
            </div>
        </div>
    );
}

export default JobCard;