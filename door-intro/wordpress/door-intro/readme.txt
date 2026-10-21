=== Door Intro ===
Requires at least: 6.3
Tested up to: 6.6
Stable tag: 1.0.0
License: MIT

Cinematic opening-doors entrance that reveals a founder photo, then fades into your existing site.

== Installation ==
1. Run `npm run build` in door-intro/ (or use the committed assets/door-intro.js).
2. Zip this `door-intro` folder and upload it in Plugins → Add New → Upload Plugin, or copy it to wp-content/plugins/.
3. Activate, then open Settings → Door Intro.
4. Upload the founders portrait to the Media Library, copy its URL into "Founder / hero image URL", save.
5. Visit any page with ?doorintro=1 to preview.

== Notes ==
* Adds one deferred script (about 9 KB gzipped) and an optional inline pre-paint guard. Theme templates and content are never modified.
* Filters: `door_intro_enabled` (bool) and `door_intro_config` (array) for per-page control from a theme or another plugin.
* Caching plugins: exclude nothing; the intro decides client-side whether to play.
