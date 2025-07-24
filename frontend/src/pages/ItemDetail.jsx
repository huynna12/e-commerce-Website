import React, { useEffect, useState, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { gsap } from 'gsap';
import api from '../api';
import Navbar from '../components/NavBar';

const ItemDetail = () => {
  const { itemId } = useParams();

  const [item, setItem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const containerRef = useRef(null);
  const imageRef = useRef(null);
  const detailsRef = useRef(null);
  const priceRef = useRef(null);
  const buttonRef = useRef(null);

  useEffect(() => {
    const fetchItem = async () => {
      try {
        setLoading(true);
        const response = await api.get(`items/${itemId}/`);
        setItem(response.data);
        setError(null);
      } catch (error) {
        console.error('Error fetching item:', error);
        setError('Failed to load item');
      } finally {
        setLoading(false);
      }
    };

    fetchItem();
  }, [itemId]);

  useEffect(() => {
    if (item && containerRef.current) {
      const tl = gsap.timeline();

      gsap.set([imageRef.current, detailsRef.current], {
        opacity: 0,
        y: 50
      });

      tl.to(imageRef.current, {
        opacity: 1,
        y: 0,
        duration: 0.8,
        ease: 'power2.out'
      })
        .to(detailsRef.current, {
          opacity: 1,
          y: 0,
          duration: 0.6,
          ease: 'power2.out'
        }, '-=0.4')
        .to(priceRef.current, {
          scale: 1.1,
          duration: 0.3,
          ease: 'back.out(1.7)'
        }, '-=0.2')
        .to(priceRef.current, {
          scale: 1,
          duration: 0.2
        });
    }
  }, [item]);

  const getConditionColor = (condition) => {
    const colors = {
      new: 'bg-green-100 text-green-800',
      like_new: 'bg-blue-100 text-blue-800',
      good: 'bg-yellow-100 text-yellow-800',
      fair: 'bg-orange-100 text-orange-800',
      poor: 'bg-red-100 text-red-800'
    };
    return colors[condition] || 'bg-gray-100 text-gray-800';
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(price);
  };

  if (loading) return <div className="animate-pulse text-center py-10">Loading...</div>;
  if (error) return <div className="text-center text-red-500 py-10">{error}</div>;
  if (!item) return <div className="text-center py-10">Item not found.</div>;

  return (
    <div ref={containerRef} className="min-h-screen bg-gray-50 w-full">
      <Navbar/>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 py-12 px-4 sm:px-6 lg:px-8">
        <div ref={imageRef} className="rounded-2xl shadow-lg overflow-hidden">
          <img src={item.item_image || 'https://via.placeholder.com/600'} alt={item.item_name} className="w-full h-full object-cover" />
        </div>

        <div ref={detailsRef} className="space-y-6">
          <h1 className="text-3xl font-bold text-gray-900">{item.item_name}</h1>
          <p className="text-sm text-gray-600">Sold by {item.seller}</p>

          <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${getConditionColor(item.item_condition)}`}>
            {item.item_condition.replace('_', ' ').toUpperCase()}
          </span>

          <div ref={priceRef} className="space-y-2">
            <div className="flex items-baseline gap-2">
              <span className="text-4xl font-bold text-gray-900">{formatPrice(item.item_price)}</span>
              {item.is_on_sale && item.sale_price && (
                <span className="text-2xl text-gray-400 line-through">{formatPrice(item.sale_price)}</span>
              )}
            </div>
            {item.is_on_sale && (
              <p className="text-green-600 font-medium">
                Save {formatPrice(item.item_price - (item.sale_price || 0))}!
              </p>
            )}
          </div>

          <div>
            <h3 className="text-lg font-semibold text-gray-900">Description</h3>
            <p className="text-gray-700 whitespace-pre-line">{item.item_desc || 'No description available.'}</p>
          </div>

          <div className="grid grid-cols-2 gap-4 py-6 border-t border-gray-200">
            <div>
              <h4 className="text-gray-900 font-medium">Category</h4>
              <p className="text-gray-600 capitalize">{item.item_category}</p>
            </div>
            <div>
              <h4 className="text-gray-900 font-medium">Origin</h4>
              <p className="text-gray-600">{item.item_origin}</p>
            </div>
            <div>
              <h4 className="text-gray-900 font-medium">Availability</h4>
              <p className={item.is_available ? 'text-green-600 font-semibold' : 'text-red-600 font-semibold'}>
                {item.is_available ? '✓ In Stock' : '✗ Out of Stock'}
              </p>
            </div>
            <div>
              <h4 className="text-gray-900 font-medium">Listed</h4>
              <p className="text-gray-600">{new Date(item.created_at).toLocaleDateString()}</p>
            </div>
          </div>

          <button
            ref={buttonRef}
            onMouseEnter={() => gsap.to(buttonRef.current, { scale: 1.05, duration: 0.2 })}
            onMouseLeave={() => gsap.to(buttonRef.current, { scale: 1, duration: 0.2 })}
            className="w-full py-3 text-white bg-blue-600 hover:bg-blue-700 rounded-xl font-semibold transition-transform"
          >
            Add to Cart
          </button>
        </div>
      </div>
    </div>
  );
};

export default ItemDetail;