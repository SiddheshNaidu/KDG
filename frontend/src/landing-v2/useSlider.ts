"use client";

import { useEffect, useRef, type RefObject } from "react";
import { gsap } from "./gsap";

export type SliderApi = { next: () => void; prev: () => void };

type Options = {
  /** snap items to the centre of the viewport (CenterSlider) */
  center?: boolean;
  lerp?: number;
  /** called every frame per item; norm = distance from viewport centre in item widths */
  onItem?: (el: HTMLElement, norm: number, index: number) => void;
  onState?: (s: { atStart: boolean; atEnd: boolean }) => void;
  endPad?: number;
};

/**
 * Lightweight drag / wheel / button slider with lerped motion and rubber-band edges.
 * Stand-in for the site's Smooothy `ParallaxSlider` and `CenterSlider` classes.
 * Returns a ref exposing `next()` / `prev()` for the arrow buttons.
 */
export function useSlider(
  wrapRef: RefObject<HTMLElement | null>,
  trackRef: RefObject<HTMLElement | null>,
  { center = false, lerp = 0.225, onItem, onState, endPad = 0 }: Options = {},
) {
  const api = useRef<SliderApi | null>(null);
  useEffect(() => {
    const wrap = wrapRef.current;
    const track = trackRef.current;
    if (!wrap || !track) return;

    const items = Array.from(track.children) as HTMLElement[];
    let x = 0;
    let target = 0;
    let min = 0;
    let max = 0;
    let snaps: number[] = [];
    let ww = wrap.clientWidth;
    let dragging = false;
    let moved = 0;
    let startX = 0;
    let startTarget = 0;
    let lastX = 0;
    let vel = 0;
    let lastState = "";
    let initialised = false;

    const measure = () => {
      ww = wrap.clientWidth;
      if (center) {
        snaps = items.map(
          (el) => ww / 2 - (el.offsetLeft + el.offsetWidth / 2),
        );
        max = snaps[0] ?? 0;
        min = snaps[snaps.length - 1] ?? 0;
        if (!initialised) {
          initialised = true;
          target = x = max;
        }
      } else {
        max = 0;
        min = Math.min(0, ww - track.scrollWidth - endPad);
        snaps = [];
      }
      target = Math.max(min, Math.min(max, target));
    };

    const clampSoft = (v: number) => {
      if (v > max) return max + (v - max) * 0.35;
      if (v < min) return min + (v - min) * 0.35;
      return v;
    };

    const nearestSnap = (v: number) =>
      snaps.reduce((a, b) => (Math.abs(b - v) < Math.abs(a - v) ? b : a), snaps[0]);

    const settle = (extra = 0) => {
      let v = target + extra;
      v = Math.max(min, Math.min(max, v));
      target = center ? nearestSnap(v) : v;
    };

    const step = (dir: 1 | -1) => {
      if (center) {
        const i = snaps.indexOf(nearestSnap(target));
        const n = Math.max(0, Math.min(snaps.length - 1, i + dir));
        target = snaps[n];
      } else {
        const w = (items[0]?.offsetWidth ?? 300) * 1.05;
        target = Math.max(min, Math.min(max, target - dir * w));
      }
    };

    api.current = { next: () => step(1), prev: () => step(-1) };

    const down = (e: PointerEvent) => {
      if (e.pointerType === "mouse" && e.button !== 0) return;
      dragging = true;
      moved = 0;
      startX = lastX = e.clientX;
      startTarget = target;
      vel = 0;
      wrap.setPointerCapture?.(e.pointerId);
      wrap.classList.add("is--dragging");
    };
    const move = (e: PointerEvent) => {
      if (!dragging) return;
      const dx = e.clientX - startX;
      moved = Math.max(moved, Math.abs(dx));
      vel = e.clientX - lastX;
      lastX = e.clientX;
      target = clampSoft(startTarget + dx);
    };
    const up = () => {
      if (!dragging) return;
      dragging = false;
      wrap.classList.remove("is--dragging");
      settle(vel * 12);
    };
    const click = (e: MouseEvent) => {
      if (moved > 6) {
        e.preventDefault();
        e.stopPropagation();
      }
    };
    const wheel = (e: WheelEvent) => {
      const horizontal = Math.abs(e.deltaX) > Math.abs(e.deltaY) || e.shiftKey;
      if (!horizontal) return;
      e.preventDefault();
      const d = e.shiftKey && !e.deltaX ? e.deltaY : e.deltaX;
      target = clampSoft(target - d);
      window.clearTimeout(wheelTimer);
      wheelTimer = window.setTimeout(() => settle(), 120);
    };
    let wheelTimer = 0;

    const tick = () => {
      const k = 1 - Math.pow(1 - lerp, gsap.ticker.deltaRatio(60));
      x += (target - x) * k;
      if (Math.abs(target - x) < 0.05) x = target;
      track.style.transform = `translate3d(${x}px,0,0)`;
      if (onItem) {
        for (let i = 0; i < items.length; i++) {
          const el = items[i];
          const cx = x + el.offsetLeft + el.offsetWidth / 2;
          onItem(el, (cx - ww / 2) / el.offsetWidth, i);
        }
      }
      if (onState) {
        const s = { atStart: target >= max - 1, atEnd: target <= min + 1 };
        const key = `${s.atStart}${s.atEnd}`;
        if (key !== lastState) {
          lastState = key;
          onState(s);
        }
      }
    };

    measure();
    x = target;
    gsap.ticker.add(tick);
    const ro = new ResizeObserver(measure);
    ro.observe(wrap);
    ro.observe(track);
    wrap.addEventListener("pointerdown", down);
    wrap.addEventListener("pointermove", move);
    wrap.addEventListener("pointerup", up);
    wrap.addEventListener("pointercancel", up);
    wrap.addEventListener("click", click, true);
    wrap.addEventListener("wheel", wheel, { passive: false });

    return () => {
      gsap.ticker.remove(tick);
      ro.disconnect();
      wrap.removeEventListener("pointerdown", down);
      wrap.removeEventListener("pointermove", move);
      wrap.removeEventListener("pointerup", up);
      wrap.removeEventListener("pointercancel", up);
      wrap.removeEventListener("click", click, true);
      wrap.removeEventListener("wheel", wheel);
      window.clearTimeout(wheelTimer);
      api.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  return api;
}
