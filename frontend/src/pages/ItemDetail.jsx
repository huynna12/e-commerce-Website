import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import api from '../api';
import Navbar from '../components/layout/Navbar';
import NotFound from './NotFound';
import '../index.css';
import Rating from '../components/ui/Rating';
import ItemRow from '../components/items/ItemRow';
import ReviewCard from '../components/items/ReviewCard';
import ImagesDisplayGrid from '../components/items/ImagesDisplayGrid';

const ItemDetail = () => {
  const { itemId } = useParams();
  const [item, setItem] = useState(null);
  const [error, setError] = useState(null);
  const [suggestions, setSuggestions] = useState(null);
  const [quantity, setQuantity] = useState(null);

  useEffect(() => {
    api.get(`items/${itemId}/`)
      .then(res => setItem(res.data))
      .catch(() => setError('Failed to load the item with the given url'));
  }, [itemId]);

  useEffect(() => {
    api.get(`items/${itemId}/suggestions/`)
      .then(res => { setSuggestions(res.data); })
      .catch(() => setError('Failed to load suggestions'));
  }, [itemId]);

  if (!item) return <div className='text-center py-10 text-lg'>Loading ...</div>;
  if (error) return <NotFound />;

  return (
    <>
      <Navbar />
      {/* Content is here */}
      <main className='screen-max-width px-8 py-24'>
        <div className='grid grid-cols-5 gap-8'>
          <div className='flex flex-col items-center justify-center col-span-3'>
            <div className='col-span-3 flex flex-col items-center justify-center'>
          <ImagesDisplayGrid images={item.item_images} />
        </div>
          </div>

          {/* Details Section */}
          <div className='flex flex-col justify-start col-span-2'>
            <div className='mb-6'>
              <p className='text-4xl font-bold text-gray-900'>{item.item_name} 
                <span className='ml-2 text-[#daaa56] font semibold text-lg'> {item.display_condition}</span>
              </p>
              <p className='text-lg text-gray-500'>{item.display_category}</p>
              <Rating rate={item.review_stats?.average_rating} numRating={item.review_stats?.total_reviews} />
            </div>
            <p className='mb-6 text-gray-700'>{item.item_summary}</p>

            {/* Item quantity to add */}
            <div className='py-5'>
              <label htmlFor='quantity' className='block text-sm font-medium text-gray-700 mb-1'>
                Quantity
              </label>
              <input
                id='quantity'
                type='number'
                min={1}
                max={item.item_quantity}
                value={quantity || 1}
                onChange={e => setQuantity(Number(e.target.value))}
                className='px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-[#E8C999]'
              />
              {item.item_quantity && (
                <span className='ml-2 text-sm text-gray-500'>In stock: {item.item_quantity}</span>
              )}
            </div>
            
            {/* Item price */}
            <div className='font-semibold text-4xl mb-4'>
              ${item.current_price}
            </div>
            {item.is_on_sale && (
              <div className='text-sm text-[#E8C999] mb-2'>
                <span className='line-through'>Was ${item.item_price}</span>
              </div>
            )}

            {/* Add to cart button and out of stock announcement if item is not in stock */}
            <button
              className='form-button w-full py-3 bg-black text-[#E8C999] px-4 rounded-full hover:bg-[#8E1616] hover:text-white transition-colors font-semibold disabled:opacity-50 disabled:cursor-not-allowed'
              type='button'
              disabled={!item.is_in_stock || item.item_quantity === 0}
              onClick={async () => {
                try {
                  const qty = quantity || 1;
                  const res = await api.post('cart/items/', { item_id: item.id, quantity: qty });
                  window.dispatchEvent(new CustomEvent('cart:updated', { detail: { total_quantity: res.data?.total_quantity } }));
                  alert('Added to cart');
                } catch {
                  alert('Please log in to add to cart');
                }
              }}
            >
              Add to cart
            </button>
            {(!item.is_in_stock || item.item_quantity === 0) && (
              <div className='text-[#8E1616] mt-2 font-semibold'>Out of stock</div>
            )}
          </div>
        </div>

        {/* Item information */}
        <div className='mb-56 mt-32'>
          <h1 className='text-4xl mb-4 font-sans font-semibold'>Information</h1>
          <div>
            {item.item_desc}
          </div>
        </div>

        {/* Suggesions for the user */}
        {suggestions &&
          <div>
            <ItemRow title='Other items from this seller' itemList={suggestions.seller_items} />
            <ItemRow title='Related items' itemList={suggestions.related} />
            <ItemRow title={`Best sellers in ${item.display_category}`} itemList={suggestions.best_sellers_in_category}/>
          </div>        
        }

        {/* Reviews */}
        <h1 className='text-4xl mb-6 font-sans font-semibold mt-24'>Customer reviews</h1>
        <div className='grid grid-cols-5 gap-x-20'>
          <div className='col-span-2'>
            <Rating rate={item.review_stats?.average_rating} numRating={item.review_stats?.total_reviews} bigSize/>
             
            {item.review_stats?.rating_distribution && (
              <div className='mt-6 pl-0'>
                {[5, 4, 3, 2, 1].map(star => {
                  const count = item.review_stats.rating_distribution[String(star)];
                  const total = item.review_stats.total_reviews;
                  const percent = total ? Math.round((count / total) * 100) : 0;
                  return (
                    <div key={star} className='flex'>
                      <span className='w-auto text-right mr-2 font-semibold text-gray-700'>{star}</span>
                      <div className='flex-1 mx-2 bg-gray-200 rounded h-4 relative'>
                        <div
                          className='bg-[#000000] h-4 rounded'
                          style={{ width: `${percent}%` }}
                        />
                      </div>
                      <span className='ml-2 text-sm text-gray-500'>{count}</span>
                    </div>
                  );
                })}
              </div>
            )}
         
          </div>

          {/* Customers' review content */}
          <div className='col-span-3'>  
            {item.reviews && item.reviews.length > 0 ? (
              item.reviews.map(review => (
                <ReviewCard key={review.id} review={review} />
              ))
            ) : (
              <div className='text-[#daaa56] italic'>No reviews to display</div>
            )}
          </div>
        </div>
      </main>
    </>
  );
};

export default ItemDetail;