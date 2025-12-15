import { useState } from "react";
import Stepper, { Step } from '../Stepper';
import { supabase } from '../lib/supabaseClient';
import './ProfileSetup.css';
import type {UserFormData} from '../lib/types/user';

type ProfileSetupProps = {
    userId: string;
    userEmail: string;
    onComplete: () => void;
};

export default function ProfileSetup({ userId, userEmail, onComplete }: ProfileSetupProps) {
    const [loading, setLoading] = useState(false);
    const [formData, setFormData] = useState<UserFormData>({
        full_name: '',
        major: '',
        graduation_year: '',
        gpa: '',
        nuworks_password: ''
    });

    const handleSubmit = async () => {
        try {
            setLoading(true);

            const { error } = await supabase
                .from('users')
                .upsert([
                    {
                        id: userId,
                        email: userEmail,
                        full_name: formData.full_name,
                        major: formData.major,
                        graduation_year: parseInt(formData.graduation_year),
                        gpa: parseFloat(formData.gpa),
                        nuworks_password: formData.nuworks_password  // ADDED THIS
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

                <Stepper
                    initialStep={1}
                    onStepChange={(step) => {
                        console.log('Current step:', step);
                    }}
                    onFinalStepCompleted={handleSubmit}
                    backButtonText="Previous"
                    nextButtonText="Next"
                    nextButtonProps={{ disabled: loading }}
                    backButtonProps={{ disabled: loading }}
                >
                    <Step>
                        <h3>Personal Information</h3>
                        <input
                            type="text"
                            placeholder="Full Name"
                            value={formData.full_name}
                            onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                            required
                        />
                    </Step>

                    <Step>
                        <h3>Academic Details</h3>
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
                    </Step>

                    <Step>
                        <h3>Academic Performance</h3>
                        <input
                            type="number"
                            step="0.01"
                            placeholder="GPA (e.g., 3.83)"
                            value={formData.gpa}
                            onChange={(e) => setFormData({ ...formData, gpa: e.target.value })}
                            required
                        />
                    </Step>

                    {/* NEW STEP - NUworks Password */}
                    <Step>
                        <h3>NUworks Access</h3>
                        <p style={{ fontSize: '14px', color: '#666', marginBottom: '15px' }}>
                            ⚠️ We need your NUworks password to automatically search for co-op jobs for you.
                            Your credentials are stored securely.
                        </p>
                        <input
                            type="password"
                            placeholder="NUworks Password"
                            value={formData.nuworks_password}
                            onChange={(e) => setFormData({ ...formData, nuworks_password: e.target.value })}
                            required
                        />
                        <p style={{ fontSize: '12px', color: '#999', marginTop: '10px' }}>
                            Your email ({userEmail}) will be used as your NUworks username.
                        </p>
                        <p style={{ fontSize: '14px', marginTop: '15px' }}>
                            Review your information and click Complete to finish.
                        </p>
                    </Step>
                </Stepper>
            </div>
        </div>
    );
}