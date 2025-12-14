import React, { useEffect, useState } from 'react';
import axios from 'axios';

const Profile = () => {
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

  if (error) return <p className="text-center text-red-600 mt-10">{error}</p>;
  if (!profile) return <p className="text-center mt-10">Loading...</p>;

  return (
    <main className="screen-max-width px-8 py-24 flex justify-center items-center">
      <div className="form-container">
        {/* Profile image */}
        {profile.image && (
          <img
            src={profile.image}
            alt={`${profile.username}'s avatar`}
            className="w-32 h-32 rounded-full mb-4 border-2 border-black object-cover"
          />
        )}
        <div className="form-heading text-3xl font-bold text-center mb-2">{profile.username}</div>
        
        {/* Profile bio */}
        {profile.bio && (
          <p className="text-gray-700 text-center mb-4">
            <span className="font-semibold">Bio:</span> {profile.bio} This is the user's bio
          </p>
        )}
        

      </div>
    </main>
  );
};

export default Profile;