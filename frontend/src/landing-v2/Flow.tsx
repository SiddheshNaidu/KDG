"use client";

import { useRef, type CSSProperties } from "react";
import { BlobBg, LogoMark, StepArt } from "./art";
import { ButtonAlt } from "./Button";
import { gsap } from "./gsap";
import { reducedMotion, useGsap } from "./useGsap";

const STEPS = [
  {
    n: 1 as const,
    title: "Upload",
    text: "Drop in a Mumbai University NEP syllabus PDF. If it holds several subjects, pick the one you want.",
    color: "var(--cyan)",
  },
  {
    n: 2 as const,
    title: "Read the topics",
    text: "Each subject is split into clean topics, in syllabus order, without headers and page numbers.",
    color: "var(--bright-pink)",
  },
  {
    n: 3 as const,
    title: "See the map",
    text: "Arrows show which topic comes before which, so the order and the topics that unlock the most stand out.",
    color: "var(--yellow)",
  },
  {
    n: 4 as const,
    title: "Plan your study",
    text: "Pick any topic to see everything to learn before it, plus the background your syllabus skips.",
    color: "var(--periwinkle)",
  },
];

export function Flow() {
  const root = useRef<HTMLElement>(null);

  // Port of initCallout: cards plop in, jitter at rest, and the hovered one springs forward.
  useGsap(() => {
    const container = root.current!.querySelector<HTMLElement>("[data-call-out]");
    if (!container || reducedMotion()) return;
    const cards = gsap.utils.toArray<HTMLElement>("[data-call-out-item]", container);
    const content = gsap.utils.toArray<HTMLElement>("[data-call-out-child]", container);

    cards.forEach((card) => {
      gsap.set(card, {
        xPercent: (Math.random() - 0.5) * 10,
        yPercent: (Math.random() - 0.5) * 10,
        rotation: (Math.random() - 0.5) * 15,
      });
    });

    gsap.from(cards, {
      rotation: (Math.random() - 0.5) * 15,
      yPercent: "+=150",
      duration: 1.05,
      ease: "elastic.out(1, 0.75)",
      stagger: 0.088,
      scrollTrigger: { trigger: container, start: "top 85%", once: true },
    });

    if (!window.matchMedia("(hover: hover) and (pointer: fine)").matches) return;

    let current = 0;
    const portion = (i: number) => {
      gsap.to(cards[i], {
        xPercent: 0,
        yPercent: 0,
        rotation: 0,
        scale: 1.075,
        duration: 0.85,
        ease: "elastic.out(1, 0.75)",
        overwrite: "auto",
      });
      content.forEach((c, idx) => {
        gsap.to(c, {
          xPercent: idx !== i ? 45 / (idx - i) : 0,
          duration: 0.85,
          ease: "elastic.out(1, 0.75)",
          overwrite: "auto",
        });
      });
    };
    const reset = (i: number) => {
      gsap.to(cards[i], {
        xPercent: (Math.random() - 0.5) * 10,
        yPercent: (Math.random() - 0.5) * 10,
        rotation: (Math.random() - 0.5) * 20,
        scale: 1,
        duration: 0.85,
        ease: "elastic.out(1, 0.75)",
        overwrite: "auto",
      });
    };

    const move = (e: MouseEvent) => {
      const r = container.getBoundingClientRect();
      const pct = (e.clientX - r.left) / r.width;
      const active = Math.ceil(pct * cards.length);
      if (active !== current && active > 0 && active <= cards.length) {
        if (current !== 0) reset(current - 1);
        current = active;
        portion(current - 1);
      }
    };
    const leave = () => {
      if (current > 0) reset(current - 1);
      current = 0;
      gsap.to(content, { xPercent: 0, duration: 0.85, ease: "elastic.out(1, 0.75)" });
    };
    container.addEventListener("mousemove", move);
    container.addEventListener("mouseleave", leave);
    return () => {
      container.removeEventListener("mousemove", move);
      container.removeEventListener("mouseleave", leave);
    };
  }, root);

  return (
    <section ref={root} id="how-it-works" className="flow is--inner-clip is--bg-soft-pink">
      <div className="flow__bg" aria-hidden="true">
        <BlobBg variant="flow" className="flow__bg-svg" />
      </div>
      <div className="flow__inner">
        <div className="u-container">
          <div className="flow__header">
            <h2 className="flow__title h-l">How it works</h2>
            <div className="flow__text-outer">
              <div className="flow__text-wrap">
                <p className="hand flow__text" data-handwritten-text-inview>
                  From a PDF to a plan
                </p>
              </div>
            </div>
            <div className="flow__cta">
              <LogoMark className="flow__cta-logo" />
              <ButtonAlt href="#upload">Upload your syllabus</ButtonAlt>
            </div>
          </div>

          <div className="flow__content">
            <ul className="flow__list" data-call-out>
              {STEPS.map((s) => (
                <li className="flow__list-item" key={s.n} data-call-out-item>
                  <div
                    className="flow__card"
                    style={{ "--card": s.color } as CSSProperties}
                    data-call-out-child
                  >
                    <div className="flow__card-inner">
                      <div className="flow__card-header">
                        <span className="hand flow__step">Step #{s.n}</span>
                      </div>
                      <div className="flow__card-img-wrap">
                        <StepArt n={s.n} />
                      </div>
                      <div className="flow__card-content">
                        <h3 className="h-s">{s.title}</h3>
                        <p className="p-small">{s.text}</p>
                      </div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </section>
  );
}
