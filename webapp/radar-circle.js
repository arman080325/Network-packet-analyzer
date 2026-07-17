// NetScope — circular radar fix (JS half, v2).
// Loaded AFTER app.js and theme-enhancements.js.
// Purely additive, like theme-enhancements.js:
//   - injects one new decorative <div class="radar-grid"> with an
//     inline SVG (spokes + degree marks) — never touches #map-svg,
//     host state, or any function app.js defines
//   - measures .radar-wrap with a ResizeObserver and sets
//     --radar-diameter (px) on it, which radar-circle.css uses to
//     size the sweep/rings/grid as a true circle
// v2 change: sizing is no longer conditional on CSS container-query
// support — it always runs. Simpler, one code path, no @supports
// branching to keep in sync with the CSS file.
// Safe to delete: without it you lose the grid overlay and the
// sweep/rings fall back to 100% (the panel's rectangle) since
// --radar-diameter is never set.

(() => {
  const SPOKE_COUNT = 12; // one spoke every 30°
  const DEGREE_MARKS = [0, 90, 180, 270]; // N / E / S / W positions

  function buildGridSvg() {
    const NS = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(NS, "svg");
    svg.setAttribute("viewBox", "0 0 100 100");
    svg.setAttribute("aria-hidden", "true"); // decorative only — the threats table is the accessible data source

    const cx = 50, cy = 50, r = 47;

    for (let i = 0; i < SPOKE_COUNT; i++) {
      const angle = (i * 360) / SPOKE_COUNT;
      const rad = (angle - 90) * (Math.PI / 180); // rotate so 0° points up
      const x2 = (cx + r * Math.cos(rad)).toFixed(2);
      const y2 = (cy + r * Math.sin(rad)).toFixed(2);
      const line = document.createElementNS(NS, "line");
      line.setAttribute("x1", cx);
      line.setAttribute("y1", cy);
      line.setAttribute("x2", x2);
      line.setAttribute("y2", y2);
      line.setAttribute("class", "spoke" + (angle % 90 === 0 ? " cardinal" : ""));
      svg.appendChild(line);
    }

    DEGREE_MARKS.forEach((deg) => {
      const rad = (deg - 90) * (Math.PI / 180);
      const lx = (cx + (r + 4) * Math.cos(rad)).toFixed(2);
      const ly = (cy + (r + 4) * Math.sin(rad)).toFixed(2);
      const text = document.createElementNS(NS, "text");
      text.setAttribute("x", lx);
      text.setAttribute("y", ly);
      text.setAttribute("text-anchor", "middle");
      text.setAttribute("dominant-baseline", "middle");
      text.setAttribute("class", "tick-label");
      text.textContent = deg + "\u00B0";
      svg.appendChild(text);
    });

    return svg;
  }

  function initGrid(wrap) {
    if (wrap.querySelector(".radar-grid")) return;
    const grid = document.createElement("div");
    grid.className = "radar-grid";
    grid.appendChild(buildGridSvg());
    const mapSvg = document.getElementById("map-svg");
    wrap.insertBefore(grid, mapSvg || null); // grid sits below the node layer
  }

  function initSize(wrap) {
    if (typeof ResizeObserver === "undefined") return; // graceful no-op on ancient browsers — CSS 100% fallback still applies
    const update = () => {
      const { width, height } = wrap.getBoundingClientRect();
      const diameter = Math.max(0, Math.min(width, height));
      if (diameter > 0) wrap.style.setProperty("--radar-diameter", diameter + "px");
    };
    update(); // set immediately, before the observer's first async callback, to avoid a flash of the old rectangle
    new ResizeObserver(update).observe(wrap);
  }

  document.addEventListener("DOMContentLoaded", () => {
    const wrap = document.querySelector(".radar-wrap");
    if (!wrap) return;
    initGrid(wrap);
    initSize(wrap);
  });
})();