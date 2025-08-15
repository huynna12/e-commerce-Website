import { useState } from "react";
import api from "../api";

const AddItem = () => {
    const [data, setData] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const res = api.get(`items/create/`,{ 
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(postBody)
            });

            if (!res.ok){
                throw new Error("Response was not ok");
            }

            const jsonRes = await res.json();
            console.log('POST request successful', jsonRes);
        } catch (error){
            console.error('POST request failed', error);
        }
    }

    const updateData = (name, value) => {
        setData({...data, [name]: value});
    }

    return (
        <form onSubmit={handleSubmit}>
            <input
                type="text"
                placeholder="Item name"
                name="item_name"
                value={item_name}
                onChange={e => updateData(e.target.name, e.target.value)}
            />
            <input
                type="number"
                placeholder="Price"
                name="item_price"
                value={item_price}
                onChange={e => updateData(e.target.name, e.target.value)}
            />

            <input
                type="text"
                placeholder="Summary"
                name="item_summary"
                value={item_summary}
                onChange={e => updateData(e.target.name, e.target.value)}
            />

            <input
                type="text"
                placeholder="Description"
                name="item_desc"
                value={item_desc}
                onChange={e => updateData(e.target.name, e.target.value)}
            />

            <input
                type="number"
                placeholder="Quantity"
                name="item_quantity"
                value={item_quantity}
                onChange={e => updateData(e.target.name, e.target.value)}
            />

            <input
                type="number"
                placeholder="Price"
                name="item_price"
                value={item_price}
                onChange={e => updateData(e.target.name, e.target.value)}
            />

            <input
                type="number"
                placeholder="Price"
                name="item_price"
                value={item_price}
                onChange={e => updateData(e.target.name, e.target.value)}
            />

            {/* Add more fields as needed */}
            <button type="submit">Add Item</button>
        </form>
    );
};

export default AddItem;