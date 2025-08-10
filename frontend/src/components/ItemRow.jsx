import PropTypes from 'prop-types';
import { Link } from 'react-router-dom';
import Rating from './Rating';
const apiUrl = import.meta.env.VITE_API_URL;

const ItemRow = ({ title, itemList }) => {
  return (
    <div className='py-8'>
      <h1 className='text-4xl mb-4 font-semibold'>{title}</h1>
      <div className='flex gap-8 overflow-x-auto'>
        {itemList && itemList.length > 0 ? (
          itemList.map(item => {
            const image_src =
              item.item_image?.image_url
                ? item.item_image.image_url
                : apiUrl + item.item_image?.image_file;
            return (
              <Link to={`/items/${item.id}`} className='block' key={item.id}>
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
                  >
                    Add to cart
                  </button>
                </div>
              </Link>
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
};

export default ItemRow;