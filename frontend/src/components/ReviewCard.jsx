import PropTypes from 'prop-types';
import { useState } from 'react';
import api from '../api';
import ImagesDisplay from './ImagesDisplay'

const ReviewCard = ({ review}) => {
    const [helpfulCount, setHelpfulCount] = useState(review.helpful_count);
    const [upvoted, setUpvoted] = useState(review.is_upvoted);

const handleUpvote = async () => {
    try {
        const res = await api.post(`/reviews/${review.id}/upvote/`);
        setHelpfulCount(res.data.helpful_count);
        setUpvoted(res.data.is_upvoted);
    } catch (error) {
        if (error.response && error.response.status === 401){
            alert('Please log in to upvote reviews.');
        }
        else {
            alert('An error occurred. Please try again.');
        }
    }
};

    return (
        <div className="mb-4">
            <div className="flex gap-x-4 mb-2">
                <span className="font-semibold">{review.reviewer}</span> 
                <span className="text-gray-400 text-sm">{new Date(review.created_at).toLocaleDateString()}</span>
                <button
                  onClick={handleUpvote}
                  style={{ background: 'none', border: 'none', padding: 0, cursor: 'pointer' }}
                  aria-label="Upvote"
                >
                  <img
                    src={upvoted ? "/assets/icons/fill_like.png" : "/assets/icons/nofill_like.png"}
                    alt="Upvote"
                    style={{ width: 18, height: 18 }}
                  />
                </button>
            </div>
            <p className="py-2">{review.content}</p>
            <ImagesDisplay images={review.media}/>
        </div>
    )
}

ReviewCard.propTypes = {
  review: PropTypes.object.isRequired,
};

export default ReviewCard;
