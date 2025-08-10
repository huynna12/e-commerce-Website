import { useState } from 'react';
import api from '../api';
import { useNavigate, Link } from 'react-router-dom';
import { ACCESS_TOKEN, REFRESH_TOKEN } from '../constants';
import LoadingIndicator from './LoadingIndicator';
import Navbar from './Navbar';
import PropTypes from 'prop-types';

const Form = ({ route, method }) => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [password2, setPassword2] = useState('');
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      const payload = method === 'register'
        ? { username, email, password, password2 }
        : { username, password };
      const res = await api.post(route, payload);
      if (method === 'login') {
        localStorage.setItem(ACCESS_TOKEN, res.data.access);
        localStorage.setItem(REFRESH_TOKEN, res.data.refresh);
        localStorage.setItem('username', username);
        navigate('/heidi');
      } else {
        navigate('/login');
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
        <form
          onSubmit={handleSubmit}
          className="bg-[#F8EEDF] shadow-lg rounded-2xl px-8 pt-8 pb-8 w-full max-w-sm flex flex-col items-center border-2 border-black"
        >
          <h1 className="text-3xl font-bold mb-8 text-[#8E1616]">{name}</h1>
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
          <label className="w-full text-left mb-1 font-medium text-black" htmlFor="username">Username</label>
          <input
            id="username"
            className="form-input mb-4 w-full px-3 py-2 border border-[#E8C999] rounded focus:outline-none focus:ring-2 focus:ring-[#E8C999] bg-white text-black"
            type="text"
            value={username}
            onChange={e => setUsername(e.target.value)}
            placeholder="Enter your username"
            required
          />
          {method === 'register' && (
            <>
              <label className="w-full text-left mb-1 font-medium text-black" htmlFor="email">Email</label>
              <input
                id="email"
                className="form-input mb-4 w-full px-3 py-2 border border-[#E8C999] rounded focus:outline-none focus:ring-2 focus:ring-[#E8C999] bg-white text-black"
                type="email"
                value={email}
                onChange={e => setEmail(e.target.value)}
                placeholder="Enter your email"
                required
              />
            </>
          )}
          <label className="w-full text-left mb-1 font-medium text-black" htmlFor="password">Password</label>
          <input
            id="password"
            className="form-input mb-4 w-full px-3 py-2 border border-[#E8C999] rounded focus:outline-none focus:ring-2 focus:ring-[#E8C999] bg-white text-black"
            type="password"
            value={password}
            onChange={e => setPassword(e.target.value)}
            placeholder="Enter your password"
            required
          />
          {method === 'register' && (
            <>
              <label className="w-full text-left mb-1 font-medium text-black" htmlFor="password2">Confirm Password</label>
              <input
                id="password2"
                className="form-input mb-8 w-full px-3 py-2 border border-[#E8C999] rounded focus:outline-none focus:ring-2 focus:ring-[#E8C999] bg-white text-black"
                type="password"
                value={password2}
                onChange={e => setPassword2(e.target.value)}
                placeholder="Confirm your password"
                required
              />
            </>
          )}
          {loading && <LoadingIndicator />}
          <button
            className="form-button w-full py-3 bg-black text-[#F8EEDF] px-4 rounded-full hover:bg-[#8E1616] hover:text-white transition-colors font-semibold"
            type="submit"
            disabled={loading}
          >
            {name}
          </button>
        </form>
      </div>
    </>
  );
}

Form.propTypes = {
  route: PropTypes.string.isRequired,
  method: PropTypes.oneOf(['login', 'register']).isRequired,
};

export default Form;