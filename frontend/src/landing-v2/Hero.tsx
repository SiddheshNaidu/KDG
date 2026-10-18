"use client";

import { useRef } from "react";
import { BlobBg, LogoMark } from "./art";
import { ButtonAlt } from "./Button";
import { Notebook3D } from "./Notebook3D";
import { gsap, ScrollTrigger } from "./gsap";
import { reducedMotion, useGsap } from "./useGsap";

const BOOKS = [
  {
    cls: "hero__book--teal",
    cover: "#1b8f96",
    spine: "#0f5d63",
    label: "Study order",
    rot: [14, -16, -28],
    depth: 0.5,
  },
  {
    cls: "hero__book--blue",
    cover: "#1f3a8f",
    spine: "#d9609f",
    label: "Syllabus map",
    rot: [16, -26, 18],
    depth: 1,
  },
  {
    cls: "hero__book--red",
    cover: "#a3202f",
    spine: "#7d3b38",
    label: "Key topics",
    rot: [12, -22, -30],
    depth: 0.8,
  },
] as const;

export function Hero() {
  const root = useRef<HTMLElement>(null);

  useGsap(() => {
    const books = gsap.utils.toArray<HTMLElement>("[data-hero-book]");
    const mid = gsap.utils.toArray<HTMLElement>("[data-hero-book-mid]");
    const inner = gsap.utils.toArray<HTMLElement>("[data-hero-book-inner]");

    BOOKS.forEach((b, i) => {
      gsap.set(inner[i], {
        rotationX: b.rot[0],
        rotationY: b.rot[1],
        rotationZ: b.rot[2],
        transformPerspective: 1400,
      });
    });

    if (reducedMotion()) return;

    // idle bob
    inner.forEach((el, i) => {
      gsap.to(el, {
        y: "+=0.9em",
        rotationZ: `+=${i % 2 ? -2.5 : 2.5}`,
        duration: 3.2 + i * 0.7,
        ease: "sine.inOut",
        yoyo: true,
        repeat: -1,
      });
    });

    // scroll: books drift up and spin as the hero leaves
    books.forEach((el, i) => {
      gsap.to(el, {
        yPercent: -22 - i * 10,
        rotate: (i % 2 ? 1 : -1) * 14,
        ease: "none",
        scrollTrigger: {
          trigger: root.current,
          start: "top top",
          end: "bottom top",
          scrub: true,
        },
      });
    });

    // pointer parallax
    const fine = window.matchMedia("(hover: hover) and (pointer: fine)").matches;
    if (!fine) return;
    const setters = mid.map((el, i) => ({
      x: gsap.quickTo(el, "x", { duration: 0.9, ease: "power3.out" }),
      y: gsap.quickTo(el, "y", { duration: 0.9, ease: "power3.out" }),
      d: BOOKS[i].depth,
    }));
    const onMove = (e: MouseEvent) => {
      const nx = e.clientX / window.innerWidth - 0.5;
      const ny = e.clientY / window.innerHeight - 0.5;
      setters.forEach((s) => {
        s.x(nx * -38 * s.d);
        s.y(ny * -28 * s.d);
      });
    };
    window.addEventListener("mousemove", onMove);
    return () => window.removeEventListener("mousemove", onMove);
  }, root);

  // refresh trigger positions once fonts settle
  useGsap(() => {
    document.fonts?.ready.then(() => ScrollTrigger.refresh());
  }, root);

  return (
    <section ref={root} className="hero" id="top" data-intro-home>
      <div className="hero__bg" data-hero-bg>
        <BlobBg variant="hero" className="hero__bg-svg" />
      </div>

      <div className="hero__sequence" data-hero-sequence aria-hidden="true">
        <div className="hero__sequence-element">
          {BOOKS.map((b) => (
            <div key={b.cls} className={`hero__book ${b.cls}`} data-hero-book>
              <div data-hero-book-mid>
                <div data-hero-book-inner>
                  <Notebook3D
                    w={27}
                    h={37}
                    d={3.6}
                    cover={b.cover}
                    spine={b.spine}
                    label={b.label}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="hero__container u-container">
        <div className="hero__content">
          <div className="hero__header">
            <h1 className="hero__title h-xxl" data-hero-title>
              Study in the right order
            </h1>
            <p className="hero__paragraph p-regular" data-hero-paragraph>
              Upload a syllabus and see how its topics depend on each other:
              what to learn first, what unlocks the most, and what you are missing.
            </p>
          </div>
          <ButtonAlt href="#upload" data-button-alt="">
            Upload your syllabus
          </ButtonAlt>
        </div>
      </div>

      <div className="hero__text-outer">
        <div className="hero__text-wrap">
          <p className="hero__text hand" data-hero-handwritten-text>
            Your syllabus, as a map
          </p>
        </div>
      </div>

      <div className="hero__logo-easter-egg" data-hero-easter-egg>
        <LogoMark className="egg" />
      </div>
    </section>
  );
}
