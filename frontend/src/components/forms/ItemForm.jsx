import { useEffect, useMemo, useState } from "react";

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

const buildFormData = (data, images, imageUrls) => {
	const formData = new FormData();
	Object.entries(data).forEach(([key, value]) => {
		// Keep empty strings so DRF can treat them as blank/null where appropriate.
		formData.append(key, value ?? "");
	});

	for (const image of images) {
		formData.append("images", image);
	}

	imageUrls.forEach((url) => {
		const trimmed = String(url || "").trim();
		if (trimmed) formData.append("image_urls", trimmed);
	});

	return formData;
};

const formatApiErrors = (err) => {
	const data = err?.response?.data;
	if (!data) return "Request failed";
	if (typeof data === "string") return data;
	if (typeof data !== "object") return "Request failed";

	return Object.entries(data)
		.map(([field, msg]) => `${field}: ${Array.isArray(msg) ? msg.join(", ") : msg}`)
		.join("\n");
};

const ItemForm = ({
	initialData,
	title = "Item",
	submitLabel = "Save",
	onSubmit,
}) => {
	const [data, setData] = useState(initialData);
	const [images, setImages] = useState([]);
	const [imageUrls, setImageUrls] = useState([""]);
	const [errorMsg, setErrorMsg] = useState("");
	const [isSubmitting, setIsSubmitting] = useState(false);

	useEffect(() => {
		setData(initialData);
	}, [initialData]);

	const isOtherCategory = useMemo(() => data?.item_category === "other", [data?.item_category]);

	const updateData = (name, value) => {
		if (name === "item_price" || name === "sale_price") {
			value = value ? Number(value).toFixed(2) : "";
		}

		const next = { ...data, [name]: value };

		// If user switches away from "other", clear custom_category.
		if (name === "item_category" && value !== "other") {
			next.custom_category = "";
		}

		// If sale is unchecked, clear sale fields.
		if (name === "is_on_sale" && value === false) {
			next.sale_price = "";
			next.sale_start_date = "";
			next.sale_end_date = "";
		}

		setData(next);
	};

	const handleImageChange = (e) => {
		const newFiles = Array.from(e.target.files);
		setImages((prev) => {
			const allFiles = [...prev, ...newFiles];
			const uniqueFiles = [];
			const seen = new Set();
			for (const file of allFiles) {
				const key = `${file.name}:${file.size}`;
				if (!seen.has(key)) {
					uniqueFiles.push(file);
					seen.add(key);
				}
			}
			return uniqueFiles;
		});
		e.target.value = "";
	};

	const handleRemoveImage = (idx) => {
		setImages(images.filter((_, i) => i !== idx));
	};

	const handleImageUrlChange = (idx, value) => {
		const next = [...imageUrls];
		next[idx] = value;
		setImageUrls(next);
	};

	const addImageUrlField = () => setImageUrls([...imageUrls, ""]);
	const removeImageUrlField = (idx) => setImageUrls(imageUrls.filter((_, i) => i !== idx));

	const handleSubmit = async (e) => {
		e.preventDefault();
		setErrorMsg("");

		// Mirror backend validation: custom_category is required for "other".
		if (data.item_category === "other" && !String(data.custom_category || "").trim()) {
			setErrorMsg("custom_category: Custom category required when 'Other' selected");
			return;
		}

		const formData = buildFormData(data, images, imageUrls);

		try {
			setIsSubmitting(true);
			await onSubmit(formData);
		} catch (err) {
			setErrorMsg(formatApiErrors(err));
			// Keep console output for debugging.
			console.error(err);
		} finally {
			setIsSubmitting(false);
		}
	};

	return (
		<div className="flex items-center justify-center min-h-screen">
			<form
				onSubmit={handleSubmit}
				className="form-container mx-48 my-16"
				encType="multipart/form-data"
				autoComplete="on"
			>
				<h1 className="form-heading">{title}</h1>

				{errorMsg && <div className="mb-4 text-red-600 whitespace-pre-line">{errorMsg}</div>}

				<label className="label" htmlFor="images">Images</label>
				<input
					type="file"
					id="images"
					name="images"
					multiple
					className="form-input"
					onChange={handleImageChange}
				/>

				{images.length > 0 && (
					<ul className="mb-4">
						{images.map((file, idx) => (
							<li key={`${file.name}:${file.size}`} className="flex items-center mb-1">
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
							onChange={(e) => handleImageUrlChange(idx, e.target.value)}
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
					onChange={(e) => updateData(e.target.name, e.target.value)}
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
					onChange={(e) => updateData(e.target.name, e.target.value)}
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
					onChange={(e) => updateData(e.target.name, e.target.value)}
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
					onChange={(e) => updateData(e.target.name, e.target.value)}
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
					onChange={(e) => updateData(e.target.name, e.target.value)}
					autoComplete="off"
				/>

				<label className="label" htmlFor="item_sku">SKU</label>
				<input
					type="text"
					id="item_sku"
					className="form-input"
					name="item_sku"
					value={data.item_sku}
					onChange={(e) => updateData(e.target.name, e.target.value)}
					autoComplete="off"
				/>

				<label className="label" htmlFor="item_condition">Condition</label>
				<select
					id="item_condition"
					className="form-input"
					name="item_condition"
					value={data.item_condition}
					onChange={(e) => updateData(e.target.name, e.target.value)}
				>
					{CONDITION_OPTIONS.map((opt) => (
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
					onChange={(e) => updateData(e.target.name, e.target.value)}
					autoComplete="off"
				/>

				<label className="label" htmlFor="item_category">Category</label>
				<select
					id="item_category"
					className="form-input"
					name="item_category"
					value={data.item_category}
					onChange={(e) => updateData(e.target.name, e.target.value)}
				>
					{CATEGORY_OPTIONS.map((opt) => (
						<option key={opt.value} value={opt.value}>{opt.label}</option>
					))}
				</select>

				{isOtherCategory && (
					<>
						<label className="label" htmlFor="custom_category">Custom Category*</label>
						<input
							type="text"
							id="custom_category"
							className="form-input"
							placeholder="Custom category"
							name="custom_category"
							value={data.custom_category}
							onChange={(e) => updateData(e.target.name, e.target.value)}
							autoComplete="off"
							required
						/>
					</>
				)}

				{!isOtherCategory && (
					<>
						<label className="label" htmlFor="custom_category">Custom Category</label>
						<input
							type="text"
							id="custom_category"
							className="form-input"
							placeholder="Custom category"
							name="custom_category"
							value={data.custom_category}
							onChange={(e) => updateData(e.target.name, e.target.value)}
							autoComplete="off"
							disabled
						/>
					</>
				)}

				<label className="label flex items-center" htmlFor="is_available">
					<input
						type="checkbox"
						id="is_available"
						name="is_available"
						checked={data.is_available}
						onChange={(e) => updateData(e.target.name, e.target.checked)}
						className="mr-2"
					/><span>Available</span>
				</label>

				<label className="label flex items-center" htmlFor="is_on_sale">
					<input
						type="checkbox"
						id="is_on_sale"
						name="is_on_sale"
						checked={data.is_on_sale}
						onChange={(e) => updateData(e.target.name, e.target.checked)}
						className="mr-2"
					/><span>On sale</span>
				</label>

				<label className="label flex items-center" htmlFor="is_digital">
					<input
						type="checkbox"
						id="is_digital"
						name="is_digital"
						checked={data.is_digital}
						onChange={(e) => updateData(e.target.name, e.target.checked)}
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
					onChange={(e) => updateData(e.target.name, e.target.value)}
					autoComplete="off"
					disabled={!data.is_on_sale}
				/>

				<label className="label" htmlFor="sale_start_date">Sale Start Date</label>
				<input
					type="datetime-local"
					id="sale_start_date"
					className="form-input"
					name="sale_start_date"
					value={data.sale_start_date}
					onChange={(e) => updateData(e.target.name, e.target.value)}
					disabled={!data.is_on_sale}
				/>

				<label className="label" htmlFor="sale_end_date">Sale End Date</label>
				<input
					type="datetime-local"
					id="sale_end_date"
					className="form-input"
					name="sale_end_date"
					value={data.sale_end_date}
					onChange={(e) => updateData(e.target.name, e.target.value)}
					disabled={!data.is_on_sale}
				/>

				<button
					type="submit"
					className="form-btn"
					disabled={isSubmitting}
				>
					{isSubmitting ? "Saving..." : submitLabel}
				</button>
			</form>
		</div>
	);
};

export default ItemForm;
