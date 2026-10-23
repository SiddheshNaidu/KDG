"use client";

import { useEffect, useState } from "react";
import { Button, ButtonAlt } from "./Button";
import { BlobBg, LogoFull } from "./art";

const NAV = [
  { label: "Example maps", href: "#projects", id: "projects" },
  { label: "How it works", href: "#how-it-works", id: "how-it-works" },
  { label: "Features", href: "#tools", id: "tools" },
  { label: "FAQ", href: "#faq", id: "faq" },
];

export function Header() {
  const [active, setActive] = useState<string | null>(null);
  const [open, setOpen] = useState(false);

  // Mark the nav item whose section is in view (aria-current -> "index tabs" pop out).
  useEffect(() => {
    const els = NAV.map((n) => document.getElementById(n.id)).filter(
      Boolean,
    ) as HTMLElement[];
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((e) => {
          if (e.isIntersecting) setActive(e.target.id);
        });
      },
      { rootMargin: "-45% 0px -50% 0px" },
    );
    els.forEach((el) => io.observe(el));
    const onScroll = () => {
      if (window.scrollY < 200) setActive(null);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => {
      io.disconnect();
      window.removeEventListener("scroll", onScroll);
    };
  }, []);

  useEffect(() => {
    document.documentElement.classList.toggle("rq-menu-open", open);
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    window.addEventListener("keydown", onKey);
    return () => {
      document.documentElement.classList.remove("rq-menu-open");
      window.removeEventListener("keydown", onKey);
    };
  }, [open]);

  return (
    <>
      <header className="header" data-header>
        <div className="header__inner">
          <div className="header__title">
            <a className="header__title-link" href="#top" aria-label="KDG, back to top">
              <LogoFull />
            </a>
          </div>

          <nav className="header__nav" aria-label="Primary">
            <ul className="header__nav-list">
              {NAV.map((n) => (
                <li className="header__nav-list-item" key={n.id}>
                  <Button href={n.href} current={active === n.id}>
                    {n.label}
                  </Button>
                </li>
              ))}
            </ul>
          </nav>

          <div className="header__sub">
            <ul className="header__sub-list">
              <li className="header__sub-list-item">
                <ButtonAlt href="#upload">Upload your syllabus</ButtonAlt>
              </li>
            </ul>
          </div>

          <div className="header__menu-toggle">
            <ButtonAlt className="is--menu-toggle" onClick={() => setOpen(true)} ariaLabel="Open menu">
              Menu
            </ButtonAlt>
          </div>
        </div>
      </header>

      <div className={`menu ${open ? "is--active" : ""}`} data-menu aria-hidden={!open}>
        <div className="menu__inner">
          <div className="menu__bg">
            <BlobBg variant="menu" className="menu__bg-svg" animate={false} />
          </div>
          <div className="menu__content">
            <div className="menu__header">
              <a href="#top" onClick={() => setOpen(false)} className="header__title-link">
                <LogoFull />
              </a>
              <ButtonAlt onClick={() => setOpen(false)} ariaLabel="Close menu" className="is--menu-toggle">
                Close
              </ButtonAlt>
            </div>
            <nav className="menu__nav" aria-label="Mobile">
              <ul className="menu__nav-list">
                {NAV.map((n) => (
                  <li key={n.id} className="menu__nav-list-item">
                    <a href={n.href} className="menu__link h-m" onClick={() => setOpen(false)}>
                      {n.label}
                    </a>
                  </li>
                ))}
              </ul>
            </nav>
            <div className="menu__footer">
              <ButtonAlt href="#upload" onClick={() => setOpen(false)}>
                Upload your syllabus
              </ButtonAlt>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
