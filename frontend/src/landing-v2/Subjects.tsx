"use client";

import { useRef, useState } from "react";
import { LogoMark, SubjectCard } from "./art";
import { gsap } from "./gsap";
import { reducedMotion, useGsap } from "./useGsap";

const SUBJECTS: [string, string][] = [
  ["Programming", "engineering"],
  ["Mathematics", "mathematics"],
  ["Databases", "commerce"],
  ["Operating Systems", "engineering"],
  ["Networks", "physics"],
  ["Data Science", "mathematics"],
  ["Physics", "physics"],
  ["Chemistry", "chemistry"],
  ["and more!", "more"],
];

export function Subjects() {
  const root = useRef<HTMLElement>(null);
  const [active, setActive] = useState(0);

  // Port of initGenreInteraction: holders follow the hovered row, cards shuffle on every enter,
  // and the whole cluster parallaxes with the pointer.
  useGsap(() => {
    const el = root.current!;
    const list = el.querySelector<HTMLElement>("[data-genre-interaction-list]")!;
    const scope = el.querySelector<HTMLElement>("[data-genre-interaction-scope]")!;
    const items = Array.from(el.querySelectorAll<HTMLElement>("[data-genre-interaction-item]"));
    const boxes = Array.from(el.querySelectorAll<HTMLElement>("[data-genre-interaction-box]"));
    if (reducedMotion()) return;

    const cache: { width: number }[] = [];
    const populate = () => {
      cache.length = 0;
      items.forEach((item, i) => {
        item.dataset.index = String(i);
        cache.push({ width: item.getBoundingClientRect().width });
      });
    };
    populate();
    window.addEventListener("resize", populate);

    let listBounds: DOMRect | undefined;
    const setParallax = (e: PointerEvent) => {
      if (!listBounds) return;
      const { x: ix, y: iy, width, height } = listBounds;
      boxes.forEach((b) => {
        b.style.setProperty("--px", String((e.clientX - ix) / width - 0.75));
        b.style.setProperty("--py", String((e.clientY - iy) / height - 0.75));
      });
    };

    let startIndex = 0;
    let startWidth = 0;
    const setAnchor = (e: Event) => {
      const t = e.target as HTMLElement;
      if (t.tagName !== "LI") return;
      const index = Number.parseInt(t.dataset.index ?? "0", 10);
      const bounds = cache[index];
      if (el.dataset.startSet !== "true") {
        startIndex = index;
        startWidth = bounds.width;
        el.dataset.startSet = "true";
        el.style.setProperty("--start-index", String(index));
        el.style.setProperty("--start-width", String(bounds.width));
      }
      scope.style.setProperty("--active-index", String(index - startIndex));
      scope.style.setProperty("--active-offset", String(bounds.width - startWidth));
      el.style.setProperty("--translate-speed", "0.2s");
      setActive(index);

      boxes.forEach((b) => {
        b.style.setProperty("--x", String(gsap.utils.random(-15, 15)));
        b.style.setProperty("--y", String(gsap.utils.random(-15, 15)));
        b.style.setProperty("--r", String(gsap.utils.random(-15, 15)));
      });

      listBounds = list.getBoundingClientRect();
      list.addEventListener("pointermove", setParallax, true);
    };

    const removeAnchor = async (e: Event) => {
      if ((e.target as HTMLElement).tagName !== "LI") return;
      const anims = boxes[0]
        .getAnimations()
        .filter((a) => (a as CSSTransition).transitionProperty === "scale");
      await Promise.allSettled(anims.map((a) => a.finished));
      if (
        anims.length &&
        anims[0].playState === "finished" &&
        getComputedStyle(boxes[0]).scale === "0"
      ) {
        delete el.dataset.startSet;
        el.style.removeProperty("--start-index");
        el.style.removeProperty("--start-width");
        scope.style.removeProperty("--active-index");
        scope.style.removeProperty("--active-offset");
        el.style.removeProperty("--translate-speed");
        boxes.forEach((b) => {
          b.style.removeProperty("--px");
          b.style.removeProperty("--py");
        });
        listBounds = undefined;
        list.removeEventListener("pointermove", setParallax, true);
      }
    };

    list.addEventListener("pointerenter", setAnchor, true);
    list.addEventListener("pointerleave", removeAnchor, true);
    return () => {
      window.removeEventListener("resize", populate);
      list.removeEventListener("pointerenter", setAnchor, true);
      list.removeEventListener("pointerleave", removeAnchor, true);
      list.removeEventListener("pointermove", setParallax, true);
    };
  }, root);

  return (
    <section ref={root} className="genre is--bright-pink" data-genre-interaction>
      <div className="genre__container u-container">
        <div className="genre__inner">
          <div className="genre__header">
            <div className="genre__text-outer">
              <div className="genre__text-wrap">
                <p className="hand genre__text" data-handwritten-text-inview>
                  A map for every subject
                </p>
              </div>
            </div>
            <h2 className="genre__title">Maps for</h2>
          </div>

          <div className="genre__list-wrap">
            <ul className="genre__list" data-genre-interaction-list>
              {SUBJECTS.map(([label]) => (
                <li className="genre__list-item" key={label} data-genre-interaction-item>
                  <span className="genre__link">
                    <span className="genre__link-default">{label}</span>
                    <span className="genre__link-hover" aria-hidden="true">{label}</span>
                  </span>
                </li>
              ))}
            </ul>
            <div className="genre__holding" aria-hidden="true">
              <div className="genre__scope" data-genre-interaction-scope>
                {[0, 1, 2, 3].map((h) => (
                  <div className="genre__holder" key={h}>
                    <div className="genre__box" data-genre-interaction-box>
                      <SubjectCard
                        kind={SUBJECTS[active][1]}
                        label={SUBJECTS[active][0] === "and more!" ? "More" : SUBJECTS[active][0]}
                        variant={h}
                        index={active}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="genre__easter-egg">
            <LogoMark className="egg" />
          </div>
        </div>
      </div>
    </section>
  );
}
