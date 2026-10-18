"use client";

import { useRef } from "react";
import { ButtonAlt } from "./Button";
import { Notebook3D } from "./Notebook3D";
import { gsap } from "./gsap";
import { reducedMotion, useGsap } from "./useGsap";

const TECH = ["Planning", "Revising", "Exams"];

export function Study() {
  const root = useRef<HTMLElement>(null);

  useGsap(() => {
    const el = root.current!;
    const textPath = el.querySelector<SVGTextPathElement>("textPath");
    const path = el.querySelector<SVGPathElement>("[data-tagline-curve-svg] path");
    if (reducedMotion() || !textPath || !path) return;

    // Port of initTaglineCurve: the headline rides a curve and slides along it on scroll.
    const pathLen = path.getTotalLength();
    // start with the phrase just inside the curve, end with its last letter leaving on the left
    const endOffset = () => -((textPath.getComputedTextLength() * 100) / pathLen) - 2;

    gsap.fromTo(
      textPath,
      { attr: { startOffset: "8%" } },
      {
        attr: { startOffset: () => `${endOffset()}%` },
        ease: "none",
        scrollTrigger: {
          trigger: el.querySelector("[data-tagline-curve]"),
          start: "-40% bottom",
          end: "60% top",
          scrub: 0.5,
          invalidateOnRefresh: true,
        },
      },
    );

    // notebook pops in tilted
    gsap.fromTo(
      el.querySelector("[data-gift-item]"),
      { rotate: 30, scale: 0 },
      {
        rotate: -21,
        scale: 1,
        ease: "elastic.out(1,0.75)",
        duration: 0.95,
        scrollTrigger: { trigger: el, start: "top 72%", once: true },
      },
    );
  }, root);

  return (
    <section ref={root} className="gift" data-gift>
      <div className="tagline-curve" data-tagline-curve>
        <svg className="tagline-curve__svg" data-tagline-curve-svg viewBox="0 0 1920 560" aria-label="Track what you know, soon" role="img">
          <path id="rq-curve" d="M-160 470C420 520 960 440 1440 250S2060 20 2320 -20" fill="none" />
          <text data-tagline-curve-text fontSize="170" className="tagline-curve__text">
            <textPath id="textpath" href="#rq-curve" startOffset="4%">
              Track what you know, soon
            </textPath>
          </text>
        </svg>
      </div>

      <div className="gift__inner">
        <div className="gift__content">
          <div className="gift__content-top">
            <span className="tag-small" style={{ background: "var(--yellow)" }}>
              <span className="tag-small__text">Coming soon</span>
            </span>
            <p className="p-large">
              Mark topics as known and watch the map update: a topic unlocks
              once everything before it is done, and you can pick up where you
              left off next time.
            </p>
            <ButtonAlt href="#upload">Upload your syllabus</ButtonAlt>
          </div>

          <div className="gift__content-bottom">
            <div className="gift__content-handwritten-wrap">
              <div className="gift__content-handwritten-outer">
                <p className="gift__content-handwritten hand" data-handwritten-text-inview>
                  Made for
                </p>
              </div>
            </div>
            <div className="gift__content-box-wrap">
              {TECH.map((t) => (
                <div className="gift__content-box" key={t}>
                  <span>{t}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="gift__visual" aria-hidden="true">
          <div className="gift__visual-img" data-gift-item>
            <div className="gift__nb">
              <Notebook3D w={27} h={37} d={3.6} cover="#3b308f" spine="#ff008c" label="Progress" />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
