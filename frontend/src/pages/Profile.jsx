import React, { useEffect, useMemo, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import api from '../api';
import ErrorState from '../components/ErrorState';
import LoadingIndicator from '../components/ui/LoadingIndicator';
import { backendOrigin } from '../constants';
import ItemRow from '../components/items/ItemRow';

const Profile = () => {
  const { username } = useParams();
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState('');
  const [sellerItems, setSellerItems] = useState([]);
  const [orders, setOrders] = useState([]);
  const [isOwnerFromApi, setIsOwnerFromApi] = useState(false);

  const viewerUsername = localStorage.getItem('username');
  const isOwnProfile = Boolean(
    (viewerUsername && username && viewerUsername.toLowerCase() === username.toLowerCase()) ||
    isOwnerFromApi
  );

  const resolveMediaUrl = (value) => {
    if (!value) return '';
    const str = String(value);
    if (str.startsWith('http://') || str.startsWith('https://')) return str;
    if (str.startsWith('/')) return `${backendOrigin}${str}`;
    // fallback
    return `${backendOrigin}/${str}`;
  };

  const fmtDate = (value) => {
    if (!value) return '';
    const d = new Date(value);
    if (Number.isNaN(d.getTime())) return '';
    return d.toLocaleDateString();
  };

  const aggregatePurchasedItems = (orders) => {
    const map = new Map();
    for (const order of orders) {
      const createdAt = order?.created_at ? new Date(order.created_at) : null;
      const items = order?.items || [];
      for (const it of items) {
        const itemId = it?.item_id;
        if (!itemId) continue;

        const prev = map.get(itemId) || {
          item_id: itemId,
          item_name: it?.item_name || `Item #${itemId}`,
          total_quantity: 0,
          last_purchased_at: createdAt,
        };

        const qty = Number(it?.quantity || 0);
        prev.total_quantity += Number.isFinite(qty) ? qty : 0;

        if (createdAt && (!prev.last_purchased_at || createdAt > prev.last_purchased_at)) {
          prev.last_purchased_at = createdAt;
        }

        map.set(itemId, prev);
      }
    }

    return Array.from(map.values()).sort((a, b) => {
      const ad = a.last_purchased_at ? a.last_purchased_at.getTime() : 0;
      const bd = b.last_purchased_at ? b.last_purchased_at.getTime() : 0;
      return bd - ad;
    });
  };

  const purchasedItems = useMemo(() => {
    if (!orders || orders.length === 0) return [];
    return aggregatePurchasedItems(orders);
  }, [orders]);

  useEffect(() => {
    if (!username) {
      setError('No username provided.');
      return;
    }

    api
      .get(`/profile/${username}/`)
      .then((response) => {
        const data = response.data;
        setProfile(data);
        // Private serializer includes fields like marketing_emails/buyer_orders.
        setIsOwnerFromApi(Boolean(data && (Object.hasOwn(data, 'buyer_orders') || Object.hasOwn(data, 'marketing_emails'))));
      })
      .catch(() => {
        setError('Profile not found.');
        setProfile(null);
        setIsOwnerFromApi(false);
      });
  }, [username]);

  useEffect(() => {
    if (!username) return;
    // If viewing own profile, show items even if is_seller flag is off.
    if (!isOwnProfile && !profile?.is_seller) return;
    api
      .get(`items/?seller=${encodeURIComponent(username)}`)
      .then((res) => setSellerItems(res.data))
      .catch(() => setSellerItems([]));
  }, [isOwnProfile, profile?.is_seller, username]);

  useEffect(() => {
    if (!isOwnProfile) return;
    api
      .get('orders/')
      .then((res) => setOrders(res.data))
      .catch(() => setOrders([]));
  }, [isOwnProfile]);

  if (error) return <ErrorState title="Profile error" message={error} />;
  if (!profile) return <LoadingIndicator />;

  return (
    <main className="screen-max-width px-8 py-24">
      <div className="grid grid-cols-5 gap-10">
        <section className="col-span-2">
          <div className="form-container">
            {profile.image && (
              <img
                src={resolveMediaUrl(profile.image)}
                alt={`${profile.username}'s avatar`}
                className="w-32 h-32 rounded-full mb-4 border-2 border-black object-cover mx-auto"
              />
            )}

            <div className="form-heading text-3xl font-bold text-center mb-2">
              {profile.username}
            </div>

            <div className="text-center text-gray-600 mb-4">
              Joined: {fmtDate(profile.created_at) || '—'}
            </div>

            {profile.bio && (
              <p className="text-gray-700 text-center mb-4">
                <span className="font-semibold">Bio:</span> {profile.bio}
              </p>
            )}

            {profile.is_seller && (
              <div className="mt-6">
                <div className="font-semibold text-lg mb-2">Seller stats</div>
                <div className="text-gray-700">Rating: {profile.seller_rating ?? 0}</div>
                <div className="text-gray-700">Total sales: {profile.total_sales ?? 0}</div>
              </div>
            )}

            {isOwnProfile && (
              <div className="mt-6 flex justify-center">
                <Link
                  to={`/profile/${username}/edit`}
                  className="form-btn text-center"
                  style={{ width: 'fit-content' }}
                >
                  Edit profile
                </Link>
              </div>
            )}

            {isOwnProfile && (
              <div className="mt-6">
                <div className="font-semibold text-lg mb-2">Private info</div>
                <div className="text-gray-700">Phone: {profile.phone_number || '—'}</div>
                <div className="text-gray-700">Address: {profile.address || '—'}</div>
                <div className="text-gray-700">City: {profile.city || '—'}</div>
                <div className="text-gray-700">Postal: {profile.postal_code || '—'}</div>
                <div className="text-gray-700">Country: {profile.country || '—'}</div>
              </div>
            )}
          </div>
        </section>

        <section className="col-span-3">
          {(isOwnProfile || profile.is_seller) && (
            <ItemRow
              title={isOwnProfile ? 'My items' : 'Items for sale'}
              itemList={sellerItems}
              showEdit={Boolean(isOwnProfile)}
            />
          )}

          {isOwnProfile && (
            <div className="py-8">
              <h1 className="text-4xl mb-4 font-semibold">Orders placed</h1>

              {orders && orders.length > 0 ? (
                <div className="space-y-4">
                  {orders.map((o) => (
                    <div key={o.id} className="bg-white border border-gray-200 rounded-xl p-4">
                      <div className="flex justify-between items-center">
                        <Link to={`/orders/${o.id}`} className="font-semibold hover:underline">
                          Order #{o.id}
                        </Link>
                        <div className="text-gray-600">{fmtDate(o.created_at) || '—'}</div>
                      </div>
                      <div className="mt-1 text-gray-700">Status: {o.status}</div>
                      <div className="text-gray-700">Total: ${o.total_price}</div>

                      {o.items && o.items.length > 0 && (
                        <ul className="mt-3 list-disc pl-6 text-gray-700">
                          {o.items.slice(0, 5).map((it) => (
                            <li key={`${o.id}-${it.item_id}`}>x{it.quantity} {it.item_name}</li>
                          ))}
                          {o.items.length > 5 && (
                            <li>…and {o.items.length - 5} more</li>
                          )}
                        </ul>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-[#daaa56] italic">No orders to display</div>
              )}

              <div className="mt-10">
                <h2 className="text-3xl mb-4 font-semibold">Items purchased</h2>
                {purchasedItems.length > 0 ? (
                  <div className="space-y-2">
                    {purchasedItems.map((it) => (
                      <div key={it.item_id} className="flex justify-between items-center bg-white border border-gray-200 rounded-xl p-3">
                        <div>
                          <Link to={`/items/${it.item_id}`} className="font-semibold hover:underline">
                            {it.item_name}
                          </Link>
                          <div className="text-sm text-gray-600">
                            Last purchased: {it.last_purchased_at ? it.last_purchased_at.toLocaleDateString() : '—'}
                          </div>
                        </div>
                        <div className="text-gray-700">Qty: {it.total_quantity}</div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-[#daaa56] italic">No purchased items to display</div>
                )}
              </div>
            </div>
          )}
        </section>
      </div>
    </main>
  );
};

export default Profile;