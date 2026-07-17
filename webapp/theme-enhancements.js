// NetScope — UI enhancement layer.
// Loaded AFTER app.js. Reads the DOM app.js already renders; never
// redefines or calls into app.js functions, never touches ws/state.
// Safe to delete without affecting any core functionality.

(() => {
  const THEME_KEY = "netscope.theme";

  // ── Theme toggle (light/dark) ─────────────────────────────
  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    const btn = document.getElementById("theme-toggle");
    if (btn) btn.setAttribute("aria-pressed", String(theme === "light"));
  }

  function initTheme() {
    const saved = localStorage.getItem(THEME_KEY);
    const preferred = saved || (window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark");
    applyTheme(preferred);

    const btn = document.getElementById("theme-toggle");
    if (!btn) return;
    btn.addEventListener("click", () => {
      const next = document.documentElement.getAttribute("data-theme") === "light" ? "dark" : "light";
      localStorage.setItem(THEME_KEY, next);
      applyTheme(next);
    });
  }

  // ── Keyboard navigation for tabs (roving tabindex, arrow keys) ──
  function initTabKeyboardNav() {
    const tabs = Array.from(document.querySelectorAll(".tab"));
    tabs.forEach((tab, i) => {
      tab.setAttribute("tabindex", tab.classList.contains("active") ? "0" : "-1");
      tab.addEventListener("keydown", (e) => {
        let target = null;
        if (e.key === "ArrowRight") target = tabs[(i + 1) % tabs.length];
        else if (e.key === "ArrowLeft") target = tabs[(i - 1 + tabs.length) % tabs.length];
        else if (e.key === "Home") target = tabs[0];
        else if (e.key === "End") target = tabs[tabs.length - 1];
        if (!target) return;
        e.preventDefault();
        tabs.forEach((t) => t.setAttribute("tabindex", "-1"));
        target.setAttribute("tabindex", "0");
        target.focus();
        target.click(); // reuses app.js's existing click handler — no logic duplicated
      });
    });
  }

  // ── Keyboard-operable packet stream rows ──────────────────
  // app.js prepends <tr> elements continuously; delegate at the
  // container so every future row (including ones added after
  // this script runs) gets Enter/Space support without touching
  // app.js's addStreamRow().
  function initStreamRowKeyboard() {
    const body = document.getElementById("stream-body");
    if (!body) return;
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((m) => {
        m.addedNodes.forEach((node) => {
          if (node.nodeType === 1 && node.tagName === "TR") {
            node.setAttribute("tabindex", "0");
            node.setAttribute("role", "button");
          }
        });
      });
    });
    observer.observe(body, { childList: true });

    body.addEventListener("keydown", (e) => {
      if (e.key !== "Enter" && e.key !== " ") return;
      const row = e.target.closest("tr");
      if (!row) return;
      e.preventDefault();
      row.click(); // triggers the same listener app.js attached
    });
  }

  // ── Polite live-region announcements for connection state ─
  // Watches #conn-label (already updated by app.js) and mirrors
  // its text into an off-screen aria-live region so screen-reader
  // users hear "Live" / "Disconnected" without extra chatter.
  function initConnAnnouncer() {
    const label = document.getElementById("conn-label");
    if (!label) return;
    const live = document.createElement("div");
    live.className = "sr-only";
    live.setAttribute("aria-live", "polite");
    live.id = "conn-announcer";
    document.body.appendChild(live);

    const mirror = () => { live.textContent = "Connection status: " + label.textContent; };
    mirror();
    new MutationObserver(mirror).observe(label, { childList: true, characterData: true, subtree: true });
  }

  // ── Skip link target ───────────────────────────────────────
  function initSkipLink() {
    const main = document.querySelector("main.grid");
    if (main && !main.hasAttribute("tabindex")) main.setAttribute("tabindex", "-1");
  }

  document.addEventListener("DOMContentLoaded", () => {
    initTheme();
    initTabKeyboardNav();
    initStreamRowKeyboard();
    initConnAnnouncer();
    initSkipLink();
  });
})();