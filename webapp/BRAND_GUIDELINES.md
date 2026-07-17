# NetScope — Brand Identity Guidelines

## 1. Logo concept

**Core idea:** a hex "aperture" — an outer six-sided ring (the network
perimeter NetScope watches over) with a smaller solid hex nested inside
it (the "scope" — the lens doing the inspecting). A single accent dot
sits on one outer vertex: a flagged packet caught mid-transit, and the
one deliberately asymmetric detail that makes the mark recognizable
even in silhouette. Net + Scope, literally: a net (the hex boundary)
being watched (the aperture) with something moving through it (the dot).

This isn't a new concept — it formalizes the hex mark already animating
in the product header (`.brand-mark` in `style.css`) and the ad-hoc
inline favicon that was hand-coded into `index.html`. Same geometry,
same two polygons, now extracted into standalone, reusable files.

**Color palettes (HEX):**

| Role | Dark mode (primary) | Light mode |
|---|---|---|
| Base | `#060911` (void) | `#F4F7FC` (void) |
| Surface | `#0F1726` | `#FFFFFF` |
| Signal / brand-primary | `#31F2A0` | `#0EA573` |
| Warn | `#FFB13C` | `#B26A00` |
| Danger | `#FF3E6C` | `#D6274F` |
| Accent (packet-node dot) | `#8C6BFF` | `#6438E0` |
| Text | `#EAF1FB` | `#101826` |

Dark mode is the product's native environment (a threat console lives
on screens, usually dim rooms) and is the primary palette. Light mode
exists for print, embeds, and daylight use — same relationships,
darkened/saturated for 4.5:1+ contrast on white.

**Typography:**

- **Display / wordmark:** Chakra Petch (700) — fallback `'JetBrains
  Mono', ui-monospace, monospace`. Its squared-off, slightly
  technical letterforms read as instrumentation, not marketing.
- **Data / mono:** JetBrains Mono — fallback `ui-monospace,
  SFMono-Regular, Menlo, monospace`. Used for taglines, labels, and
  anything meant to look like a live readout.
- **Body:** Inter — fallback `system-ui, -apple-system, sans-serif`.

## 2. Logo variations

| File | Use |
|---|---|
| `logo-horizontal.svg` | Primary lockup — headers, nav bars, dark backgrounds |
| `logo-horizontal-on-light.svg` | Same lockup, recolored for light/white backgrounds |
| `logo-stacked.svg` | Centered icon-over-wordmark — splash screens, title slides, square social profiles |
| `icon-mark.svg` | Standalone hex mark, transparent background — favicons, app icons, watermarks, anywhere the wordmark doesn't fit |
| `icon-mark-simple.svg` | Same mark without the accent dot — for sub-24px contexts where the dot would just be noise |

## 3. Favicon and app icon

- `favicon-16.png`, `favicon-32.png`, `favicon-48.png`, `favicon-60.png` —
  raster favicons, opaque `#060911` square background (no reliance on
  alpha transparency, so it renders identically across every browser
  and OS favicon tray).
- `favicon-tile.svg` — the scalable source for the above; can also be
  served directly as `<link rel="icon" type="image/svg+xml">` in
  browsers that support SVG favicons.
- `apple-touch-icon-180.png` — iOS home-screen icon.
- `app-icon-512.png` (+ `app-icon.svg` source) — square with rounded
  corners (22% radius, iOS/Android convention), radial glow behind the
  mark for depth at large sizes.
- At 16px the outer ring, inner hex, and accent dot all stay legible
  as a two-tone glyph, one flagged corner — this is the simplified
  mark (`icon-mark-simple.svg`) already omitting the dot.

## 4. Usage guidelines

- **Clear space:** keep clear space around the mark equal to at least
  the width of the outer ring's stroke × 3 on every side. Don't let
  UI chrome, text, or other logos enter that zone.
- **Minimum size:** icon mark, 16px; horizontal lockup, 120px wide;
  stacked lockup, 96px wide. Below that, use `icon-mark-simple.svg`.
- **Color usage:** the hex mark is always two-tone (ring + inner
  fill) plus one accent dot — never render it as a single flat color,
  and never recolor the accent dot to anything but the palette's
  accent value. On dark surfaces use the dark palette; on light
  surfaces, the light palette — don't mix ring/fill colors across the
  two.
- **When to use which variant:** horizontal for anywhere wide (nav
  bars, email signatures, headers); stacked for anywhere square or
  tall (app icons that need a wordmark, social avatars, cover slides);
  icon mark alone once the product name has already been established
  on the page (favicons, repeated watermarks, loading states).
- **Don't:** stretch or skew any lockup off its native aspect ratio,
  drop shadow the mark outside `app-icon.svg`'s built-in glow, place
  the dark-palette lockup on a light background or vice versa, or
  rebuild the hex from scratch at an angle other than point-up.
- **Accessibility:** `#31F2A0` on `#060911` is ~11.6:1 contrast;
  `#0EA573` on `#FFFFFF` is ~4.6:1 — both clear AA for the sizes
  they're used at (large text / graphical objects). The wordmark's
  primary color (`#EAF1FB` on `#060911`, ~15.8:1) exceeds AAA.

## 5. Deliverables

**Vector:** `icon-mark.svg`, `icon-mark-simple.svg`, `favicon-tile.svg`,
`app-icon.svg`, `logo-horizontal.svg`, `logo-horizontal-on-light.svg`,
`logo-stacked.svg`. All hand-authored SVG (no embedded raster), safe to
open and edit directly, or re-export to AI/EPS from any vector editor
that imports SVG (Illustrator, Affinity, Inkscape) since the geometry
is plain polygons/circles with no filters beyond the app icon's glow
gradients.

**Raster:** `favicon-16.png`, `favicon-32.png`, `favicon-48.png`,
`favicon-60.png`, `apple-touch-icon-180.png`, `app-icon-512.png`.

**Tokens:** `brand-tokens.css` (CSS custom properties) and
`brand-tokens.json` (same values, framework-agnostic) — both mirror
`style.css`'s existing `--signal/--warn/--danger/--accent` values
exactly, so brand assets never drift from the live UI.

**Config:** `site.webmanifest` for installable/PWA icon metadata.

**Rationale:** the biggest constraint here was continuity, not
invention — `style.css` already had a fully worked-out palette, type
system, and even a hex-shaped `.brand-mark` doing real work in the
header. Designing a "new" identity on top of that would have meant
either two competing brand marks or a rebuild the product doesn't
need. Instead, this package takes the mark that was already there,
gives it standalone files at every size the product actually needs
(favicon through app icon), and adds the one asset that was genuinely
missing: a wordmark lockup, since `.brand-mark` was CSS-only and had
no exportable logo file behind it.
