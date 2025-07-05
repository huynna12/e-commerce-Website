import { useState } from 'react';
import api from '../api';
import { useNavigate, Link } from 'react-router-dom';
import { ACCESS_TOKEN, REFRESH_TOKEN } from '../constants';
import LoadingIndicator from './LoadingIndicator';
import Navbar from './NavBar';

function Form({ route, method }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [hovered, setHovered] = useState(null);
  const navigate = useNavigate();

  const name = method === 'login' ? 'Login' : 'Register';
  const activeTab = hovered || name;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await api.post(route, { username, password });
      if (method === 'login') {
        localStorage.setItem(ACCESS_TOKEN, res.data.access);
        localStorage.setItem(REFRESH_TOKEN, res.data.refresh);
        navigate('/');
      } else {
        navigate('/login');
      }
    } catch (error) {
      if (error.response && error.response.data) {
        alert(JSON.stringify(error.response.data));
      } else {
        alert(error.message);
      }
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
        {/* Sliding highlight tabs with outer box */}
        <div className="w-full mb-8 flex justify-center">
          <div className="relative flex w-80 h-14 bg-white border-2 border-black rounded-full overflow-hidden">
            {/* Highlight box */}
            <span
              className={`
                absolute top-0 h-full w-1/2 rounded-full transition-all duration-300
                ${activeTab === 'Register' ? 'left-0' : 'left-1/2'}
              `}
              style={{
                background: '#8E1616',
                zIndex: 1,
              }}
            />
            {/* Register Tab */}
            <a
              href="/register"
              className={`flex-1 flex items-center justify-center font-semibold cursor-pointer transition-colors z-10 relative
                ${activeTab === 'Register' ? 'text-white' : 'text-black'}
              `}
              onMouseEnter={() => setHovered('Register')}
              onMouseLeave={() => setHovered(null)}
              style={{ userSelect: 'none', height: '100%' }}
            >
              Register
            </a>
            {/* Login Tab */}
            <a
              href="/login"
              className={`flex-1 flex items-center justify-center font-semibold cursor-pointer transition-colors z-10 relative
                ${activeTab === 'Login' ? 'text-white' : 'text-black'}
              `}
              onMouseEnter={() => setHovered('Login')}
              onMouseLeave={() => setHovered(null)}
              style={{ userSelect: 'none', height: '100%' }}
            >
              Login
            </a>
          </div>
        </div>
        {/* Username */}
        <label className="w-full text-left mb-1 font-medium text-black" htmlFor="username">Username</label>
        <input
          id="username"
          className="form-input mb-4 w-full px-3 py-2 border border-[#E8C999] rounded focus:outline-none focus:ring-2 focus:ring-[#E8C999] bg-white text-black"
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Enter your username"
          required
        />
        {/* Password */}
        <label className="w-full text-left mb-1 font-medium text-black" htmlFor="password">Password</label>
        <input
          id="password"
          className="form-input mb-8 w-full px-3 py-2 border border-[#E8C999] rounded focus:outline-none focus:ring-2 focus:ring-[#E8C999] bg-white text-black"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Enter your password"
          required
        />
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

export default Form;