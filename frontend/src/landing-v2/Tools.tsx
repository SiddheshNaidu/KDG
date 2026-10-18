"use client";

import { useRef, useState, type ReactNode } from "react";
import { LogoMark } from "./art";
import { gsap, ScrollTrigger } from "./gsap";
import { reducedMotion, useGsap } from "./useGsap";
import { useSlider } from "./useSlider";

/* ------------------------------ mock interfaces (example data) ------------------------------ */

const MockOrder = () => (
  <div className="mock">
    <div className="mock__tabs"><span className="is-on">Unit 1</span><span>All units</span></div>
    <h4 className="mock__h">Study order</h4>
    <p className="mock__lead">Start with the topics nothing else is waiting on.</p>
    <div className="mock__label">Learn first</div>
    <ul className="mock__list">
      <li>1. Relational model</li>
      <li>2. Keys and constraints</li>
      <li>3. Normal forms</li>
    </ul>
    <div className="mock__label">Then</div>
    <div className="mock__chips"><span>Joins</span><span>Transactions</span><span>Indexing</span></div>
  </div>
);

const MockKey = () => (
  <div className="mock">
    <div className="mock__meta"><span>Key topics</span><span>Example</span></div>
    <h4 className="mock__q">Which topics unlock the most?</h4>
    {[
      ["1", "Relational model · unlocks 14", "is-right"],
      ["2", "Keys and constraints · unlocks 11", ""],
      ["3", "Normal forms · unlocks 7", ""],
      ["4", "Joins · unlocks 3", ""],
    ].map(([k, t, c]) => (
      <div key={k} className={`mock__opt ${c}`}><b>{k}</b>{t}{c && <i>★</i>}</div>
    ))}
    <div className="mock__foot"><span className="mock__pill">Key topic</span><span className="mock__small">Ranked by what each unlocks</span></div>
  </div>
);

const MockMissing = () => (
  <div className="mock mock--center">
    <div className="mock__meta"><span>Before: Relational model</span><span>Example</span></div>
    <div className="mock__flip">
      <span className="mock__small">Not taught in the syllabus</span>
      <h4 className="mock__q">Basic set theory</h4>
      <span className="mock__hint">needed for the relational model</span>
    </div>
    <div className="mock__btns"><span className="is-learn">Revise first</span><span className="is-know">Already know it</span></div>
  </div>
);

const MockPlan = () => (
  <div className="mock mock--sheet">
    <h4 className="mock__h">Plan: Normal forms</h4>
    <div className="mock__label">Learn first</div>
    <p className="mock__lead">Relational model, keys and constraints, functional dependencies</p>
    <div className="mock__label">Your goal</div>
    <p className="mock__lead">Normal forms</p>
    <div className="mock__label">Background to revise</div>
    <div className="mock__formula">Basic set theory</div>
    <div className="mock__label">Next up</div>
    <ul className="mock__list"><li>Joins</li><li>Transactions</li></ul>
  </div>
);

const MockMap = () => (
  <div className="mock">
    <div className="mock__label">Arrows</div>
    <p className="mock__lead">Keys → Normal forms → Joins → Transactions</p>
    <div className="mock__label">How to read it</div>
    <p className="mock__lead">An arrow means the topic on the left should be learned before the one on the right.</p>
    <span className="mock__small">Click any topic on the map to light up its path.</span>
  </div>
);

const MockSubjects = () => (
  <div className="mock">
    <div className="mock__label">This PDF has several subjects</div>
    <ul className="mock__list">
      <li>Engineering Mathematics</li>
      <li>Analysis of Algorithms</li>
      <li>Operating System</li>
      <li>Microprocessor</li>
    </ul>
    <span className="mock__small">Choose one to map</span>
  </div>
);

/* ---------------------------------- cards ---------------------------------- */

