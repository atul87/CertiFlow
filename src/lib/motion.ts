/* ─────────────────────────────────────────────
   CERTIFLOW — Motion Configuration
   Central animation tokens for Motion library
   ───────────────────────────────────────────── */

export const duration = {
  instant: 0.1,
  micro: 0.15,
  normal: 0.25,
  emphasis: 0.4,
  large: 0.6,
} as const;

export const ease = {
  out: [0.22, 1, 0.36, 1] as const,
  inOut: [0.4, 0, 0.2, 1] as const,
  spring: [0.34, 1.56, 0.64, 1] as const,
};

/* Re-usable animation variants */
export const fadeIn = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: { duration: duration.normal, ease: ease.out },
  },
};

export const fadeInUp = {
  hidden: { opacity: 0, y: 24 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: duration.emphasis, ease: ease.out },
  },
};

export const fadeInDown = {
  hidden: { opacity: 0, y: -16 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: duration.normal, ease: ease.out },
  },
};

export const scaleIn = {
  hidden: { opacity: 0, scale: 0.95 },
  visible: {
    opacity: 1,
    scale: 1,
    transition: { duration: duration.emphasis, ease: ease.out },
  },
};

export const staggerContainer = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.08,
      delayChildren: 0.1,
    },
  },
};

export const staggerItem = {
  hidden: { opacity: 0, y: 16 },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: duration.emphasis, ease: ease.out },
  },
};

/* Scroll-triggered viewport settings */
export const viewportOnce = {
  once: true,
  margin: "-80px" as const,
};
