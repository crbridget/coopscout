import { useState, useEffect } from 'react';
import { supabase } from '../lib/supabaseClient';
import { useNavigate } from 'react-router-dom';
import './EditProfile.css'

interface ProfileData {
    full_name: string;
    major: string;
    graduation_year: number;
    gpa: number;
}

function EditProfile() {
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [currentProfile, setCurrentProfile] = useState<ProfileData | null>(null);
    const [formData, setFormData] = useState({
        full_name: '',
        major: '',
        graduation_year: '',
        gpa: ''
    });

    useEffect(() => {
        fetchProfile();
    }, []);

    const fetchProfile = async () => {
        try {
            const { data: { user } } = await supabase.auth.getUser();

            if (!user) {
                navigate('/');
                return;
            }

            const { data, error } = await supabase
                .from('users')
                .select('*')
                .eq('id', user.id)
                .single();

            if (error) throw error;

            if (data) {
                setCurrentProfile({
                    full_name: data.full_name || '',
                    major: data.major || '',
                    graduation_year: data.graduation_year || new Date().getFullYear(),
                    gpa: data.gpa || 0
                });
            }
        } catch (error) {
            console.error('Error fetching profile:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setSaving(true);

        try {
            const { data: { user } } = await supabase.auth.getUser();

            if (!user) throw new Error('No user found');

            const updates: any = {
                updated_at: new Date().toISOString()
            };

            if (formData.full_name.trim()) {
                updates.full_name = formData.full_name.trim();
            }
            if (formData.major.trim()) {
                updates.major = formData.major.trim();
            }
            if (formData.graduation_year) {
                updates.graduation_year = parseInt(formData.graduation_year);
            }
            if (formData.gpa) {
                updates.gpa = parseFloat(formData.gpa);
            }

            // Check if there's anything to update
            if (Object.keys(updates).length === 1) { // Only updated_at
                alert('Please fill in at least one field to update');
                setSaving(false);
                return;
            }

            const { error } = await supabase
                .from('users')
                .update(updates)
                .eq('id', user.id);

            if (error) throw error;

            alert('Profile updated successfully!');
            navigate('/profile');
        } catch (error) {
            console.error('Error updating profile:', error);
            alert('Failed to update profile. Please try again.');
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return <div className="edit-profile-container">Loading...</div>;
    }

    return (
        <div className="edit-profile-container">
            <h1>Edit Profile</h1>

            <form onSubmit={handleSubmit} className="edit-profile-form">
                <div className="form-group">
                    <label>Full Name</label>
                    <input
                        type="text"
                        value={formData.full_name}
                        onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                        placeholder={currentProfile?.full_name || 'Enter your full name'}
                    />
                </div>

                <div className="form-group">
                    <label>Major</label>
                    <input
                        type="text"
                        value={formData.major}
                        onChange={(e) => setFormData({ ...formData, major: e.target.value })}
                        placeholder={currentProfile?.major || 'Enter your major'}
                    />
                </div>

                <div className="form-group">
                    <label>Graduation Year</label>
                    <input
                        type="number"
                        value={formData.graduation_year}
                        onChange={(e) => setFormData({ ...formData, graduation_year: e.target.value })}
                        placeholder={currentProfile?.graduation_year.toString() || 'Enter graduation year'}
                    />
                </div>

                <div className="form-group">
                    <label>GPA</label>
                    <input
                        type="number"
                        step="0.01"
                        min="0"
                        max="4.0"
                        value={formData.gpa}
                        onChange={(e) => setFormData({ ...formData, gpa: e.target.value })}
                        placeholder={currentProfile?.gpa.toString() || 'Enter your GPA'}
                    />
                </div>

                <div className="button-group">
                    <button type="submit" disabled={saving}>
                        {saving ? 'Saving...' : 'Save Changes'}
                    </button>
                    <button type="button" onClick={() => navigate('/profile')}>
                        Cancel
                    </button>
                </div>
            </form>
        </div>
    );
}

export default EditProfile;