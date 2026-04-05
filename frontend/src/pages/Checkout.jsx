import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

import api from '../api';
import Navbar from '../components/layout/Navbar';
import LoadingIndicator from '../components/ui/LoadingIndicator';
import ErrorState from '../components/ErrorState';

const Checkout = () => {
  const navigate = useNavigate();

  const [cart, setCart] = useState(null);
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  const [form, setForm] = useState({
    shipping_address: '',
    shipping_city: '',
    shipping_postal_code: '',
    shipping_country: '',
    payment_method: 'mock',
    notes: '',
  });

  useEffect(() => {
    setError('');
    api
      .get('cart/')
      .then((res) => setCart(res.data))
      .catch(() => setError('Please log in to checkout'));
  }, []);

  const onChange = (e) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const placeOrder = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError('');

    try {
      const res = await api.post('checkout/', form);
      globalThis.dispatchEvent(new CustomEvent('cart:updated', { detail: { total_quantity: 0 } }));
      navigate(`/orders/${res.data.id}`);
    } catch (err) {
      const msg = err?.response?.data?.detail || 'Checkout failed';
      setError(msg);
    } finally {
      setBusy(false);
    }
  };

  if (error) return <ErrorState title="Checkout error" message={error} />;
  if (!cart) return <LoadingIndicator />;

  const isEmpty = !cart.items || cart.items.length === 0;

  return (
    <>
      <Navbar />
      <main className="screen-max-width px-8 py-24">
        <div className="form-container">
          <div className="form-heading text-3xl font-bold text-center mb-6">Checkout</div>

          {isEmpty ? (
            <div className="text-[#daaa56] italic">Your cart is empty</div>
          ) : (
            <>
              <div className="text-gray-700 mb-6">
                <div>Total items: {cart.total_quantity}</div>
                <div className="text-xl font-bold">Total: ${cart.total_price}</div>
              </div>

              <form onSubmit={placeOrder} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="shipping_address">
                    Shipping address
                  </label>
                  <input
                    id="shipping_address"
                    name="shipping_address"
                    value={form.shipping_address}
                    onChange={onChange}
                    className="form-input"
                    placeholder="123 Main St"
                    required
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="shipping_city">
                      City
                    </label>
                    <input
                      id="shipping_city"
                      name="shipping_city"
                      value={form.shipping_city}
                      onChange={onChange}
                      className="form-input"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="shipping_postal_code">
                      Postal code
                    </label>
                    <input
                      id="shipping_postal_code"
                      name="shipping_postal_code"
                      value={form.shipping_postal_code}
                      onChange={onChange}
                      className="form-input"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="shipping_country">
                    Country
                  </label>
                  <input
                    id="shipping_country"
                    name="shipping_country"
                    value={form.shipping_country}
                    onChange={onChange}
                    className="form-input"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="payment_method">
                    Payment method
                  </label>
                  <select
                    id="payment_method"
                    name="payment_method"
                    value={form.payment_method}
                    onChange={onChange}
                    className="form-input"
                  >
                    <option value="mock">Mock payment (demo)</option>
                    <option value="credit_card">Credit card (placeholder)</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1" htmlFor="notes">
                    Notes (optional)
                  </label>
                  <textarea
                    id="notes"
                    name="notes"
                    value={form.notes}
                    onChange={onChange}
                    className="form-input"
                    rows={3}
                  />
                </div>

                <button
                  type="submit"
                  disabled={busy}
                  className="form-button w-full py-3 bg-black text-[#E8C999] rounded-full hover:bg-[#8E1616] hover:text-white transition-colors font-semibold disabled:opacity-50"
                >
                  {busy ? 'Placing order…' : 'Place order'}
                </button>
              </form>
            </>
          )}
        </div>
      </main>
    </>
  );
};

export default Checkout;