const TOOLS: { title: string; text: string; emoji: string; n: string; mock: ReactNode; bg: string }[] = [
  { title: "Study order", text: "Every topic in an order that makes sense, with each topic's prerequisites listed.", emoji: "📋", n: "01", mock: <MockOrder />, bg: "#fff" },
  { title: "Key topics", text: "The few topics that unlock the most of the syllabus, highlighted on the map.", emoji: "🔑", n: "02", mock: <MockKey />, bg: "var(--pale-blue)" },
  { title: "Missing prerequisites", text: "Background the syllabus assumes you already know but never teaches.", emoji: "🧩", n: "03", mock: <MockMissing />, bg: "var(--pale-pink)" },
  { title: "Plan for one topic", text: "Choose a goal and see everything to learn before it, in order.", emoji: "🎯", n: "04", mock: <MockPlan />, bg: "#fffdf4" },
  { title: "Concept map", text: "Arrows show which topic comes before which, so the structure is clear at a glance.", emoji: "🗺️", n: "05", mock: <MockMap />, bg: "var(--pale-green)" },
  { title: "Pick a subject", text: "A PDF with several subjects? Choose the one you want to map.", emoji: "📚", n: "06", mock: <MockSubjects />, bg: "var(--pale-periwinkle)" },
];

function Starburst({ n }: { n: string }) {
  const pts = Array.from({ length: 28 }, (_, i) => {
    const a = (i / 28) * Math.PI * 2;
    const r = i % 2 ? 41 : 50;
    return `${(50 + Math.cos(a) * r).toFixed(1)},${(50 + Math.sin(a) * r).toFixed(1)}`;
  }).join(" ");
  return (
    <div className="choice-slider__year" data-plop-in-item>
      <svg viewBox="0 0 100 100" aria-hidden="true">
        <polygon points={pts} fill="var(--orange)" />
      </svg>
      <span className="choice-slider__year-text h-l">{n}</span>
    </div>
  );
}

