"use client";

import { useRef } from "react";
import { BlobBg } from "./art";
import { gsap } from "./gsap";
import { reducedMotion, useGsap } from "./useGsap";

function Band({
  text,
  blue,
  reverse,
}: {
  text: string;
  blue?: boolean;
  reverse?: boolean;
}) {
  const run = Array.from({ length: 4 }, (_, i) => (
    <span className="badge__item-title" key={i}>
      {text}
      <span className="badge__star" aria-hidden="true">✦</span>
    </span>
  ));
  return (
    <div className="badge__item" data-badge-item>
      <div className={`badge__item-bg ${blue ? "is--blue" : ""}`}>
        <BlobBg variant="badge" className="badge__item-bg-svg" animate={false} />
      </div>
      <div className="badge__item-title-outer">
        <div className={`marquee ${reverse ? "is--reverse" : ""}`} aria-label={text}>
          <div className="marquee__track" aria-hidden="true">
            {run}
            {run}
          </div>
        </div>
      </div>
    </div>
  );
}

export function Badge() {
  const root = useRef<HTMLElement>(null);

  // Port of initBadge: the two bands drop in and settle at their angles.
  useGsap(() => {
    if (reducedMotion()) return;
    const items = gsap.utils.toArray<HTMLElement>("[data-badge-item]");
    const [item1, item2] = items;
    if (!item1 || !item2) return;
    const mobile = window.matchMedia("(max-width: 990px)").matches;
    gsap.set(item1, { rotate: -2, y: "-2em" });
    gsap.set(item2, { rotate: 1, y: "-6em" });
    const tl = gsap.timeline({ paused: true });
    tl.to(item1, { y: "0em", rotate: 0, duration: 1, ease: "elastic.out(1, 0.75)" }, 0).to(
      item2,
      { y: mobile ? "-0.25em" : "-1em", rotate: -4.7, duration: 1, ease: "elastic.out(1, 0.75)" },
      0.0088,
    );
    gsap.timeline({
      scrollTrigger: { trigger: root.current, start: "top 80%", end: "bottom top", onEnter: () => tl.play() },
    });
  }, root);

  return (
    <section ref={root} className="badge" data-badge>
      <div className="badge__inner">
        <Band text="Your syllabus. Your map. " />
        <Band text="Upload it. Map it. Plan it. " blue reverse />
      </div>
    </section>
  );
}
