import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api";

const CATEGORY_OPTIONS = [
  { value: "", label: "Select category" },
  { value: "electronics", label: "Electronics & Tech" },
  { value: "clothing", label: "Clothing & Fashion" },
  { value: "home_kitchen", label: "Home & Kitchen" },
  { value: "books_media", label: "Books & Media" },
  { value: "sports_outdoors", label: "Sports & Outdoors" },
  { value: "beauty_personal", label: "Beauty & Personal Care" },
  { value: "toys_games", label: "Toys & Games" },
  { value: "automotive", label: "Automotive & Tools" },
  { value: "health_wellness", label: "Health & Wellness" },
  { value: "jewelry_accessories", label: "Jewelry & Accessories" },
  { value: "baby_kids", label: "Baby & Kids" },
  { value: "pet_supplies", label: "Pet Supplies" },
  { value: "office_supplies", label: "Office & School Supplies" },
  { value: "collectibles", label: "Collectibles & Art" },
  { value: "other", label: "Other" },
];

const CONDITION_OPTIONS = [
  { value: "", label: "Select condition" },
  { value: "new", label: "New" },
  { value: "used", label: "Used" },
  { value: "open_box", label: "Open Box" },
  { value: "refurbished", label: "Refurbished" },
];

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
  is_available: false,
  is_on_sale: false,
  is_digital: false,
  sale_price: "",
  sale_start_date: getCurrentDateTimeLocal(),
  sale_end_date: "",
};

