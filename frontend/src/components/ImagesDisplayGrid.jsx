import PropTypes from "prop-types";
import { useState } from "react";
import { DEFAULT_IMAGE } from "../constants";

const ImagesDisplayGrid = ({ images }) => {
  const [selectedIdx, setSelectedIdx] = useState(0);

  if (!images || images.length === 0) return null;

  const getImageSrc = img => {
    if (!img) return DEFAULT_IMAGE;
    if (typeof img === "string" && img !== "null" && img !== "") return img;
    if (img.image_url && img.image_url !== "null" && img.image_url !== "") return img.image_url;
    if (img.image_file && img.image_file !== "null" && img.image_file !== "") return img.image_file;
    return DEFAULT_IMAGE;
  };

  return (
    <div className="grid grid-cols-8 gap-8 w-full">
      {/* Left column: thumbnails, now smaller */}
      <div className="flex flex-col col-span-1 items-center">
        {images.filter(Boolean).map((img, idx) => (
          <button
            key={getImageSrc(img) || idx}
            type="button"
            className="mb-2 focus:outline-none"
            onClick={() => setSelectedIdx(idx)}
            aria-label={`Select thumbnail ${idx + 1}`}
            tabIndex={0}
            style={{ background: "none", border: "none", padding: 0 }}
          >
            <img
              src={getImageSrc(img)}
              alt={`Thumbnail ${idx + 1}`}
              className={`w-15 h-15 object-cover rounded border cursor-pointer ${selectedIdx === idx ? "border-[#E8C999] border-2" : "border-gray-300"}`}
            />
          </button>
        ))}
      </div>
      {/* Right: main image, fills parent */}
      <div className="flex items-center justify-center col-span-7 w-full h-full">
        <img
          src={getImageSrc(images[selectedIdx])}
          alt={`Product preview ${selectedIdx + 1}`}
          className="w-full h-full max-h-[500px] object-contain rounded shadow border-2 border-black"
          style={{ aspectRatio: "1/1" }}
        />
      </div>
    </div>
  );
};

ImagesDisplayGrid.propTypes = {
  images: PropTypes.arrayOf(
    PropTypes.oneOfType([
      PropTypes.shape({
        image_url: PropTypes.string,
        image_file: PropTypes.string,
      }),
      PropTypes.string,
    ])
  ).isRequired,
};

export default ImagesDisplayGrid;