# DoorIntro — cinematic "opening doors" entrance

A reusable, dependency-free website entrance: a fullscreen doorway with two
detailed 3D doors that swing open toward the visitor. Behind them is a founder
portrait, team photo or branded scene. The overlay then fades away to reveal
the existing site, which is left untouched.

- About 9 KB gzipped, with no dependencies and no external fonts or requests other than your image.
- Three to five seconds by default (`duration: 4500`). Plays once per browser session by default.
- Sound is off. It never autoplays: when `soundUrl` is set, a toggle appears.
- Includes a skip button, Escape key, click-to-skip and scroll-to-skip, so visitors are never trapped.
- Shows a floating replay button afterwards. Any `[data-door-intro-replay]` element also replays the intro.
- When the visitor prefers reduced motion, it shows a short opacity-only fade with no 3D doors. You can also turn the intro off completely for them.
- Crawlers get the untouched page. The overlay carries `data-nosnippet` and is removed from the DOM when it finishes.
- No layout shift: the overlay is `position: fixed`, and the page underneath never moves (tested at CLS = 0).

## Files

| Path | Purpose |
|---|---|
| `src/door-intro.js` | Source of truth (readable). Styles are injected by the script. |
| `dist/door-intro(.min).js` | Brand-neutral build. |
| `dist/opendoors/door-intro(.min).js` | Open Doors Financial Group preset baked in, so the bare `<script src="/door-intro.js" defer>` tag works. |
| `snippets/head-prepaint.html` | Optional inline `<head>` guard that prevents a flash of the page before the intro starts. |
| `react/DoorIntro.jsx`, `react/DoorIntro.d.ts`, `react/door-intro.js` | React / Next.js component. |
| `wordpress/door-intro/` | Installable WordPress plugin with a settings page. |
| `webflow/door-intro-embed.html` | Paste-in Webflow embed (generated). |
| `demo/index.html` | Playground for testing branding and timing. It generates the config for you. |
| `build.mjs` | Builds every distribution from `src/`. |
| `tests/run-tests.mjs` | End-to-end tests in real Chromium. |

```bash
cd door-intro
npm install          # dev-only: terser, playwright, esbuild, react (runtime has no deps)
npm run build        # regenerate dist/, wordpress/, webflow/, react/ and ../site/door-intro.js
npm test             # build + 20 browser tests at 375 / 768 / 1440 px
```

Edit only `src/door-intro.js`, then run `npm run build`. Every other copy is generated.

## Where it integrates

DoorIntro mounts a single `position: fixed` element as the first child of
`<body>`, so the skip button is the first tab stop. It adds a `door-intro-active`
class to `<html>` while it plays and removes both when it finishes. It never
edits, hides or reorders your markup, never sets `inert`, and never locks
scrolling. Your CTAs, forms, analytics tags and click handlers keep working.

## Static site / Cloudflare Pages (this repository)

`site/` is the existing Arrington Abundance Architects site, extracted from
`abundance-architects-site.zip` (the zip itself is unchanged). Only
`site/index.html` gained four lines in `<head>`:

```html
<!-- optional pre-paint guard: snippets/head-prepaint.html with img="" set -->
<style>html.door-intro-pending::before{…}</style>
<script>(function(){var img="/images/door-intro/arrington-founders.jpg";…})();</script>
<!-- the intro itself -->
<script src="/door-intro.js" defer></script>
```

`site/door-intro.js` is the minified Open Doors build. On any other static
site, copy `dist/opendoors/door-intro.min.js` to your web root as
`door-intro.js`, or copy `dist/door-intro.min.js` and configure it (see below).

### Deploy to Cloudflare Pages

1. Add the founders portrait as `site/images/door-intro/arrington-founders.jpg` (see "Changing the imagery").
2. In the Cloudflare dashboard, go to **Workers & Pages → Create → Pages → Connect to Git** and pick this repository.
3. Settings: framework preset **None**, build command *(empty)*, build output directory **`site`**.
4. Deploy, then open `https://<project>.pages.dev/?doorintro=1` to force the intro.
5. Optionally, attach your custom domain under **Custom domains**.

Or from a terminal, after `npx wrangler login`:

```bash
npx wrangler pages deploy site --project-name=arrington-abundance
```

`site/_headers` caches the script for 1 hour and the intro images for 1 day,
so a replaced portrait reaches visitors within a day.

## Configuration

Options are merged in this order, with later sources winning: built-in
defaults → `preset` → build defaults → `window.DoorIntroConfig` → `data-*`
attributes on the script tag → `DoorIntro.init(options)`.

