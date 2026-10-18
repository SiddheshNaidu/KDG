import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { SplitText } from "gsap/SplitText";
import { DrawSVGPlugin } from "gsap/DrawSVGPlugin";
import { CustomEase } from "gsap/CustomEase";
import { InertiaPlugin } from "gsap/InertiaPlugin";

if (typeof window !== "undefined") {
  gsap.registerPlugin(
    ScrollTrigger,
    SplitText,
    DrawSVGPlugin,
    CustomEase,
    InertiaPlugin,
  );
  CustomEase.create("osmo", "0.625, 0.05, 0, 1");
  CustomEase.create("energy", "M0,0 C0.32,0.72 0,1 1,1");
  gsap.defaults({ ease: "osmo", duration: 0.6 });
}

export { gsap, ScrollTrigger, SplitText };
