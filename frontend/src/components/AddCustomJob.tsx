import { useState, useEffect } from 'react';
import { supabase } from '../lib/supabaseClient';
import './AddCustomJob.css';

interface AddCustomJobProps {
    userId: string;
    onClose: () => void;
    onJobAdded: () => void;
}

function AddCustomJob({ userId, onClose, onJobAdded }: AddCustomJobProps) {
    const [formData, setFormData] = useState({
        title: '',
        company: '',
        location: '',
        deadline: '',
        compensation: '',
        targeted_major: '',
        minimum_GPA: '',
        description: '',
        job_link: '',
        status: 'saved'
    });
    const [saving, setSaving] = useState(false);
    const [loadingProfile, setLoadingProfile] = useState(true);

    useEffect(() => {
        loadUserProfile();
    }, [userId]);

    const loadUserProfile = async () => {
        try {
            const { data, error } = await supabase
                .from('users')
                .select('major')
                .eq('id', userId)
                .single();

            if (error) throw error;

            if (data?.major) {
                setFormData(prev => ({
                    ...prev,
                    targeted_major: data.major
                }));
            }
        } catch (error) {
            console.error('Error loading user profile:', error);
        } finally {
            setLoadingProfile(false);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSaving(true);

        try {
            // First, create the job in the jobs table
            const { data: jobData, error: jobError } = await supabase
                .from('jobs')
                .insert({
                    title: formData.title,
                    company: formData.company,
                    location: formData.location,
                    deadline: formData.deadline || null,
                    compensation: formData.compensation || 'Not specified',
                    targeted_major: formData.targeted_major || 'Any',
                    minimum_GPA: formData.minimum_GPA || '0.0',
                    description: formData.description || 'No description provided',
                    job_link: formData.job_link || null
                })
                .select()
                .single();

            if (jobError) throw jobError;

            // Then, add it to applications
            const { error: appError } = await supabase
                .from('applications')
                .insert({
                    user_id: userId,
                    job_id: jobData.id,
                    status: formData.status,
                    applied_date: formData.status === 'applied' ? new Date().toISOString() : null
                });

            if (appError) throw appError;

            alert('Job added successfully!');
            onJobAdded();
            onClose();
        } catch (error) {
            console.error('Error adding job:', error);
            alert('Failed to add job. Please try again.');
        } finally {
            setSaving(false);
        }
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2>Add External Job Application</h2>
                    <button className="close-btn" onClick={onClose}>✕</button>
                </div>

                {loadingProfile ? (
                    <div style={{ padding: '2rem', textAlign: 'center' }}>
                        Loading...
                    </div>
                ) : (
                    <form onSubmit={handleSubmit} className="custom-job-form">
                        <div className="form-row">
                            <div className="form-group">
                                <label>Job Title *</label>
                                <input
                                    type="text"
                                    value={formData.title}
                                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                                    required
                                />
                            </div>

                            <div className="form-group">
                                <label>Company *</label>
                                <input
                                    type="text"
                                    value={formData.company}
                                    onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                                    required
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <label>Job Posting Link</label>
                            <input
                                type="url"
                                value={formData.job_link}
                                onChange={(e) => setFormData({ ...formData, job_link: e.target.value })}
                                placeholder="https://example.com/job-posting"
                            />
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label>Location</label>
                                <input
                                    type="text"
                                    value={formData.location}
                                    onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                                    placeholder="e.g., Boston, MA, USA"
                                />
                            </div>

                            <div className="form-group">
                                <label>Application Deadline</label>
                                <input
                                    type="date"
                                    value={formData.deadline}
                                    onChange={(e) => setFormData({ ...formData, deadline: e.target.value })}
                                />
                            </div>
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label>Compensation</label>
                                <input
                                    type="text"
                                    value={formData.compensation}
                                    onChange={(e) => setFormData({ ...formData, compensation: e.target.value })}
                                    placeholder="e.g., $25/hr"
                                />
                            </div>

                            <div className="form-group">
                                <label>Targeted Major</label>
                                <input
                                    type="text"
                                    value={formData.targeted_major}
                                    onChange={(e) => setFormData({ ...formData, targeted_major: e.target.value })}
                                    placeholder="e.g., Computer Science"
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <label>Minimum GPA</label>
                            <input
                                type="text"
                                value={formData.minimum_GPA}
                                onChange={(e) => setFormData({ ...formData, minimum_GPA: e.target.value })}
                                placeholder="e.g., 3.0"
                            />
                        </div>

                        <div className="form-group">
                            <label>Job Description</label>
                            <textarea
                                value={formData.description}
                                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                rows={4}
                                placeholder="Brief description of the role..."
                            />
                        </div>

                        <div className="form-group">
                            <label>Application Status *</label>
                            <select
                                value={formData.status}
                                onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                            >
                                <option value="saved">Saved</option>
                                <option value="applied">Applied</option>
                                <option value="interview">Interview</option>
                                <option value="offer">Offer</option>
                                <option value="rejected">Rejected</option>
                            </select>
                        </div>

                        <div className="modal-buttons">
                            <button type="submit" disabled={saving} className="submit-btn">
                                {saving ? 'Adding...' : 'Add Job'}
                            </button>
                            <button type="button" onClick={onClose} className="cancel-btn">
                                Cancel
                            </button>
                        </div>
                    </form>
                )}
            </div>
        </div>
    );
}

export default AddCustomJob;