"use client";

import { useRef, useState, type CSSProperties } from "react";
import { NotePage } from "./art";
import { ButtonAlt } from "./Button";
import { gsap } from "./gsap";
import { useSlider } from "./useSlider";

type Kind = "erd" | "os" | "math" | "net" | "chem" | "tree";

const PROJECTS: {
  title: string;
  text: string;
  bg: string;
  fg: string;
  kind: Kind;
  page: string;
  tags: [string, string, string?][];
  badge: [string, string];
}[] = [
  {
    title: "Database Management Systems",
    text: "Keys and normal forms come before joins and transactions.",
    bg: "#8e88b5",
    fg: "#fff",
    kind: "erd",
    page: "Normalization",
    tags: [["Example map", "var(--pale-green)"], ["Study order", "var(--yellow)"], ["Key topics", "#000", "#fff"]],
    badge: ["Example", "var(--green)"],
  },
  {
    title: "Operating Systems",
    text: "Processes and scheduling come before deadlocks and memory.",
    bg: "#c5e03d",
    fg: "#000",
    kind: "os",
    page: "OS layers",
    tags: [["Example map", "#000", "#fff"], ["Study order", "var(--cyan)"], ["Key topics", "var(--pale-yellow)"]],
    badge: ["Example", "var(--green)"],
  },
  {
    title: "Engineering Mathematics",
    text: "Limits and differentiation come before integrals and series.",
    bg: "#214e3b",
    fg: "#fff",
    kind: "math",
    page: "Integration",
    tags: [["Example map", "var(--pale-green)"], ["Study order", "var(--periwinkle)", "#000"], ["Key topics", "var(--yellow)"]],
    badge: ["Example", "var(--magenta)"],
  },
  {
    title: "Computer Networks",
    text: "Layers and addressing come before routing and transport.",
    bg: "#ffee00",
    fg: "#000",
    kind: "net",
    page: "OSI model",
    tags: [["Example map", "#000", "#fff"], ["Study order", "var(--pale-pink)"]],
    badge: ["Example", "var(--green)"],
  },
  {
    title: "Organic Chemistry",
    text: "Bonding and structure come before reaction mechanisms.",
    bg: "#2bb0ee",
    fg: "#000",
    kind: "chem",
    page: "Benzene",
    tags: [["Example map", "var(--pale-yellow)"], ["Study order", "#000", "#fff"], ["Key topics", "var(--pale-green)"]],
    badge: ["Example", "var(--green)"],
  },
  {
    title: "Data Structures",
    text: "Arrays and lists come before trees, graphs and heaps.",
    bg: "#ff7ad9",
    fg: "#000",
    kind: "tree",
    page: "Binary trees",
    tags: [["Example map", "#000", "#fff"], ["Study order", "var(--cyan)"], ["Key topics", "var(--pale-yellow)"]],
    badge: ["Example", "var(--green)"],
  },
];

const BASE = [
  { r: -2.4, y: 1.4 },
  { r: 3.2, y: -1.6 },
  { r: -1.8, y: 1.8 },
  { r: 2.6, y: -0.8 },
  { r: -3, y: 1.2 },
  { r: 2.2, y: -1.4 },
];

