import { useEffect, useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

import api from '../api';
import Navbar from '../components/layout/Navbar';
import LoadingIndicator from '../components/ui/LoadingIndicator';
import ErrorState from '../components/ErrorState';
import { apiUrl, DEFAULT_IMAGE } from '../constants';

const getImageSrc = (itemImage) => {
  if (!itemImage) return DEFAULT_IMAGE;
  if (itemImage.image_url && itemImage.image_url !== 'null' && itemImage.image_url !== '') return itemImage.image_url;
  if (itemImage.image_file && itemImage.image_file !== 'null' && itemImage.image_file !== '') return apiUrl + itemImage.image_file;
  return DEFAULT_IMAGE;
};

const Cart = () => {
  const navigate = useNavigate();
  const [cart, setCart] = useState(null);
  const [error, setError] = useState('');
  const [busyItemId, setBusyItemId] = useState(null);

  const items = cart?.items || [];

  const total = useMemo(() => {
    const totalPrice = cart?.total_price ?? '0.00';
    const totalQuantity = cart?.total_quantity ?? 0;
    return { totalPrice, totalQuantity };
  }, [cart]);

  const refreshCart = () => {
    setError('');
    api
      .get('cart/')
      .then((res) => setCart(res.data))
      .catch(() => setError('Please log in to view your cart'));
  };

  useEffect(() => {
    refreshCart();
  }, []);

  const updateQuantity = async (itemId, quantity) => {
    setBusyItemId(itemId);
    try {
      const res = await api.patch(`cart/items/${itemId}/`, { quantity });
      setCart(res.data);
      window.dispatchEvent(new CustomEvent('cart:updated', { detail: { total_quantity: res.data?.total_quantity } }));
    } catch {
      setError('Failed to update quantity');
    } finally {
      setBusyItemId(null);
    }
  };

  const removeItem = async (itemId) => {
    setBusyItemId(itemId);
    try {
      const res = await api.delete(`cart/items/${itemId}/`);
      setCart(res.data);
      window.dispatchEvent(new CustomEvent('cart:updated', { detail: { total_quantity: res.data?.total_quantity } }));
    } catch {
      setError('Failed to remove item');
    } finally {
      setBusyItemId(null);
    }
  };

  if (error) return <ErrorState title="Cart error" message={error} />;
  if (!cart) return <LoadingIndicator />;

  return (
    <>
      <Navbar />
      <main className="screen-max-width px-8 py-24">
        <div className="form-container">
          <div className="form-heading text-3xl font-bold text-center mb-6">Your Cart</div>

          {items.length === 0 ? (
            <div className="text-[#daaa56] italic">Your cart is empty</div>
          ) : (
            <div className="space-y-4">
              {items.map((it) => (
                <div key={it.item_id} className="flex items-center gap-4 border rounded-xl p-4 bg-white">
                  <img
                    src={getImageSrc(it.item_image)}
                    alt={it.item_name}
                    className="w-20 h-20 object-cover rounded border"
                  />

                  <div className="flex-1">
                    <Link to={`/items/${it.item_id}`} className="font-semibold text-gray-900 hover:underline">
                      {it.item_name}
                    </Link>
                    <div className="text-gray-700">${it.current_price} each</div>
                    <div className="text-gray-700">Subtotal: ${it.subtotal}</div>
                  </div>

                  <div className="flex items-center gap-2">
                    <input
                      type="number"
                      min={1}
                      value={it.quantity}
                      disabled={busyItemId === it.item_id}
                      onChange={(e) => updateQuantity(it.item_id, Number(e.target.value))}
                      className="px-2 py-1 border border-gray-300 rounded w-20"
                    />
                    <button
                      type="button"
                      disabled={busyItemId === it.item_id}
                      onClick={() => removeItem(it.item_id)}
                      className="px-3 py-1 rounded-full bg-black text-[#E8C999] hover:bg-[#8E1616] hover:text-white transition-colors font-semibold"
                    >
                      Remove
                    </button>
                  </div>
                </div>
              ))}

              <div className="mt-6 flex items-center justify-between">
                <div className="text-gray-800">
                  <div>Total items: {total.totalQuantity}</div>
                  <div className="text-xl font-bold">Total: ${total.totalPrice}</div>
                </div>

                <button
                  type="button"
                  className="form-button px-6 py-3 bg-black text-[#E8C999] rounded-full hover:bg-[#8E1616] hover:text-white transition-colors font-semibold"
                  onClick={() => navigate('/checkout')}
                >
                  Checkout
                </button>
              </div>
            </div>
          )}
        </div>
      </main>
    </>
  );
};

export default Cart;
