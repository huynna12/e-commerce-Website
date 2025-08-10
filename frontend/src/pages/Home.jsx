import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import ItemRow from '../components/ItemRow';
import LoadingIndicator from '../components/LoadingIndicator';
import NotFound from './NotFound';
import api from '../api';

const Home = () => {
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  useEffect(() => {
    api.get(`/homepage/`)
      .then(res => setData(res.data))
      .catch(() => setError('Failed to load the data'));
  }, []); // Only run once on mount

  if (!data) return <LoadingIndicator />;
  if (error) return <NotFound />;

  return (
    <>
      <Navbar />
      <div className='px-8'>
        <ItemRow title="Featured items" itemList={data.featured} />
        <ItemRow title="Trending" itemList={data.trending} />
        <ItemRow title="Recently viewed items" itemList={data.recently_viewed} />
        <ItemRow
        title={`Recommended for ${localStorage.getItem('username') || 'you'}`}
        itemList={data.recommended}
        />
      </div>
    </>
  );
};

export default Home;