import { useState, useEffect } from 'react';
import { supabase } from '../lib/supabaseClient';
import Auth from '../components/Auth';
import './Profile.css';

function Profile() {
    const [user, setUser] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        supabase.auth.getSession().then(({ data: { session } }) => {
            setUser(session?.user ?? null);
            setLoading(false);
        });

        const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
            setUser(session?.user ?? null);
        });

        return () => subscription.unsubscribe();
    }, []);

    const handleSignOut = async () => {
        await supabase.auth.signOut();
    };

    if (loading) {
        return <div>Loading...</div>;
    }

    if (!user) {
        return <Auth />;
    }

    return (
        <div className="profile-page">
            <h1 className="title">Profile Page</h1>
            <p className="paragraph">Welcome, {user.email}!</p>
            <button onClick={handleSignOut}>Sign Out</button>
        </div>
    );
}

export default Profile;