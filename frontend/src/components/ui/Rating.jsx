import PropTypes from 'prop-types';

const Rating = ({ rate, numRating, compact = false, bigSize = false }) => {
  const fullStars = Math.floor(rate);
  const hasHalfStar = rate - fullStars >= 0.25 && rate - fullStars < 0.75;
  const stars = [];

  if (!rate || rate === 0.0) {
    return (
      <div className={bigSize ? 'text-[#daaa56] text-lg italic' : 'text-[#daaa56] text-xs italic'}>
        No rating
      </div>
    );
  }

  const starClass = bigSize ? 'w-6 h-6' : 'w-3 h-3';

  for (let i = 0; i < fullStars; i++) {
    stars.push(
      <img
        key={`full-${i}`}
        src='/assets/icons/fs_yellow.png'
        alt='Full Star'
        className={starClass}
      />
    );
  }

  if (hasHalfStar) {
    stars.push(
      <img
        key='half'
        src='/assets/icons/hs_yellow.png'
        alt='Half Star'
        className={starClass}
      />
    );
  }

  const totalStars = fullStars + (hasHalfStar ? 1 : 0);
  for (let i = totalStars; i < 5; i++) {
    stars.push(
      <img
        key={`empty-${i}`}
        src='/assets/icons/empty.png'
        alt='Empty Star'
        className={starClass}
      />
    );
  }

  return (
    <div className='flex items-center gap-2'>
      <span className={bigSize ? 'text-xl font-bold' : 'text-base font-semibold'}>
        {rate ? rate.toFixed(1) : '0.0'}
      </span>
      <div className='flex gap-1'>{stars}</div>
      <span className={bigSize ? 'ml-2 text-sm text-gray-400' : 'ml-2 text-xs text-gray-400'}>
        {compact ? `(${numRating})` : `${numRating} ratings`}
      </span>
    </div>
  );
};

Rating.propTypes = {
  rate: PropTypes.number.isRequired,
  numRating: PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.number
  ]).isRequired,
  compact: PropTypes.bool,
  bigSize: PropTypes.bool,
};

export default Rating;