import PropTypes from "prop-types";
import { useState } from "react";
import { DEFAULT_IMAGE } from "../../constants";

const ImagesDisplayRow = ({ images }) => {
  const [showAll, setShowAll] = useState(false);
  const [previewIdx, setPreviewIdx] = useState(null);

  if (!images || images.length === 0) return null;

  const getImageSrc = img => {
    if (!img) return DEFAULT_IMAGE;
    if (img.image_url && img.image_url !== "null" && img.image_url !== "") return img.image_url;
    if (img.image_file && img.image_file !== "null" && img.image_file !== "") return img.image_file;
    if (typeof img === "string" && img !== "null" && img !== "") return img;
    return DEFAULT_IMAGE;
  };
  const displayImages = showAll ? images : images.slice(0, 5);

  return (
    <>
      <div className="flex gap-2 flex-wrap mt-2">
        {displayImages.map((img, idx) => {
          const image_src = getImageSrc(img);
          return (
            <button
              key={image_src || idx}
              type="button"
              className="p-0 border-none bg-transparent max-w-[80px] rounded cursor-pointer"
              style={{ objectFit: "cover", height: 80 }}
              onClick={() => setPreviewIdx(idx)}
              aria-label={`Preview media-${idx + 1}`}
            >
              <img
                src={image_src}
                alt={`media-${idx + 1}`}
                className="max-w-[80px] rounded"
                style={{ objectFit: "cover", height: 80 }}
              />
            </button>
          );
        })}
        {images.length > 5 && !showAll && (
          <button
            className="max-w-[80px] h-[80px] rounded bg-gray-200 flex items-center justify-center font-semibold text-gray-700"
            style={{ minWidth: 80 }}
            onClick={() => setShowAll(true)}
            aria-label="Show more images"
          >
            +{images.length - 5} more
          </button>
        )}
      </div>
      {previewIdx !== null && (
        <div className="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50">
          <div className="relative bg-white rounded shadow-lg p-4 flex flex-col items-center">
            <button
              className="absolute top-2 right-2 text-2xl text-[#8E1616] hover:bg-[#f8d7da] rounded px-2"
              onClick={() => setPreviewIdx(null)}
              aria-label="Close preview"
              style={{ minWidth: "2rem", minHeight: "2rem" }}
            >
              &#10005;
            </button>
            <img
              src={getImageSrc(images[previewIdx])}
              alt={`Preview media-${previewIdx + 1}`}
              className="max-w-[80vw] max-h-[80vh] rounded"
              style={{ objectFit: "contain" }}
            />
          </div>
        </div>
      )}
    </>
  );
};

ImagesDisplayRow.propTypes = {
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

export default ImagesDisplayRow;