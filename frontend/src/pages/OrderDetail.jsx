import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import api from "../api";
import ErrorState from "../components/ErrorState";
import LoadingIndicator from "../components/ui/LoadingIndicator";

const fmtDateTime = (value) => {
  if (!value) return "";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return "";
  return d.toLocaleString();
};

const OrderDetail = () => {
  const { orderId } = useParams();
  const [order, setOrder] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!orderId) {
      setError("No order id provided");
      return;
    }

    setError("");
    api
      .get(`orders/${orderId}/`)
      .then((res) => setOrder(res.data))
      .catch(() => setError("Order not found (or you don't have access)") );
  }, [orderId]);

  if (error) return <ErrorState title="Order error" message={error} />;
  if (!order) return <LoadingIndicator />;

  return (
    <main className="screen-max-width px-8 py-24">
      <div className="form-container">
        <div className="form-heading text-3xl font-bold text-center mb-2">Order #{order.id}</div>

        <div className="text-gray-700">Status: {order.status}</div>
        <div className="text-gray-700">Total: ${order.total_price}</div>
        <div className="text-gray-700">Placed: {fmtDateTime(order.created_at) || "—"}</div>

        <div className="mt-6">
          <div className="font-semibold text-lg mb-2">Items</div>
          {order.items && order.items.length > 0 ? (
            <ul className="list-disc pl-6 text-gray-700">
              {order.items.map((it) => (
                <li key={`${order.id}-${it.item_id}`}>x{it.quantity} {it.item_name} — ${it.price}</li>
              ))}
            </ul>
          ) : (
            <div className="text-[#daaa56] italic">No items to display</div>
          )}
        </div>
      </div>
    </main>
  );
};

export default OrderDetail;
