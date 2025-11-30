import './Profile.css'

function Profile() {
    console.log("Profile component rendered!");
    return (
        <div className="profile-page" style={{backgroundColor: 'lightblue'}}>
            <h1 className="title">Profile Page</h1>
            <p className="paragraph">This is your profile!</p>
        </div>
    );
}

export default Profile;