```html
<!-- Option A: data attributes (kebab-case) -->
<script src="/door-intro.js" defer
        data-preset="opendoors"
        data-image-url="/images/door-intro/arrington-founders.jpg"
        data-image-position="center 30%"
        data-play-mode="session"></script>

<!-- Option B: a config object, placed before the script -->
<script>
  window.DoorIntroConfig = {
    preset: 'neutral',
    brandName: 'Acme Advisors',
    logoUrl: '/logo.svg',
    imageUrl: '/images/team.jpg',
    primaryColor: '#0b1a2a', accentColor: '#c0a060', accentColor2: '#f0dca0',
    welcomeText: 'Welcome to Acme', revealText: 'Advice you can trust.',
    doorStyle: 'modern', duration: 4000
  };
</script>
<script src="/door-intro.js" defer></script>
```

| Option | Default | Notes |
|---|---|---|
| `preset` | `neutral` | `neutral` or `opendoors`. |
| `brandName` | preset | Shown as a gold wordmark when there is no logo. |
| `logoUrl` / `logoAlt` / `logoHeight` | – / brand / `72` | Prefer an SVG or transparent PNG. If the logo fails to load, the wordmark is shown instead. |
| `imageUrl` | – | The revealed photo. When it is empty or fails to load, the branded scene is shown instead. |
| `imageSrcset` / `imageSizes` | – / `100vw` | Responsive image sources. |
| `imageAlt` | preset | Leave it empty if the image is decorative. |
| `imagePosition` | `center 35%` | CSS `object-position`, which keeps faces in frame on phones. |
| `imageFit` | `auto` | `cover` (full-bleed), `contain` (whole photo at full height over a blurred copy of itself) or `auto` (contain only when a tall photo would otherwise be cropped hard, for example a portrait on a widescreen display). |
| `imageTimeout` | `1500` | Maximum time (ms) the doors wait for the image before opening anyway. |
| `welcomeText` / `revealText` | preset | Shown on the closed doors and over the photo. Use `''` to hide. |
| `primaryColor` / `accentColor` / `accentColor2` / `textColor` | preset | Hex colors. Door wood tones are derived from primary + accent. |
| `doorColor` | derived | Overrides the door base color. |
| `doorStyle` | `classic` | `classic` (raised panels), `modern` (inlaid lines), `glass` (frosted panels). |
| `showHandles` / `showFrame` | `true` | Gold pull handles and the architrave frame. |
| `fontDisplay` / `fontBody` | serif / system | Uses only fonts that are already available. Nothing is downloaded. |
| `duration` | `4500` | Total length in ms, clamped to 2500–8000. |
| `playMode` | `session` | `session` (sessionStorage), `once` (localStorage), `always`, or `manual` (only on `play()`). |
| `storageKey` | `door-intro:seen` | If you change it, update the pre-paint snippet too. |
| `urlParam` | `doorintro` | `?doorintro=1` forces the intro and `?doorintro=0` disables it. |
| `reducedMotion` | `fade` | `fade` (opacity only, about 2 s) or `skip`. |
| `skipForBots` | `true` | Crawlers see the plain page. |
| `skipButton` / `skipLabel` | `true` / `Skip intro` | |
| `clickToSkip` / `skipOnScroll` | `true` / `true` | |
| `replayButton` / `replayLabel` / `replayPosition` | `floating` / `Replay intro` / `bottom-left` | Set `none` to hide. Positions: `bottom-left`, `bottom-right`, `top-left`, `top-right`. |
| `replaySelector` | `[data-door-intro-replay]` | Any matching element replays the intro. |
| `soundUrl` / `soundLabel` | – / `Play sound` | Plays only after the visitor presses the toggle. |
| `zIndex` | `2147483000` | |
| `onStart` / `onComplete(reason)` | – | `reason` is `complete` or `skip`. |
| `autoInit` | `true` | Set `data-auto-init="false"` to call `DoorIntro.init()` yourself. |

JavaScript API: `DoorIntro.init(opts)`, `.play()`, `.replay()`, `.skip()`,
`.reset()`, `.destroy()`, `.isPlaying()`, `.config()`. Events:
`doorintro:start` and `doorintro:complete` are dispatched on `document`.
For example, to send an analytics event when the intro finishes:

```js
document.addEventListener('doorintro:complete', (e) => gtag?.('event', 'intro_' + e.detail.reason));
```

A replay link in your own markup:

```html
<a href="#" data-door-intro-replay>Watch the intro again</a>
```

## Changing the imagery

1. Export the portrait as a JPEG or WebP, about 2000 px on the long side, at 70–80 % quality. Aim for under 350 KB.
   A landscape crop works best. Keep both faces in the upper-middle third so they stay in frame on phones.
