import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useEffect } from 'react';

import Register from './pages/Register';
import Login from './pages/Login';
import NotFound from './pages/NotFound';
import Home from './pages/Home';
import Profile from './pages/Profile';
import ProfileEdit from './pages/ProfileEdit';
import ItemDetail from './pages/ItemDetail';
import AddItem from './pages/AddItem';
import UpdateItem from './pages/UpdateItem';
import OrderDetail from './pages/OrderDetail';
import Cart from './pages/Cart';
import Checkout from './pages/Checkout';

import './index.css';

function RegisterAndClear() {
  useEffect(() => {
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    localStorage.removeItem('user');
  }, []);

  return <Register />;
}

function App() {
  return (
    <div className="w-full h-full bg-white">
      <BrowserRouter>
        <Routes>
          {/* homepage */}
          <Route path="/" element={<Home />} />

          <Route path="/items/:itemId" element={<ItemDetail />} />
          <Route path="/items/create" element={<AddItem />} />
          <Route path="/items/:itemId/edit" element={<UpdateItem />} />

          <Route path="/cart" element={<Cart />} />
          <Route path="/checkout" element={<Checkout />} />

          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<RegisterAndClear />} />
          <Route path="/profile/:username" element={<Profile />} />
          <Route path="/profile/:username/edit" element={<ProfileEdit />} />
          <Route path="/orders/:orderId" element={<OrderDetail />} />

          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;