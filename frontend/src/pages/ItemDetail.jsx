import React, { useEffect, useState, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { distribute, gsap } from 'gsap';
import api from '../api';
import Navbar from '../components/NavBar';

const ItemDetail = () => {
  // Get the id of the item from URL
  // const {slug} = useParams();
  const {id} = useParams();
  
  const [item, setItem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const myRef = useRef(null);

  useEffect(() => {
    fetch(api.get('/items/${id}'))
    .then(res => res.json())
    .then(item => {
      setItem(item);
      setLoading(false);
    })
    .catch(() => {
      setError('Failed to load the item with the given url');
      setLoading(false);
    })
  }, [id]);

  // Animation part

  // Render
  if (loading) return <div>Loading ...</div>;
  if (error) return <div>{error}</div>
  
  return (
    <>
      <Navbar/>ß
      <main className='w-full px8 py-4'>
        <div className='grid grid-cols-5 gap-4'>
          <div className="col-span-2"></div>
          <div className="cols-span-2"></div>
          <div className="col-span-1"></div>
        </div>
      </main>
    </>
  )
};

export default ItemDetail;