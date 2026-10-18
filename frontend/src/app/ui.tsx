import { useEffect, useLayoutEffect, useRef, useState } from "react";
import { tweenNumber } from "./motion";

/** One soft colour per syllabus unit (used on the map, the order list and the cards). */
export const UNIT_COLORS = ["#ffd24a", "#7ee9ee", "#feb6fa", "#b9a8f0", "#fbbe63", "#8af08f"];
export const unitColor = (unit: number) => UNIT_COLORS[(Math.max(1, unit) - 1) % UNIT_COLORS.length];

export const Check = ({ size = 14 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 16 16" fill="none" aria-hidden="true">
    <path d="M3 8.5l3.2 3.2L13 4.8" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

export const Star = ({ size = 14 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 16 16" aria-hidden="true">
    <path fill="currentColor" d="M8 1.2l2 4.3 4.7.6-3.4 3.2.9 4.6L8 11.5 3.8 13.9l.9-4.6L1.3 6.1 6 5.5z" />
  </svg>
);

export const Arrow = ({ size = 16 }: { size?: number }) => (
  <svg width={size} height={size} viewBox="0 0 16 16" fill="none" aria-hidden="true">
    <path d="M2 8h11M8.5 3.5L13 8l-4.5 4.5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

type TabItem<T extends string> = { id: T; label: string };

/** Pill tabs with a sliding highlight. */
export function Tabs<T extends string>({ items, value, onChange }: { items: TabItem<T>[]; value: T; onChange: (v: T) => void }) {
  const wrap = useRef<HTMLDivElement>(null);
  const [box, setBox] = useState({ left: 0, width: 0 });

  useLayoutEffect(() => {
    const measure = () => {
      const btn = wrap.current?.querySelector<HTMLElement>(`[data-tab="${value}"]`);
      if (btn) setBox({ left: btn.offsetLeft, width: btn.offsetWidth });
    };
    measure();
    // fonts load after first paint and change the button widths
    document.fonts?.ready.then(measure);
    const ro = new ResizeObserver(measure);
    if (wrap.current) ro.observe(wrap.current);
    wrap.current?.querySelectorAll("button").forEach((b) => ro.observe(b));
    return () => ro.disconnect();
  }, [value, items]);

  return (
    <div className="kd-tabs" ref={wrap} role="tablist">
      <span className="kd-tabs__pill" style={{ transform: `translateX(${box.left}px)`, width: box.width }} />
      {items.map((t) => (
        <button key={t.id} data-tab={t.id} role="tab" aria-selected={value === t.id} className={value === t.id ? "on" : ""} onClick={() => onChange(t.id)}>
          {t.label}
        </button>
      ))}
    </div>
  );
}

/** Circular progress with a counting number. */
export function Ring({ value, label = "learned" }: { value: number; label?: string }) {
  const num = useRef<HTMLElement>(null);
  const prev = useRef(0);
  const r = 34;
  const c = 2 * Math.PI * r;

  useEffect(() => {
    tweenNumber(num.current, prev.current, value, "%");
    prev.current = value;
  }, [value]);

  return (
    <div className="kd-ring" title="Topics you marked as learned">
      <svg viewBox="0 0 80 80" aria-hidden="true">
        <circle cx="40" cy="40" r={r} className="kd-ring__bg" />
        <circle cx="40" cy="40" r={r} className="kd-ring__fg" strokeDasharray={c} strokeDashoffset={c * (1 - Math.min(100, value) / 100)} />
      </svg>
      <div className="kd-ring__text">
        <b ref={num}>0%</b>
        <span>{label}</span>
      </div>
    </div>
  );
}

/** Little decorative map used on the sign-in and upload screens. */
export function MapArt({ className = "" }: { className?: string }) {
  const nodes = [
    { x: 14, y: 30, c: "#ffd24a" }, { x: 14, y: 110, c: "#ffd24a" }, { x: 130, y: 20, c: "#7ee9ee" },
    { x: 130, y: 85, c: "#feb6fa" }, { x: 130, y: 150, c: "#7ee9ee" }, { x: 246, y: 60, c: "#b9a8f0" },
    { x: 246, y: 130, c: "#8af08f" },
  ];
  const links = [[0, 2], [0, 3], [1, 3], [1, 4], [2, 5], [3, 5], [3, 6], [4, 6]];
  return (
    <svg className={`kd-mapart ${className}`} viewBox="0 0 370 210" aria-hidden="true">
      {links.map(([a, b], i) => (
        <path key={i} className="kd-mapart__edge" style={{ animationDelay: `${i * 0.12}s` }}
          d={`M${nodes[a].x + 96} ${nodes[a].y + 16} C ${nodes[a].x + 124} ${nodes[a].y + 16}, ${nodes[b].x - 28} ${nodes[b].y + 16}, ${nodes[b].x} ${nodes[b].y + 16}`} />
      ))}
      {nodes.map((n, i) => (
        <g key={i} className="kd-mapart__node" style={{ animationDelay: `${0.3 + i * 0.1}s` }}>
          <rect x={n.x} y={n.y} width="96" height="32" rx="10" fill="#fff" stroke="#1b1340" strokeWidth="2.5" />
          <rect x={n.x} y={n.y} width="10" height="32" rx="5" fill={n.c} stroke="#1b1340" strokeWidth="2.5" />
          <rect x={n.x + 20} y={n.y + 10} width="58" height="5" rx="2.5" fill="#1b1340" opacity=".75" />
          <rect x={n.x + 20} y={n.y + 19} width="36" height="4" rx="2" fill="#1b1340" opacity=".25" />
        </g>
      ))}
    </svg>
  );
}
