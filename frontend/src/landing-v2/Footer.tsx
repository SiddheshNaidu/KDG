"use client";

import { useRef } from "react";
import { LogoFull } from "./art";
import { Button, ButtonAlt } from "./Button";
import { Notebook3D } from "./Notebook3D";
import { gsap } from "./gsap";
import { reducedMotion, useGsap } from "./useGsap";

export function Footer() {
  const root = useRef<HTMLElement>(null);

  // Port of initFooterParallax (desktop): content slides down while the notebook rotates up.
  useGsap(() => {
    if (reducedMotion()) return;
    const mm = gsap.matchMedia();
    mm.add("(min-width: 991px)", () => {
      const el = root.current!;
      const tl = gsap.timeline({
        scrollTrigger: { trigger: el, start: "clamp(top bottom)", end: "clamp(top top)", scrub: 0.2 },
      });
      tl.fromTo("[data-footer-parallax-top]", { y: "-12.5em" }, { y: "0em", ease: "none" })
        .fromTo("[data-footer-parallax-bottom]", { y: "-12.5em" }, { y: "0em", ease: "none" }, "<")
        .fromTo(
          "[data-footer-parallax-visual]",
          { scale: 0.9, xPercent: -35, y: "17.5em", rotate: 30 },
          { scale: 1, xPercent: 0, y: "0em", rotate: 0, ease: "none" },
          "<",
        )
        .fromTo("[data-footer-parallax-overlay]", { opacity: 0.55 }, { opacity: 0, ease: "none" }, "<");
    });
  }, root);

  return (
    <footer ref={root} className="footer" data-footer-parallax>
      <div className="footer__top" data-footer-parallax-top>
        <div className="u-container">
          <div className="footer__top-inner">
            <div className="footer__top-nav">
              <LogoFull className="footer__logo" />
              <div className="footer__cta">
                <ButtonAlt href="#upload">Upload your syllabus</ButtonAlt>
                <Button href="#how-it-works">How it works</Button>
              </div>
              <ul className="footer__links">
                <li><a className="footer__link" href="#projects"><span className="footer__bottom-text">Example maps</span></a></li>
                <li><a className="footer__link" href="#tools"><span className="footer__bottom-text">Features</span></a></li>
                <li><a className="footer__link" href="#faq"><span className="footer__bottom-text">FAQ</span></a></li>
              </ul>
            </div>
            <div className="footer__top-form">
              <h3 className="footer__form-title h-xs">Ready to map your syllabus?</h3>
              <p className="footer__form-text">
                Upload a syllabus PDF and see its topics laid out in study order.
              </p>
              <div className="footer__form-cta">
                <ButtonAlt href="#upload">Upload your syllabus</ButtonAlt>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="footer__visual" aria-hidden="true">
        <div className="footer__visual-wrap" data-footer-parallax-visual>
          <Notebook3D w={26} h={36} d={3.6} cover="#3b308f" spine="#ff008c" label="KDG" className="footer__nb" />
        </div>
      </div>

      <div className="footer__bottom" data-footer-parallax-bottom>
        <div className="u-container">
          <div className="footer__bottom-inner">
            <div className="footer__bottom-copyright">
              <span className="footer__bottom-text">© 2026 KDG. All rights reserved.</span>
            </div>
            <div className="footer__bottom-credit">
              <span className="footer__bottom-text">Knowledge Dependency Graph</span>
            </div>
          </div>
        </div>
      </div>
      <div className="footer__overlay" data-footer-parallax-overlay />
    </footer>
  );
}
