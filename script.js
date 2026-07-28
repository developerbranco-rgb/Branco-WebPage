/* =====================================================================
   CONFIGURACIÓN — EDITÁ SOLO ESTAS LÍNEAS
   ---------------------------------------------------------------------
   1) WHATSAPP: tu número con código de país, sin +, sin espacios ni guiones.
      Argentina: 549 + código de área + número.  Ej: "5493471234567"
   2) INSTAGRAM: tu usuario, sin la @.  Ej: "branco.sax"
   3) EMAIL: tu correo de contacto.
   ===================================================================== */
const CONFIG = {
  WHATSAPP:  "5493466459010",      // Branco — WhatsApp (54 9 3466 459010)
  INSTAGRAM: "branco.sax",         // Instagram @branco.sax
  EMAIL:     "brancoantu9@gmail.com"
};
/* ===================================================================== */

(function () {
  "use strict";

  const waBase = "https://wa.me/" + CONFIG.WHATSAPP;
  const waMsg = (t) => waBase + "?text=" + encodeURIComponent(t);
  const igURL = "https://instagram.com/" + CONFIG.INSTAGRAM;

  // ---- Enlaces de contacto ----
  const setHref = (id, href) => { const el = document.getElementById(id); if (el) el.href = href; };
  const defaultWa = waMsg("¡Hola Branco! Me gustaría consultarte por un show de saxo para mi evento.");
  setHref("waFloat", defaultWa);
  setHref("waLine", defaultWa);
  setHref("footWa", defaultWa);
  setHref("igLine", igURL);
  setHref("footIg", igURL);
  setHref("emailLine", "mailto:" + CONFIG.EMAIL + "?subject=Consulta%20por%20show%20de%20saxo");

  // ---- Año del footer ----
  const yr = document.getElementById("year");
  if (yr) yr.textContent = new Date().getFullYear();

  // ---- Navbar: fondo al hacer scroll ----
  const nav = document.getElementById("nav");
  const onScroll = () => nav.classList.toggle("scrolled", window.scrollY > 40);
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  // ---- Menú móvil ----
  const toggle = document.getElementById("navToggle");
  const links = document.getElementById("navLinks");
  toggle.addEventListener("click", () => links.classList.toggle("open"));
  links.querySelectorAll("a").forEach((a) =>
    a.addEventListener("click", () => links.classList.remove("open"))
  );

  // ---- Reveal on scroll ----
  const io = new IntersectionObserver(
    (entries) => entries.forEach((e) => { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } }),
    { threshold: 0.12 }
  );
  document.querySelectorAll(".reveal").forEach((el) => io.observe(el));

  /* ===================================================================
     UN SOLO AUDIO A LA VEZ
     Si un video arranca CON sonido, se pausa cualquier otro video.
     =================================================================== */
  document.addEventListener(
    "play",
    (e) => {
      const v = e.target;
      if (v.tagName !== "VIDEO" || v.muted) return;
      document.querySelectorAll("video").forEach((o) => { if (o !== v && !o.paused) o.pause(); });
    },
    true
  );

  /* ===================================================================
     VIDEO DEL HERO — arranca CON SONIDO, sin que el usuario haga nada.
     Los navegadores sólo permiten autoplay silenciado, así que:
     1) arranca muteado (para que se reproduzca sí o sí),
     2) intentamos quitar el mute enseguida,
     3) si el navegador lo bloquea, lo activamos solo en la primera
        interacción del visitante (un toque o tecla en cualquier lado).
     =================================================================== */
  const hero = document.getElementById("heroVideo");
  const hint = document.getElementById("soundHint");

  if (hero) {
    let soundOn = false;
    let trying = false;

    const enableSound = () => {
      if (soundOn || trying) return Promise.resolve();
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

    // Sólo eventos que el navegador considera "interacción del usuario".
    const GESTURES = ["pointerdown", "touchend", "keydown", "click"];
    const onGesture = () => { if (!soundOn) enableSound(); };
    const detach = () => GESTURES.forEach((g) => window.removeEventListener(g, onGesture, true));
    const attach = () => GESTURES.forEach((g) => window.addEventListener(g, onGesture, true));

    // 1er intento apenas hay imagen; si falla, quedan los listeners esperando.
    attach();
    if (hero.readyState >= 2) enableSound();
    else hero.addEventListener("loadeddata", () => enableSound(), { once: true });

    if (hint) hint.addEventListener("click", (e) => { e.stopPropagation(); enableSound(); });

    // Si el usuario silencia a mano con los controles, respetamos su decisión.
    hero.addEventListener("volumechange", () => {
      if (soundOn && hero.muted) { detach(); if (hint) hint.hidden = true; }
    });

    // Pausar cuando el video sale de pantalla (no queremos audio fantasma).
    let wasPlaying = false;
    const hio = new IntersectionObserver(
      (entries) => entries.forEach((en) => {
        if (en.isIntersecting) { if (wasPlaying) hero.play().catch(() => {}); }
        else if (!hero.paused) { wasPlaying = true; hero.pause(); }
      }),
      { threshold: 0.25 }
    );
    hio.observe(hero);
    hero.addEventListener("play", () => { wasPlaying = true; });
  }

  /* ===================================================================
     CARRUSELES (videos y fotos) — flechas izquierda / derecha
     =================================================================== */
  document.querySelectorAll("[data-carousel]").forEach((car) => {
    const track = car.querySelector(".carousel__track");
    if (!track) return;

    const maxScroll = () => track.scrollWidth - track.clientWidth;
    const posOf = (el) => {
      const centered = el.offsetLeft - (track.clientWidth - el.offsetWidth) / 2;
      return Math.max(0, Math.min(centered, maxScroll()));
    };

    const go = (dir) => {
      const stops = Array.from(track.children).map(posOf);
      const cur = track.scrollLeft;
      let target;
      if (dir > 0) {
        target = stops.find((p) => p > cur + 8);
        if (target === undefined) target = 0;               // vuelve al principio
      } else {
        const before = stops.filter((p) => p < cur - 8);
        target = before.length ? before[before.length - 1] : maxScroll(); // va al final
      }
      track.scrollTo({ left: target, behavior: "smooth" });
    };

    car.querySelectorAll(".carousel__btn").forEach((b) =>
      b.addEventListener("click", () => go(Number(b.dataset.dir) || 1))
    );

    track.addEventListener("keydown", (e) => {
      if (e.key === "ArrowRight") { e.preventDefault(); go(1); }
      if (e.key === "ArrowLeft") { e.preventDefault(); go(-1); }
    });
  });

  /* ===================================================================
     VIDEOS DEL CARRUSEL
     Hover = preview sin sonido · Click = reproduce CON sonido y controles
     =================================================================== */
  const canHover = window.matchMedia("(hover: hover)").matches;

  // Enter / Espacio activan lo mismo que un click (accesibilidad por teclado).
  const clickableWithKeyboard = (el) =>
    el.addEventListener("keydown", (e) => {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); el.click(); }
    });

  document.querySelectorAll(".vslide").forEach((card) => {
    const v = card.querySelector("video");
    if (!v) return;

    const preview = () => {
      if (card.classList.contains("sound")) return;
      v.muted = true;
      v.play().catch(() => {});
    };
    const stopPreview = () => {
      if (card.classList.contains("sound")) return;
      v.pause();
      v.currentTime = 0;
    };

    if (canHover) {
      card.addEventListener("mouseenter", preview);
      card.addEventListener("mouseleave", stopPreview);
    }

    card.addEventListener("click", () => {
      if (card.classList.contains("sound")) return; // ya tiene controles nativos
      card.classList.add("sound");
      v.muted = false;
      v.volume = 1;
      v.controls = true;
      v.play().catch(() => { v.muted = true; v.play().catch(() => {}); });
    });

    clickableWithKeyboard(card);
    v.addEventListener("play", () => card.classList.add("playing"));
    v.addEventListener("pause", () => card.classList.remove("playing"));
  });

  /* ===================================================================
     LIGHTBOX DE FOTOS
     =================================================================== */
  const lb = document.getElementById("lightbox");
  const lbImg = document.getElementById("lbImg");
  let lastFocus = null;
  document.querySelectorAll(".pslide").forEach((fig) => {
    const img = fig.querySelector("img");
    if (!img) return;
    fig.addEventListener("click", () => {
      lbImg.src = img.currentSrc || img.src;
      lbImg.alt = img.alt;
      lb.classList.add("open");
      lastFocus = fig;
      document.getElementById("lbClose").focus();
    });
    clickableWithKeyboard(fig);
  });
  const closeLb = () => {
    if (!lb.classList.contains("open")) return;
    lb.classList.remove("open");
    if (lastFocus) { lastFocus.focus(); lastFocus = null; }
  };
  document.getElementById("lbClose").addEventListener("click", closeLb);
  lb.addEventListener("click", (e) => { if (e.target === lb) closeLb(); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeLb(); });

  /* ===================================================================
     FORMULARIO -> WHATSAPP
     =================================================================== */
  const form = document.getElementById("contactForm");
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
})();
