import { useState } from 'react';
import api from '../../api';
import { useNavigate, Link } from 'react-router-dom';
import { ACCESS_TOKEN, REFRESH_TOKEN } from '../../constants';
import LoadingIndicator from '../ui/LoadingIndicator';
import Navbar from '../layout/Navbar';
import PropTypes from 'prop-types';

function formatErrorMessage(errorData) {
  if (typeof errorData === 'string') return errorData;
  if (Array.isArray(errorData)) return errorData.join('\n');

  if (typeof errorData === 'object' && errorData) {
    return Object.entries(errorData)
      .map(([field, messages]) =>
        Array.isArray(messages)
          ? `${field}: ${messages.join(', ')}`
          : `${field}: ${messages}`
      )
      .join('\n');
  }
  return 'An unknown error occurred.';
}

const AuthForm = ({ route, method }) => {
  const name = method === 'login' ? 'Login' : 'Register';
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    password2: '',
  });

  const [hovered, setHovered] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const activeTab = hovered || name;

  const updateData = (fieldName, value) => {
    setFormData((prev) => ({ ...prev, [fieldName]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    if (method === 'register') {
      if (formData.password !== formData.password2) {
        setError('Passwords do not match.');
        setLoading(false);
        return;
      }
    }

    try {
      // Match backend serializers exactly
      const payload =
        method === 'register'
          ? {
              username: formData.username,
              email: formData.email,
              password: formData.password,
              password2: formData.password2,
            }
          : {
              username: formData.username,
              password: formData.password,
            };

      const res = await api.post(route, payload);

      if (method === 'login') {
        localStorage.setItem(ACCESS_TOKEN, res.data.access);
        localStorage.setItem(REFRESH_TOKEN, res.data.refresh);
        localStorage.setItem('username', formData.username);
        navigate('/');
      } else {
        // Register succeeded; send user to login
        navigate('/login');
      }
    } catch (err) {
      setError(err.response?.data ? formatErrorMessage(err.response.data) : err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Navbar />
      <div className="flex items-center justify-center min-h-screen">
        <form onSubmit={handleSubmit} className="form-container max-w-sm">
          <h1 className="form-heading">{name}</h1>

          <div className="w-full mb-8 flex justify-center">
            <div className="relative flex w-80 h-14 bg-white border-2 border-black rounded-full overflow-hidden">
              <span
                className={`
                  absolute top-0 h-full w-1/2 rounded-full transition-all duration-300
                  ${activeTab === 'Register' ? 'left-0' : 'left-1/2'}
                `}
                style={{ background: '#8E1616', zIndex: 1 }}
              />

              <Link
                to="/register"
                className={`flex-1 flex items-center justify-center font-semibold cursor-pointer transition-colors z-10 relative
                  ${activeTab === 'Register' ? 'text-white' : 'text-black'}
                `}
                onMouseEnter={() => setHovered('Register')}
                onMouseLeave={() => setHovered(null)}
                style={{ userSelect: 'none', height: '100%' }}
              >
                Register
              </Link>

              <Link
                to="/login"
                className={`flex-1 flex items-center justify-center font-semibold cursor-pointer transition-colors z-10 relative
                  ${activeTab === 'Login' ? 'text-white' : 'text-black'}
                `}
                onMouseEnter={() => setHovered('Login')}
                onMouseLeave={() => setHovered(null)}
                style={{ userSelect: 'none', height: '100%' }}
              >
                Login
              </Link>
            </div>
          </div>

          {error && (
            <div className="w-full mb-4 text-center text-red-600 bg-red-100 rounded p-2 border border-red-300 whitespace-pre-line">
              {error}
            </div>
          )}

          <label className="label" htmlFor="username">
            Username
          </label>
          <input
            name="username"
            className="form-input"
            type="text"
            value={formData.username}
            onChange={(e) => updateData(e.target.name, e.target.value)}
            placeholder="Enter your username"
            required
          />

          {method === 'register' && (
            <>
              <label className="label" htmlFor="email">
                Email
              </label>
              <input
                name="email"
                className="form-input"
                type="email"
                value={formData.email}
                onChange={(e) => updateData(e.target.name, e.target.value)}
                placeholder="Enter your email"
                required
              />
            </>
          )}

          <label className="label" htmlFor="password">
            Password
          </label>
          <input
            name="password"
            className="form-input"
            type="password"
            value={formData.password}
            onChange={(e) => updateData(e.target.name, e.target.value)}
            placeholder="Enter your password"
            required
          />

          {method === 'register' && (
            <>
              <label className="label" htmlFor="password2">
                Confirm Password
              </label>
              <input
                name="password2"
                className="form-input"
                type="password"
                value={formData.password2}
                onChange={(e) => updateData(e.target.name, e.target.value)}
                placeholder="Confirm your password"
                required
              />
            </>
          )}

          {loading && <LoadingIndicator />}

          <button className="form-btn" type="submit" disabled={loading}>
            {name}
          </button>
        </form>
      </div>
    </>
  );
};

AuthForm.propTypes = {
  route: PropTypes.string.isRequired,
  method: PropTypes.oneOf(['login', 'register']).isRequired,
};

export default AuthForm;