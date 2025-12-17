import { useNavigate } from 'react-router-dom';
import type { Job } from '../lib/types/job';
import './JobCard.css';

interface JobCardProps {
    job: Job;
    onToggleFavorite: () => void;
    isFavorite: boolean;
}

function JobCard({ job, onToggleFavorite, isFavorite }: JobCardProps) {
    const navigate = useNavigate();

    const handleTitleClick = () => {
        navigate(`/job/${job.id}`);
    };

    const handleFavoriteClick = (e: React.MouseEvent) => {
        e.stopPropagation();
        onToggleFavorite();
    };

    return (
        <div className="job-card">
            <div className="card-header">
                <h2 className="job-title" onClick={handleTitleClick}>
                    {job.title}
                </h2>
                <button
                    className={`favorite-btn ${isFavorite ? 'favorited' : ''}`}
                    onClick={handleFavoriteClick}
                >
                    {isFavorite ? '★' : '☆'}
                </button>
            </div>

            <h3 className="job-company">{job.company}</h3>

            <div className="job-details">
                <p><strong>Location:</strong> {job.location}</p>
                <p><strong>Deadline:</strong> {job.deadline}</p>
                <p><strong>Compensation:</strong> {job.compensation}</p>
                <p><strong>Major:</strong> {job.targeted_major}</p>
                <p><strong>Min GPA:</strong> {job.minimum_GPA}</p>
            </div>

            <div className="job-description">
                <p>{job.description}</p>
            </div>
        </div>
    );
}

export default JobCard;