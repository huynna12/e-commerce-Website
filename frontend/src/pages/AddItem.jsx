import { useMemo } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";
import ItemForm from "../components/forms/ItemForm";

const getCurrentDateTimeLocal = () => {
  const now = new Date();
  now.setSeconds(0, 0);
  const pad = n => String(n).padStart(2, "0");
  return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}T${pad(now.getHours())}:${pad(now.getMinutes())}`;
};

const initialData = {
  item_name: "",
  item_price: "",
  item_summary: "",
  item_desc: "",
  item_quantity: "",
  item_sku: "",
  item_condition: "",
  item_origin: "",
  item_category: "",
  custom_category: "",
  is_available: true,
  is_on_sale: false,
  is_digital: false,
  sale_price: "",
  sale_start_date: getCurrentDateTimeLocal(),
  sale_end_date: "",
};

const AddItem = () => {
  const navigate = useNavigate();

  const handleSubmit = useMemo(() => {
    return async (formData) => {
      const res = await api.post("items/", formData);
      if (res.data?.id) navigate(`/items/${res.data.id}`);
    };
  }, [navigate]);

  return (
    <ItemForm
      initialData={initialData}
      title="Add item"
      submitLabel="Add Item"
      onSubmit={handleSubmit}
    />
  );
};

export default AddItem;