import './Profile.css'

function Profile() {
    console.log("Profile component rendered!");
    return (
        <div className="App" style={{backgroundColor: 'lightblue', minHeight: '100vh'}}>
            <h1 className="title">Profile Page</h1>
            <p className="paragraph">This is your profile!</p>
        </div>
    );
}

export default Profile;