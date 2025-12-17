import { useState, useEffect } from 'react';
import { supabase } from '../lib/supabaseClient';
import { useNavigate } from 'react-router-dom';
import type { Application } from '../lib/types/application';
import type { Job } from '../lib/types/job';
import './ApplicationTracker.css';

interface ApplicationWithJob extends Application {
    job?: Job;
}

function ApplicationTracker() {
    const navigate = useNavigate();
    const [applications, setApplications] = useState<ApplicationWithJob[]>([]);
    const [loading, setLoading] = useState(true);
    const [filter, setFilter] = useState<string>('all');

    useEffect(() => {
        checkAuthAndLoadApplications();
    }, []);

    const checkAuthAndLoadApplications = async () => {
        const { data: { user } } = await supabase.auth.getUser();

        if (!user) {
            navigate('/profile');
            return;
        }

        loadApplications(user.id);
    };

    const loadApplications = async (userId: string) => {
        try {
            const { data, error } = await supabase
                .from('applications')
                .select(`
          *,
          jobs (*)
        `)
                .eq('user_id', userId)
                .order('updated_at', { ascending: false });

            if (error) throw error;

            // Flatten the data structure
            const applicationsWithJobs = data.map(app => ({
                ...app,
                job: app.jobs
            }));

            setApplications(applicationsWithJobs);
        } catch (error) {
            console.error('Error loading applications:', error);
        } finally {
            setLoading(false);
        }
    };

    const updateApplicationStatus = async (appId: number, newStatus: string) => {
        try {
            const { error } = await supabase
                .from('applications')
                .update({
                    status: newStatus,
                    updated_at: new Date().toISOString()
                })
                .eq('id', appId);

            if (error) throw error;

            const { data: { user } } = await supabase.auth.getUser();
            if (user) loadApplications(user.id);
        } catch (error) {
            console.error('Error updating status:', error);
            alert('Failed to update status');
        }
    };

    const deleteApplication = async (appId: number) => {
        if (!confirm('Are you sure you want to delete this application?')) return;

        try {
            const { error } = await supabase
                .from('applications')
                .delete()
                .eq('id', appId);

            if (error) throw error;

            setApplications(applications.filter(app => app.id !== appId));
        } catch (error) {
            console.error('Error deleting application:', error);
            alert('Failed to delete application');
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'saved': return '#6b7280';
            case 'applied': return '#3b82f6';
            case 'interview': return '#f59e0b';
            case 'offer': return '#10b981';
            case 'rejected': return '#ef4444';
            default: return '#6b7280';
        }
    };

    const filteredApplications = filter === 'all'
        ? applications
        : applications.filter(app => app.status === filter);

    if (loading) {
        return <div className="tracker-page">Loading...</div>;
    }

    return (
        <div className="tracker-page">
            <h1>Application Tracker</h1>

            <div className="tracker-stats">
                <div className="stat-card">
                    <span className="stat-number">{applications.length}</span>
                    <span className="stat-label">Total Applications</span>
                </div>
                <div className="stat-card">
          <span className="stat-number">
            {applications.filter(a => a.status === 'applied').length}
          </span>
                    <span className="stat-label">Applied</span>
                </div>
                <div className="stat-card">
          <span className="stat-number">
            {applications.filter(a => a.status === 'interview').length}
          </span>
                    <span className="stat-label">Interviews</span>
                </div>
                <div className="stat-card">
          <span className="stat-number">
            {applications.filter(a => a.status === 'offer').length}
          </span>
                    <span className="stat-label">Offers</span>
                </div>
            </div>

            <div className="filter-bar">
                <button
                    className={filter === 'all' ? 'active' : ''}
                    onClick={() => setFilter('all')}
                >
                    All
                </button>
                <button
                    className={filter === 'saved' ? 'active' : ''}
                    onClick={() => setFilter('saved')}
                >
                    Saved
                </button>
                <button
                    className={filter === 'applied' ? 'active' : ''}
                    onClick={() => setFilter('applied')}
                >
                    Applied
                </button>
                <button
                    className={filter === 'interview' ? 'active' : ''}
                    onClick={() => setFilter('interview')}
                >
                    Interview
                </button>
                <button
                    className={filter === 'offer' ? 'active' : ''}
                    onClick={() => setFilter('offer')}
                >
                    Offer
                </button>
                <button
                    className={filter === 'rejected' ? 'active' : ''}
                    onClick={() => setFilter('rejected')}
                >
                    Rejected
                </button>
            </div>

            {filteredApplications.length === 0 ? (
                <div className="no-applications">
                    <p>No applications found.</p>
                    <button onClick={() => navigate('/')}>Browse Jobs</button>
                </div>
            ) : (
                <div className="applications-list">
                    {filteredApplications.map((app) => (
                        <div key={app.id} className="application-card">
                            <div className="app-header">
                                <div>
                                    <h3
                                        className="app-title"
                                        onClick={() => navigate(`/job/${app.job_id}`)}
                                    >
                                        {app.job?.title || 'Unknown Position'}
                                    </h3>
                                    <p className="app-company">{app.job?.company || 'Unknown Company'}</p>
                                </div>
                                <button
                                    className="delete-btn"
                                    onClick={() => deleteApplication(app.id)}
                                >
                                    ✕
                                </button>
                            </div>

                            <div className="app-info">
                                <p><strong>Location:</strong> {app.job?.location || 'N/A'}</p>
                                <p><strong>Deadline:</strong> {app.job?.deadline || 'N/A'}</p>
                                {app.applied_date && (
                                    <p><strong>Applied:</strong> {new Date(app.applied_date).toLocaleDateString()}</p>
                                )}
                                {app.interview_date && (
                                    <p><strong>Interview:</strong> {new Date(app.interview_date).toLocaleString()}</p>
                                )}
                            </div>

                            <div className="app-status-section">
                                <label>Status:</label>
                                <select
                                    value={app.status}
                                    onChange={(e) => updateApplicationStatus(app.id, e.target.value)}
                                    style={{ borderColor: getStatusColor(app.status) }}
                                >
                                    <option value="saved">Saved</option>
                                    <option value="applied">Applied</option>
                                    <option value="interview">Interview</option>
                                    <option value="offer">Offer</option>
                                    <option value="rejected">Rejected</option>
                                </select>
                            </div>

                            {app.notes && (
                                <div className="app-notes">
                                    <strong>Notes:</strong>
                                    <p>{app.notes}</p>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

export default ApplicationTracker;