"use client";

import { useEffect, type RefObject } from "react";
import { gsap } from "./gsap";

/** Runs `setup` inside a gsap.context scoped to `scope`; reverts everything on unmount. */
export function useGsap(
  setup: (ctx: gsap.Context) => void | (() => void),
  scope: RefObject<HTMLElement | null>,
) {
  useEffect(() => {
    const ctx = gsap.context((self) => setup(self), scope);
    return () => ctx.revert();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
}

export const reducedMotion = () =>
  typeof window !== "undefined" &&
  window.matchMedia("(prefers-reduced-motion: reduce)").matches;