const NavArrow = () => (
  <svg className="books-slider__controls-button-icon" viewBox="0 0 18 16" fill="none" aria-hidden="true">
    <path d="M1.5 8h14M9.5 1.8 16 8l-6.5 6.2" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

export function Projects() {
  const wrap = useRef<HTMLDivElement>(null);
  const track = useRef<HTMLUListElement>(null);
  const [edge, setEdge] = useState({ atStart: true, atEnd: false });

  const api = useSlider(wrap, track, {
    lerp: 0.225,
    endPad: 32,
    onState: setEdge,
    onItem: (el, norm, i) => {
      const s = Math.sin(gsap.utils.clamp(-2, 2, norm) * 1.2);
      const b = BASE[i % BASE.length];
      el.style.setProperty("--tilt", `${(b.r + s * 3).toFixed(2)}deg`);
      el.style.setProperty("--lift", `${(b.y - Math.abs(s) * 1.1).toFixed(2)}em`);
      if (typeof window !== "undefined" && window.matchMedia("(max-width: 991px)").matches) {
        const dist = Math.abs(norm);
        el.style.setProperty("--focus-opacity", `${Math.max(0.45, 1 - dist * 0.55).toFixed(2)}`);
        el.style.setProperty("--focus-scale", `${Math.max(0.94, 1 - dist * 0.05).toFixed(2)}`);
      } else {
        el.style.setProperty("--focus-opacity", "1");
        el.style.setProperty("--focus-scale", "1");
      }
    },
  });

  return (
    <section id="projects" className="books is--bg-white" data-books-slider>
      <div className="books__inner">
        <div className="books__header u-container">
          <div className="books__text-outer">
            <div className="books__text-wrap">
              <p className="hand books__text" data-handwritten-text-inview>
                Every subject becomes its own map
              </p>
            </div>
          </div>
          <div className="books__header-content">
            <h2 className="books__title h-l">One map per subject</h2>
            <p className="books__paragraph p-regular">
              Upload a syllabus and pick a subject. Its topics are laid out as a map
              you can follow from the first idea to the last. These are examples.
            </p>
          </div>
        </div>

        <div className="books-slider" ref={wrap} data-books-slider-wrapper>
          <ul className="books-slider__list" ref={track}>
            {PROJECTS.map((p) => (
              <li
                className="books-slider__list-item"
                key={p.title}
                style={{ "--card": p.bg, "--card-fg": p.fg } as CSSProperties}
              >
                <article className="books-slider__item">
                  <div className="books-slider__item-inner">
                    <div className="books-slider__item-bg-ears" aria-hidden="true">
                      <span className="books-slider__item-bg-left-ear" />
                      <span className="books-slider__item-bg-right-ear" />
                    </div>
                    <div className="books-slider__item-bg-bottom" aria-hidden="true" />
                    <div className="books-slider__item-bg" />
                    <div className="books-slider__item-container">
                      <div className="books-slider__item-cover">
                        <NotePage title={p.page} kind={p.kind} />
                        <span className="books-slider__badge" style={{ background: p.badge[1] }}>
                          {p.badge[0]}
                        </span>
                      </div>
                      <div className="books-slider__item-content">
                        <div className="books-slider__item-text">
                          <h3 className="books-slider__item-title h-s">{p.title}</h3>
                          <p className="books-slider__item-paragraph p-small">{p.text}</p>
                        </div>
                        <ul className="books-slider__genre-list">
                          {p.tags.map(([t, bg, fg]) => (
                            <li className="tag-small" key={t} style={{ background: bg, color: fg ?? "#000" }}>
                              <span className="tag-small__text">{t}</span>
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                    <div className="books-slider__item-cta">
                      <ButtonAlt href="#upload">Map your syllabus</ButtonAlt>
                    </div>
                  </div>
                </article>
              </li>
            ))}
          </ul>
        </div>

        <div className="books-slider__controls home">
          <button
            type="button"
            className="books-slider__controls-button is--previous"
            aria-label="Previous maps"
            disabled={edge.atStart}
            onClick={() => api.current?.prev()}
          >
            <span className="books-slider__controls-button-bg" />
            <span className="books-slider__controls-button-icon-wrap"><NavArrow /></span>
          </button>
          <button
            type="button"
            className="books-slider__controls-button"
            aria-label="Next maps"
            disabled={edge.atEnd}
            onClick={() => api.current?.next()}
          >
            <span className="books-slider__controls-button-bg" />
            <span className="books-slider__controls-button-icon-wrap"><NavArrow /></span>
          </button>
        </div>
      </div>
    </section>
  );
}
