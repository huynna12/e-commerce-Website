import { useState } from 'react';
import api from '../api';
import { useNavigate, Link } from 'react-router-dom';
import { ACCESS_TOKEN, REFRESH_TOKEN } from '../constants';
import LoadingIndicator from './LoadingIndicator';
import Navbar from './Navbar';
import PropTypes from 'prop-types';
import { parsePhoneNumberFromString } from 'libphonenumber-js';

const Form = ({ route, method }) => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    password2: '',
    address: '',
    phone_number: '',
  });

  const [loading, setLoading] = useState(false);
  const [hovered, setHovered] = useState(null);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const name = method === 'login' ? 'Login' : 'Register';
  const activeTab = hovered || name;

  function formatErrorMessage(errorData) {
    if (typeof errorData === 'string') return errorData;
    if (typeof errorData === 'object') {
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

  const updateData = (name, value) => {
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const isValidPhone = (value) => {
    if (!value) return false;
    try {
      const phone_number = parsePhoneNumberFromString(value);
      return phone_number ? phone_number.isValid() : false;
    } catch {
      return false;
    }
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
      if (!isValidPhone(formData.phone_number)) {
        setError('Please enter a valid phone number (include country code).');
        setLoading(false);
        return;
      }
    }

    try {
      const payload =
        method === 'register'
          ? {
              username: formData.username,
              email: formData.email,
              password: formData.password,
              password2: formData.password2,
              address: formData.address,
              phone_number: formData.phone_number,
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
        navigate('/heidi');
      } else {
        // trigger backend to send verification code (adjust endpoint if needed)
        try {
          await api.post('/api/send-phone-code/', {
            username: formData.username,
            phone_number: formData.phone_number,
          });
        } catch (sendErr) {
          // non-fatal: still proceed to verification page but surface a console warning
          // backend may already send code during registration; this is a best-effort call.
          // eslint-disable-next-line no-console
          console.warn('Failed to request phone verification code:', sendErr);
        }
        navigate('/verify-phone', { state: { username: formData.username, phone_number: formData.phone_number } });
      }
    } catch (error) {
      setError(
        error.response?.data
          ? formatErrorMessage(error.response.data)
          : error.message
      );
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

          <label className="label" htmlFor="username">Username</label>
          <input
            name="username"
            className="form-input"
            type="text"
            value={formData.username}
            onChange={e => updateData(e.target.name, e.target.value)}
            placeholder="Enter your username"
            required
          />

          {method === 'register' && (
            <>
              <label className="label" htmlFor="email">Email</label>
              <input
                name="email"
                className="form-input"
                type="email"
                value={formData.email}
                onChange={e => updateData(e.target.name, e.target.value)}
                placeholder="Enter your email"
                required
              />

              <label className="label" htmlFor="address">Address</label>
              <input
                name="address"
                className="form-input"
                type="text"
                value={formData.address}
                onChange={e => updateData(e.target.name, e.target.value)}
                placeholder="Enter your address"
              />

              <label className="label" htmlFor="phone_number">Phone number</label>
              <input
                name="phone_number"
                className="form-input"
                type="tel"
                value={formData.phone_number}
                onChange={e => updateData(e.target.name, e.target.value)}
                placeholder="+1234567890 (include country code)"
                required
              />
            </>
          )}

          <label className="label" htmlFor="password">Password</label>
          <input
            name="password"
            className="form-input"
            type="password"
            value={formData.password}
            onChange={e => updateData(e.target.name, e.target.value)}
            placeholder="Enter your password"
            required
          />

          {method === 'register' && (
            <>
              <label className="label" htmlFor="password2">Confirm Password</label>
              <input
                name="password2"
                className="form-input"
                type="password"
                value={formData.password2}
                onChange={e => updateData(e.target.name, e.target.value)}
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

Form.propTypes = {
  route: PropTypes.string.isRequired,
  method: PropTypes.oneOf(['login', 'register']).isRequired,
};

export default Form;