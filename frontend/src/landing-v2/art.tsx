import type { CSSProperties, ReactNode } from "react";

/* -------------------------------------------------------------------------- */
/*  Logo                                                                      */
/* -------------------------------------------------------------------------- */

export function LogoMark({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 100 100"
      fill="none"
      aria-hidden="true"
    >
      <circle
        cx="50"
        cy="50"
        r="44"
        stroke="currentColor"
        strokeWidth="7"
        strokeLinecap="round"
      />
      {/* pen nib */}
      <path
        fill="currentColor"
        fillRule="evenodd"
        d="M37 22h26l5 25-18 31-18-31Zm13 17.5a4.5 4.5 0 1 0 .01 0ZM48.7 46h2.6v28h-2.6Z"
      />
      <path
        d="M30 24c2-5 6-8 12-9"
        stroke="currentColor"
        strokeWidth="0"
      />
    </svg>
  );
}

export function LogoFull({ className }: { className?: string }) {
  return (
    <span className={`logo ${className ?? ""}`}>
      <LogoMark className="logo__mark" />
      <span className="logo__word">KDG</span>
    </span>
  );
}

/* -------------------------------------------------------------------------- */
/*  Section background blobs (breathing — see initBackgroundAnimation)        */
/* -------------------------------------------------------------------------- */

const BLOBS: Record<string, { vb: string; paths: { d: string; color?: string }[] }> = {
  hero: {
    vb: "0 0 1920 1400",
    paths: [
      {
        d: "M470 1400C430 1230 590 1110 640 950C700 760 520 600 690 430C850 270 1090 360 1230 190C1330 70 1560 50 1700 130C1850 215 1930 340 1960 520L1960 1400Z",
      },
      {
        d: "M860 1400C880 1250 1000 1190 990 1070C980 950 1100 890 1220 930C1360 980 1390 870 1500 830C1620 790 1740 860 1770 990C1800 1120 1710 1260 1790 1400Z",
        color: "var(--orange)",
      },
    ],
  },
  flow: {
    vb: "0 0 1920 760",
    paths: [
      {
        d: "M-40 760C20 560 -20 400 150 360C320 320 380 470 560 420C760 360 700 160 920 130C1150 100 1200 300 1420 280C1640 260 1700 100 1960 140L1960 760Z",
      },
    ],
  },
  faq: {
    vb: "0 0 1920 1100",
    paths: [
      {
        d: "M-40 220C140 60 330 160 400 330C470 500 330 640 480 780C640 930 900 800 1010 900C1120 1000 1050 1110 1010 1160L-40 1160Z",
      },
      {
        d: "M1100 -40C1260 80 1360 200 1520 220C1700 240 1780 130 1960 170L1960 -40Z",
      },
      {
        d: "M1520 1160C1500 1010 1640 930 1710 820C1790 700 1700 560 1830 470C1900 420 1950 440 1980 460L1980 1160Z",
      },
    ],
  },
  benefits: {
    vb: "0 0 1920 1080",
    paths: [
      {
        d: "M-40 360C100 220 310 260 400 420C490 580 380 700 520 820C660 940 900 860 1020 970C1100 1040 1090 1100 1090 1120L-40 1120Z",
      },
      {
        d: "M1400 -40C1480 160 1620 180 1700 330C1780 480 1680 640 1810 740C1880 790 1940 780 1980 770L1980 -40Z",
      },
    ],
  },
  badge: {
    vb: "0 0 1920 400",
    paths: [
      {
        d: "M-40 210C110 90 280 130 380 230C480 330 620 340 740 250C860 160 990 90 1130 170C1270 250 1360 320 1520 260C1680 200 1790 90 1980 170L1980 420L-40 420Z",
      },
    ],
  },
  menu: {
    vb: "0 0 1000 700",
    paths: [
      {
        d: "M-20 700C60 520 220 560 300 440C380 320 520 400 640 300C760 200 900 260 1020 160L1020 720Z",
      },
    ],
  },
};

export function BlobBg({
  variant,
  animate = true,
  className,
  small,
  style,
}: {
  variant: keyof typeof BLOBS | string;
  animate?: boolean;
  className?: string;
  small?: boolean;
  style?: CSSProperties;
}) {
  const b = BLOBS[variant] ?? BLOBS.hero;
  return (
    <svg
      className={className}
      viewBox={b.vb}
      preserveAspectRatio="xMidYMid slice"
      fill="none"
      aria-hidden="true"
      style={style}
      {...(animate ? { "data-background-animation": "" } : {})}
      {...(small ? { "data-background-animation-small": "" } : {})}
    >
      {b.paths.map((p, i) => (
        <path
          key={i}
          d={p.d}
          fill={p.color ?? "currentColor"}
          stroke={p.color ?? "currentColor"}
          strokeLinejoin="round"
          strokeWidth="0"
        />
      ))}
    </svg>
  );
}