const NavArrow = () => (
  <svg className="books-slider__controls-button-icon" viewBox="0 0 18 16" fill="none" aria-hidden="true">
    <path d="M1.5 8h14M9.5 1.8 16 8l-6.5 6.2" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

const RAIN = ["🗺️", "📚", "⭐", "💡", "🧩", "📝"];

export function Tools() {
  const root = useRef<HTMLElement>(null);
  const wrap = useRef<HTMLDivElement>(null);
  const track = useRef<HTMLUListElement>(null);
  const [edge, setEdge] = useState({ atStart: true, atEnd: false });

  const api = useSlider(wrap, track, { center: true, onState: setEdge });

  // emoji rain (initEmojiRain) + sticker plop-ins
  useGsap(() => {
    if (reducedMotion()) return;
    const el = root.current!;
    const box = el.querySelector<HTMLElement>("[data-emoji-rain-container]")!;
    let running = false;
    let timeout = 0;

    const rain = () => {
      if (running) return;
      running = true;
      const h = box.offsetHeight;
      const made: HTMLElement[] = [];
      const ri = (a: number, b: number) => Math.floor(Math.random() * (b - a + 1)) + a;
      for (let i = 0; i < 40; i++) {
        const scale = Math.random() * 0.7 + 0.4;
        const rot = ri(-28, 28);
        const delay = 0.001 * ri(0, 1250);
        const speed = ri(800, 1800) * 0.001;
        const wrapEl = document.createElement("div");
        wrapEl.className = "choice__single-rain-emoji";
        wrapEl.style.left = `${ri(0, 10)}0%`;
        const child = document.createElement("div");
        child.className = "choice__rain-glyph";
        child.textContent = RAIN[ri(0, RAIN.length - 1)];
        wrapEl.appendChild(child);
        box.appendChild(wrapEl);
        made.push(wrapEl);
        gsap.fromTo(
          wrapEl,
          { y: h, xPercent: -50, rotate: 0.001, scale },
          { y: "-110%", xPercent: -50, rotate: 0.001, delay, ease: "power1.in", duration: speed },
        );
        gsap.fromTo(
          child,
          { xPercent: -25, rotate: rot },
          { xPercent: 25, rotate: -rot, ease: "power1.inOut", delay, duration: 0.8, repeat: -1, yoyo: true },
        );
      }
      timeout = window.setTimeout(() => {
        made.forEach((m) => {
          gsap.killTweensOf([m, m.firstChild]);
          m.remove();
        });
        running = false;
      }, 2750);
    };

    const st = ScrollTrigger.create({
      trigger: el,
      start: "top 80%",
      onEnter: (self) => self.direction === 1 && rain(),
    });

    // initPlopIn for the corner stickers
    el.querySelectorAll<HTMLElement>("[data-plop-in]").forEach((p) => {
      const item = p.querySelector<HTMLElement>("[data-plop-in-item]");
      if (!item) return;
      gsap.set(item, { scale: 0, rotate: -20, y: "-4em" });
      const tl = gsap.timeline({ paused: true }).to(item, {
        scale: 1,
        y: "0em",
        rotate: 11,
        duration: 0.7,
        ease: "elastic.out(1, 0.72)",
      });
      ScrollTrigger.create({ trigger: p, start: "top 80%", end: "bottom top", onEnter: () => tl.play() });
    });

    return () => {
      st.kill();
      window.clearTimeout(timeout);
      box.innerHTML = "";
    };
  }, root);

  return (
    <section ref={root} id="tools" className="choice is--outer-clip is--bg-yellow">
      <div className="choice__emoji-rain-container" data-emoji-rain-container aria-hidden="true" />
      <div className="choice__container u-container">
        <div className="choice__header">
          <div className="choice__visual" data-plop-in aria-hidden="true">
            <span className="choice__sticker" data-plop-in-item>🧠</span>
          </div>
          <div className="choice__visual choice__visual--r" data-plop-in aria-hidden="true">
            <span className="choice__sticker" data-plop-in-item>⭐</span>
          </div>
          <div className="choice__header-content">
            <div className="choice__easter-egg"><LogoMark className="egg" /></div>
            <h2 className="choice__title h-l">Everything the map shows</h2>
            <p className="choice__paragraph p-regular">
              Everything is built from the topics in your own syllabus. The
              illustrations below use example data.
            </p>
          </div>
        </div>

        <div className="choice__content">
          <div className="books-slider choice-slider" ref={wrap}>
            <ul className="choice-slider__list" ref={track}>
              {TOOLS.map((t) => (
                <li className="choice-slider__list-item" key={t.title}>
                  <article className="choice-slider__item">
                    <div className="choice-slider__item-inner">
                      <div className="books-slider__item-bg-ears choice-slider__item-bg-ears" aria-hidden="true">
                        <span className="books-slider__item-bg-left-ear" />
                        <span className="books-slider__item-bg-right-ear" />
                      </div>
                      <div className="choice-slider__item-bg" />
                      <div className="choice-slider__item-container">
                        <div className="choice-slider__item-cover" style={{ background: t.bg }}>
                          {t.mock}
                        </div>
                        <div className="choice-slider__item-text">
                          <h3 className="h-s">{t.title}</h3>
                          <p className="p-small">{t.text}</p>
                        </div>
                      </div>
                      <div className="choice-slider__author" aria-hidden="true"><span>{t.emoji}</span></div>
                      <Starburst n={t.n} />
                    </div>
                  </article>
                </li>
              ))}
            </ul>
          </div>

          <div className="books-slider__controls is--choice-slider">
            <button type="button" className="books-slider__controls-button is--previous" aria-label="Previous tool" disabled={edge.atStart} onClick={() => api.current?.prev()}>
              <span className="books-slider__controls-button-bg" />
              <span className="books-slider__controls-button-icon-wrap"><NavArrow /></span>
            </button>
            <button type="button" className="books-slider__controls-button" aria-label="Next tool" disabled={edge.atEnd} onClick={() => api.current?.next()}>
              <span className="books-slider__controls-button-bg" />
              <span className="books-slider__controls-button-icon-wrap"><NavArrow /></span>
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
