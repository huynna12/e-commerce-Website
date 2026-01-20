import React, { useState, useEffect } from 'react';
import Navbar from '../components/layout/Navbar';
import ItemRow from '../components/items/ItemRow';
import LoadingIndicator from '../components/ui/LoadingIndicator';
import ErrorState from '../components/ErrorState';
import api from '../api';

const Home = () => {
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  useEffect(() => {
    api
      .get('/homepage/')
      .then((res) => setData(res.data))
      .catch(() => setError('Failed to load the homepage data'));
  }, []);

  if (error) {
    return (
      <>
        <Navbar />
        <ErrorState message={error} />
      </>
    );
  }

  if (!data) return <LoadingIndicator />;

  return (
    <>
      <Navbar />
      <div className="px-8">
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