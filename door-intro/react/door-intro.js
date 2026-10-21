/*!
 * DoorIntro v1.0.0 — cinematic "opening doors" website entrance.
 * Dependency-free, brand-neutral, accessible. Adds a fixed overlay on top of
 * an existing page; it never rewrites, hides or reorders the page's content.
 *
 * Configuration sources (later wins):
 *   built-in defaults → preset → build defaults → window.DoorIntroConfig
 *   → data-* attributes on the <script> tag → DoorIntro.init(options)
 *
 * Public API (window.DoorIntro, or module.exports under CommonJS):
 *   init(options)  merge options and play if the play policy allows it
 *   play()         play now, ignoring the play policy
 *   replay()       alias of play()
 *   skip()         end the intro immediately
 *   reset()        forget that the intro was seen
 *   destroy()      remove everything this script added
 *   isPlaying()    true while the overlay is on screen
 *   config()       a copy of the resolved configuration
 *
 * Events dispatched on document: "doorintro:start", "doorintro:complete"
 * (detail.reason is "complete", "skip" or "destroy").
 */
(function (root, factory) {
  var currentScript = typeof document !== 'undefined' ? document.currentScript : null;
  var api = factory(root, currentScript);
  var commonjs = typeof module === 'object' && module && module.exports;
  if (commonjs) module.exports = api;
  if (root && typeof root === 'object' && root.document) {
    root.DoorIntro = api;
    // Auto-init only when loaded through a classic <script> tag. Bundlers
    // (React, Next.js, Vite) import the file and call init() themselves.
    if (currentScript && !commonjs) api.__autoInit();
  }
})(typeof window !== 'undefined' ? window : this, function (win, currentScript) {
  'use strict';

  var VERSION = '1.0.0';

  // Replaced by build.mjs for brand-specific distributions.
  var BUILD_DEFAULTS = {} /*@build-defaults*/;

  var PRESETS = {
    neutral: {
      brandName: '',
      primaryColor: '#0e0f12',
      accentColor: '#b9a27a',
      accentColor2: '#e4d6b8',
      textColor: '#ffffff',
      welcomeText: 'Welcome',
      revealText: ''
    },
    opendoors: {
      brandName: 'Open Doors Financial Group',
      primaryColor: '#080808',
      accentColor: '#C9A24A',
      accentColor2: '#E8D18A',
      textColor: '#FFFFFF',
      doorStyle: 'classic',
      welcomeText: 'Your Future Begins With an Open Door.',
      revealText: 'Education. Protection. Opportunity. Legacy.',
      imageAlt: 'Rashon and Marie Arrington, founders of Open Doors Financial Group'
    }
  };

  var DEFAULTS = {
    preset: 'neutral',
    // Brand
    brandName: '',
    logoUrl: '',
    logoAlt: '',
    logoHeight: 72,
    // Scene revealed behind the doors
    imageUrl: '',
    imageSrcset: '',
    imageSizes: '100vw',
    imageAlt: '',
    imagePosition: 'center 35%',
    imageTimeout: 1500,
    // Copy
    welcomeText: 'Welcome',
    revealText: '',
    // Colors and style
    primaryColor: '#0e0f12',
    accentColor: '#b9a27a',
    accentColor2: '#e4d6b8',
    textColor: '#ffffff',
    doorColor: '',
    doorStyle: 'classic',          // classic | modern | glass
    showHandles: true,
    showFrame: true,
    fontDisplay: '"Cormorant Garamond", "Playfair Display", "Bodoni 72", Didot, Georgia, "Times New Roman", serif',
    fontBody: 'system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
    // Timing
    duration: 4500,                // total ms, clamped to 2500–8000
    // Play policy
    playMode: 'session',           // session | once | always | manual
    storageKey: 'door-intro:seen',
    urlParam: 'doorintro',         // ?doorintro=1 forces, ?doorintro=0 disables
    reducedMotion: 'fade',         // fade | skip
    skipForBots: true,
    // Controls
    skipButton: true,
    skipLabel: 'Skip intro',
    clickToSkip: true,
    skipOnScroll: true,
    replayButton: 'floating',      // floating | none
    replayLabel: 'Replay intro',
    replayPosition: 'bottom-left', // bottom-left | bottom-right | top-left | top-right
    replaySelector: '[data-door-intro-replay]',
    // Optional sound. Never autoplays: a toggle appears and sound plays only
    // after the visitor presses it.
    soundUrl: '',
    soundLabel: 'Play sound',
    zIndex: 2147483000,
    autoInit: true,
    onStart: null,
    onComplete: null
  };

  var BOT_RE = /bot\b|crawler|spider|slurp|bingpreview|facebookexternalhit|embedly|linkedinbot|twitterbot|whatsapp|telegrambot|discordbot|applebot|yandex|baiduspider|duckduckbot|semrush|ahrefs|mediapartners/i;
  var STYLE_ID = 'door-intro-styles';
  var ROOT_CLASS = 'door-intro-active';
  var PENDING_CLASS = 'door-intro-pending';

  var cfg = null;
  var state = null;      // active playback state
  var replayEl = null;
  var replayHandler = null;

  // ---------------------------------------------------------------- utils

  function assign(target) {
    for (var i = 1; i < arguments.length; i++) {
      var src = arguments[i];
      if (!src) continue;
      for (var k in src) {
        if (Object.prototype.hasOwnProperty.call(src, k) && src[k] !== undefined) target[k] = src[k];
      }
    }
    return target;
  }

  function coerce(value, sample) {
    if (typeof value !== 'string') return value;
    if (typeof sample === 'number') {
      var n = parseFloat(value);
      return isNaN(n) ? sample : n;
    }
    if (typeof sample === 'boolean') return !/^(false|0|no|off)$/i.test(value);
    return value;
  }

  function readDataAttributes(script) {
    var out = {};
    if (!script || !script.dataset) return out;
    for (var key in script.dataset) {
      if (!Object.prototype.hasOwnProperty.call(script.dataset, key)) continue;
      var sample = DEFAULTS[key];
      out[key] = coerce(script.dataset[key], sample);
    }
    return out;
  }

  function hexToRgb(hex) {
    var h = String(hex || '').trim().replace('#', '');
    if (h.length === 3) h = h.replace(/./g, function (c) { return c + c; });
    if (!/^[0-9a-f]{6}$/i.test(h)) return null;
    return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)];
  }

  function mix(a, b, t) {
    var x = hexToRgb(a), y = hexToRgb(b);
    if (!x || !y) return a;
    var r = [0, 1, 2].map(function (i) { return Math.round(x[i] + (y[i] - x[i]) * t); });
    return '#' + r.map(function (v) { return ('0' + v.toString(16)).slice(-2); }).join('');
  }

  function rgba(hex, alpha) {
    var c = hexToRgb(hex);
    return c ? 'rgba(' + c[0] + ',' + c[1] + ',' + c[2] + ',' + alpha + ')' : hex;
  }

  function storage(kind) {
    try {
      var s = win[kind];
      var probe = '__door_intro__';
      s.setItem(probe, '1');
      s.removeItem(probe);
      return s;
    } catch (e) {
      return null;
    }
  }

  function el(tag, className, attrs) {
    var node = document.createElement(tag);
    if (className) node.className = className;
    if (attrs) for (var k in attrs) node.setAttribute(k, attrs[k]);
    return node;
  }

  function prefersReducedMotion() {
    return !!(win.matchMedia && win.matchMedia('(prefers-reduced-motion: reduce)').matches);
  }

  function clearPending() {
    document.documentElement.classList.remove(PENDING_CLASS);
  }

  // --------------------------------------------------------------- config

  function resolveConfig(options) {
    var user = assign({}, BUILD_DEFAULTS, win.DoorIntroConfig, readDataAttributes(currentScript), options);
    var preset = PRESETS[user.preset] ? user.preset : 'neutral';
    var resolved = assign({}, DEFAULTS, PRESETS[preset], user);
    resolved.preset = preset;
    resolved.duration = Math.min(8000, Math.max(2500, Number(resolved.duration) || DEFAULTS.duration));
    return resolved;
  }

  function urlOverride(c) {
    try {
      var v = new URLSearchParams(win.location.search).get(c.urlParam);
      if (v === null) return null;
      if (/^(0|off|false|no)$/i.test(v)) return false;
      return true;
    } catch (e) {
      return null;
    }
  }

  function seenStore(c) {
    if (c.playMode === 'once') return storage('localStorage');
    if (c.playMode === 'session') return storage('sessionStorage');
    return null;
  }

  function shouldPlay(c) {
    var forced = urlOverride(c);
    if (forced !== null) return forced;
    if (c.skipForBots && BOT_RE.test(navigator.userAgent || '')) return false;
    if (c.playMode === 'manual') return false;
    if (c.playMode === 'always') return true;
    var store = seenStore(c);
    return !(store && store.getItem(c.storageKey));
  }

  function markSeen(c) {
    var store = seenStore(c);
    if (store) store.setItem(c.storageKey, String(Date.now()));
  }

  // ---------------------------------------------------------------- styles

  var CSS = [
    '.di-root{position:fixed;inset:0;z-index:var(--di-z);overflow:hidden;background:var(--di-primary);color:var(--di-text);font-family:var(--di-font-body);line-height:1.3;-webkit-font-smoothing:antialiased;opacity:1;contain:layout paint style;transition:opacity var(--di-leave-ms) ease;-webkit-tap-highlight-color:transparent;text-align:center}',
    '.di-root *,.di-root *::before,.di-root *::after{box-sizing:border-box;margin:0;padding:0}',
    '.di-root.di--leave{opacity:0;pointer-events:none}',
    '.di-root.di--leave *{pointer-events:none!important}',

    /* revealed scene */
    '.di-scene{position:absolute;inset:0;background:radial-gradient(ellipse 70% 60% at 50% 42%,var(--di-accent-a22),transparent 70%),var(--di-primary)}',
    '.di-photo{position:absolute;inset:0;width:100%;height:100%;max-width:none;object-fit:cover;object-position:var(--di-img-pos);opacity:0;transform:scale(1.14);transition:opacity .6s ease,transform calc(var(--di-open-ms) * 2.4) cubic-bezier(.2,.7,.2,1)}',
    '.di--img-ready .di-photo{opacity:1}',
    '.di--open .di-photo{transform:scale(1.02)}',
    '.di-scrim{position:absolute;inset:0;background:linear-gradient(to top,rgba(0,0,0,.78) 0%,rgba(0,0,0,.28) 34%,rgba(0,0,0,0) 58%),radial-gradient(ellipse at center,rgba(0,0,0,0) 55%,rgba(0,0,0,.55) 100%)}',
    '.di-fallback{position:absolute;inset:0;display:none;flex-direction:column;align-items:center;justify-content:center;gap:18px;padding:24px}',
    '.di--no-img .di-fallback{display:flex}',
    '.di-fallback .di-mark{width:clamp(56px,9vw,96px);height:auto;color:var(--di-accent)}',
    '.di-fallback .di-wordmark{font-size:clamp(1.05rem,2.8vw,1.9rem)}',
    '.di-reveal{position:absolute;left:0;right:0;bottom:max(10vh,92px);padding:0 24px;opacity:0;transform:translateY(16px);transition:opacity .9s ease,transform .9s ease}',
    '.di--reveal .di-reveal{opacity:1;transform:none}',
    '.di-reveal-text{font-family:var(--di-font-display);font-weight:500;font-size:clamp(1.05rem,2.6vw,2.1rem);letter-spacing:.1em;color:var(--di-text);text-shadow:0 2px 18px rgba(0,0,0,.7)}',
    '.di-rule{display:block;width:clamp(64px,10vw,120px);height:1px;margin:14px auto 0;background:linear-gradient(90deg,transparent,var(--di-accent2),transparent)}',
    '.di-reveal-brand{display:block;margin-top:12px;font-size:clamp(.62rem,1.1vw,.8rem);letter-spacing:.32em;text-transform:uppercase;color:var(--di-accent2)}',

    /* doorway */
    '.di-doorway{position:absolute;inset:0;perspective:max(480px,130vw);perspective-origin:50% 45%;transition:opacity .5s ease}',
    '.di-door{position:absolute;top:0;bottom:0;width:50.2%;backface-visibility:hidden;will-change:transform}',
    '.di-door--left{left:0;transform-origin:0 50%}',
    '.di-door--right{right:0;transform-origin:100% 50%}',
    /* Doors swing toward the viewer: a soft unlatch, a slow visible swing,
       then they accelerate past the camera. */
    '.di--open .di-door--left{animation:di-open-left var(--di-open-ms) linear forwards}',
    '.di--open .di-door--right{animation:di-open-right var(--di-open-ms) linear forwards}',
    '@keyframes di-open-left{0%{transform:rotateY(0);animation-timing-function:cubic-bezier(.3,0,.5,1)}12%{transform:rotateY(-3deg);animation-timing-function:cubic-bezier(.45,0,.55,1)}72%{transform:rotateY(-48deg);animation-timing-function:cubic-bezier(.55,0,.9,.6)}100%{transform:rotateY(-100deg)}}',
    '@keyframes di-open-right{0%{transform:rotateY(0);animation-timing-function:cubic-bezier(.3,0,.5,1)}12%{transform:rotateY(3deg);animation-timing-function:cubic-bezier(.45,0,.55,1)}72%{transform:rotateY(48deg);animation-timing-function:cubic-bezier(.55,0,.9,.6)}100%{transform:rotateY(100deg)}}',
    '.di--revealed .di-doorway{opacity:0}',
    '.di-face{position:absolute;inset:0;overflow:hidden;background:repeating-linear-gradient(90deg,rgba(255,255,255,.012) 0 2px,rgba(0,0,0,.035) 2px 5px,rgba(255,255,255,0) 5px 9px),linear-gradient(90deg,var(--di-door-dark),var(--di-door) 22%,var(--di-door-light) 52%,var(--di-door) 80%,var(--di-door-dark))}',
    '.di-door--left .di-face{box-shadow:inset -2px 0 0 rgba(0,0,0,.75),inset -3px 0 0 var(--di-accent-a35),inset 18px 0 40px rgba(0,0,0,.45)}',
    '.di-door--right .di-face{box-shadow:inset 2px 0 0 rgba(0,0,0,.75),inset 3px 0 0 var(--di-accent-a35),inset -18px 0 40px rgba(0,0,0,.45)}',
    '.di-face::after{content:"";position:absolute;inset:0;background:#000;opacity:0;transition:opacity var(--di-open-ms) ease}',
    '.di--open .di-face::after{opacity:.4}',
    '.di-panels{position:absolute;inset:clamp(28px,7vh,72px) clamp(16px,11%,64px);display:grid;grid-template-columns:1fr 1fr;grid-template-rows:1fr 2.3fr 1.25fr;gap:clamp(12px,2.6vh,28px) clamp(10px,7%,28px)}',
    '.di-panel{position:relative;border-radius:2px;background:linear-gradient(160deg,var(--di-door-light),var(--di-door) 45%,var(--di-door-dark));box-shadow:inset 0 0 0 1px rgba(0,0,0,.6),inset 0 0 0 clamp(5px,.9vw,9px) var(--di-door),inset 0 0 0 calc(clamp(5px,.9vw,9px) + 1px) var(--di-accent-a45),inset 10px 12px 22px rgba(0,0,0,.55),inset -6px -8px 16px rgba(255,255,255,.035),0 1px 0 rgba(255,255,255,.05),0 -1px 0 rgba(0,0,0,.7)}',
    '.di-panel::before{content:"";position:absolute;inset:clamp(14px,2.1vw,24px);border:1px solid var(--di-accent-a22);border-radius:1px}',
    '@media (max-width:820px){.di-panels{grid-template-columns:1fr}.di-panel:nth-child(n+4){display:none}}',
    '.di-style-modern .di-panel{background:none;box-shadow:none}',
    '.di-style-modern .di-panel::before{display:none}',
    '.di-style-modern .di-panels::before,.di-style-modern .di-panels::after{content:"";position:absolute;top:-4%;bottom:-4%;width:1px;background:linear-gradient(to bottom,transparent,var(--di-accent-a60) 15%,var(--di-accent-a60) 85%,transparent)}',
    '.di-style-modern .di-panels::before{left:22%}',
    '.di-style-modern .di-panels::after{left:30%}',
    '.di-style-modern .di-door--right .di-panels::before{left:auto;right:22%}',
    '.di-style-modern .di-door--right .di-panels::after{left:auto;right:30%}',
    '.di-style-glass .di-panel{background:linear-gradient(160deg,rgba(255,255,255,.14),rgba(255,255,255,.03) 50%,rgba(255,255,255,.08));box-shadow:inset 0 0 0 1px var(--di-accent-a60),inset 0 0 30px rgba(0,0,0,.35)}',
    '.di-style-glass .di-panel::before{border-color:rgba(255,255,255,.08)}',
    '.di-handle{position:absolute;top:50%;width:clamp(7px,.8vw,13px);height:clamp(110px,26vh,260px);transform:translateY(-50%);border-radius:999px;background:linear-gradient(90deg,var(--di-accent-dark),var(--di-accent) 30%,var(--di-accent2) 46%,#fff9e8 52%,var(--di-accent) 64%,var(--di-accent-dark));box-shadow:0 8px 16px rgba(0,0,0,.65),0 0 0 1px rgba(0,0,0,.35)}',
    '.di-handle::before,.di-handle::after{content:"";position:absolute;left:50%;width:clamp(10px,1.2vw,18px);height:6px;transform:translateX(-50%);border-radius:2px;background:linear-gradient(var(--di-accent2),var(--di-accent-dark));box-shadow:0 3px 6px rgba(0,0,0,.6)}',
    '.di-handle::before{top:12%}',
    '.di-handle::after{bottom:12%}',
    '.di-door--left .di-handle{right:clamp(14px,5%,36px)}',
    '.di-door--right .di-handle{left:clamp(14px,5%,36px)}',
    '.di-seam{position:absolute;top:0;bottom:0;left:50%;width:2px;transform:translateX(-50%);background:linear-gradient(to bottom,transparent,var(--di-accent2) 18%,#fff 50%,var(--di-accent2) 82%,transparent);box-shadow:0 0 18px 3px var(--di-accent-a60),0 0 70px 14px var(--di-accent-a22);opacity:0;transition:opacity .9s ease}',
    '.di--in .di-seam{opacity:.85}',
    '.di--open .di-seam{opacity:0;transition-duration:.45s}',
    '.di-bloom{position:absolute;inset:0;pointer-events:none;opacity:0;background:radial-gradient(ellipse 40% 70% at 50% 50%,rgba(255,250,235,.55),var(--di-accent-a22) 45%,transparent 75%)}',
    '.di--open .di-bloom{animation:di-bloom var(--di-open-ms) ease-out forwards}',
    '@keyframes di-bloom{0%{opacity:0}25%{opacity:1}100%{opacity:0}}',
    '.di-frame{position:absolute;inset:0;pointer-events:none;box-shadow:inset 0 0 0 var(--di-frame-w) var(--di-door-dark),inset 0 0 0 calc(var(--di-frame-w) + 1px) var(--di-accent-a60),inset 0 0 0 calc(var(--di-frame-w) + 3px) rgba(0,0,0,.6),inset 0 0 90px rgba(0,0,0,.75);transition:transform 1.4s cubic-bezier(.2,.7,.2,1),opacity 1.1s ease}',
    '.di--reveal .di-frame{transform:scale(1.18);opacity:0}',

    /* crest: logo + welcome text */
    '.di-crest{position:absolute;left:50%;top:max(23%,calc(50% - 13vh - 150px));width:min(92vw,760px);transform:translate(-50%,-50%);display:flex;flex-direction:column;align-items:center;gap:clamp(12px,2.2vh,22px);opacity:0;transition:opacity .9s ease,transform 1.2s cubic-bezier(.2,.7,.2,1);pointer-events:none}',
    '.di--in .di-crest{opacity:1}',
    '.di--open .di-crest{opacity:0;transform:translate(-50%,-50%) scale(1.06);transition-duration:.55s,1s}',
    '.di-logo{display:block;height:var(--di-logo-h);width:auto;max-width:min(70vw,420px);object-fit:contain;filter:drop-shadow(0 4px 14px rgba(0,0,0,.6))}',
    '.di-mark{display:block;width:clamp(44px,6vw,64px);height:auto;color:var(--di-accent);filter:drop-shadow(0 2px 10px rgba(0,0,0,.6))}',
    '.di-wordmark{font-family:var(--di-font-display);font-weight:600;font-size:clamp(.9rem,2.1vw,1.35rem);letter-spacing:.26em;text-transform:uppercase;color:var(--di-accent2);text-shadow:0 2px 14px rgba(0,0,0,.75)}',
    '.di-welcome{font-family:var(--di-font-display);font-weight:500;font-style:italic;font-size:clamp(1.25rem,3.6vw,2.6rem);line-height:1.2;color:var(--di-text);text-shadow:0 2px 20px rgba(0,0,0,.85);padding:0 12px}',

    /* controls */
    '.di-root .di-btn{position:absolute;bottom:max(18px,env(safe-area-inset-bottom));display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:44px;min-width:44px;padding:0 18px;border:1px solid var(--di-accent-a60);border-radius:999px;background:rgba(0,0,0,.42);color:var(--di-text);font:600 11px/1 var(--di-font-body);letter-spacing:.22em;text-transform:uppercase;cursor:pointer;opacity:.82;-webkit-backdrop-filter:blur(6px);backdrop-filter:blur(6px);transition:opacity .2s ease,background .2s ease,border-color .2s ease}',
    '.di-root .di-btn:hover{opacity:1;background:rgba(0,0,0,.65);border-color:var(--di-accent2)}',
    '.di-root .di-btn:focus-visible,.di-replay:focus-visible{outline:2px solid var(--di-accent2);outline-offset:3px;opacity:1}',
    '.di-root .di-skip{right:max(18px,env(safe-area-inset-right))}',
    '.di-root .di-sound{left:max(18px,env(safe-area-inset-left));letter-spacing:.14em}',
    '.di-replay{position:fixed;z-index:var(--di-z);display:inline-flex;align-items:center;justify-content:center;width:42px;height:42px;padding:0;margin:0;border:1px solid var(--di-accent-a60);border-radius:50%;background:var(--di-replay-bg);color:var(--di-accent2);cursor:pointer;opacity:.6;box-shadow:0 4px 14px rgba(0,0,0,.35);transition:opacity .2s ease,transform .2s ease;animation:di-fade-in .5s ease both}',
    '.di-replay:hover{opacity:1;transform:scale(1.06)}',
    '.di-replay svg{width:18px;height:18px;display:block}',
    '.di-replay--bottom-left{left:max(14px,env(safe-area-inset-left));bottom:max(14px,env(safe-area-inset-bottom))}',
    '.di-replay--bottom-right{right:max(14px,env(safe-area-inset-right));bottom:max(14px,env(safe-area-inset-bottom))}',
    '.di-replay--top-left{left:max(14px,env(safe-area-inset-left));top:max(14px,env(safe-area-inset-top))}',
    '.di-replay--top-right{right:max(14px,env(safe-area-inset-right));top:max(14px,env(safe-area-inset-top))}',
    '@keyframes di-fade-in{from{opacity:0}}',
    '.di-sr{position:absolute!important;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}',

    /* reduced-motion fade variant: no doors, opacity only */
    '.di-reduced .di-photo{transform:none;transition:opacity .4s ease}',
    '.di-reduced .di-reveal{transform:none;transition:opacity .4s ease}',
    '.di-reduced .di-crest{top:auto;bottom:calc(max(10vh,92px) + 84px);transform:translateX(-50%);opacity:1;transition:none}',
    '@media (prefers-reduced-motion:reduce){.di-replay{animation:none;transition:none}}',
    '@media print{.di-root,.di-replay{display:none!important}}'
  ].join('\n');

  function injectStyles() {
    if (document.getElementById(STYLE_ID)) return;
    var style = el('style', null, { id: STYLE_ID });
    style.textContent = CSS;
    (document.head || document.documentElement).appendChild(style);
  }

  function cssVars(c, node) {
    var door = c.doorColor || mix(c.primaryColor, c.accentColor, 0.13);
    var vars = {
      '--di-z': String(c.zIndex),
      '--di-primary': c.primaryColor,
      '--di-text': c.textColor,
      '--di-accent': c.accentColor,
      '--di-accent2': c.accentColor2,
      '--di-accent-dark': mix(c.accentColor, '#000000', 0.45),
      '--di-accent-a22': rgba(c.accentColor, 0.22),
      '--di-accent-a35': rgba(c.accentColor, 0.35),
      '--di-accent-a45': rgba(c.accentColor, 0.45),
      '--di-accent-a60': rgba(c.accentColor, 0.6),
      '--di-door': door,
      '--di-door-light': mix(door, '#ffffff', 0.07),
      '--di-door-dark': mix(door, '#000000', 0.5),
      '--di-frame-w': 'clamp(6px,1.1vw,16px)',
      '--di-img-pos': c.imagePosition,
      '--di-logo-h': 'clamp(40px,' + (c.logoHeight / 9).toFixed(2) + 'vh,' + c.logoHeight + 'px)',
      '--di-font-display': c.fontDisplay,
      '--di-font-body': c.fontBody,
      '--di-replay-bg': rgba(c.primaryColor, 0.78)
    };
    for (var k in vars) node.style.setProperty(k, vars[k]);
  }

  // ----------------------------------------------------------------- build

  var DOOR_MARK = '<svg class="di-mark" viewBox="0 0 64 64" fill="none" aria-hidden="true" focusable="false">' +
    '<path d="M14 58V24a18 18 0 0 1 36 0v34" stroke="currentColor" stroke-width="2.4"/>' +
    '<path d="M20 58V26a12 12 0 0 1 12-12v44H20z" fill="currentColor" fill-opacity=".18" stroke="currentColor" stroke-width="1.6"/>' +
    '<path d="M44 58V26a12 12 0 0 0-12-12" stroke="currentColor" stroke-width="1.6"/>' +
    '<circle cx="28.5" cy="38" r="1.6" fill="currentColor"/><path d="M8 58h48" stroke="currentColor" stroke-width="2.4"/></svg>';

  var REPLAY_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M3 12a9 9 0 1 0 3-6.7"/><path d="M3 4v5h5"/></svg>';

  function textNode(tag, className, text) {
    var node = el(tag, className);
    node.textContent = text;
    return node;
  }

  function brandBlock(c, container) {
    if (c.logoUrl) {
      var logo = el('img', 'di-logo', { src: c.logoUrl, alt: c.logoAlt || c.brandName || '', decoding: 'async' });
      logo.addEventListener('error', function () {
        logo.remove();
        if (c.brandName) container.insertBefore(textNode('div', 'di-wordmark', c.brandName), container.firstChild);
      });
      container.appendChild(logo);
    } else {
      container.insertAdjacentHTML('beforeend', DOOR_MARK);
      if (c.brandName) container.appendChild(textNode('div', 'di-wordmark', c.brandName));
    }
  }

  function buildDoor(side, c) {
    var door = el('div', 'di-door di-door--' + side);
    var face = el('div', 'di-face');
    var panels = el('div', 'di-panels');
    for (var i = 0; i < 6; i++) panels.appendChild(el('div', 'di-panel'));
    face.appendChild(panels);
    if (c.showHandles) face.appendChild(el('div', 'di-handle'));
    door.appendChild(face);
    return door;
  }

  function buildOverlay(c, reduced) {
    var rootEl = el('div', 'di-root di-style-' + (/^(modern|glass)$/.test(c.doorStyle) ? c.doorStyle : 'classic'), {
      role: 'region',
      'aria-label': (c.brandName ? c.brandName + ' ' : '') + 'introduction',
      'data-nosnippet': '',
      id: 'door-intro'
    });
    if (reduced) rootEl.classList.add('di-reduced');
    cssVars(c, rootEl);

    // Scene behind the doors.
    var scene = el('div', 'di-scene', { 'aria-hidden': c.imageUrl && c.imageAlt ? 'false' : 'true' });
    var photo = null;
    if (c.imageUrl) {
      photo = el('img', 'di-photo', { alt: c.imageAlt || '', decoding: 'async', fetchpriority: 'high', draggable: 'false' });
      if (c.imageSrcset) {
        photo.setAttribute('srcset', c.imageSrcset);
        photo.setAttribute('sizes', c.imageSizes);
      }
      photo.src = c.imageUrl;
      scene.appendChild(photo);
    } else {
      rootEl.classList.add('di--no-img');
    }
    var fallback = el('div', 'di-fallback', { 'aria-hidden': 'true' });
    brandBlock(assign({}, c, { logoUrl: '' }), fallback);
    scene.appendChild(fallback);
    scene.appendChild(el('div', 'di-scrim'));
    if (c.revealText || c.brandName) {
      var reveal = el('div', 'di-reveal');
      if (c.revealText) {
        reveal.appendChild(textNode('p', 'di-reveal-text', c.revealText));
        reveal.appendChild(el('span', 'di-rule', { 'aria-hidden': 'true' }));
      }
      if (c.brandName && c.imageUrl) reveal.appendChild(textNode('span', 'di-reveal-brand', c.brandName));
      scene.appendChild(reveal);
    }
    rootEl.appendChild(scene);

    // Doors.
    if (!reduced) {
      var doorway = el('div', 'di-doorway', { 'aria-hidden': 'true' });
      doorway.appendChild(buildDoor('left', c));
      doorway.appendChild(buildDoor('right', c));
      doorway.appendChild(el('div', 'di-seam'));
      rootEl.appendChild(doorway);
      rootEl.appendChild(el('div', 'di-bloom', { 'aria-hidden': 'true' }));
      if (c.showFrame) rootEl.appendChild(el('div', 'di-frame', { 'aria-hidden': 'true' }));
    }

    // Crest with logo and welcome message (hidden once the doors open).
    var crest = el('div', 'di-crest');
    brandBlock(c, crest);
    if (c.welcomeText && !reduced) crest.appendChild(textNode('p', 'di-welcome', c.welcomeText));
    if (!reduced || !c.revealText) rootEl.appendChild(crest);

    // Controls.
    var skip = null;
    if (c.skipButton) {
      skip = el('button', 'di-btn di-skip', { type: 'button', 'aria-label': c.skipLabel + ' and go to the website' });
      skip.textContent = c.skipLabel;
      rootEl.appendChild(skip);
    }
    var sound = null;
    if (c.soundUrl) {
      sound = el('button', 'di-btn di-sound', { type: 'button', 'aria-pressed': 'false' });
      sound.textContent = '♪ ' + c.soundLabel;
      rootEl.appendChild(sound);
    }
    return { root: rootEl, photo: photo, skip: skip, sound: sound };
  }

  // -------------------------------------------------------------- playback

  function waitForImage(photo, timeout, done) {
    var finished = false;
    var timer = setTimeout(function () { finish(false); }, timeout);
    function finish(ok) {
      if (finished) return;
      finished = true;
      clearTimeout(timer);
      done(ok);
    }
    if (!photo) return finish(false);
    photo.addEventListener('error', function () { finish(false); }, { once: true });
    var ready = function () { finish(true); };
    if (photo.decode) {
      photo.decode().then(ready, function () {
        if (photo.complete && photo.naturalWidth) ready();
      });
    } else if (photo.complete && photo.naturalWidth) {
      ready();
    } else {
      photo.addEventListener('load', ready, { once: true });
    }
  }

  function later(fn, ms) {
    var id = setTimeout(fn, ms);
    state.timers.push(id);
    return id;
  }

  function on(target, type, fn, opts) {
    target.addEventListener(type, fn, opts);
    state.listeners.push(function () { target.removeEventListener(type, fn, opts); });
  }

  function play() {
    if (typeof document === 'undefined') return false;
    if (!cfg) cfg = resolveConfig();
    if (state) return false;
    var c = cfg;
    var reduced = prefersReducedMotion();
    if (reduced && c.reducedMotion === 'skip') {
      clearPending();
      markSeen(c);
      return false;
    }

    injectStyles();
    removeReplayButton();
    var parts = buildOverlay(c, reduced);
    var rootEl = parts.root;
    var D = c.duration;
    var times = reduced
      ? { inMs: 0, openMs: 0, leaveMs: 450, holdMs: Math.min(1800, D * 0.4) }
      : { inMs: Math.round(D * 0.2), openMs: Math.round(D * 0.36), leaveMs: Math.round(D * 0.2) };
    rootEl.style.setProperty('--di-open-ms', times.openMs + 'ms');
    rootEl.style.setProperty('--di-leave-ms', times.leaveMs + 'ms');

    state = {
      root: rootEl,
      timers: [],
      listeners: [],
      leaving: false,
      started: Date.now(),
      prevFocus: document.activeElement,
      audio: null
    };

    // First element in <body> so the skip button is the first tab stop.
    document.body.insertBefore(rootEl, document.body.firstChild);
    document.documentElement.classList.add(ROOT_CLASS);
    clearPending();

    // Input never gets trapped: Escape, any click, wheel or swipe ends it.
    var skipNow = function () { finish('skip'); };
    on(document, 'keydown', function (e) {
      if (e.key === 'Escape' || e.key === 'Esc') skipNow();
    });
    if (parts.skip) on(parts.skip, 'click', function (e) { e.stopPropagation(); skipNow(); });
    if (c.clickToSkip) on(rootEl, 'click', function (e) {
      if (parts.sound && parts.sound.contains(e.target)) return;
      skipNow();
    });
    if (c.skipOnScroll) {
      on(win, 'wheel', skipNow, { passive: true });
      on(win, 'touchmove', skipNow, { passive: true });
    }
    if (parts.sound) on(parts.sound, 'click', function (e) {
      e.stopPropagation();
      toggleSound(parts.sound);
    });

    var imageDone = !parts.photo;
    var introElapsed = false;
    var opened = false;

    function begin() {
      if (opened || !imageDone || !introElapsed) return;
      opened = true;
      if (reduced) {
        rootEl.classList.add('di--reveal');
        later(function () { finish('complete'); }, times.holdMs);
        return;
      }
      rootEl.classList.add('di--open');
      later(function () { rootEl.classList.add('di--reveal'); }, Math.round(times.openMs * 0.62));
      later(function () { rootEl.classList.add('di--revealed'); }, times.openMs);
      var hold = Math.max(600, D - times.inMs - times.openMs - times.leaveMs);
      later(function () { finish('complete'); }, times.openMs + hold);
    }

    function startTimeline() {
      // Next frame so the closed state paints before transitions start.
      win.requestAnimationFrame(function () {
        if (!state) return;
        rootEl.classList.add('di--in');
        later(function () { introElapsed = true; begin(); }, times.inMs);
      });
      if (parts.photo) {
        waitForImage(parts.photo, c.imageTimeout, function (ok) {
          if (!state) return;
          imageDone = true;
          rootEl.classList.add(ok ? 'di--img-ready' : 'di--no-img');
          begin();
        });
      }
    }

    // A tab opened in the background waits until it is visible.
    if (document.hidden) {
      var onVisible = function () {
        if (document.hidden) return;
        document.removeEventListener('visibilitychange', onVisible);
        if (state) startTimeline();
      };
      on(document, 'visibilitychange', onVisible);
    } else {
      startTimeline();
    }

    if (typeof c.onStart === 'function') safeCall(c.onStart);
    dispatch('doorintro:start', { reduced: reduced });
    return true;
  }

  function toggleSound(button) {
    if (!state) return;
    if (!state.audio) {
      state.audio = new Audio(cfg.soundUrl);
      state.audio.volume = 0.6;
    }
    var playing = button.getAttribute('aria-pressed') === 'true';
    if (playing) {
      state.audio.pause();
      button.setAttribute('aria-pressed', 'false');
    } else {
      var p = state.audio.play();
      if (p && p.catch) p.catch(function () {});
      button.setAttribute('aria-pressed', 'true');
    }
  }

  function finish(reason) {
    if (!state || state.leaving) return;
    var s = state;
    s.leaving = true;
    s.timers.forEach(clearTimeout);
    s.timers = [];
    var leaveMs = reason === 'skip' ? 350 : parseInt(s.root.style.getPropertyValue('--di-leave-ms'), 10) || 600;
    s.root.style.setProperty('--di-leave-ms', leaveMs + 'ms');
    s.root.classList.add('di--leave');
    markSeen(cfg);
    var focusInside = s.root.contains(document.activeElement);
    setTimeout(function () { teardown(reason, focusInside); }, leaveMs + 20);
  }

  function teardown(reason, restoreFocus) {
    var s = state;
    if (!s) return;
    s.timers.forEach(clearTimeout);
    s.listeners.forEach(function (off) { off(); });
    if (s.audio) s.audio.pause();
    if (s.root.parentNode) s.root.parentNode.removeChild(s.root);
    document.documentElement.classList.remove(ROOT_CLASS);
    state = null;
    if (restoreFocus) {
      var target = s.prevFocus && s.prevFocus !== document.body && document.contains(s.prevFocus)
        ? s.prevFocus
        : document.querySelector('main, [role="main"]');
      if (target) {
        if (!target.hasAttribute('tabindex') && !/^(A|BUTTON|INPUT|SELECT|TEXTAREA)$/.test(target.tagName)) {
          target.setAttribute('tabindex', '-1');
          target.addEventListener('blur', function () { target.removeAttribute('tabindex'); }, { once: true });
        }
        try { target.focus({ preventScroll: true }); } catch (e) { target.focus(); }
      }
    }
    if (reason !== 'destroy') {
      addReplayButton();
      if (typeof cfg.onComplete === 'function') safeCall(cfg.onComplete, reason);
    }
    dispatch('doorintro:complete', { reason: reason });
  }

  function addReplayButton() {
    if (!cfg || cfg.replayButton !== 'floating' || replayEl) return;
    injectStyles();
    replayEl = el('button', 'di-replay di-replay--' + cfg.replayPosition, {
      type: 'button',
      'aria-label': cfg.replayLabel,
      title: cfg.replayLabel,
      'data-nosnippet': ''
    });
    cssVars(cfg, replayEl);
    replayEl.innerHTML = REPLAY_ICON + '<span class="di-sr"></span>';
    replayEl.lastChild.textContent = cfg.replayLabel;
    replayEl.addEventListener('click', function () { play(); });
    document.body.appendChild(replayEl);
  }

  function removeReplayButton() {
    if (replayEl && replayEl.parentNode) replayEl.parentNode.removeChild(replayEl);
    replayEl = null;
  }

  function bindReplaySelector() {
    if (replayHandler || !cfg.replaySelector) return;
    replayHandler = function (e) {
      var target = e.target && e.target.closest ? e.target.closest(cfg.replaySelector) : null;
      if (!target) return;
      e.preventDefault();
      play();
    };
    document.addEventListener('click', replayHandler);
  }

  function safeCall(fn, arg) {
    try { fn(arg); } catch (e) { if (win.console) win.console.error('[DoorIntro]', e); }
  }

  function dispatch(name, detail) {
    try { document.dispatchEvent(new CustomEvent(name, { detail: detail })); } catch (e) { /* old browsers */ }
  }

  // ------------------------------------------------------------------- API

  function init(options) {
    if (typeof document === 'undefined') return api;
    cfg = resolveConfig(options);
    var run = function () {
      bindReplaySelector();
      if (shouldPlay(cfg)) {
        play();
      } else {
        clearPending();
        if (!(cfg.skipForBots && BOT_RE.test(navigator.userAgent || ''))) addReplayButton();
      }
    };
    if (document.body) run();
    else document.addEventListener('DOMContentLoaded', run, { once: true });
    return api;
  }

  var api = {
    version: VERSION,
    presets: PRESETS,
    init: init,
    play: function () { if (!cfg) cfg = resolveConfig(); return play(); },
    replay: function () { if (!cfg) cfg = resolveConfig(); return play(); },
    skip: function () { finish('skip'); },
    reset: function () {
      var c = cfg || resolveConfig();
      ['sessionStorage', 'localStorage'].forEach(function (k) {
        var s = storage(k);
        if (s) s.removeItem(c.storageKey);
      });
    },
    destroy: function () {
      if (state) {
        state.timers.forEach(clearTimeout);
        teardown('destroy', false);
      }
      removeReplayButton();
      if (replayHandler) document.removeEventListener('click', replayHandler);
      replayHandler = null;
      clearPending();
    },
    isPlaying: function () { return !!state; },
    config: function () { return assign({}, cfg); },
    __autoInit: function () {
      var c = resolveConfig();
      if (c.autoInit === false) return;
      init();
    }
  };

  return api;
});
