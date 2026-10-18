"use client";

import "lenis/dist/lenis.css";
import "./landing.css";
import "./landing-2.css";
import "./landing-3.css";

import { useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../app/auth";
import Lenis from "lenis";
import { fontClassName } from "./fonts";
import { gsap, ScrollTrigger, SplitText } from "./gsap";
import { reducedMotion } from "./useGsap";
import { LogoMark } from "./art";
import { Header } from "./Header";
import { Hero } from "./Hero";
import { Projects } from "./Projects";
import { Flow } from "./Flow";
import { BoxScroll } from "./BoxScroll";
import { Subjects } from "./Subjects";
import { Benefits } from "./Benefits";
import { Faq } from "./Faq";
import { Study } from "./Study";
import { Badge } from "./Badge";
import { Tools } from "./Tools";
import { Ask } from "./Ask";
import { Footer } from "./Footer";

/** Five fat wavy strokes that cover the screen; DrawSVG wipes them away to reveal the page. */
const WIPE_PATHS = [100, 300, 500, 700, 900].map(
  (y, i) =>
    `M-100 ${y} C 200 ${y + (i % 2 ? 70 : -70)}, 400 ${y + (i % 2 ? -70 : 70)}, 600 ${y} S 1000 ${y + (i % 2 ? 60 : -60)}, 1100 ${y}`,
);

export default function Landing() {
  const root = useRef<HTMLDivElement>(null);
  const lenisRef = useRef<Lenis | null>(null);
  const navigate = useNavigate();
  const { session } = useAuth();
  const signedIn = useRef(false);
  signedIn.current = Boolean(session);

  useEffect(() => {
    const el = root.current!;
    const reduced = reducedMotion();
    const desktop = window.matchMedia("(min-width: 992px)").matches;

    if ("scrollRestoration" in history) history.scrollRestoration = "manual";
    window.scrollTo(0, 0);

    /* ---------- smooth scroll (Lenis) wired into ScrollTrigger ---------- */
    const lenis = new Lenis({ lerp: 0.2, anchors: true, autoRaf: false });
    lenis.on("scroll", (l: Lenis) => {
      ScrollTrigger.update();
      el.dataset.scrollingStarted = l.scroll > 24 ? "true" : "false";
    });
    const tick = (t: number) => lenis.raf(t * 1000);
    gsap.ticker.add(tick);
    gsap.ticker.lagSmoothing(0);
    lenis.stop();
    lenisRef.current = lenis;

    const q = <T extends Element = HTMLElement>(s: string) => el.querySelector<T>(s);
    const wipe = q("[data-transition-wrap]") as HTMLElement;

    const finish = () => {
      wipe.style.display = "none";
      lenis.start();
      ScrollTrigger.refresh();
    };

    const ctx = gsap.context(() => {
      /* ---------- generic scroll-in effects ---------- */
      el.querySelectorAll<HTMLElement>("[data-handwritten-text-inview]").forEach((node) => {
        if (reduced) return;
        const split = new SplitText(node, { type: "words, chars", wordsClass: "split-word", charsClass: "split-char" });
        gsap.set(split.words, { display: "inline-block" });
        gsap.set(split.chars, { display: "inline-block", opacity: 0, rotate: 22, x: "-0.25em", y: "0.5em" });
        gsap.to(split.chars, {
          opacity: 1,
          rotate: 0,
          x: "0em",
          y: "0em",
          ease: "elastic.out(1, 0.75)",
          duration: 0.75,
          stagger: 0.016,
          scrollTrigger: { trigger: node, start: "top 95%" },
        });
      });

      // blobs "breathe": stroke grows and shrinks while in view (initBackgroundAnimation)
      if (!reduced) {
        el.querySelectorAll<SVGElement>("[data-background-animation]").forEach((svg) => {
          const paths = svg.querySelectorAll("path");
          const stroke = svg.hasAttribute("data-background-animation-small") ? 35 : 60;
          gsap.set(paths, { attr: { "stroke-width": 0 }, rotate: 0, transformOrigin: "center center", transformBox: "fill-box" });
          const tl = gsap
            .timeline({ paused: true, repeat: -1 })
            .to(paths, { attr: { "stroke-width": stroke }, rotate: 2, duration: 3, ease: "sine.inOut" })
            .to(paths, { attr: { "stroke-width": 0 }, rotate: 0, duration: 3, ease: "sine.inOut" });
          ScrollTrigger.create({
            trigger: svg,
            start: "top bottom",
            end: "bottom top",
            onEnter: () => tl.play(),
            onEnterBack: () => tl.play(),
            onLeave: () => tl.pause(),
            onLeaveBack: () => tl.pause(),
          });
        });
      }

      /* ---------- intro: preloader -> header -> hero (runPageOnceAnimation) ---------- */
      if (reduced) {
        finish();
        return;
      }

      const header = q("[data-header]");
      const paths = wipe.querySelectorAll("svg path");
      const logo = wipe.querySelector("[data-transition-logo]");
      const heroBg = q("[data-hero-bg]");
      const title = q("[data-hero-title]");
      const para = q("[data-hero-paragraph]");
      const btn = q("[data-intro-home] [data-button-alt]");
      const hand = q("[data-hero-handwritten-text]");
      const egg = q("[data-hero-easter-egg]");
      const seq = q("[data-hero-sequence]");

      const titleSplit = new SplitText(title!, { type: "words", wordsClass: "split-word" });
      const handSplit = new SplitText(hand!, { type: "words, chars", wordsClass: "split-word", charsClass: "split-char" });

      const tl = gsap.timeline({ paused: true });
      tl.set(header, { yPercent: -100 });
      tl.set(paths, { drawSVG: "0% 100%" });
      tl.set(logo, { scale: 0, rotate: -64, autoAlpha: 0 });
      if (desktop) tl.set(heroBg, { clipPath: "ellipse(20% 0% at 100% 100%)" });
      tl.set(titleSplit.words, {
        willChange: "transform",
        display: "inline-block",
        transformOrigin: "top left",
        yPercent: -10,
        xPercent: 40,
        scaleY: 0.1,
        scaleX: 0.85,
        rotate: 8,
        opacity: 0,
      });
      tl.set(para, { opacity: 0, y: "-0.75em" });
      tl.set(btn, { opacity: 0, y: "-0.75em" });
      tl.set(egg, { opacity: 0 });
      tl.set(handSplit.words, { display: "inline-block" });
      tl.set(handSplit.chars, { display: "inline-block", opacity: 0, rotate: 22, x: "-0.25em", y: "0.5em" });
      tl.set(seq, { opacity: 0, scale: 1.15, rotate: 6 });

      tl.to(
        paths,
        {
          keyframes: {
            "95%": { strokeWidth: 90, ease: "circ.out" },
            "100%": { drawSVG: "100% 100%" },
          },
          duration: 1.25,
          delay: 0.65,
        },
        "start",
      );
      tl.to(logo, { scale: 1, rotate: 0, autoAlpha: 1, delay: 0.05, duration: 0.65, ease: "elastic.out(1,0.72)" }, "start");
      tl.to(logo, { scale: 0, rotate: 64, autoAlpha: 0, delay: 0.5, duration: 0.6, ease: "elastic.in(1,0.72)" }, "start");
      tl.to(header, { yPercent: 0, duration: 0.5, delay: 0.5, ease: "energy" }, "start+=1.1");

      if (desktop) {
        tl.to(heroBg, { clipPath: "ellipse(150% 130% at 100% 100%)", duration: 1.1, delay: 0.2, ease: "circ.out" }, "start+=1.1");
      }
      tl.to(
        titleSplit.words,
        {
          keyframes: {
            "0%": { yPercent: -10, xPercent: 40, scaleY: 0.1, scaleX: 0.85, rotate: 8, opacity: 0 },
            "10%": { opacity: 1 },
            "100%": { yPercent: 0, xPercent: 0, scaleY: 1, scaleX: 1, rotate: 0, ease: "elastic.out(1,0.72)" },
          },
          duration: 0.875,
          stagger: 0.088,
          delay: 0.25,
        },
        "start+=1.1",
      );
      tl.to(para, { opacity: 1, y: "0em", duration: 0.35, delay: 0.45, ease: "energy" }, "start+=1.1");
      tl.to(btn, { opacity: 1, y: "0em", duration: 0.35, delay: 0.525, ease: "energy" }, "start+=1.1");
      tl.to(
        handSplit.chars,
        { opacity: 1, rotate: 0, x: "0em", y: "0em", ease: "elastic.out(1, 0.75)", duration: 0.75, delay: 0.45, stagger: 0.016 },
        "start+=1.1",
      );
      tl.to(egg, { opacity: 1, duration: 0.35, delay: 0.45, ease: "energy" }, "start+=1.1");
      tl.to(seq, { opacity: 1, scale: 1, rotate: 0, duration: 0.85, delay: 0.5, ease: "expo.out" }, "start+=1.1");
      tl.call(finish, undefined, 2.6);

      // wait for fonts so split text and trigger positions are measured with the real faces
      let started = false;
      const go = () => {
        if (started) return;
        started = true;
        tl.play();
      };
      document.fonts?.ready.then(() => requestAnimationFrame(go));
      window.setTimeout(go, 2500);
    }, el);

    const onResize = () => ScrollTrigger.refresh();
    window.addEventListener("load", onResize);

    return () => {
      window.removeEventListener("load", onResize);
      ctx.revert();
      gsap.ticker.remove(tick);
      lenis.destroy();
      ScrollTrigger.getAll().forEach((t) => t.kill());
    };
  }, []);

  // every "Upload your syllabus" button (href="#upload") goes to the app (sign in first if needed)
  useEffect(() => {
    const onClick = (e: MouseEvent) => {
      const a = (e.target as Element | null)?.closest?.('a[href="#upload"]');
      if (!a) return;
      e.preventDefault();
      navigate(signedIn.current ? "/app/new" : "/login?next=/app/new");
    };
    document.addEventListener("click", onClick, true);
    return () => document.removeEventListener("click", onClick, true);
  }, [navigate]);

  return (
    <div ref={root} className={`rq ${fontClassName}`} data-scrolling-started="false">
      <div className="transition" data-transition-wrap aria-hidden="true">
        <div className="transition__shape">
          <svg className="transition__svg" viewBox="0 0 1000 1000" preserveAspectRatio="none">
            {WIPE_PATHS.map((d) => (
              <path key={d} d={d} />
            ))}
          </svg>
        </div>
        <div className="transition__logo" data-transition-logo>
          <LogoMark className="transition__logo-svg" />
        </div>
      </div>

      <Header />

      <main className="main">
        <Hero />
        <Projects />
        <Flow />
        <BoxScroll />
        <Subjects />
        <Benefits />
        <Faq />
        <Study />
        <Badge />
        <Tools />
        <Ask />
      </main>

      <Footer />
    </div>
  );
}
