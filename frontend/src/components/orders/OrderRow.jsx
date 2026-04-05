import PropTypes from "prop-types";
const OrderRow = ({ orders: _orders }) => {
  void _orders;
  return null;
};

OrderRow.propTypes = {
  orders: PropTypes.array.isRequired,
};

export default OrderRow;