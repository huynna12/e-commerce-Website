import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../api";
import ItemForm from "../components/forms/ItemForm";

const toDateTimeLocal = (value) => {
  if (!value) return "";
  const d = new Date(value);
  if (Number.isNaN(d.getTime())) return "";
  d.setSeconds(0, 0);
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
};

const UpdateItem = () => {
  const { itemId } = useParams();
  const navigate = useNavigate();

  const [initialData, setInitialData] = useState(null);
  const [loadError, setLoadError] = useState("");

  useEffect(() => {
    setLoadError("");
    api
      .get(`items/${itemId}/`)
      .then((res) => {
        const item = res.data;
        setInitialData({
          item_name: item?.item_name ?? "",
          item_price: item?.item_price ?? "",
          item_summary: item?.item_summary ?? "",
          item_desc: item?.item_desc ?? "",
          item_quantity: item?.item_quantity ?? "",
          item_sku: item?.item_sku ?? "",
          item_condition: item?.item_condition ?? "",
          item_origin: item?.item_origin ?? "",
          item_category: item?.item_category ?? "",
          custom_category: item?.custom_category ?? "",
          is_available: Boolean(item?.is_available),
          is_on_sale: Boolean(item?.is_on_sale),
          is_digital: Boolean(item?.is_digital),
          sale_price: item?.sale_price ?? "",
          sale_start_date: toDateTimeLocal(item?.sale_start_date),
          sale_end_date: toDateTimeLocal(item?.sale_end_date),
        });
      })
      .catch(() => setLoadError("Failed to load item for editing"));
  }, [itemId]);

  const handleSubmit = useMemo(() => {
    return async (formData) => {
      await api.patch(`items/${itemId}/`, formData);
      navigate(`/items/${itemId}`);
    };
  }, [itemId, navigate]);

  if (loadError) return <div className="text-center py-10 text-lg">{loadError}</div>;
  if (!initialData) return <div className="text-center py-10 text-lg">Loading ...</div>;

  return (
    <ItemForm
      initialData={initialData}
      title="Update item"
      submitLabel="Update Item"
      onSubmit={handleSubmit}
    />
  );
};

export default UpdateItem;
