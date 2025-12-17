import { useState, useEffect } from 'react';
import { supabase } from '../lib/supabaseClient';
import { useNavigate } from 'react-router-dom';

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
    const [profile, setProfile] = useState<ProfileData>({
        full_name: '',
        major: '',
        graduation_year: new Date().getFullYear(),
        gpa: 0
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
                .from('profiles')
                .select('*')
                .eq('id', user.id)
                .single();

            if (error) throw error;

            if (data) {
                setProfile({
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

            const { error } = await supabase
                .from('profiles')
                .update({
                    full_name: profile.full_name,
                    major: profile.major,
                    graduation_year: profile.graduation_year,
                    gpa: profile.gpa,
                    updated_at: new Date().toISOString()
                })
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

    return (
        <div className="edit-profile-container">
            <h1>Edit Profile</h1>

            {loading ? (
                <p>Loading...</p>
            ) : (
                <form onSubmit={handleSubmit} className="edit-profile-form">
                    <div className="form-group">
                        <label>Full Name</label>
                        <input
                            type="text"
                            value={profile.full_name}
                            onChange={(e) => setProfile({ ...profile, full_name: e.target.value })}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label>Major</label>
                        <input
                            type="text"
                            value={profile.major}
                            onChange={(e) => setProfile({ ...profile, major: e.target.value })}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label>Graduation Year</label>
                        <input
                            type="number"
                            value={profile.graduation_year}
                            onChange={(e) => setProfile({ ...profile, graduation_year: parseInt(e.target.value) })}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label>GPA</label>
                        <input
                            type="number"
                            step="0.01"
                            min="0"
                            max="4.0"
                            value={profile.gpa}
                            onChange={(e) => setProfile({ ...profile, gpa: parseFloat(e.target.value) })}
                            required
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
            )}
        </div>
    );
}

export default EditProfile;