/* -------------------------------------------------------------------------- */
/*  Step illustrations                                                        */
/* -------------------------------------------------------------------------- */

const line: CSSProperties = {
  stroke: "#000",
  strokeWidth: 4,
  strokeLinecap: "round",
  strokeLinejoin: "round",
};

const sparkle = (x: number, y: number, s = 1, fill = "#ffd24a") => (
  <path
    transform={`translate(${x} ${y}) scale(${s})`}
    d="M0-14 4-4 14 0 4 4 0 14-4 4-14 0-4-4Z"
    fill={fill}
    style={line}
  />
);

export function StepArt({ n }: { n: 1 | 2 | 3 | 4 }) {
  let body: ReactNode = null;
  if (n === 1) {
    body = (
      <>
        <g transform="rotate(-7 120 140)">
          <rect x="50" y="46" width="132" height="176" rx="12" fill="#fff" style={line} />
          <path d="M76 92c10-18 20-18 30 0s20 18 30 0" fill="none" style={line} />
          <path d="M76 132h86M76 158h60M76 184h74" fill="none" style={line} />
          <path d="M76 204h40" fill="none" style={{ ...line, stroke: "#ff008c" }} />
        </g>
        <g transform="rotate(32 218 150)">
          <rect x="206" y="64" width="24" height="116" rx="8" fill="#ff008c" style={line} />
          <path d="M206 182 218 220 230 182Z" fill="#fff" style={line} />
          <path d="M213 206 218 220 223 206Z" fill="#000" />
          <path d="M206 92h24" fill="none" style={line} />
        </g>
        {sparkle(250, 62, 1)}
        {sparkle(36, 40, 0.7, "#fff")}
      </>
    );
  } else if (n === 2) {
    body = (
      <>
        <g transform="rotate(-5 110 190)">
          <rect x="52" y="148" width="116" height="76" rx="10" fill="#fff" style={line} />
          <path d="M70 176h70M70 196h46" fill="none" style={line} />
        </g>
        <g transform="rotate(4 125 130)">
          <rect x="64" y="104" width="116" height="76" rx="10" fill="#ffdbfd" style={line} />
          <path d="M82 132h70M82 152h46" fill="none" style={line} />
        </g>
        <g transform="rotate(-3 150 84)">
          <rect x="84" y="52" width="116" height="76" rx="10" fill="#fff" style={line} />
          <path d="M102 80h70M102 100h46" fill="none" style={line} />
        </g>
        <circle cx="58" cy="60" r="17" fill="#ffd24a" style={line} />
        <text x="58" y="67" textAnchor="middle" fontSize="20" fontWeight="800" fill="#000">1</text>
        <path d="M214 92c34-12 52 22 22 52" fill="none" style={line} />
        <path d="M226 144l12-8-2 15" fill="none" style={line} />
        {sparkle(250, 56, 0.9, "#fff")}
      </>
    );
  } else if (n === 3) {
    // a small dependency map: arrows lead from earlier topics to later ones
    body = (
      <>
        <path d="M70 72H170M70 72V172M170 72L224 172M70 172H224" fill="none" style={line} />
        {[
          [70, 72],
          [170, 72],
          [70, 172],
          [224, 172],
        ].map(([x, y], i) => (
          <circle key={i} cx={x} cy={y} r="24" fill={i === 3 ? "#ffd24a" : "#fff"} style={line} />
        ))}
        {sparkle(250, 52, 0.9, "#ff008c")}
        {sparkle(40, 220, 0.7, "#fff")}
      </>
    );
  } else {
    // a goal flag with a tick: the plan for one chosen topic
    body = (
      <>
        <path d="M86 216V52" fill="none" style={{ ...line, strokeWidth: 8 }} />
        <path d="M88 56H192L170 90L192 124H88Z" fill="#ff008c" style={line} />
        <circle cx="216" cy="192" r="34" fill="#2de124" style={line} />
        <path d="M200 192l12 12 22-26" fill="none" style={{ ...line, strokeWidth: 7 }} />
        {sparkle(52, 40, 0.8, "#fff")}
        {sparkle(262, 80, 0.7, "#ffd24a")}
      </>
    );
  }
  return (
    <svg viewBox="0 0 300 260" fill="none" aria-hidden="true" className="flow__card-img">
      {body}
    </svg>
  );
}

/* -------------------------------------------------------------------------- */
/*  Mini note pages (cover of project cards)                                  */
/* -------------------------------------------------------------------------- */

const pen = "#2b3a9f";
const penLine: CSSProperties = {
  stroke: pen,
  strokeWidth: 3,
  strokeLinecap: "round",
  strokeLinejoin: "round",
  fill: "none",
};

