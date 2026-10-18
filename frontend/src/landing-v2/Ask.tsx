"use client";

import { useRef } from "react";
import { ButtonAlt } from "./Button";
import { gsap, SplitText } from "./gsap";
import { reducedMotion, useGsap } from "./useGsap";

export function Ask() {
  const root = useRef<HTMLElement>(null);

  // Messages pop in one after another when the demo scrolls into view.
  useGsap(() => {
    if (reducedMotion()) return;
    const el = root.current!;
    const msgs = gsap.utils.toArray<HTMLElement>("[data-chat-msg]", el);
    const decor = gsap.utils.toArray<HTMLElement>("[data-ask-decor]", el);
    const answers = gsap.utils.toArray<HTMLElement>("[data-chat-type]", el);

    gsap.set(msgs, { opacity: 0, y: "1.2em", scale: 0.92, transformOrigin: "0 100%" });
    gsap.set(decor, { scale: 0, rotate: () => gsap.utils.random(-30, 30) });

    const splits = answers.map(
      (a) => new SplitText(a, { type: "words", wordsClass: "split-word" }),
    );
    splits.forEach((s) => gsap.set(s.words, { opacity: 0 }));

    const tl = gsap.timeline({
      scrollTrigger: { trigger: el.querySelector(".exclusive-slider__item"), start: "top 70%", once: true },
    });
    msgs.forEach((m, i) => {
      tl.to(m, { opacity: 1, y: "0em", scale: 1, duration: 0.7, ease: "elastic.out(1, 0.75)" }, i * 1.15);
      const s = splits.find((sp) => m.contains(sp.elements[0]));
      if (s) tl.to(s.words, { opacity: 1, duration: 0.01, stagger: 0.045 }, i * 1.15 + 0.25);
    });
    tl.to(decor, { scale: 1, rotate: (i, t) => t.dataset.rot ?? 0, duration: 0.95, ease: "elastic.out(1, 0.75)", stagger: 0.088 }, 0.2);
  }, root);

  return (
    <section ref={root} className="exclusive is--bg-white">
      <div className="exclusive__inner">
        <div className="exclusive__header u-container">
          <div className="exclusive__header-content">
            <h2 className="exclusive__title h-l">Pick a topic, see the path</h2>
            <p className="exclusive__paragraph p-regular">
              Choose any topic to get everything to learn before it, in order,
              plus the background your syllabus skips.
            </p>
          </div>
        </div>

        <div className="exclusive-slider__list-item">
          <div className="exclusive-slider__item">
            <div className="exclusive-slider__item-outer">
              <div className="exclusive-slider__item-inner">
                <div className="chat">
                  <div className="chat__head">
                    <span className="chat__title">Operating System</span>
                    <span className="chat__scope"><b>Goal</b><i>Path</i><i>Order</i></span>
                  </div>

                  <div className="chat__body">
                    <div className="chat__msg chat__msg--me" data-chat-msg>
                      I want to learn Virtual Memory
                    </div>
                    <div className="chat__msg chat__msg--ai" data-chat-msg>
                      <p data-chat-type>
                        Learn these first, in order: Memory Partitioning, Paging, Segmentation. Then Virtual Memory.
                      </p>
                      <span className="chat__chips"><b>Paging</b><b>Segmentation</b></span>
                    </div>
                    <div className="chat__msg chat__msg--me" data-chat-msg>
                      What about Deadlocks?
                    </div>
                    <div className="chat__msg chat__msg--ai chat__msg--none" data-chat-msg>
                      <p data-chat-type>Learn Processes and Semaphores first. Nothing outside the syllabus is needed.</p>
                    </div>
                  </div>

                  <div className="chat__input"><span>Choose a topic…</span><i aria-hidden="true">↑</i></div>
                </div>
              </div>

              <div className="exclusive-slider__add-on" aria-hidden="true">
                <div className="exclusive-slider__quote-01" data-ask-decor data-rot="-12">
                  <p className="exclusive-slider__handwritten-text hand">Built from your own syllabus</p>
                </div>
                <div className="exclusive-slider__quote-02" data-ask-decor data-rot="5">
                  <p className="exclusive-slider__handwritten-text hand is--quote-02">Pick any topic as your goal</p>
                </div>
                <span className="exclusive-slider__emoji exclusive-slider__emoji-01" data-ask-decor data-rot="-5">🔍</span>
                <span className="exclusive-slider__emoji exclusive-slider__emoji-02" data-ask-decor data-rot="-10">👀</span>
                <span className="exclusive-slider__emoji exclusive-slider__emoji-03" data-ask-decor data-rot="-10">✨</span>
                <div className="exclusive-slider__authors" data-ask-decor data-rot="4">
                  <h3 className="exclusive-slider__authors-title">Learn first</h3>
                  <p className="exclusive-slider__authors-paragraph">
                    Memory Partitioning
                    <br />
                    Paging
                  </p>
                </div>
              </div>

              <div className="exclusive-slider__cta">
                <ButtonAlt href="#upload">Upload your syllabus</ButtonAlt>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
