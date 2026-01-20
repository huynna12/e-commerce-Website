import React from 'react';
import PropTypes from 'prop-types';
import { Link } from 'react-router-dom';

export default function ErrorState({
  title = 'Something went wrong',
  message = 'An unexpected error occurred.',
  showHomeLink = true,
}) {
  return (
    <div className="px-8 py-6">
      <h2 className="text-lg font-semibold">{title}</h2>
      <p className="mt-2 text-red-900">{message}</p>

      {showHomeLink && (
        <div className="mt-4">
          <Link className="text-blue-600 underline" to="/">
            Go back home
          </Link>
        </div>
      )}
    </div>
  );
}

ErrorState.propTypes = {
  title: PropTypes.string,
  message: PropTypes.string,
  showHomeLink: PropTypes.bool,
};