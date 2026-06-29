import { useRef, useState } from "react";
import { getPaletteSync } from "colorthief";

const SWATCH_COUNT = 6;

export default function ColorSpine({ imageUrl }) {
  const imgRef = useRef(null);
  const [colors, setColors] = useState([]);

  function handleLoad() {
    try {
      const palette = getPaletteSync(imgRef.current, { colorCount: SWATCH_COUNT });
      setColors((palette || []).map((color) => color.css()));
    } catch {
      setColors([]);
    }
  }

  return (
    <>
      <img
        key={imageUrl}
        ref={imgRef}
        src={imageUrl}
        crossOrigin="anonymous"
        alt=""
        style={{ display: "none" }}
        onLoad={handleLoad}
        onError={() => setColors([])}
      />
      {colors.length > 0 && (
        <div className="color-spine">
          {colors.map((color, index) => (
            <div key={index} className="color-spine-band" style={{ backgroundColor: color }} />
          ))}
        </div>
      )}
    </>
  );
}
