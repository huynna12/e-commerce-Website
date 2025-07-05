import React, { useEffect, useState } from 'react';
import axios from 'axios';

const Profile = () => {
  const [user, setUser] = useState(null);

  useEffect(() => {
    axios.get('http://localhost:8000/api/profile/', {
      headers: {
        Authorization: `Bearer ${localStorage.getItem('access_token')}`,  // adjust as needed
      },
    })
    .then(response => setUser(response.data))
    .catch(error => console.error('Error fetching profile:', error));
  }, []);

  if (!user) return <p>Loading...</p>;

  return (
    <div>
      <h2>Welcome, {user.username}</h2>
      <p>Email: {user.email}</p>
    </div>
  );
};

export default Profile;