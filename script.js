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

  // ---- Videos del grid: play al pasar / tocar, pausa al salir ----
  document.querySelectorAll(".vcard").forEach((card) => {
    const v = card.querySelector("video");
    const play = () => {
      document.querySelectorAll(".vcard.playing").forEach((c) => {
        if (c !== card) { c.classList.remove("playing"); c.querySelector("video").pause(); }
      });
      card.classList.add("playing");
      v.play().catch(() => {});
    };
    const stop = () => { card.classList.remove("playing"); v.pause(); };
    card.addEventListener("mouseenter", play);
    card.addEventListener("mouseleave", stop);
    // En touch: primer tap reproduce/pausa
    card.addEventListener("click", () => {
      if (card.classList.contains("playing")) stop(); else play();
    });
  });

  // ---- Lightbox de la galería ----
  const lb = document.getElementById("lightbox");
  const lbImg = document.getElementById("lbImg");
  document.querySelectorAll(".gallery img").forEach((img) => {
    img.addEventListener("click", () => {
      lbImg.src = img.src;
      lbImg.alt = img.alt;
      lb.classList.add("open");
    });
  });
  const closeLb = () => lb.classList.remove("open");
  document.getElementById("lbClose").addEventListener("click", closeLb);
  lb.addEventListener("click", (e) => { if (e.target === lb) closeLb(); });
  document.addEventListener("keydown", (e) => { if (e.key === "Escape") closeLb(); });

  // ---- Formulario -> WhatsApp ----
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
