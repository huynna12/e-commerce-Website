import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { FaShoppingCart, FaSearch, FaUser, FaSignOutAlt } from 'react-icons/fa';
import { ACCESS_TOKEN } from '../../constants';
import api from '../../api';

const Navbar = () => {
  const [cartCount, setCartCount] = useState(0);
  const [search, setSearch] = useState('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  const fetchCartCount = () => {
    api.get('cart/').then((res) => {
      setCartCount(res.data?.total_quantity || 0);
    }).catch(() => {
      setCartCount(0);
    });
  };

  useEffect(() => {
    const checkAuthStatus = async () => {
      const token = localStorage.getItem(ACCESS_TOKEN);
      if (token) {
          // Try to get username from localStorage first
          let username = localStorage.getItem('username');
          setIsLoggedIn(true);
          setUser({ username: username || 'Profile'});

          // Best-effort cart count (ignore failures)
          fetchCartCount();
        }
    };
    checkAuthStatus();
  }, []);

  useEffect(() => {
    const onCartUpdated = (e) => {
      const next = e?.detail?.total_quantity;
      if (typeof next === 'number') {
        setCartCount(next);
        return;
      }
      if (isLoggedIn) fetchCartCount();
    };

    window.addEventListener('cart:updated', onCartUpdated);
    return () => window.removeEventListener('cart:updated', onCartUpdated);
  }, [isLoggedIn]);

  const displayName = user?.username || 'Profile';

  const handleSearch = (e) => {
    e.preventDefault();
    alert(`Searching for: ${search}`);
  };

  const handleLogout = () => {
    localStorage.clear()
    setIsLoggedIn(false);
    setUser(null);
    setCartCount(0);
    navigate('/');
    alert('Successfully logged out!');
  };

  return (
    <nav className="w-full flex items-center justify-between p-3 bg-[#F8EEDF] border-b-2 border-black">
      {/* Logo */}
      <div className="flex items-center">
        <Link to="/">
          <img src="/assets/images/logo.png" alt="H-Commerce Logo" className="ml-3 h-10 w-auto" />
        </Link>
      </div>

      {/* Search Bar */}
      <div className="flex-1 mx-4 max-w-md">
        <form className="relative" onSubmit={handleSearch}>
          <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-[#8E1616]">
            <FaSearch size={18} />
          </span>
          <input
            type="text"
            placeholder="Search for products..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-[#E8C999] rounded-full bg-white text-black focus:outline-none focus:ring-2 focus:ring-[#E8C999] focus:border-transparent transition-all"
          />
        </form>
      </div>

      {/* Conditional Navigation Buttons */}
      <div className="flex items-center space-x-4 mr-3">
        {isLoggedIn ? (
          <>
            <Link
              to="/items/create"
              className="flex items-center gap-2 font-semibold text-black hover:text-[#8E1616] transition-colors">    
              <span>Sell Item</span>
            </Link>
            {user?.username ? (
              <Link 
                to={`/profile/${user.username}`} 
                className="flex items-center gap-2 font-semibold text-black hover:text-[#8E1616] transition-colors"
              >
                <FaUser size={16} />
                <span>{displayName}</span>
              </Link>
            ) : null}
            <button 
              onClick={handleLogout}
              className="flex items-center gap-2 font-semibold text-black hover:text-[#8E1616] transition-colors"
            >
              <FaSignOutAlt size={16} />
              <span>Logout</span>
            </button>
          </>
        ) : (
          <>
            <Link to="/register" className="font-semibold text-black hover:text-[#8E1616] transition-colors">
              Sign Up
            </Link>
            <Link to="/login" className="font-semibold text-black hover:text-[#8E1616] transition-colors">
              Log In
            </Link>
          </>
        )}

        {/* Cart - Always visible */}
        <Link to="/cart" className="relative text-black hover:text-[#8E1616] transition-colors">
          <FaShoppingCart size={22} />
          {cartCount > 0 && (
            <span className="absolute -top-2 -right-2 bg-[#8E1616] text-white text-xs w-5 h-5 flex items-center justify-center rounded-full">
              {cartCount}
            </span>
          )}
        </Link>
      </div>
    </nav>
  );
};

export default Navbar;