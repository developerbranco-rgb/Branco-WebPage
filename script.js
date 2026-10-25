
const CONFIG = {
  WHATSAPP:  "5493466459010",      // Branco — WhatsApp (54 9 3466 459010)
  INSTAGRAM: "branco.sax",         // Instagram @branco.sax
  EMAIL:     "brancoantu9@gmail.com"
};
/* ===================================================================== */

(function () {
  "use strict";

  const $ = (s, root = document) => root.querySelector(s);
  const $$ = (s, root = document) => Array.from(root.querySelectorAll(s));

  const waBase = "https://wa.me/" + CONFIG.WHATSAPP;
  const waMsg = (t) => waBase + "?text=" + encodeURIComponent(t);
  const igURL = "https://instagram.com/" + CONFIG.INSTAGRAM;

  // ---- Enlaces de contacto (todas las páginas) ----
  const pageName = document.title.split(" — ")[0];
  const defaultWa = waMsg(
    document.body.classList.contains("page-index")
      ? "¡Hola Branco! Me gustaría consultarte por un show de saxo para mi evento."
      : "¡Hola Branco! Vi tus videos de " + pageName + " y me gustaría consultarte por un show."
  );
  $$("[data-wa]").forEach((a) => { a.href = defaultWa; a.target = "_blank"; a.rel = "noopener"; });
  $$("[data-ig]").forEach((a) => (a.href = igURL));
  $$("[data-mail]").forEach((a) => (a.href = "mailto:" + CONFIG.EMAIL + "?subject=Consulta%20por%20show%20de%20saxo"));
  $$("[data-mail-text]").forEach((el) => (el.textContent = CONFIG.EMAIL));
  $$("[data-ig-text]").forEach((el) => (el.textContent = "@" + CONFIG.INSTAGRAM));
  $$("[data-year]").forEach((el) => (el.textContent = new Date().getFullYear()));

  // ---- Navbar: fondo al hacer scroll ----
  const nav = $("#nav");
  const onScroll = () => nav.classList.toggle("scrolled", window.scrollY > 40);
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  // ---- Menú móvil ----
  const toggle = $("#navToggle");
  const links = $("#navLinks");
  const setMenu = (open) => {
    links.classList.toggle("open", open);
    toggle.classList.toggle("open", open);
    toggle.setAttribute("aria-expanded", String(open));
    document.body.classList.toggle("menu-open", open);
  };
  toggle.addEventListener("click", () => setMenu(!links.classList.contains("open")));
  links.querySelectorAll("a").forEach((a) => a.addEventListener("click", () => setMenu(false)));
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") setMenu(false); });

  // ---- Reveal on scroll ----
  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver(
      (entries) => entries.forEach((e) => { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } }),
      { threshold: 0.08, rootMargin: "0px 0px -40px 0px" }
    );
    $$(".reveal").forEach((el) => io.observe(el));
  } else {
    $$(".reveal").forEach((el) => el.classList.add("in"));
  }

  // ---- Submenú de secciones: marca la sección visible ----
  const subnav = $(".subnav");
  if (subnav && "IntersectionObserver" in window) {
    const chips = $$("a", subnav);
    const byId = new Map(chips.map((a) => [a.getAttribute("href").slice(1), a]));
    const sio = new IntersectionObserver(
      (entries) => entries.forEach((e) => {
        if (!e.isIntersecting) return;
        const chip = byId.get(e.target.id);
        if (!chip) return;
        chips.forEach((c) => c.classList.toggle("active", c === chip));
        chip.scrollIntoView({ block: "nearest", inline: "center", behavior: "smooth" });
      }),
      { rootMargin: "-45% 0px -50% 0px" }
    );
    byId.forEach((_, id) => { const el = document.getElementById(id); if (el) sio.observe(el); });
  }

  /* ===================================================================
     UN SOLO AUDIO A LA VEZ
     =================================================================== */
  document.addEventListener(
    "play",
    (e) => {
      const v = e.target;
      if (v.tagName !== "VIDEO" || v.muted) return;
      $$("video").forEach((o) => { if (o !== v && !o.paused) o.pause(); });
    },
    true
  );

  /* ===================================================================
     VIDEO DEL HERO (inicio) — intenta arrancar con sonido.
     Los navegadores solo permiten autoplay silenciado: si bloquean el
     sonido, se activa en la primera interacción del visitante.
     =================================================================== */
  const hero = $("#heroVideo");
  const hint = $("#soundHint");
  if (hero) {
    let soundOn = false;
    let trying = false;
    const GESTURES = ["pointerdown", "touchend", "keydown", "click"];
    const onGesture = (e) => {
      // No "robar" el gesto si el visitante está abriendo otro video.
      if (e.target.closest && e.target.closest("[data-video], .player")) return;
      if (!soundOn) enableSound();
    };
    const detach = () => GESTURES.forEach((g) => window.removeEventListener(g, onGesture, true));
    const attach = () => GESTURES.forEach((g) => window.addEventListener(g, onGesture, true));

    const enableSound = () => {
      if (soundOn || trying || !heroVisible) return Promise.resolve();
      trying = true;
      hero.muted = false;
      hero.volume = 1;
      let p;
      try { p = hero.play(); } catch (_) { p = null; }
      return Promise.resolve(p)
        .then(() => new Promise((r) => setTimeout(r, 60)))
        .then(() => {
          if (hero.muted || hero.paused) throw new Error("blocked");
          soundOn = true;
          trying = false;
          if (hint) hint.hidden = true;
          detach();
        })
        .catch(() => {
          trying = false;
          hero.muted = true;
          hero.play().catch(() => {});
          if (hint) hint.hidden = false;
        });
    };

    let heroVisible = true;
    attach();
    if (hero.readyState >= 2) enableSound();
    else hero.addEventListener("loadeddata", () => enableSound(), { once: true });
    if (hint) hint.addEventListener("click", (e) => { e.stopPropagation(); enableSound(); });

    hero.addEventListener("volumechange", () => {
      if (soundOn && hero.muted) { detach(); if (hint) hint.hidden = true; }
    });

    // Pausar cuando sale de pantalla (sin audio fantasma).
    let wasPlaying = false;
    new IntersectionObserver(
      (entries) => entries.forEach((en) => {
        heroVisible = en.isIntersecting;
        if (en.isIntersecting) { if (wasPlaying && !playerOpen()) hero.play().catch(() => {}); }
        else if (!hero.paused) { wasPlaying = true; hero.pause(); }
      }),
      { threshold: 0.25 }
    ).observe(hero);
    hero.addEventListener("play", () => { wasPlaying = true; });
  }

  /* ===================================================================
     REPRODUCTOR — cada tarjeta de video abre el reproductor grande.
     Flechas / teclado / deslizar para pasar al siguiente.
     =================================================================== */
  const player = $("#player");
  const pv = $("#playerVideo");
  const ptitle = $("#playerTitle");
  const pcount = $("#playerCount");
  const cards = $$("[data-video]");
  let idx = -1;
  let lastCard = null;
  const playerOpen = () => player && !player.hidden;

  const show = (i) => {
    if (!cards.length) return;
    idx = (i + cards.length) % cards.length;
    const c = cards[idx];
    pv.pause();
    pv.poster = c.dataset.poster || "";
    pv.src = c.getAttribute("href");
    ptitle.textContent = c.dataset.title || groupTitle(c) || "";
    pcount.textContent = cards.length > 1 ? idx + 1 + " / " + cards.length : "";
    pv.muted = false;
    pv.play().catch(() => {});
  };
  const groupTitle = (c) => {
    const g = c.closest(".group");
    const h = g && g.querySelector(".group__head h2, .group__head h3");
    return h ? h.textContent : "";
  };
  const open = (i, card) => {
    lastCard = card;
    player.hidden = false;
    document.body.classList.add("no-scroll");
    if (hero && !hero.paused) hero.pause();
    show(i);
    $("#playerClose").focus({ preventScroll: true });
  };
  const close = () => {
    if (!playerOpen()) return;
    pv.pause();
    pv.removeAttribute("src");
    pv.load();
    player.hidden = true;
    document.body.classList.remove("no-scroll");
    if (document.fullscreenElement) document.exitFullscreen().catch(() => {});
    if (lastCard) lastCard.focus({ preventScroll: true });
  };

  if (player) {
    cards.forEach((c, i) =>
      c.addEventListener("click", (e) => {
        if (e.metaKey || e.ctrlKey || e.shiftKey) return; // abrir en pestaña nueva
        e.preventDefault();
        open(i, c);
      })
    );
    $("#playerClose").addEventListener("click", close);
    $("#playerPrev").addEventListener("click", () => show(idx - 1));
    $("#playerNext").addEventListener("click", () => show(idx + 1));
    player.addEventListener("click", (e) => { if (e.target === player || e.target.id === "playerStage") close(); });
    if (cards.length < 2) player.classList.add("player--single");

    document.addEventListener("keydown", (e) => {
      if (!playerOpen()) return;
      if (e.key === "Escape") close();
      else if (e.key === "ArrowRight" && e.target !== pv) show(idx + 1);
      else if (e.key === "ArrowLeft" && e.target !== pv) show(idx - 1);
      else if (e.key === "Tab") {
        // mantener el foco dentro del reproductor
        const f = $$("button, video", player).filter((el) => el.offsetParent !== null);
        const first = f[0], last = f[f.length - 1];
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    });

    // Deslizar con el dedo (en la parte de arriba del video, para no
    // chocar con la barra de controles de abajo).
    let sx = 0, sy = 0, st = 0, track = false;
    const stage = $("#playerStage");
    stage.addEventListener("touchstart", (e) => {
      const t = e.touches[0];
      const r = pv.getBoundingClientRect();
      track = e.touches.length === 1 && t.clientY < r.bottom - 70;
      sx = t.clientX; sy = t.clientY; st = Date.now();
    }, { passive: true });
    stage.addEventListener("touchend", (e) => {
      if (!track) return;
      const t = e.changedTouches[0];
      const dx = t.clientX - sx, dy = t.clientY - sy;
      if (Date.now() - st < 600 && Math.abs(dx) > 60 && Math.abs(dx) > Math.abs(dy) * 1.5) {
        show(idx + (dx < 0 ? 1 : -1));
      } else if (Date.now() - st < 600 && dy > 110 && Math.abs(dy) > Math.abs(dx) * 1.5) {
        close(); // deslizar hacia abajo cierra
      }
    }, { passive: true });
  }

  /* ===================================================================
     CARRUSEL DE FOTOS — flechas izquierda / derecha
     =================================================================== */
  $$("[data-carousel]").forEach((car) => {
    const track = $(".carousel__track", car);
    if (!track) return;
    const maxScroll = () => track.scrollWidth - track.clientWidth;
    const posOf = (el) => Math.max(0, Math.min(el.offsetLeft - (track.clientWidth - el.offsetWidth) / 2, maxScroll()));
    const go = (dir) => {
      const stops = Array.from(track.children).map(posOf);
      const cur = track.scrollLeft;
      let target;
      if (dir > 0) {
        target = stops.find((p) => p > cur + 8);
        if (target === undefined) target = 0;
      } else {
        const before = stops.filter((p) => p < cur - 8);
        target = before.length ? before[before.length - 1] : maxScroll();
      }
      track.scrollTo({ left: target, behavior: "smooth" });
    };
    $$(".carousel__btn", car).forEach((b) => b.addEventListener("click", () => go(Number(b.dataset.dir) || 1)));
    track.addEventListener("keydown", (e) => {
      if (e.key === "ArrowRight") { e.preventDefault(); go(1); }
      if (e.key === "ArrowLeft") { e.preventDefault(); go(-1); }
    });
  });

  /* ===================================================================
     LIGHTBOX DE FOTOS
     =================================================================== */
  const lb = $("#lightbox");
  const lbImg = $("#lbImg");
  let lastFocus = null;
  const clickableWithKeyboard = (el) =>
    el.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); el.click(); }
    });
  $$(".pslide").forEach((fig) => {
    const img = $("img", fig);
    if (!img) return;
    fig.addEventListener("click", () => {
      lbImg.src = img.currentSrc || img.src;
      lbImg.alt = img.alt;
      lb.classList.add("open");
      document.body.classList.add("no-scroll");
      lastFocus = fig;
      $("#lbClose").focus();
    });
    clickableWithKeyboard(fig);
  });
  const closeLb = () => {
    if (!lb || !lb.classList.contains("open")) return;
    lb.classList.remove("open");
    document.body.classList.remove("no-scroll");
    if (lastFocus) { lastFocus.focus(); lastFocus = null; }
  };
  if (lb) {
    $("#lbClose").addEventListener("click", closeLb);
    lb.addEventListener("click", (e) => { if (e.target === lb) closeLb(); });
    document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeLb(); });
  }

  /* ===================================================================
     NÚMEROS: cuentan hacia arriba al aparecer
     =================================================================== */
  const counters = $$("[data-count]");
  if (counters.length && "IntersectionObserver" in window && !matchMedia("(prefers-reduced-motion: reduce)").matches) {
    const cio = new IntersectionObserver((entries) => entries.forEach((e) => {
      if (!e.isIntersecting) return;
      cio.unobserve(e.target);
      const el = e.target, end = Number(el.dataset.count), t0 = performance.now();
      const step = (t) => {
        const k = Math.min(1, (t - t0) / 1200);
        el.textContent = Math.round(end * (1 - Math.pow(1 - k, 3)));
        if (k < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    }), { threshold: 0.6 });
    counters.forEach((el) => cio.observe(el));
  }

  /* ===================================================================
     FORMULARIO -> WHATSAPP
     =================================================================== */
  const form = $("#contactForm");
  if (form) {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      const g = (id) => (document.getElementById(id).value || "").trim();
      const texto =
        "¡Hola Branco! Quiero consultarte por un show de saxo.\n\n" +
        "• Nombre: " + (g("nombre") || "-") + "\n" +
        "• Teléfono: " + (g("tel") || "-") + "\n" +
        "• Tipo de evento: " + g("tipo") + "\n" +
        "• Fecha: " + (g("fecha") || "a definir") + "\n" +
        "• Mensaje: " + (g("msg") || "-");
      window.open(waMsg(texto), "_blank");
    });
  }
})();
