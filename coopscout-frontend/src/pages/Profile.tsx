import { useState, useEffect } from 'react';
import { supabase } from '../lib/supabaseClient';
import Auth from '../components/Auth';
import ProfileSetup from '../components/ProfileSetup';
import './Profile.css';
import type { User } from '../lib/types/user';

function Profile() {
    const [session, setSession] = useState<any>(null);
    const [userProfile, setUserProfile] = useState<User | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Get current session
        supabase.auth.getSession().then(({ data: { session } }) => {
            setSession(session);
            if (session?.user) {
                checkProfile(session.user.id);
            } else {
                setLoading(false);
            }
        });

        // Listen for auth changes
        const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
            setSession(session);
            if (session?.user) {
                checkProfile(session.user.id);
            } else {
                setUserProfile(null);
                setLoading(false);
            }
        });

        return () => subscription.unsubscribe();
    }, []);

    const checkProfile = async (userId: string) => {
        try {
            const { data, error } = await supabase
                .from('users')
                .select('*')
                .eq('id', userId)
                .single();

            if (error && error.code !== 'PGRST116') { // PGRST116 = no rows returned
                throw error;
            }

            setUserProfile(data);
        } catch (error: any) {
            console.error('Error loading profile:', error.message);
        } finally {
            setLoading(false);
        }
    };

    const handleProfileComplete = () => {
        // Reload the profile data after setup
        if (session?.user) {
            checkProfile(session.user.id);
        }
    };

    const handleSignOut = async () => {
        await supabase.auth.signOut();
        setSession(null);
        setUserProfile(null);
    };

    if (loading) {
        return <div className="profile-page">Loading...</div>;
    }

    // Not logged in - show Auth component
    if (!session) {
        return <Auth />;
    }

    // Logged in but no profile data - show setup form
    if (!userProfile) {
        return (
            <ProfileSetup
                userId={session.user.id}
                userEmail={session.user.email || ''}
                onComplete={handleProfileComplete}
            />
        );
    }

    // Profile exists - show profile data
    return (
        <div className="profile-page">
            <h1 className="title">Profile Page</h1>
            <div className="profile-info">
                <p><strong>Name:</strong> {userProfile.full_name}</p>
                <p><strong>Email:</strong> {userProfile.email}</p>
                <p><strong>Major:</strong> {userProfile.major}</p>
                <p><strong>Graduation Year:</strong> {userProfile.graduation_year}</p>
                <p><strong>GPA:</strong> {userProfile.gpa}</p>
            </div>
            <button onClick={handleSignOut}>Sign Out</button>
        </div>
    );
}

export default Profile;