function Doodle({ kind }: { kind: string }) {
  switch (kind) {
    case "erd":
      return (
        <g>
          <rect x="34" y="190" width="92" height="52" rx="6" style={penLine} />
          <rect x="190" y="190" width="92" height="52" rx="6" style={penLine} />
          <path d="M126 216h64" style={penLine} />
          <path d="M158 216 148 208M158 216 148 224" style={penLine} />
          <path d="M80 242v44M236 242v44" style={penLine} />
          <path d="M158 300 196 326 158 352 120 326Z" style={penLine} />
          <rect x="102" y="372" width="116" height="48" rx="6" style={penLine} />
          <path d="M60 210h44M60 224h30M214 210h44M214 224h30" style={{ ...penLine, strokeWidth: 2 }} />
          <path d="M158 352v20" style={penLine} />
        </g>
      );
    case "os":
      return (
        <g>
          {[0, 1, 2, 3].map((i) => (
            <rect key={i} x={50 + i * 8} y={190 + i * 56} width={220 - i * 16} height="44" rx="8" style={penLine} />
          ))}
          <path d="M160 234v12M160 290v12M160 346v12" style={penLine} />
          <path d="M70 212h60M74 268h80M78 324h70M82 380h90" style={{ ...penLine, strokeWidth: 2 }} />
        </g>
      );
    case "math":
      return (
        <g>
          <path d="M44 400V210M44 400h232" style={penLine} />
          <path d="M44 380C100 380 110 230 170 250S240 320 276 220" style={{ ...penLine, stroke: "#ff008c" }} />
          <path d="M120 400v-130M200 400v-100" style={{ ...penLine, strokeDasharray: "4 8" }} />
          <text x="62" y="214" fontSize="34" fontFamily="var(--font-rq-hand), cursive" fill={pen}>∫ f(x) dx</text>
        </g>
      );
    case "net":
      return (
        <g>
          {[[70, 220], [170, 200], [260, 250], [120, 320], [230, 350], [70, 400]].map(([x, y], i) => (
            <circle key={i} cx={x} cy={y} r="16" style={penLine} />
          ))}
          <path d="M84 216 154 204M186 206 246 244M254 266 238 336M170 214 128 306M136 322 216 346M110 334 82 386M214 358 88 396" style={penLine} />
        </g>
      );
    case "chem":
      return (
        <g>
          <path d="M160 200 205 226V278L160 304 115 278V226Z" style={penLine} />
          <path d="M160 214 193 232V272L160 292 127 272V232Z" style={{ ...penLine, strokeWidth: 2, strokeDasharray: "3 7" }} />
          <path d="M205 226 250 200M115 278 70 304M160 304v50" style={penLine} />
          <path d="M70 304h-30M250 200l30 2" style={penLine} />
          <text x="150" y="388" fontSize="34" fontFamily="var(--font-rq-hand), cursive" fill={pen}>C₆H₆</text>
        </g>
      );
    default:
      return (
        <g>
          <circle cx="160" cy="214" r="22" style={penLine} />
          <circle cx="96" cy="300" r="22" style={penLine} />
          <circle cx="224" cy="300" r="22" style={penLine} />
          <circle cx="62" cy="388" r="20" style={penLine} />
          <circle cx="130" cy="388" r="20" style={penLine} />
          <path d="M146 232 108 282M174 232 212 282M84 318 68 370M108 318 124 370" style={penLine} />
        </g>
      );
  }
}

export function NotePage({
  title,
  kind,
}: {
  title: string;
  kind: "erd" | "os" | "math" | "net" | "chem" | "tree";
}) {
  return (
    <div className="notepage">
      <svg viewBox="0 0 320 493" aria-hidden="true">
        <rect width="320" height="493" fill="#fffdf4" />
        {Array.from({ length: 15 }, (_, i) => (
          <path key={i} d={`M0 ${74 + i * 28}H320`} stroke="#c9d6f2" strokeWidth="1.5" />
        ))}
        <path d="M44 0V493" stroke="#f5a3b8" strokeWidth="2" />
        <Doodle kind={kind} />
        <path d="M60 126C110 132 190 120 270 128" style={{ ...penLine, stroke: "#ff008c" }} />
      </svg>
      <span className="notepage__title">{title}</span>
    </div>
  );
}

/* -------------------------------------------------------------------------- */
/*  Subject cards (hover pop-ups on the pink section)                         */
/* -------------------------------------------------------------------------- */

const SUBJECT_COLORS = [
  "#ffd24a",
  "#1ce8ed",
  "#9982de",
  "#ff9d00",
  "#69fe6f",
  "#ffdbfd",
  "#a4f6f8",
  "#fbbe63",
];

