"use client";

import { useRef, useState, type CSSProperties } from "react";
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
  const [activeStep, setActiveStep] = useState(0);

  const handleListScroll = (e: React.UIEvent<HTMLUListElement>) => {
    const list = e.currentTarget;
    const item = list.firstElementChild as HTMLElement | null;
    if (!item) return;
    const itemWidth = item.offsetWidth;
    const gap = 16;
    const idx = Math.round(list.scrollLeft / (itemWidth + gap));
    setActiveStep(Math.max(0, Math.min(STEPS.length - 1, idx)));
  };

  const goToStep = (idx: number) => {
    const list = root.current?.querySelector<HTMLUListElement>(".flow__list");
    if (!list) return;
    const item = list.children[idx] as HTMLElement | null;
    if (item) {
      item.scrollIntoView({
        behavior: "smooth",
        inline: "center",
        block: "nearest",
      });
    }
  };

  // Port of initCallout: cards plop in, jitter at rest, and the hovered one springs forward.
  useGsap(() => {
    const container = root.current!.querySelector<HTMLElement>("[data-call-out]");
    if (!container || reducedMotion()) return;
    const cards = gsap.utils.toArray<HTMLElement>("[data-call-out-item]", container);
    const content = gsap.utils.toArray<HTMLElement>("[data-call-out-child]", container);

    const isMobile = typeof window !== "undefined" && window.matchMedia("(max-width: 991px)").matches;

    if (!isMobile) {
      cards.forEach((card) => {
        gsap.set(card, {
          xPercent: (Math.random() - 0.5) * 10,
          yPercent: (Math.random() - 0.5) * 10,
          rotation: (Math.random() - 0.5) * 15,
        });
      });
    } else {
      cards.forEach((card) => {
        gsap.set(card, {
          xPercent: 0,
          yPercent: 0,
          rotation: 0,
        });
      });
    }

    gsap.from(cards, {
      rotation: isMobile ? 0 : (Math.random() - 0.5) * 15,
      yPercent: "+=120",
      duration: 0.85,
      ease: isMobile ? "power3.out" : "elastic.out(1, 0.75)",
      stagger: 0.088,
      scrollTrigger: { trigger: container, start: "top 85%", once: true },
    });

    if (!window.matchMedia("(hover: hover) and (pointer: fine)").matches) return;

    let current = 0;
    const portion = (i: number) => {
      cards[i].style.zIndex = "10";
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
      cards[i].style.zIndex = String(i + 1);
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
            <ul className="flow__list" data-call-out onScroll={handleListScroll}>
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
            <div className="flow__mobile-dots" role="tablist" aria-label="Step carousel indicators">
              {STEPS.map((s, idx) => (
                <button
                  key={s.n}
                  type="button"
                  role="tab"
                  aria-selected={idx === activeStep}
                  aria-label={`Step ${s.n}: ${s.title}`}
                  className={`flow__mobile-dot${idx === activeStep ? " is--active" : ""}`}
                  onClick={() => goToStep(idx)}
                />
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
