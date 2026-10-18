"use client";

import { useRef } from "react";
import { LogoMark } from "./art";
import { Button, ButtonAlt } from "./Button";
import { gsap, ScrollTrigger, SplitText } from "./gsap";
import { reducedMotion, useGsap } from "./useGsap";

const W = 34; // em
const T = 2.6; // page-stack thickness, em

/** wobbly handwriting-style line for the bullet rows */
function squiggle(x: number, y: number, len: number) {
  let d = `M${x} ${y}`;
  const seg = 18;
  const n = Math.max(1, Math.floor(len / seg));
  for (let i = 0; i < n; i++) d += ` q${seg / 4} ${i % 2 ? 7 : -7} ${seg / 2} 0 t${seg / 2} 0`;
  return d;
}

export function BoxScroll() {
  const wrap = useRef<HTMLDivElement>(null);

  useGsap(() => {
    const wrapEl = wrap.current!;
    const q = gsap.utils.selector(wrapEl);
    // GSAP may evaluate these lazily (even while reverting on unmount), so don't read the ref here
    const em = () => parseFloat(getComputedStyle(wrapEl).fontSize) || 16;
    // the notebook rig can be scaled via CSS on small screens; its em is what W and T are measured in
    const obEl = q(".ob")[0];
    const obEm = () => (obEl ? parseFloat(getComputedStyle(obEl).fontSize) : 0) || em();

    const tilt = q("[data-ob-tilt]")[0];
    const spin = q("[data-ob-spin]")[0];
    const cover = q("[data-ob-cover]")[0];
    const strokes = q("[data-ob-stroke]");
    const heading = q("[data-ob-heading]")[0];
    const highlight = q("[data-ob-highlight]")[0];
    const note = q("[data-ob-note]")[0];
    const handText = q("[data-box-sequence-handwritten-text]")[0];
    const title = q("[data-box-sequence-title]")[0];
    const finalText = q("[data-box-sequence-text-final]")[0];
    const buttons = q("[data-box-sequence-button]");
    const pageInk = q("[data-ob-ink]")[0];

    if (reducedMotion()) {
      gsap.set(cover, { rotationY: -179 });
      gsap.set([title, buttons, finalText], { autoAlpha: 1 });
      return;
    }

    /* ---- scrubbed 3D timeline ---- */
    const tl = gsap.timeline({ paused: true, defaults: { ease: "none" } });

    tl.fromTo(
      tilt,
      { rotationX: 62, y: () => 7 * obEm(), scale: 0.86 },
      { rotationX: 46, y: () => 0, scale: 0.9, duration: 0.34 },
      0,
    )
      .fromTo(spin, { rotationZ: -34 }, { rotationZ: -9, duration: 0.34 }, 0)
      .fromTo(
        cover,
        { rotationY: 0, z: () => (T + 0.3) * obEm() },
        { rotationY: -179, z: () => 0.4 * obEm(), duration: 0.34, ease: "power2.inOut" },
        0,
      )
      .fromTo(tilt, { x: 0 }, { x: () => (W / 2) * obEm() * 0.88, duration: 0.34 }, 0)
      // handwriting appears
      .fromTo(heading, { clipPath: "inset(0 100% 0 0)" }, { clipPath: "inset(0 0% 0 0)", duration: 0.07 }, 0.3)
      .fromTo(strokes, { drawSVG: "0%" }, { drawSVG: "100%", duration: 0.07, stagger: 0.026 }, 0.34)
      .fromTo(highlight, { scaleX: 0 }, { scaleX: 1, duration: 0.06 }, 0.52)
      // camera drifts overhead, then dives into the page
      .to(tilt, { rotationX: 30, duration: 0.3 }, 0.34)
      .to(spin, { rotationZ: -2, duration: 0.3 }, 0.34)
      .to(tilt, { rotationX: 4, scale: 2.35, y: () => -1.2 * obEm(), x: () => 0, duration: 0.22 }, 0.76)
      .to(spin, { rotationZ: 0, duration: 0.22 }, 0.76)
      .to(pageInk, { opacity: 0.22, duration: 0.14 }, 0.82)
      .set({}, {}, 1);

    /* ---- text beats (same thresholds as initBoxSequence) ---- */
    const handSplit = new SplitText(handText, { type: "words, chars", wordsClass: "split-word", charsClass: "split-char" });
    gsap.set(handSplit.words, { display: "inline-block" });
    gsap.set(handSplit.chars, { display: "inline-block", opacity: 0, rotate: 22, x: "-0.25em", y: "0.5em" });
    const handTl = gsap.timeline({ paused: true }).to(handSplit.chars, {
      opacity: 1,
      rotate: 0,
      x: "0em",
      y: "0em",
      ease: "elastic.out(1, 0.75)",
      duration: 0.625,
      stagger: 0.011,
    });

    const finalSplit = new SplitText(finalText, { type: "words, chars", wordsClass: "split-word", charsClass: "split-char" });
    gsap.set(finalSplit.words, { display: "inline-block" });
    gsap.set(finalSplit.chars, { display: "inline-block", opacity: 0, rotate: 22, x: "-0.25em", y: "0.5em" });
    gsap.set(title, { opacity: 0, y: "1em" });
    gsap.set(buttons, { rotate: gsap.utils.random(-16, 16), scale: 0 });
    gsap.set(note, { scale: 0, rotate: -24 });

    const finalTl = gsap.timeline({ paused: true });
    finalTl
      .to(finalSplit.chars, { opacity: 1, rotate: 0, x: "0em", y: "0em", ease: "elastic.out(1, 0.75)", duration: 0.625, stagger: 0.011 }, "start")
      .to(title, { opacity: 1, y: "0em", ease: "elastic.out(1, 0.75)", duration: 0.625 }, "start")
      .to(buttons, { rotate: 0, scale: 1, ease: "elastic.out(1, 0.75)", duration: 0.625, stagger: 0.026 }, "start+=0.15");

    const noteTl = gsap
      .timeline({ paused: true })
      .to(note, { scale: 1, rotate: 5, duration: 0.7, ease: "elastic.out(1, 0.72)" });

    let textState = "before";
    let finalState = "before";
    let noteState = false;

    const st = ScrollTrigger.create({
      trigger: wrapEl,
      start: "top top",
      end: "bottom bottom",
      scrub: 0.6,
      animation: tl,
      invalidateOnRefresh: true,
      onUpdate: (self) => {
        const p = self.progress;
        if (p >= 0.6) {
          if (textState !== "reversed") {
            handTl.timeScale(3.5).reverse();
            textState = "reversed";
          }
        } else if (p >= 0.3) {
          if (textState !== "played") {
            handTl.timeScale(1.5).play();
            textState = "played";
          }
        } else if (textState !== "before") {
          handTl.timeScale(3.5).reverse();
          textState = "before";
        }

        const showNote = p >= 0.62 && p < 0.8;
        if (showNote !== noteState) {
          noteState = showNote;
          noteTl.timeScale(showNote ? 1 : 3).reversed(!showNote).play();
        }

        if (p >= 0.81) {
          if (finalState !== "played") {
            finalTl.timeScale(1.25).play();
            finalState = "played";
          }
        } else if (finalState !== "before") {
          finalTl.timeScale(3.5).reverse();
          finalState = "before";
        }
      },
    });

    return () => {
      st.kill();
      handSplit.revert();
      finalSplit.revert();
    };
  }, wrap);

  return (
    <section className="box" data-box-sequence>
      <div className="box__wrap" ref={wrap}>
        <div className="box__sticky">
          <div className="box__element" data-box-sequence-element>
            <div className="box__scene" aria-hidden="true">
              <div className="ob-tilt" data-ob-tilt>
                <div className="ob-spin" data-ob-spin>
                  <div className="ob" style={{ "--W": `${W}em`, "--T": `${T}em` } as React.CSSProperties}>
                    <div className="ob__shadow" />
                    <div className="ob__plate" />

                    {/* page stack (cuboid, top face at z = T) */}
                    <div className="ob__block">
                      <div className="ob__face ob__edge ob__edge--r" />
                      <div className="ob__face ob__edge ob__edge--t" />
                      <div className="ob__face ob__edge ob__edge--b" />
                      <div className="ob__face ob__edge ob__edge--l" />
                      <div className="ob__face ob__page">
                        <div className="ob__ink" data-ob-ink>
                          <h3 className="ob__heading" data-ob-heading>
                            Normalization
                          </h3>
                          <svg className="ob__strokes" viewBox="0 0 340 460" fill="none">
                            <rect className="ob__highlight" data-ob-highlight x="46" y="170" width="236" height="22" rx="4" />
                            <path data-ob-stroke className="s-pink" d="M30 96c50 10 120-10 200 2" />
                            {[
                              [142, 220],
                              [182, 190],
                              [222, 250],
                              [262, 160],
                            ].map(([y, len], i) => (
                              <g key={i}>
                                <circle cx="36" cy={y - 2} r="3.5" className="s-dot" />
                                <path data-ob-stroke d={squiggle(52, y, len)} />
                              </g>
                            ))}
                            {/* little ER diagram */}
                            <rect data-ob-stroke x="34" y="318" width="86" height="48" rx="6" />
                            <rect data-ob-stroke x="214" y="318" width="86" height="48" rx="6" />
                            <path data-ob-stroke d="M120 342h94" />
                            <path data-ob-stroke d="M204 334l10 8-10 8" />
                            <path data-ob-stroke className="s-pink" d="M170 342l-8-12M170 342l-8 12" />
                            <path data-ob-stroke d="M52 330h50M52 346h34M232 330h50M232 346h34" />
                            <path data-ob-stroke d="M77 366v36h186v-36" />
                          </svg>
                        </div>
                        <div className="ob__note" data-ob-note>
                          <span className="ob__note-chip">Topic 1</span>
                          <p>Learn keys before normal forms.</p>
                        </div>
                      </div>
                    </div>

                    {/* hinged front cover */}
                    <div className="ob__cover" data-ob-cover>
                      <div className="ob__cover-out">
                        <span className="ob__cover-band" />
                        <span className="ob__cover-label hand">Syllabus</span>
                        <span className="ob__cover-sticker"><LogoMark /></span>
                      </div>
                      <div className="ob__cover-in">
                        <span className="hand ob__belongs">This syllabus belongs to</span>
                        <span className="hand ob__belongs-line">you</span>
                        <span className="hand ob__belongs ob__belongs--sm">Subject: Databases</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="box__text-wrap">
              <div className="box__text-outer">
                <p className="box__text hand" data-box-sequence-handwritten-text>
                  Open your syllabus and see the map
                </p>
              </div>
            </div>

            <div className="box__content">
              <h2 className="box__title" data-box-sequence-title>
                <span className="box__title-line">
                  See <em>inside</em>
                </span>
                <span className="box__title-hl">the syllabus.</span>
              </h2>
              <div className="box__content-text-wrap">
                <div className="box__content-text-outer">
                  <p className="box__content-text hand" data-box-sequence-text-final>
                    Made for planning your study
                  </p>
                </div>
              </div>
              <div className="box__action">
                <div className="box__button-wrap" data-box-sequence-button>
                  <ButtonAlt href="#upload">Upload your syllabus</ButtonAlt>
                </div>
                <div className="box__button-wrap" data-box-sequence-button>
                  <Button href="#how-it-works">See how it works</Button>
                </div>
              </div>
            </div>

            <div className="box__logo-easter-egg">
              <div className="box__logo-easter-egg-inner">
                <LogoMark className="egg" />
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
