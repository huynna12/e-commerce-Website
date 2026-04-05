import { useEffect, useMemo, useState } from "react";
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

const SellerOrderDetail = () => {
  const { orderId } = useParams();
  const [order, setOrder] = useState(null);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [cancelSelection, setCancelSelection] = useState(() => new Set());
  const [cancelMsg, setCancelMsg] = useState("");
  const [notice, setNotice] = useState("");

  const pendingRequests = useMemo(() => {
    const list = Array.isArray(order?.item_cancellation_requests) ? order.item_cancellation_requests : [];
    return list.filter((x) => x?.status === "pending");
  }, [order]);

  const load = async () => {
    const res = await api.get(`seller/orders/${orderId}/`);
    setOrder(res.data);
  };

  useEffect(() => {
    if (orderId === null || orderId === undefined || orderId === "") {
      setError("No order id provided");
      return;
    }
    setError("");
    load().catch(() => setError("Order not found (or you don't have access)"));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [orderId]);

  const decideCancellation = async (cancelRequestId, decision) => {
    setBusy(true);
    setError("");
    try {
      await api.patch(`seller/orders/${orderId}/cancel-decision/`, {
        decision,
        cancel_request_id: cancelRequestId,
      });
      await load();
    } catch (e) {
      setError(e?.response?.data?.detail || "Failed to update cancellation decision");
    } finally {
      setBusy(false);
    }
  };

  const cancelMyItems = async () => {
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const itemIds = Array.from(cancelSelection.values());
      const payload = {};
      if (itemIds.length > 0) payload.item_ids = itemIds;
      if (cancelMsg.trim()) payload.message = cancelMsg.trim();

      const res = await api.post(`seller/orders/${orderId}/cancel-items/`, payload);
      const refundNotice = res?.data?.refund_notice;
      if (refundNotice) setNotice(refundNotice);

      await load();
      setCancelSelection(new Set());
      setCancelMsg("");
    } catch (e) {
      setError(e?.response?.data?.detail || "Failed to cancel items for this order");
    } finally {
      setBusy(false);
    }
  };

  if (error) return <ErrorState title="Seller order error" message={error} />;
  if (order === null) return <LoadingIndicator />;

  return (
    <main className="screen-max-width px-8 py-24">
      <div className="form-container">
        <div className="form-heading text-3xl font-bold text-center mb-2">Order #{order.id}</div>

        <div className="text-gray-700">Buyer: {order.buyer_username}</div>
        <div className="text-gray-700">Status: {order.status}</div>
        <div className="text-gray-700">Total (whole order): ${order.total_price}</div>
        <div className="text-gray-700">Placed: {fmtDateTime(order.created_at) || "—"}</div>

        {notice ? (
          <div className="mt-3 rounded-xl border border-amber-200 bg-amber-50 p-3 text-amber-900">
            {notice}
          </div>
        ) : null}

        <div className="mt-6">
          <div className="font-semibold text-lg mb-2">Shipping</div>
          <div className="text-gray-700">City: {order.shipping_city || "—"}</div>
          <div className="text-gray-700">Country: {order.shipping_country || "—"}</div>
          <div className="text-gray-700">Address: {order.shipping_address || "—"}</div>
          <div className="text-gray-700">Postal: {order.shipping_postal_code || "—"}</div>
        </div>

        <div className="mt-6">
          <div className="font-semibold text-lg mb-2">My items in this order</div>
          {order.items && order.items.length > 0 ? (
            <ul className="list-disc pl-6 text-gray-700">
              {order.items.map((it) => (
                <li key={`${order.id}-${it.item_id}`} className="mb-1">
                  <div className="flex items-center gap-2">
                    {order.status === "processing" ? (
                      <input
                        type="checkbox"
                        checked={cancelSelection.has(it.item_id)}
                        disabled={busy || it.cancellation_status === "approved"}
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

          <div className="mt-4">
            <div className="font-semibold text-gray-800">Seller actions</div>
            {order.status === "processing" ? (
              <div className="space-y-3 mt-2">
                <div className="text-sm text-gray-600">
                  Select item(s) above and cancel them (or leave unselected to cancel all your items in this order).
                </div>
                <textarea
                  className="form-input"
                  placeholder="Reason (optional)"
                  rows={2}
                  value={cancelMsg}
                  onChange={(e) => setCancelMsg(e.target.value)}
                />
                <button className="form-btn" type="button" onClick={cancelMyItems} disabled={busy}>
                  {busy ? "Working…" : "Cancel my item(s)"}
                </button>
              </div>
            ) : (
              <div className="text-gray-700">Order is not editable in current status.</div>
            )}
          </div>
        </div>

        <div className="mt-8">
          <div className="font-semibold text-lg mb-2">Cancellation requests</div>

          {pendingRequests.length > 0 ? (
            <div className="space-y-3">
              {pendingRequests.map((cr) => (
                <div key={cr.id} className="border border-gray-200 rounded-xl p-3 bg-white">
                  <div className="text-gray-700">
                    Item: <span className="font-semibold">{cr.item_name}</span> (x{cr.quantity})
                  </div>
                  <div className="text-gray-700">Status: {cr.status}</div>
                  {cr.message ? <div className="text-gray-600 text-sm">Message: {cr.message}</div> : null}

                  <div className="mt-3 flex gap-3">
                    <button
                      className="form-btn"
                      type="button"
                      disabled={busy}
                      onClick={() => decideCancellation(cr.id, "approve")}
                    >
                      Approve
                    </button>
                    <button
                      className="form-btn bg-white text-black border border-black"
                      type="button"
                      disabled={busy}
                      onClick={() => decideCancellation(cr.id, "deny")}
                    >
                      Deny
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-gray-600 text-sm">No pending cancellation requests.</div>
          )}
        </div>
      </div>
    </main>
  );
};

export default SellerOrderDetail;
