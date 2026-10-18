"use client";

// next/link replaced by a plain anchor (this app is not Next.js)
const Link = "a" as const;
import { useEffect, useRef, type ReactNode } from "react";
import { gsap } from "./gsap";
import { reducedMotion } from "./useGsap";

function Chars({ text }: { text: string }) {
  return (
    <>
      {Array.from(text).map((c, i) => (
        <span key={i} className="split-char">
          {c === " " ? " " : c}
        </span>
      ))}
    </>
  );
}

/** Port of the per-letter squash + elastic hover (initButton / initButtonAlt). */
function useCharHover(ref: React.RefObject<HTMLElement | null>) {
  useEffect(() => {
    const root = ref.current;
    if (!root) return;
    if (
      reducedMotion() ||
      !window.matchMedia("(hover: hover) and (pointer: fine)").matches
    )
      return;

    const chars = root.querySelectorAll<HTMLElement>(".split-char");
    if (!chars.length) return;

    gsap.set(chars, {
      display: "inline-block",
      transformOrigin: "center center",
      willChange: "transform",
    });

    const tl = gsap.timeline({ paused: true });
    tl.to(chars, {
      keyframes: {
        "0%": { yPercent: 0, scaleY: 1, rotate: 0 },
        "20%": { yPercent: 55, scaleY: 0.3, rotate: 17, ease: "power2.in" },
        "100%": {
          yPercent: 0,
          scaleY: 1,
          rotate: 0,
          ease: "elastic.out(1,0.4)",
        },
      },
      duration: 0.725,
      stagger: { amount: 0.225 },
    });

    const onEnter = () => tl.restart();
    const onLeave = () => {
      tl.pause();
      gsap.to(chars, {
        yPercent: 0,
        scaleY: 1,
        rotate: 0,
        duration: 0.2,
        ease: "power2.out",
        overwrite: "auto",
      });
    };

    root.addEventListener("mouseenter", onEnter);
    root.addEventListener("mouseleave", onLeave);
    root.addEventListener("focusin", onEnter);
    root.addEventListener("focusout", onLeave);
    return () => {
      root.removeEventListener("mouseenter", onEnter);
      root.removeEventListener("mouseleave", onLeave);
      root.removeEventListener("focusin", onEnter);
      root.removeEventListener("focusout", onLeave);
      tl.kill();
    };
  }, [ref]);
}

type Common = {
  href?: string;
  onClick?: () => void;
  children: string;
  className?: string;
  ariaLabel?: string;
  current?: boolean;
  type?: "button" | "submit";
  disabled?: boolean;
} & Record<`data-${string}`, string | boolean | undefined>;

function Wrapper({
  href,
  onClick,
  className,
  children,
  ariaLabel,
  innerRef,
  current,
  type = "button",
  disabled,
  ...rest
}: {
  href?: string;
  onClick?: () => void;
  className: string;
  children: ReactNode;
  ariaLabel?: string;
  innerRef: React.RefObject<HTMLElement | null>;
  current?: boolean;
  type?: "button" | "submit";
  disabled?: boolean;
}) {
  const props = {
    className,
    "aria-label": ariaLabel,
    "aria-current": current ? ("page" as const) : undefined,
    onClick,
    ...rest,
  };
  if (!href)
    return (
      <button
        type={type}
        disabled={disabled}
        ref={innerRef as React.RefObject<HTMLButtonElement>}
        {...props}
      >
        {children}
      </button>
    );
  if (href.startsWith("/"))
    return (
      <Link href={href} ref={innerRef as React.RefObject<HTMLAnchorElement>} {...props}>
        {children}
      </Link>
    );
  return (
    <a href={href} ref={innerRef as React.RefObject<HTMLAnchorElement>} {...props}>
      {children}
    </a>
  );
}

/** Pill button (nav, secondary actions). */
export function Button({ children, className = "", ...rest }: Common) {
  const ref = useRef<HTMLElement>(null);
  useCharHover(ref);
  return (
    <Wrapper className={`button ${className}`} innerRef={ref} {...rest}>
      <span className="button__bg" />
      <span className="button__inner">
        <span className="button__text" data-button-text>
          <Chars text={children} />
        </span>
      </span>
    </Wrapper>
  );
}

const Arrow = () => (
  <svg className="button-alt__icon" viewBox="0 0 14 12" fill="none" aria-hidden="true">
    <path
      d="M1 6h11M7.5 1.5 12 6l-4.5 4.5"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

/** Text + arrow button with the tilting halves (hero / CTA). */
export function ButtonAlt({ children, className = "", ...rest }: Common) {
  const ref = useRef<HTMLElement>(null);
  useCharHover(ref);
  return (
    <Wrapper className={`button-alt ${className}`} innerRef={ref} {...rest}>
      <span className="button-alt__text-wrap">
        <span className="button-alt__bg" />
        <span className="button-alt__text-outer">
          <span className="button-alt__text" data-button-alt-text>
            <Chars text={children} />
          </span>
        </span>
      </span>
      <span className="button-alt__icon-wrap">
        <span className="button-alt__bg" />
        <span className="button-alt__icon-outer">
          <Arrow />
        </span>
      </span>
    </Wrapper>
  );
}
