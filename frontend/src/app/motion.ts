import { useLayoutEffect, type RefObject } from "react";
import { gsap } from "../landing-v2/gsap";

export const reduced = () =>
  typeof window !== "undefined" && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

/** Fade + lift the matching children of `scope` in, one after another. Runs again when `deps` change. */
export function useReveal(
  scope: RefObject<HTMLElement | null>,
  selector: string,
  deps: unknown[] = [],
  vars: gsap.TweenVars = {},
) {
  useLayoutEffect(() => {
    const el = scope.current;
    if (!el || reduced()) return;
    const ctx = gsap.context(() => {
      gsap.from(selector, {
        y: 18,
        opacity: 0,
        duration: 0.55,
        ease: "power3.out",
        stagger: 0.06,
        clearProps: "transform,opacity",
        ...vars,
      });
    }, el);
    return () => ctx.revert();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
}

/** Tween a number shown in an element (for the progress counter). */
export function tweenNumber(el: HTMLElement | null, from: number, to: number, suffix = "") {
  if (!el) return;
  if (reduced() || from === to) {
    el.textContent = `${Math.round(to)}${suffix}`;
    return;
  }
  const o = { v: from };
  gsap.to(o, {
    v: to,
    duration: 0.8,
    ease: "power2.out",
    onUpdate: () => {
      el.textContent = `${Math.round(o.v)}${suffix}`;
    },
  });
}
