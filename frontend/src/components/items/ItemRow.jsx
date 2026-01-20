import PropTypes from 'prop-types';
import { Link } from 'react-router-dom';
import Rating from '../ui/Rating';
import { apiUrl, DEFAULT_IMAGE } from '../../constants';
import api from '../../api';

const ItemRow = ({ title, itemList, showEdit = false }) => {
  return (
    <div className='py-8'>
      <h1 className='text-4xl mb-4 font-semibold'>{title}</h1>
      <div className='flex gap-8 overflow-x-auto'>
        {itemList && itemList.length > 0 ? (
          itemList.map(item => {
            let image_src = DEFAULT_IMAGE;
            if (item.item_image?.image_url && item.item_image.image_url !== "null" && item.item_image.image_url !== "") {
              image_src = item.item_image.image_url;
            } else if (item.item_image?.image_file && item.item_image.image_file !== "null" && item.item_image.image_file !== "") {
              image_src = apiUrl + item.item_image.image_file;
            }
            const card = (
              <div className='bg-white rounded-xl shadow hover:shadow-lg transition-shadow p-4 cursor-pointer flex flex-col items-center w-56'>
                <img
                  src={image_src}
                  alt={item.item_name}
                  className='w-48 h-48 object-cover rounded mb-3 border'
                />
                <div className='text-lg font-semibold text-gray-900 text-center'>{item.item_name}</div>
                <Rating rate={item.review_stats?.average_rating} numRating={item.review_stats?.total_reviews} compact />
                <div className='text-base text-[#8E1616] font-bold mb-2'>${item.current_price}</div>
                <button
                  className='form-button w-full px-2 py-2 bg-black text-[#E8C999] rounded-full hover:bg-[#8E1616] hover:text-white transition-colors font-semibold text-xs'
                  type='button'
                  onClick={async (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    try {
                      const res = await api.post('cart/items/', { item_id: item.id, quantity: 1 });
                      window.dispatchEvent(new CustomEvent('cart:updated', { detail: { total_quantity: res.data?.total_quantity } }));
                      alert('Added to cart');
                    } catch {
                      alert('Please log in to add to cart');
                    }
                  }}
                >
                  Add to cart
                </button>
              </div>
            );

            if (!showEdit) {
              return (
                <Link to={`/items/${item.id}`} className='block' key={item.id}>
                  {card}
                </Link>
              );
            }

            return (
              <div key={item.id} className='block'>
                <Link to={`/items/${item.id}`} className='block'>
                  {card}
                </Link>
                <div className='mt-2 flex justify-center'>
                  <Link
                    to={`/items/${item.id}/edit`}
                    className='text-sm font-semibold text-[#8E1616] hover:underline'
                  >
                    Edit
                  </Link>
                </div>
              </div>
            );
          })
        ) : (
          <div className='text-[#daaa56] italic'>No items to display</div>
        )}
      </div>
    </div>
  );
};

ItemRow.propTypes = {
  title: PropTypes.string.isRequired,
  itemList: PropTypes.array.isRequired,
  showEdit: PropTypes.bool,
};

export default ItemRow;