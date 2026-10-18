import type { CSSProperties } from "react";
import { LogoMark } from "./art";

type Props = {
  /** width / height / depth in em */
  w?: number;
  h?: number;
  d?: number;
  cover: string;
  spine: string;
  label?: string;
  labelColor?: string;
  className?: string;
  style?: CSSProperties;
};

/** A closed notebook built from six CSS-3D faces. Rotate the wrapper to show it off. */
export function Notebook3D({
  w = 26,
  h = 36,
  d = 3.4,
  cover,
  spine,
  label,
  labelColor = "#fff",
  className = "",
  style,
}: Props) {
  const vars = {
    "--w": `${w}em`,
    "--h": `${h}em`,
    "--d": `${d}em`,
    "--cover": cover,
    "--spine": spine,
    ...style,
  } as CSSProperties;
  return (
    <div className={`nb ${className}`} style={vars}>
      <div className="nb__face nb__front">
        <span className="nb__band" />
        <span className="nb__shade" />
        {label && (
          <span className="nb__label" style={{ color: labelColor }}>
            {label}
          </span>
        )}
        <span className="nb__sticker">
          <LogoMark />
        </span>
      </div>
      <div className="nb__face nb__back" />
      <div className="nb__face nb__left" />
      <div className="nb__face nb__right" />
      <div className="nb__face nb__top" />
      <div className="nb__face nb__bottom" />
    </div>
  );
}
