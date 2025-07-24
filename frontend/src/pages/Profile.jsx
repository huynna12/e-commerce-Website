import React, { useEffect, useState } from 'react';
import axios from 'axios';

const Profile = () => {
  // Get the logged-in username from localStorage
  const username = localStorage.getItem('username');
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!username) {
      setError('No user logged in.');
      return;
    }
    axios
      .get(`http://localhost:8000/profile/${username}/`)
      .then(response => setProfile(response.data))
      .catch(() => {
        setError('Profile not found.');
        setProfile(null);
      });
  }, [username]);

  if (error) return <p>{error}</p>;
  if (!profile) return <p>Loading...</p>;

  return (
    <div>
      <h2>Welcome, {profile.username}</h2>
      {profile.bio && <p>Bio: {profile.bio}</p>}
      {profile.image && (
        <img
          src={profile.image}
          alt={`${profile.username}'s avatar`}
          style={{ width: 120, height: 120, borderRadius: '50%' }}
        />
      )}
      {/* Add more public fields as needed */}
    </div>
  );
};

export default Profile;