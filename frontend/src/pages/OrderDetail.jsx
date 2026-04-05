import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../api";
import ErrorState from "../components/ErrorState";
import LoadingIndicator from "../components/ui/LoadingIndicator";

const fmtDateTime = (value) => {
  if (value === null || value === undefined || value === "") return "";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return "";
  return d.toLocaleString();
};

const OrderDetail = () => {
  const { orderId } = useParams();
  const [order, setOrder] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [editShipping, setEditShipping] = useState(false);
  const [shippingForm, setShippingForm] = useState({
    shipping_address: "",
    shipping_city: "",
    shipping_postal_code: "",
    shipping_country: "",
    notes: "",
  });
  const [cancelMsg, setCancelMsg] = useState("");
  const [cancelSelection, setCancelSelection] = useState(() => new Set());

  useEffect(() => {
    if (orderId === null || orderId === undefined || orderId === "") {
      setError("No order id provided");
      return;
    }

    setError("");
    api
      .get(`orders/${orderId}/`)
      .then((res) => {
        setOrder(res.data);
        setShippingForm({
          shipping_address: res.data?.shipping_address || "",
          shipping_city: res.data?.shipping_city || "",
          shipping_postal_code: res.data?.shipping_postal_code || "",
          shipping_country: res.data?.shipping_country || "",
          notes: res.data?.notes || "",
        });
      })
      .catch(() => setError("Order not found (or you don't have access)") );
  }, [orderId]);

  const reload = async () => {
    const res = await api.get(`orders/${orderId}/`);
    setOrder(res.data);
    setShippingForm({
      shipping_address: res.data?.shipping_address || "",
      shipping_city: res.data?.shipping_city || "",
      shipping_postal_code: res.data?.shipping_postal_code || "",
      shipping_country: res.data?.shipping_country || "",
      notes: res.data?.notes || "",
    });
  };

  const saveShipping = async () => {
    setBusy(true);
    setError("");
    try {
      await api.patch(`orders/${orderId}/shipping/`, shippingForm);
      await reload();
      setEditShipping(false);
    } catch (e) {
      setError(e?.response?.data?.detail || "Failed to update shipping details");
    } finally {
      setBusy(false);
    }
  };

  const requestCancel = async () => {
    setBusy(true);
    setError("");
    try {
      const itemIds = Array.from(cancelSelection.values());
      if (itemIds.length === 0) {
        setError("Select at least one item to cancel");
        return;
      }

      await api.post(`orders/${orderId}/cancel-items/`, { item_ids: itemIds, message: cancelMsg });
      await reload();
    } catch (e) {
      setError(e?.response?.data?.detail || "Failed to request cancellation");
    } finally {
      setBusy(false);
    }
  };

  if (error) return <ErrorState title="Order error" message={error} />;
  if (order === null) return <LoadingIndicator />;

  return (
    <main className="screen-max-width px-8 py-24">
      <div className="form-container">
        <div className="form-heading text-3xl font-bold text-center mb-2">Order #{order.id}</div>

        <div className="text-gray-700">Status: {order.status}</div>
        <div className="text-gray-700">Total: ${order.total_price}</div>
        <div className="text-gray-700">Placed: {fmtDateTime(order.created_at) || "—"}</div>

        {order.refund_notice ? (
          <div className="mt-3 rounded-xl border border-amber-200 bg-amber-50 p-3 text-amber-900">
            {order.refund_notice}
          </div>
        ) : null}

        <div className="mt-6">
          <div className="font-semibold text-lg mb-2">Shipping</div>
          {editShipping ? (
            <div className="space-y-3">
              <input
                className="form-input"
                placeholder="Shipping address"
                value={shippingForm.shipping_address}
                onChange={(e) => setShippingForm((p) => ({ ...p, shipping_address: e.target.value }))}
              />
              <input
                className="form-input"
                placeholder="City"
                value={shippingForm.shipping_city}
                onChange={(e) => setShippingForm((p) => ({ ...p, shipping_city: e.target.value }))}
              />
              <input
                className="form-input"
                placeholder="Postal code"
                value={shippingForm.shipping_postal_code}
                onChange={(e) => setShippingForm((p) => ({ ...p, shipping_postal_code: e.target.value }))}
              />
              <input
                className="form-input"
                placeholder="Country"
                value={shippingForm.shipping_country}
                onChange={(e) => setShippingForm((p) => ({ ...p, shipping_country: e.target.value }))}
              />
              <textarea
                className="form-input"
                placeholder="Notes (optional)"
                rows={3}
                value={shippingForm.notes}
                onChange={(e) => setShippingForm((p) => ({ ...p, notes: e.target.value }))}
              />

              <div className="flex gap-3">
                <button className="form-btn" type="button" onClick={saveShipping} disabled={busy}>
                  {busy ? "Saving…" : "Save"}
                </button>
                <button
                  className="form-btn bg-white text-black border border-black"
                  type="button"
                  onClick={() => {
                    setEditShipping(false);
                    setShippingForm({
                      shipping_address: order.shipping_address || "",
                      shipping_city: order.shipping_city || "",
                      shipping_postal_code: order.shipping_postal_code || "",
                      shipping_country: order.shipping_country || "",
                      notes: order.notes || "",
                    });
                  }}
                  disabled={busy}
                >
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            <>
              <div className="text-gray-700">Address: {order.shipping_address || "—"}</div>
              <div className="text-gray-700">City: {order.shipping_city || "—"}</div>
              <div className="text-gray-700">Postal: {order.shipping_postal_code || "—"}</div>
              <div className="text-gray-700">Country: {order.shipping_country || "—"}</div>
              {order.notes ? <div className="text-gray-700">Notes: {order.notes}</div> : null}

              {order.status === "processing" && (
                <button
                  className="form-btn mt-4"
                  type="button"
                  onClick={() => setEditShipping(true)}
                  disabled={busy}
                >
                  Edit shipping details
                </button>
              )}
            </>
          )}
        </div>

        <div className="mt-6">
          <div className="font-semibold text-lg mb-2">Items</div>
          {order.items && order.items.length > 0 ? (
            <ul className="list-disc pl-6 text-gray-700">
              {order.items.map((it) => (
                <li key={`${order.id}-${it.item_id}`} className="mb-1">
                  <div className="flex items-center gap-2">
                    {order.status === "processing" ? (
                      <input
                        type="checkbox"
                        checked={cancelSelection.has(it.item_id)}
                        disabled={busy || it.cancellation_status === 'approved'}
                        onChange={(e) => {
                          setCancelSelection((prev) => {
                            const next = new Set(prev);
                            if (e.target.checked) next.add(it.item_id);
                            else next.delete(it.item_id);
                            return next;
                          });
                        }}
                      />
                    ) : null}
                    <span>
                      x{it.quantity} {it.item_name} — ${it.price}
                      {it.seller_username ? (
                        <span className="text-gray-500"> (seller: {it.seller_username})</span>
                      ) : null}
                      {it.cancellation_status ? (
                        <span className="text-gray-500"> — cancel: {it.cancellation_status}</span>
                      ) : null}
                    </span>
                  </div>
                </li>
              ))}
            </ul>
          ) : (
            <div className="text-[#daaa56] italic">No items to display</div>
          )}
        </div>

        <div className="mt-6">
          <div className="font-semibold text-lg mb-2">Cancellation</div>
          {order.status === "processing" ? (
            <div className="space-y-3">
              <div className="text-gray-600 text-sm">
                Select item(s) above, then send the request.
              </div>
              <textarea
                className="form-input"
                placeholder="Message to seller(s) (optional)"
                rows={3}
                value={cancelMsg}
                onChange={(e) => setCancelMsg(e.target.value)}
              />
              <button className="form-btn" type="button" onClick={requestCancel} disabled={busy}>
                {busy ? "Sending…" : "Request cancellation"}
              </button>
            </div>
          ) : (
            <div className="text-gray-700">Order is not cancellable in current status.</div>
          )}

          {Array.isArray(order.item_cancellation_requests) && order.item_cancellation_requests.length > 0 ? (
            <div className="mt-4 space-y-2">
              {order.item_cancellation_requests.map((cr) => (
                <div key={cr.id} className="border border-gray-200 rounded-xl p-3 bg-white">
                  <div className="text-gray-700">
                    Item: <span className="font-semibold">{cr.item_name}</span> (x{cr.quantity})
                  </div>
                  <div className="text-gray-700">Seller: {cr.seller_username}</div>
                  <div className="text-gray-700">Status: {cr.status}</div>
                  {cr.decided_by_username ? (
                    <div className="text-gray-600 text-sm">Decided by: {cr.decided_by_username}</div>
                  ) : null}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-gray-600 text-sm mt-2">No cancellation requests yet.</div>
          )}
        </div>

      </div>
    </main>
  );
};

export default OrderDetail;
