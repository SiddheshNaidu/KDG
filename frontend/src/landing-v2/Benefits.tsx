"use client";

import { useRef } from "react";
import { BlobBg, LogoMark } from "./art";
import { gsap } from "./gsap";
import { reducedMotion, useGsap } from "./useGsap";

const LABELS = [
  { text: "Study order", desc: "Logical sequence", cls: "is--first", tone: "" },
  { text: "Key topics", desc: "Unlocks the most", cls: "is--second", tone: "is--orange" },
  { text: "Prerequisites", desc: "Hidden background", cls: "is--third", tone: "is--periwinkle" },
  { text: "Topic maps", desc: "Interactive graph", cls: "is--fourth", tone: "is--cyan" },
  { text: "Start here", desc: "Zero prereqs needed", cls: "is--fifth", tone: "is--olive" },
];

export function Benefits() {
  const root = useRef<HTMLElement>(null);

  useGsap(() => {
    if (reducedMotion()) return;
    const el = root.current!;

    // pills pop in
    gsap.fromTo(
      el.querySelectorAll("[data-benefits-item]"),
      { rotate: gsap.utils.random(-33, 33), scale: 0 },
      {
        rotate: 0,
        scale: 1,
        ease: "elastic.out(1,0.75)",
        duration: 0.85,
        stagger: 0.072,
        scrollTrigger: { trigger: el, start: "top 25%", once: true },
      },
    );

    // momentum hover: pills get shoved by the pointer's velocity and coast back (InertiaPlugin)
    if (!window.matchMedia("(hover: hover) and (pointer: fine)").matches) return;
    const xyMultiplier = 12;
    const rotationMultiplier = 10;
    const inertiaResistance = 220;
    const clampXY = gsap.utils.clamp(-280, 280);
    const clampRot = gsap.utils.clamp(-35, 35);

    const rootEl = el.querySelector<HTMLElement>("[data-momentum-hover]")!;
    let prevX = 0,
      prevY = 0,
      velX = 0,
      velY = 0,
      raf: number | null = null;

    const onMove = (e: MouseEvent) => {
      if (raf) return;
      raf = requestAnimationFrame(() => {
        velX = e.clientX - prevX;
        velY = e.clientY - prevY;
        prevX = e.clientX;
        prevY = e.clientY;
        raf = null;
      });
    };
    rootEl.addEventListener("mousemove", onMove);

    const cleanups: (() => void)[] = [];
    rootEl.querySelectorAll<HTMLElement>("[data-momentum-hover-element]").forEach((item) => {
      const enter = (e: MouseEvent) => {
        const target = item.querySelector<HTMLElement>("[data-momentum-hover-target]");
        if (!target) return;
        const { left, top, width, height } = target.getBoundingClientRect();
        const offsetX = e.clientX - (left + width / 2);
        const offsetY = e.clientY - (top + height / 2);
        const rawTorque = offsetX * velY - offsetY * velX;
        const leverDist = Math.hypot(offsetX, offsetY) || 1;
        const angularForce = rawTorque / leverDist;
        gsap.to(target, {
          inertia: {
            x: { velocity: clampXY(velX * xyMultiplier), end: 0 },
            y: { velocity: clampXY(velY * xyMultiplier), end: 0 },
            rotation: { velocity: clampRot(angularForce * rotationMultiplier), end: 0 },
            resistance: inertiaResistance,
          },
        });
      };
      item.addEventListener("mouseenter", enter);
      cleanups.push(() => item.removeEventListener("mouseenter", enter));
    });

    return () => {
      rootEl.removeEventListener("mousemove", onMove);
      cleanups.forEach((c) => c());
      if (raf) cancelAnimationFrame(raf);
    };
  }, root);

  return (
    <section ref={root} className="benefits" data-benefits>
      <div className="benefits__container">
        <div className="benefits__inner">
          <div className="benefits__bg" aria-hidden="true">
            <BlobBg variant="benefits" className="benefits__bg-svg" />
          </div>

          <div className="benefits__content">
            <svg className="benefits__logo-text" viewBox="0 0 420 170" aria-label="Why KDG?" role="img">
              <defs>
                <path id="rq-arc" d="M24 160A186 186 0 0 1 396 160" fill="none" />
              </defs>
              <text className="benefits__arc">
                <textPath href="#rq-arc" startOffset="50%" textAnchor="middle">
                  Why KDG?
                </textPath>
              </text>
            </svg>
            <LogoMark className="benefits__logo" />
          </div>

          <div className="benefits__label-wrap" data-momentum-hover>
            {LABELS.map((l) => (
              <div
                key={l.text}
                className={`benefits__label ${l.cls} ${l.tone}`}
                data-benefits-item
                data-momentum-hover-element
              >
                <div className={`benefits__label-inner ${l.tone}`} data-momentum-hover-target>
                  <span className="benefits__label-text h-l">{l.text}</span>
                  <span className="benefits__label-desc">{l.desc}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
