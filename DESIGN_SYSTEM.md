# NetScope — Design System Reference

This documents the theme that already exists in `style.css`, plus the small
additive extension in `tokens-extension.css`. Nothing here requires touching
`app.js` — every hook the JS relies on (`#ids`, `.classList` values it sets)
is preserved as-is.

## 1. What's already in place

Your codebase already implements essentially the full brief:

| Area | Status | Where |
|---|---|---|
| Color tokens | ✅ Complete, dark + light | `:root` and `:root[data-theme="light"]` |
| Typography | ✅ Complete (display/mono/sans, 3 families) | `--display`, `--mono`, `--sans` |
| Dark/light mode | ✅ Toggle + system-preference fallback | `theme-enhancements.js` + `@media (prefers-color-scheme)` |
| Focus states | ✅ `:focus-visible` on all interactive elements | style.css §3 |
| Keyboard nav | ✅ Roving tabindex on tabs, Enter/Space on stream rows | `theme-enhancements.js` |
| Skip link | ✅ | style.css §3 |
| Live-region announcer | ✅ Connection status mirrored to screen readers | `theme-enhancements.js` |
| Empty/loading states | ✅ CSS-only, no JS needed | style.css §4 |
| Responsive breakpoints | ✅ 1100px / 860px / 520px | style.css §5 |
| Motion + reduced-motion | ✅ Every animation has a `prefers-reduced-motion` fallback | throughout |
| Status/badge system | ✅ clean/suspicious/malicious, consistent across map, table, badges | `.dot`, `.badge`, `colorFor()` in app.js |

## 2. Color tokens

Defined once in `:root`, redeclared with new values under
`:root[data-theme="light"]` — same variable names, so no selector below the
token layer needs to know which mode is active.

| Token | Dark | Light | Role |
|---|---|---|---|
| `--void` | `#060911` | `#F4F7FC` | Page background |
| `--surface` / `--surface-2` | `#0F1726` / `#0A1120` | `#FFFFFF` / `#EEF2F9` | Panels, inputs |
| `--text` | `#EAF1FB` | `#101826` | Primary text |
| `--muted` | `#8493B2` | `#5B6884` | Secondary text, labels |
| `--dim` | `#5B6884` | `#8493B2` | Tertiary / disabled |
| `--signal` | `#31F2A0` | `#0EA573` | Clean / brand-primary |
| `--warn` | `#FFB13C` | `#B26A00` | Suspicious |
| `--danger` | `#FF3E6C` | `#D6274F` | Malicious |
| `--accent` | `#8C6BFF` | `#6438E0` | UI accent, focus ring |

Each status color has a `-dim` companion (e.g. `--signal-dim`) used as a
translucent background behind badges and feed-item borders, keeping
foreground/background pairs from the same family.

**Contrast spot-check (WCAG AA, 4.5:1 for text under 18px):**
- `--muted` (`#8493B2`) on `--surface` (`#0F1726`), dark mode: **5.8:1** — passes.
- `--muted` (`#5B6884`) on `--surface` (`#FFFFFF`), light mode: **5.6:1** — passes.

Both are the tightest pairs in the system (secondary text on panel
background), so if those clear AA the higher-contrast pairs (primary text,
status colors on `--void`) do too. I didn't exhaustively check every
color × background combination — worth a pass with a contrast checker
browser extension if you want AAA-level confidence before a compliance
audit.

## 3. Typography

| Token | Stack | Used for |
|---|---|---|
| `--display` | Chakra Petch → JetBrains Mono → monospace | Brand name, panel headers, stat values |
| `--mono` | JetBrains Mono → SFMono → Menlo | Data: table cells, timestamps, labels |
| `--sans` | Inter → system-ui | Body copy, buttons |

There's no numbered type scale (h1–h6) because this UI has no long-form
content — every text role maps directly to a component (`.brand-name`,
`.panel-head h2`, `.stat-chip-value`, `.data-table td`) with its own
purpose-fit size. Introducing a generic h1–h6 scale would be scaffolding
with nothing to attach it to; if a settings or docs page gets added later,
that's the moment to add one.

## 4. Spacing, motion, elevation — the actual gap

The brief asks for a named spacing/elevation/motion system. Your CSS has
consistent *values* (spacing clusters around 8/12/14/16/24px, transitions
around 120/200/300ms) but they're literals repeated per-rule rather than
named tokens. `tokens-extension.css` names what's already there:

```css
--space-1: 4px;   --space-5: 24px;
--space-2: 8px;   --space-6: 32px;
--space-3: 12px;  --space-7: 48px;
--space-4: 16px;

--duration-fast: 120ms;  --ease-standard: cubic-bezier(.4,0,.2,1);
--duration-base: 200ms;  --ease-out: cubic-bezier(0,0,.2,1);
--duration-slow: 300ms;

--elevation-1 / --elevation-2 (= existing --shadow) / --elevation-3
```

I deliberately did **not** rewrite existing rules to reference these — that
would mean touching ~30 working selectors for a change with zero visible
effect, which is the opposite of what you asked for. The tokens exist so
*new* CSS you write later can pull from a scale instead of picking a new
number. Retrofitting old rules is optional cleanup, not required.

