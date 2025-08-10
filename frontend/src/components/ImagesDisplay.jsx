import PropTypes from "prop-types";

const ImagesDisplay = ({ images }) => {
  if (!images || images.length === 0) return null;

  return (
    <div className="flex gap-2 flex-wrap mt-2">
      {images.map((img, idx) => {
        const image_src = img.image_url ? img.image_url : img.image_file;
      
        return (
          <img
            key={image_src || idx}
            src={image_src}
            alt={`media-${idx + 1}`}
            className="max-w-[80px] rounded"
            style={{ objectFit: "cover", height: 80 }}
          />
        );
      })}
    </div>
  );
};

ImagesDisplay.propTypes = {
  images: PropTypes.arrayOf(PropTypes.string).isRequired,
};

export default ImagesDisplay;