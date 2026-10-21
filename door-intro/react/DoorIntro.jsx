'use client';
// React / Next.js wrapper for DoorIntro.
//
// The component renders nothing itself: on the client it loads door-intro.js
// (copied next to this file by build.mjs) and lets it mount the overlay on
// <body>. On the server it renders nothing, so it is SSR- and SEO-safe.
//
//   import DoorIntro from './DoorIntro';
//   <DoorIntro preset="opendoors" imageUrl="/images/door-intro/arrington-founders.jpg" />
//
// Every option in door-intro/README.md can be passed as a prop. Options are
// read once on mount; change `force` (or remount with a new key) to re-run.
import { useEffect, useRef } from 'react';

export default function DoorIntro({ force = false, ...options }) {
  const optionsRef = useRef(options);
  optionsRef.current = options;

  useEffect(() => {
    let cancelled = false;
    let api = null;
    import('./door-intro.js').then((mod) => {
      if (cancelled) return;
      api = window.DoorIntro || mod.default || mod;
      api.init({ ...optionsRef.current, autoInit: false });
      if (force && !api.isPlaying()) api.play();
    });
    return () => {
      cancelled = true;
      if (api) api.destroy();
    };
  }, [force]);

  return null;
}

// Use from any button or link: onClick={replayDoorIntro}
export function replayDoorIntro() {
  if (typeof window !== 'undefined' && window.DoorIntro) window.DoorIntro.replay();
}
