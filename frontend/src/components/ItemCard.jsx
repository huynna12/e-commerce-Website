import PropTypes from "prop-types";

const ItemCard = ({ item }) => {
  return (
    <div className="border rounded shadow p-4 w-64 bg-white">
      <img
        src={item.image}
        alt={item.name}
        className="w-full h-40 object-cover rounded mb-2"
      />
      <h2 className="text-lg font-bold mb-1">{item.name}</h2>
      <p className="text-[#8E1616] font-semibold">${item.price}</p>
    </div>
  );
};

ItemCard.propTypes = {
  item: PropTypes.shape({
    name: PropTypes.string.isRequired,
    price: PropTypes.number.isRequired,
    image: PropTypes.string.isRequired,
  }).isRequired,
};

export default ItemCard;