2. Save it as `site/images/door-intro/arrington-founders.jpg` (the default path in
   the Open Doors build and the pre-paint preload), or point `imageUrl` anywhere else.
   If you change the path, update `img=""` in the pre-paint snippet too.
3. If the faces are cut off on mobile, adjust `imagePosition`, for example `data-image-position="center 25%"`.
4. Optionally, add responsive versions:
   `data-image-srcset="/images/door-intro/arrington-1200.webp 1200w, /images/door-intro/arrington-2000.webp 2000w"`.

The site currently ships the supplied executive portrait (986 × 1530, re-encoded to
135 KB with metadata stripped). Because it is a tall photo, phones and tablets show it
full-bleed, while widescreen displays show the whole photo over a blurred copy of
itself (`imageFit: 'auto'`). To replace it, overwrite the file with the same name. A
couple's photo in landscape will automatically go full-bleed everywhere.
If an image is ever missing, the intro reveals a branded gold scene instead.
Visitors never see a broken image.

## Changing the branding

- **Logo**: add `data-logo-url="/images/logo.svg"`. Without a logo, the brand name is shown as a wordmark with a doorway monogram.
- **Name and copy**: use `data-brand-name`, `data-welcome-text` and `data-reveal-text`.
- **Colors**: use `data-primary-color`, `data-accent-color` and `data-accent-color2`. If you change the primary color, update the pre-paint snippet's `background` too.
- **New preset**: add an entry to `PRESETS` in `src/door-intro.js`, add a build target in `build.mjs`, then run `npm run build`.
- Use `demo/index.html` (served over HTTP, for example with `npx serve .` from `door-intro/`) to try settings and copy the generated config.

## React / Next.js

Copy `react/DoorIntro.jsx`, `react/door-intro.js` (and `DoorIntro.d.ts` for
TypeScript) into your components folder.

```jsx
// Next.js App Router: app/layout.jsx (the component is already 'use client')
import DoorIntro from '@/components/door-intro/DoorIntro';

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        {children}
        <DoorIntro preset="opendoors" imageUrl="/images/door-intro/arrington-founders.jpg" />
      </body>
    </html>
  );
}
```

In the Pages Router, render it in `pages/_app.jsx`. In Vite or CRA, render it
anywhere in `App`. It renders `null` on the server. On the client it mounts
after hydration, works with StrictMode (it plays once), and removes itself on
unmount. For a replay button, use
`import { replayDoorIntro } from './DoorIntro'` with `onClick={replayDoorIntro}`.
To avoid a flash before hydration, put the pre-paint snippet in the root
layout `<head>`. In the App Router, a plain `<script dangerouslySetInnerHTML>`
in `<head>` works.

## WordPress

1. Run `npm run build`, then zip `wordpress/door-intro/`.
2. Go to **Plugins → Add New → Upload Plugin**, upload the zip and activate it.
3. Under **Settings → Door Intro**, paste the portrait URL from the Media Library and choose the preset, play mode and colors.
4. Preview any page with `?doorintro=1`.

The plugin adds one deferred script (via `wp_enqueue_scripts` with the
`defer` strategy) and an optional pre-paint guard in `wp_head`. It doesn't
load in wp-admin, the Customizer, feeds, embeds or REST requests, and it never
modifies theme templates. It is compatible with page caches because the
decision to play happens in the browser. For developers, there are two filters:
`door_intro_enabled` (bool), for example to show the intro only on landing
pages, and `door_intro_config` (array).

## Webflow

Webflow can't host `.js` files, so `webflow/door-intro-embed.html` contains
everything inline (about 28 KB, within Webflow's custom-code limit):

1. Upload the portrait to **Assets** and copy its URL.
2. Go to **Site settings → Custom code**. Paste the PRE-PAINT block into **Head code**, and the CONFIG + SCRIPT block into **Footer code**.
3. Replace `imageUrl` with the asset URL, then publish.
4. To limit the intro to the home page, paste the same blocks into that page's
   **Page settings → Custom code** instead.

## Accessibility and performance checklist (all covered by tests)

- Skip is the first tab stop, Enter or Escape skips, Tab can leave the overlay, and focus is restored afterwards.
- Buttons have accessible names (`Skip intro and go to the website`, `Replay intro`) and touch targets of at least 44 px.
- With `prefers-reduced-motion`, there are no 3D doors (opacity-only fade) or nothing at all.
- There is no autoplaying audio.
- There is no layout shift. The script is deferred and about 9 KB gzipped, and the image is preloaded only when the intro will play.
- If the script fails to load, the pre-paint cover removes itself after 3 s.
- Crawlers and print see the original page.
