"use client";

import { useId, useState } from "react";
import { BlobBg, LogoMark } from "./art";
import { ButtonAlt } from "./Button";

const FAQ = [
  {
    q: "What do I upload?",
    a: "A Mumbai University NEP syllabus as a PDF. It can hold one subject or a whole semester. If there are several subjects, you choose the one to map.",
  },
  {
    q: "What do I get back?",
    a: "A map of the subject's topics with arrows showing what comes before what, a study order, the key topics that unlock the most, and the background the syllabus assumes but does not teach.",
  },
  {
    q: "How reliable are the arrows?",
    a: "Treat them as a guided order, not an authority. The strongest links are usually right, while weaker ones can be wrong or point the wrong way. Use the map to plan, and check it against your own judgement.",
  },
  {
    q: "Does it work for every syllabus?",
    a: "It is built for Mumbai University NEP syllabi, mostly computer and IT subjects. Other layouts, or PDFs whose text cannot be read properly, may not work, and you will see a message instead of a wrong map.",
  },
  {
    q: "Can I look at just one topic?",
    a: "Yes. Choose any topic to see everything that comes before it, in study order, plus the background you are missing.",
  },
  {
    q: "Do I need an account?",
    a: "No. Upload a PDF and the map appears. Saving your progress between visits is not available yet.",
  },
];

const Plus = () => (
  <svg viewBox="0 0 20 20" fill="none" width="100%" className="accordion__icon-plus" aria-hidden="true">
    <path fill="currentColor" d="M7.84 18.8v-7H1.12V7.88h6.72V.96h4.32v6.92h6.76v3.92h-6.76v7z" />
  </svg>
);
const Minus = () => (
  <svg viewBox="0 0 20 20" fill="none" width="100%" className="accordion__icon-minus" aria-hidden="true">
    <path fill="currentColor" d="M3.8 7.9h12.4v4.04H3.8z" />
  </svg>
);

function Item({ q, a, hidden }: { q: string; a: string; hidden?: boolean }) {
  const [open, setOpen] = useState(false);
  const id = useId();
  return (
    <div className={`accordion__details ${open ? "is--active" : ""} ${hidden ? "is--hidden" : ""}`}>
      <h3 className="accordion__title-h">
        <button
          type="button"
          className="accordion__summary"
          aria-expanded={open}
          aria-controls={id}
          onClick={() => setOpen((o) => !o)}
        >
          <span className="accordion__title-wrap">
            <span className="accordion__title p-large">{q}</span>
            <span className="accordion__icon-wrap">
              <Plus />
              <Minus />
            </span>
          </span>
        </button>
      </h3>
      <div className="accordion__content" id={id} role="region">
        <div className="accordion__content-clip">
          <div className="accordion__content-inner">
            <p>{a}</p>
          </div>
        </div>
      </div>
    </div>
  );
}

export function Faq() {
  const [all, setAll] = useState(false);
  return (
    <section id="faq" className="faq is--bg-white">
      <div className="faq__bg" aria-hidden="true">
        <BlobBg variant="faq" className="faq__bg-svg" small />
      </div>
      <div className="faq__container u-container">
        <div className="faq__inner">
          <div className="faq__header">
            <h2 className="h-l">Common questions</h2>
          </div>
          <div className="faq__content">
            {FAQ.map((f, i) => (
              <Item key={f.q} q={f.q} a={f.a} hidden={!all && i >= 3} />
            ))}
            <ButtonAlt onClick={() => setAll((a) => !a)} className="faq__more">
              {all ? "Show fewer" : "Show all FAQ"}
            </ButtonAlt>
          </div>
        </div>
      </div>
      <div className="faq__logo-easter-egg">
        <LogoMark className="egg" />
      </div>
    </section>
  );
}
