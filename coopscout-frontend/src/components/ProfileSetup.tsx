import { useState } from "react";
import { supabase } from '../lib/supabaseClient';
import './ProfileSetup.css';
import type {UserFormData} from '../lib/types/user';

type ProfileSetupProps = {
    userId: string;
    userEmail: string;
    onComplete: () => void;
};

export default function ProfileSetup({ userId, userEmail, onComplete }: ProfileSetupProps) {
    const [loading, setLoading] = useState(false); // Add this missing state
    const [formData, setFormData] = useState<UserFormData>({
        full_name: '',
        major: '',
        graduation_year: '',
        gpa: ''
    });

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        try {
            setLoading(true);

            const { error } = await supabase
                .from('users')
                .upsert([  // Changed from insert to upsert
                    {
                        id: userId,
                        email: userEmail,
                        full_name: formData.full_name,
                        major: formData.major,
                        graduation_year: parseInt(formData.graduation_year),
                        gpa: parseFloat(formData.gpa)
                    }
                ], { onConflict: 'id' });

            if (error) throw error;

            alert('Profile created successfully!');
            onComplete();
        } catch (error: any) {
            alert(error.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="profile-setup">
            <div className="profile-setup-container">
                <h2>Complete Your Profile</h2>
                <form onSubmit={handleSubmit}>
                    <input
                        type="text"
                        placeholder="Full Name"
                        value={formData.full_name}
                        onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                        required
                    />
                    <input
                        type="text"
                        placeholder="Major (e.g., Computer Science)"
                        value={formData.major}
                        onChange={(e) => setFormData({ ...formData, major: e.target.value })}
                        required
                    />
                    <input
                        type="number"
                        placeholder="Graduation Year (e.g., 2028)"
                        value={formData.graduation_year}
                        onChange={(e) => setFormData({ ...formData, graduation_year: e.target.value })}
                        required
                    />
                    <input
                        type="number"
                        step="0.01"
                        placeholder="GPA (e.g., 3.83)"
                        value={formData.gpa}
                        onChange={(e) => setFormData({ ...formData, gpa: e.target.value })}
                        required
                    />
                    <button type="submit" disabled={loading}>
                        {loading ? 'Creating Profile...' : 'Complete Profile'}
                    </button>
                </form>
            </div>
        </div>
    );
}