const AddItem = () => {
  const [data, setData] = useState(initialData);
  const [images, setImages] = useState([]);
  const [imageUrls, setImageUrls] = useState([""]);
  const [errorMsg, setErrorMsg] = useState("");
  const navigate = useNavigate();

  // Improved: Prevent duplicate files and allow removal
  const handleImageChange = (e) => {
    const newFiles = Array.from(e.target.files);
    setImages(prev => {
      // Prevent duplicates by name and size
      const allFiles = [...prev, ...newFiles];
      const uniqueFiles = [];
      const seen = new Set();
      for (const file of allFiles) {
        const key = file.name + file.size;
        if (!seen.has(key)) {
          uniqueFiles.push(file);
          seen.add(key);
        }
      }
      return uniqueFiles;
    });
    // Reset input value so user can re-upload same file if needed
    e.target.value = "";
  };

  const handleRemoveImage = (idx) => {
    setImages(images.filter((_, i) => i !== idx));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMsg("");
    const formData = new FormData();
    Object.entries(data).forEach(([key, value]) => {
      formData.append(key, value);
    });
    for (const image of images) {
      formData.append("images", image);
    }
    imageUrls.forEach(url => {
      if (url.trim()) {
        formData.append("image_urls", url.trim());
      }
    });

    // For debugging
    for (const pair of formData.entries()) {
      console.log("formData:", pair[0], pair[1]);
    }

    try {
      const res = await api.post(`items/`, formData);
      if (res.data?.id) {
        navigate(`/items/${res.data.id}`);
      }
    } catch (error) {
      if (error.response?.data) {
        setErrorMsg(
          typeof error.response.data === "object"
            ? Object.entries(error.response.data)
                .map(([field, msg]) => `${field}: ${Array.isArray(msg) ? msg.join(", ") : msg}`)
                .join("\n")
            : error.response.data
        ); 
      } else {
        setErrorMsg("POST request failed");
      }
      console.error('POST request failed', error);
    }
  };

  const updateData = (name, value) => {
    if (name === "item_price" || name === "sale_price") {
      value = value ? Number(value).toFixed(2) : "";
    }
    setData({ ...data, [name]: value });
  };

  const handleImageUrlChange = (idx, value) => {
    const newUrls = [...imageUrls];
    newUrls[idx] = value;
    setImageUrls(newUrls);
  };

  const addImageUrlField = () => {
    setImageUrls([...imageUrls, ""]);
  };

  const removeImageUrlField = (idx) => {
    setImageUrls(imageUrls.filter((_, i) => i !== idx));
  };

  return (
    <div className="flex items-center justify-center min-h-screen">
      <form
        onSubmit={handleSubmit}
        className="form-container mx-48 my-16"
        encType="multipart/form-data"
        autoComplete="on"
      >
        <h1 className="form-heading">Add item</h1>

        {errorMsg && (
          <div className="mb-4 text-red-600 whitespace-pre-line">{errorMsg}</div>
        )}

        <label className="label" htmlFor="images">Images</label>
        <input
          type="file"
          id="images"
          name="images"
          multiple
          className="form-input"
          onChange={handleImageChange}
        />

        {/* Show selected files with cross sign for removal */}
        {images.length > 0 && (
          <ul className="mb-4">
            {images.map((file, idx) => (
              <li key={idx} className="flex items-center mb-1">
                <span className="mr-2">{file.name}</span>
                <button
                  type="button"
                  className="text-[#8E1616] hover:bg-[#f8d7da] rounded px-2 text-xl"
                  onClick={() => handleRemoveImage(idx)}
                  aria-label="Remove file"
                  style={{ minWidth: "2rem", minHeight: "2rem" }}
                >
                  &#10005;
                </button>
              </li>
            ))}
          </ul>
        )}

        <label className="label" htmlFor="image_url_0">Image URLs</label>
        {imageUrls.map((url, idx) => (
          <div key={idx} className="flex mb-2 items-center">
            <input
              type="text"
              id={`image_url_${idx}`}
              className="form-input flex-1"
              placeholder="Image URL"
              value={url}
              onChange={e => handleImageUrlChange(idx, e.target.value)}
              autoComplete="url"
            />
            <button
              type="button"
              className="ml-3 mb-4 px-3 py-1 rounded text-xl bg-transparent text-[#8E1616] hover:bg-[#f8d7da] flex items-center justify-center"
              onClick={() => removeImageUrlField(idx)}
              disabled={imageUrls.length === 1}
              aria-label="Remove"
              style={{ minWidth: "2rem", minHeight: "2rem" }}
            >
              &#10005;
            </button>
          </div>
        ))}
        <button
          type="button"
          className="mb-4 px-3 py-1 bg-black text-white rounded"
          onClick={addImageUrlField}
        >
          Add another URL
        </button>

        <label className="label" htmlFor="item_name">Name*</label>
        <input
          type="text"
          id="item_name"
          className="form-input"
          placeholder="Item name"
          name="item_name"
          value={data.item_name}
          onChange={e => updateData(e.target.name, e.target.value)}
          required
          autoComplete="name"
        />

        <label className="label" htmlFor="item_price">Price*</label>
        <input
          type="number"
          id="item_price"
          step="0.01"
          className="form-input"
          placeholder="Price"
          name="item_price"
          value={data.item_price}
          onChange={e => updateData(e.target.name, e.target.value)}
          required
          autoComplete="off"
        />

        <label className="label" htmlFor="item_summary">Summary</label>
        <input
          type="text"
          id="item_summary"
          className="form-input"
          placeholder="Summary"
          name="item_summary"
          value={data.item_summary}
          onChange={e => updateData(e.target.name, e.target.value)}
          autoComplete="off"
        />

        <label className="label" htmlFor="item_desc">Detail description</label>
        <input
          type="text"
          id="item_desc"
          className="form-input"
          placeholder="Description"
          name="item_desc"
          value={data.item_desc}
          onChange={e => updateData(e.target.name, e.target.value)}
          autoComplete="off"
        />

        <label className="label" htmlFor="item_quantity">Quantity</label>
        <input
          type="number"
          id="item_quantity"
          className="form-input"
          placeholder="Quantity"
          name="item_quantity"
          value={data.item_quantity}
          onChange={e => updateData(e.target.name, e.target.value)}
          autoComplete="off"
        />

        <label className="label" htmlFor="item_sku">SKU</label>
        <input
          type="text"
          id="item_sku"
          className="form-input"
          name="item_sku"
          value={data.item_sku}
          onChange={e => updateData(e.target.name, e.target.value)}
          autoComplete="off"
        />

        <label className="label" htmlFor="item_condition">Condition</label>
        <select
          id="item_condition"
          className="form-input"
          name="item_condition"
          value={data.item_condition}
          onChange={e => updateData(e.target.name, e.target.value)}
        >
          {CONDITION_OPTIONS.map(opt => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>

        <label className="label" htmlFor="item_origin">Origin</label>
        <input
          type="text"
          id="item_origin"
          className="form-input"
          placeholder="Where it comes from?"
          name="item_origin"
          value={data.item_origin}
          onChange={e => updateData(e.target.name, e.target.value)}
          autoComplete="off"
        />

        <label className="label" htmlFor="item_category">Category</label>
        <select
          id="item_category"
          className="form-input"
          name="item_category"
          value={data.item_category}
          onChange={e => updateData(e.target.name, e.target.value)}
        >
          {CATEGORY_OPTIONS.map(opt => (
            <option key={opt.value} value={opt.value}>{opt.label}</option>
          ))}
        </select>

        <label className="label" htmlFor="custom_category">Custom Category</label>
        <input
          type="text"
          id="custom_category"
          className="form-input"
          placeholder="Custom category"
          name="custom_category"
          value={data.custom_category}
          onChange={e => updateData(e.target.name, e.target.value)}
          autoComplete="off"
        />

        <label className="label flex items-center" htmlFor="is_available">
          <input
            type="checkbox"
            id="is_available"
            name="is_available"
            checked={data.is_available}
            onChange={e => updateData(e.target.name, e.target.checked)}
            className="mr-2"
          /><span>Available</span>
        </label>

        <label className="label flex items-center" htmlFor="is_on_sale">
          <input
            type="checkbox"
            id="is_on_sale"
            name="is_on_sale"
            checked={data.is_on_sale}
            onChange={e => updateData(e.target.name, e.target.checked)}
            className="mr-2"
          /><span>On sale</span>
        </label>

        <label className="label flex items-center" htmlFor="is_digital">
          <input
            type="checkbox"
            id="is_digital"
            name="is_digital"
            checked={data.is_digital}
            onChange={e => updateData(e.target.name, e.target.checked)}
            className="mr-2"
          /><span>Digital Item</span>
        </label>

        <label className="label" htmlFor="sale_price">Sale Price</label>
        <input
          type="number"
          id="sale_price"
          step="0.01"
          className="form-input"
          placeholder="Sale price"
          name="sale_price"
          value={data.sale_price}
          onChange={e => updateData(e.target.name, e.target.value)}
          autoComplete="off"
        />

        <label className="label" htmlFor="sale_start_date">Sale Start Date</label>
        <input
          type="datetime-local"
          id="sale_start_date"
          className="form-input"
          name="sale_start_date"
          value={data.sale_start_date}
          onChange={e => updateData(e.target.name, e.target.value)}
        />

        <label className="label" htmlFor="sale_end_date">Sale End Date</label>
        <input
          type="datetime-local"
          id="sale_end_date"
          className="form-input"
          name="sale_end_date"
          value={data.sale_end_date}
          onChange={e => updateData(e.target.name, e.target.value)}
        />

        <button
          type="submit"
          className="form-btn"
        >
          Add Item
        </button>
      </form>
    </div>
  );
};

export default AddItem;