const ink: CSSProperties = {
  stroke: "#000",
  strokeWidth: 5,
  strokeLinecap: "round",
  strokeLinejoin: "round",
  fill: "none",
};

function SubjectIcon({ kind }: { kind: string }) {
  switch (kind) {
    case "engineering":
      return (
        <g>
          <circle cx="50" cy="50" r="17" style={ink} />
          <circle cx="50" cy="50" r="6" style={{ ...ink, fill: "#fff" }} />
          {Array.from({ length: 8 }, (_, i) => (
            <rect key={i} x="45" y="12" width="10" height="13" rx="2" style={{ ...ink, fill: "#fff" }} transform={`rotate(${i * 45} 50 50)`} />
          ))}
        </g>
      );
    case "medicine":
      return (
        <g>
          <path d="M38 14h24v24h24v24H62v24H38V62H14V38h24Z" style={{ ...ink, fill: "#fff" }} />
          <path d="M20 50h14l6-10 10 22 6-12h14" style={{ ...ink, stroke: "#ff008c" }} />
        </g>
      );
    case "law":
      return (
        <g>
          <path d="M50 14v70M30 84h40M20 28h60" style={ink} />
          <path d="M20 28 8 56a14 8 0 0 0 24 0ZM80 28 68 56a14 8 0 0 0 24 0Z" style={{ ...ink, fill: "#fff" }} />
        </g>
      );
    case "commerce":
      return (
        <g>
          <rect x="14" y="56" width="16" height="28" style={{ ...ink, fill: "#fff" }} />
          <rect x="42" y="40" width="16" height="44" style={{ ...ink, fill: "#fff" }} />
          <rect x="70" y="22" width="16" height="62" style={{ ...ink, fill: "#fff" }} />
          <path d="M10 40 38 22 56 30 88 8M74 8h14v14" style={{ ...ink, stroke: "#ff008c" }} />
        </g>
      );
    case "mathematics":
      return (
        <text x="50" y="76" textAnchor="middle" fontSize="92" fontWeight="800" fontFamily="var(--font-rq-display)" fill="#000">
          Σ
        </text>
      );
    case "physics":
      return (
        <g>
          {[0, 60, 120].map((r) => (
            <ellipse key={r} cx="50" cy="50" rx="40" ry="15" style={ink} transform={`rotate(${r} 50 50)`} />
          ))}
          <circle cx="50" cy="50" r="8" style={{ ...ink, fill: "#ff008c" }} />
        </g>
      );
    case "chemistry":
      return (
        <g>
          <path d="M38 12h24M42 12v26L20 80a6 6 0 0 0 5 9h50a6 6 0 0 0 5-9L58 38V12" style={{ ...ink, fill: "#fff" }} />
          <path d="M30 66h40" style={ink} />
          <circle cx="46" cy="76" r="3" style={ink} />
          <circle cx="58" cy="72" r="2.4" style={ink} />
        </g>
      );
    case "biology":
      return (
        <g>
          <path d="M16 78C12 40 40 14 86 14c4 42-22 70-70 64Z" style={{ ...ink, fill: "#fff" }} />
          <path d="M16 78 62 36M40 56l-1-18M52 46l16 2" style={ink} />
        </g>
      );
    case "history":
      return (
        <g>
          <path d="M12 34 50 12 88 34Z" style={{ ...ink, fill: "#fff" }} />
          {[24, 44, 64].map((x) => (
            <rect key={x} x={x} y="38" width="12" height="38" style={{ ...ink, fill: "#fff" }} />
          ))}
          <path d="M10 84h80" style={ink} />
        </g>
      );
    case "literature":
      return (
        <g>
          <path d="M84 12C52 14 30 36 22 72l8 4C44 62 64 44 84 12Z" style={{ ...ink, fill: "#fff" }} />
          <path d="M22 72 12 90M40 56l14 2" style={ink} />
        </g>
      );
    default:
      return (
        <g>
          <path d="M50 10 58 40 88 50 58 60 50 90 42 60 12 50 42 40Z" style={{ ...ink, fill: "#fff" }} />
          <path d="M82 14v14M75 21h14" style={ink} />
        </g>
      );
  }
}

export function SubjectCard({
  kind,
  label,
  variant = 0,
  index = 0,
}: {
  kind: string;
  label: string;
  variant?: number;
  index?: number;
}) {
  const bg = SUBJECT_COLORS[(index + variant * 2) % SUBJECT_COLORS.length];
  return (
    <div className="subject-card" style={{ background: bg }}>
      <svg viewBox="0 0 100 100" aria-hidden="true" style={{ transform: `rotate(${(variant - 1.5) * 6}deg)` }}>
        <SubjectIcon kind={kind} />
      </svg>
      <span className="subject-card__label">{label}</span>
    </div>
  );
}