## 5. Component reference (existing classes — API guidance)

Since this is vanilla HTML/CSS/JS rather than a component framework, "props"
map to class combinations and data attributes already wired to `app.js`:

**Button**
- `.btn-primary` — filled, `--signal` background. Primary action (Connect).
- `.btn-secondary` — tinted, `--accent-dim` background. (Added in style.css §6, not yet used in markup — available for a future secondary action.)
- `.btn-ghost` — outline only. Dismiss/cancel actions.
- Disabled state is automatic via `button:disabled` (opacity .5, no hover transform) — no extra class needed, just the `disabled` attribute.

**Badge** — `.badge` + status modifier: `.clean` / `.suspicious` / `.malicious`. Driven by `classify()` in app.js; don't hand-author these strings elsewhere or you'll drift from the scoring logic.

**Tag/status dot** — `.dot` + same three modifiers. Used in legends where a full badge is too heavy.

**Table** — `.data-table`, optional `.zebra` modifier (defined, not currently applied to either table — safe to add via `class="data-table zebra"` in the HTML, no JS impact since `app.js` only ever writes into `tbody`, never touches the `<table>` element's class list).

**Tabs** — `.tab` (+ `.active`) / `.tab-panel` (+ `.active`). Click handling and `aria-selected` are owned by `app.js`; keyboard roving-tabindex is owned by `theme-enhancements.js`. Don't add a new tab without registering it in both places (the `data-tab` value has to match the panel's `id="tab-<value>"`).

**Card/Panel** — `.panel`, with role variants `.panel-map` / `.panel-gauges` / `.panel-tabs` / `.panel-stream` that each tint the top-edge accent line differently. A new panel type should follow the same pattern: base `.panel` class + a role class that only sets `::before`'s gradient color.

**Modal** — native `<dialog>` element (`#conn-dialog`), not a custom implementation. Gets you focus trapping and Escape-to-close for free from the browser. Follow this pattern for any future modal rather than building a custom overlay.

**Feed item** — `.feed-item` + severity modifier `.sev-low` / `.sev-med` / `.sev-high`, sets a colored left border. Used identically for alerts and crypto events.

## 6. Accessibility summary

Already handled, confirmed by reading the code (not assumed):
- Skip link, `:focus-visible` with a visible ring + halo on every interactive element type
- Screen-reader-only live region mirrors connection state changes
- Tabs use full roving-tabindex + arrow/Home/End keyboard support
- Packet stream rows are keyboard-operable (`tabindex`, `role="button"`, Enter/Space) — added via `MutationObserver` so it self-applies to every row `app.js` prepends, no changes to `addStreamRow()` needed
- Reduced-motion respected for scanline, radar sweep, data-rail, skeleton shimmer, and alert-row flash

Not yet covered — worth flagging, not blocking:
- The radar map's SVG nodes (`ensureNode()` in app.js) have no `aria-label`, so a screen-reader user gets nothing from the network map itself. The threats table is the accessible equivalent of that data, so it's not a hard gap, but a `<title>` element per SVG node (added inside `ensureNode()`) would close it if you want full parity later.
- `#stream-filter`'s syntax (`ip:`, `proto:`, `port:`, `enc:`) is discoverable only via the placeholder text — no `aria-describedby` pointing to help text for screen-reader users who tab past the placeholder.

## 7. Responsive breakpoints (existing)

- **≤1100px** — three-column grid collapses to single column, panels stack.
- **≤860px** — topbar compresses, stat chips go edge-to-edge, brand tagline hides, Info column drops from the stream table.
- **≤520px** — Time column drops from the stream table too, stat chip/filter type sizes shrink.

No gap here — the three breakpoints cover phone/tablet/desktop cleanly and every step removes the least-critical column rather than shrinking everything proportionally, which is the right call for a data table.

## 8. Integration

1. Drop `tokens-extension.css` next to `style.css`.
2. Add one line to `index.html`, after the existing stylesheet link:
   ```html
   <link rel="stylesheet" href="style.css" />
   <link rel="stylesheet" href="tokens-extension.css" />
   ```
3. Nothing else changes. No selector in the extension file matches an
   existing one, so cascade order doesn't matter beyond "after style.css."
4. Use the new tokens (`var(--space-4)`, `var(--duration-base)`,
   `var(--elevation-3)`) in whatever CSS you write next; existing rules are
   untouched until you choose to migrate a literal to a token by hand.

## 9. Phase 2 ideas (not built — for when you're ready)

These would need one class attribute added to existing markup, no JS changes:
- `class="panel elevated"` on the detail view when a packet is selected, using the new `--elevation-3` token, to visually promote it above the other three panels.
- `class="data-table zebra"` on the packet stream table — the CSS rule already exists (§6 in style.css) and has just never been applied.
- SVG node `<title>` tooltips on the radar map for screen-reader parity (touches `ensureNode()` — the one item here that *is* a JS change, flagged separately since it falls outside the "no logic" constraint).