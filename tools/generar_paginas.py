"""
Arma todas las páginas HTML del sitio a partir de:
  - data/medios.json        (lo genera procesar_medios.py)
  - tools/ajustes.json      (títulos / lugares / nombres opcionales)
  - tools/plantillas/*.html (diseño común e inicio)

Cada carpeta dentro de videos/ es una página. Si mañana creás una carpeta
nueva (ej. videos/Casamientos), aparece sola en el menú.

No hace falta correrlo a mano: usá actualizar.bat
"""

import html
import json
import re
import sys
import unicodedata
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
TPL = Path(__file__).resolve().parent / "plantillas"

# Si cambiás de dominio, cambialo solo acá.
SITE_URL = "https://developerbranco-rgb.github.io/Branco-WebPage/"

# Páginas conocidas (en el orden del menú). "carpeta" = nombre de la carpeta en videos/
PAGINAS = [
    {
        "carpeta": "solista en bares", "slug": "solista-en-bares", "menu": "Solista en Bares",
        "modo": "lugares",
        "titulo": "Solista en Bares",
        "eyebrow": "Saxo en vivo en tu bar",
        "intro": "El show solista de saxo en bares y pubs: música en vivo que acompaña la noche y llena el lugar.",
        "desc": "Branco, saxofonista solista en bares y pubs. Videos en vivo de cada lugar.",
    },
    {
        "carpeta": "lugares", "slug": "lugares", "menu": "Lugares", "modo": "lugares",
        "titulo": "Lugares",
        "eyebrow": "Dónde toqué",
        "intro": "Bares, complejos y salones donde llevé el show de saxo en vivo.",
        "desc": "Videos de Branco tocando el saxo en vivo en bares, complejos y salones.",
    },
    {
        "carpeta": "eventos", "slug": "eventos", "menu": "Eventos", "modo": "simple",
        "titulo": "Eventos",
        "eyebrow": "Fiestas · Empresas · Celebraciones",
        "intro": "Saxo en vivo para fiestas privadas, eventos corporativos, cumpleaños y celebraciones.",
        "desc": "Videos de Branco, saxofonista, en fiestas privadas, eventos corporativos y celebraciones.",
    },
    {
        "carpeta": "juegos suramericanos", "slug": "juegos-suramericanos",
        "menu": "Juegos Suramericanos", "modo": "juegos",
        "titulo": "Juegos Suramericanos",
        "eyebrow": "Escenario internacional",
        "intro": "Show de saxo en vivo en los Juegos Suramericanos Santa Fe 2026, frente a público de todo el continente.",
        "desc": "Branco tocando el saxo en vivo en los Juegos Suramericanos Santa Fe 2026: momentos y canciones completas por día.",
    },
    {
        "carpeta": "dopashock", "slug": "dopashock", "menu": "DopaShock", "modo": "dopashock",
        "titulo": "DopaShock",
        "eyebrow": "Proyecto en vivo",
        "intro": "Saxo, beats y energía de pista. El show de DopaShock en cada lugar donde se presentó.",
        "desc": "DopaShock: show en vivo de saxo y electrónica. Videos por lugar.",
        "tema": "dopa",
    },
    {
        "carpeta": "bandas", "slug": "bandas", "menu": "Bandas", "modo": "bandas",
        "titulo": "Bandas",
        "eyebrow": "Colaboraciones",
        "intro": "Bandas y proyectos con los que toco o toqué el saxo.",
        "desc": "Bandas con las que tocó Branco, saxofonista. Videos en vivo de cada una.",
    },
]

ICON_PLAY = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5v14l11-7z"/></svg>'


# ---------------------------------------------------------------- utilidades
def nfc(s):
    return unicodedata.normalize("NFC", s)


def slug(text):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower() or "x"


def natural_key(s):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", s)]


SMALL = {"de", "la", "el", "a", "en", "y", "los", "las", "del", "al", "of", "the",
         "on", "in", "and", "to", "for", "it"}


def pretty(text):
    """'TAKE ON ME' -> 'Take on Me' ; 'CityCenter' -> 'City Center'."""
    text = nfc(text).replace("_", " ")
    if " " not in text.strip() and re.search(r"[a-z][A-Z]", text):
        text = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", text)
    text = re.sub(r"\s+", " ", text).strip(" -·")
    if text.isupper() or text.islower():
        words = text.lower().split(" ")
        text = " ".join(
            w if (i and w in SMALL) else w[:1].upper() + w[1:]
            for i, w in enumerate(words)
        )
    return text


def esc(s):
    return html.escape(s or "", quote=True)


def fmt_dur(sec):
    sec = int(round(sec or 0))
    return f"{sec // 60}:{sec % 60:02d}"


SIN_TITULO = re.compile(
    r"^(img|vid|dsc|pxl|mov|video)[ _-]?\d+$|^[0-9a-f]{8}-[0-9a-f-]{20,}$|^[0-9a-f]{16,}$|^eventos?( ?\(\d+\))?$",
    re.I,
)


# ---------------------------------------------------------------- datos
class Ajustes:
    def __init__(self, data):
        low = lambda d: {nfc(k).strip().lower(): v for k, v in (d or {}).items()}
        self.titulos = low(data.get("titulos"))
        self.lugares = low(data.get("lugares"))
        self.nombres = low(data.get("nombres"))
        self.portadas = data.get("portadas") or {}

    def titulo(self, stem, auto):
        k = nfc(stem).strip().lower()
        return self.titulos[k] if k in self.titulos else auto

    def lugar(self, stem):
        return self.lugares.get(nfc(stem).strip().lower())

    def nombre(self, text):
        p = pretty(text)
        return self.nombres.get(p.lower(), p)


def cargar():
    medios = json.loads((ROOT / "data" / "medios.json").read_text(encoding="utf-8"))
    aj_path = Path(__file__).resolve().parent / "ajustes.json"
    aj = Ajustes(json.loads(aj_path.read_text(encoding="utf-8")) if aj_path.exists() else {})
    return medios, aj


def videos_por_carpeta(medios):
    """{ 'lugares': [video, ...], ... }  (clave = carpeta en minúsculas)"""
    out = {}
    for rel, info in medios["videos"].items():
        parts = rel.split("/")
        if len(parts) < 2:
            continue
        v = dict(info)
        v["rel"] = rel
        v["parts"] = parts[1:-1]              # subcarpetas dentro de la categoría
        v["stem"] = nfc(Path(parts[-1]).stem)
        v["folder"] = parts[0]
        out.setdefault(nfc(parts[0]).lower(), []).append(v)
    for lst in out.values():
        lst.sort(key=lambda v: natural_key(v["rel"]))
    return out


def auto_title(stem):
    t = pretty(stem)
    return "" if SIN_TITULO.match(stem.strip()) or SIN_TITULO.match(t) else t


# ---------------------------------------------------------------- agrupado por página
def group(titulo, items, sub=""):
    return {"titulo": titulo, "sub": sub, "items": items}


def armar_lugares(vs, aj):
    groups = {}
    for v in vs:
        if v["parts"]:
            place = aj.nombre(v["parts"][0])
        else:
            place = aj.lugar(v["stem"])
            if not place:
                m = re.search(r"(?:^|\s|[a-z])[Ee]n\s*([A-ZÁÉÍÓÚÑ].*)$", pretty(v["stem"]))
                place = aj.nombre(m[1]) if m else aj.nombre(v["stem"])
        auto = auto_title(v["stem"])
        if re.sub(r"^en\s+", "", auto.lower()) == place.lower():
            auto = ""
        v["titulo"] = aj.titulo(v["stem"], auto)
        groups.setdefault(place, []).append(v)
    keys = sorted(groups, key=lambda k: (k.startswith("Otros"), natural_key(k)))
    return [{"titulo": "", "grupos": [group(k, groups[k]) for k in keys]}]


def armar_simple(vs, aj):
    groups = {}
    for v in vs:
        v["titulo"] = aj.titulo(v["stem"], auto_title(v["stem"]))
        key = aj.nombre(v["parts"][0]) if v["parts"] else ""
        groups.setdefault(key, []).append(v)
    keys = sorted(groups, key=lambda k: (k != "", natural_key(k)))
    return [{"titulo": "", "grupos": [group(k, groups[k]) for k in keys]}]


DIA = re.compile(r"d[ií]a\s*(\d+)", re.I)


def armar_juegos(vs, aj):
    momentos, dias = [], {}
    for v in vs:
        stem = v["stem"]
        entero = "ENTER" in stem.upper()
        t = re.sub(r"[-\s]*ENTERO.*$", "", stem, flags=re.I)
        t = re.sub(r"\bUNA PARTE\b", "", t, flags=re.I)
        t = DIA.sub("", t)
        v["titulo"] = aj.titulo(stem, "" if SIN_TITULO.match(stem.strip()) else pretty(t))
        if entero:
            m = DIA.search(stem)
            dias.setdefault(int(m[1]) if m else 0, []).append(v)
        else:
            momentos.append(v)
    secciones = []
    if momentos:
        secciones.append({
            "titulo": "Momentos", "id": "momentos",
            "intro": "Fragmentos del show en el escenario de los Juegos.",
            "grupos": [group("", momentos)],
        })
    if dias:
        secciones.append({
            "titulo": "Canciones enteras", "id": "canciones-enteras",
            "intro": "Temas completos, de principio a fin, ordenados por día.",
            "grupos": [
                group(f"Día {d}" if d else "Otros días", dias[d],
                      f"{len(dias[d])} {'canción' if len(dias[d]) == 1 else 'canciones'}")
                for d in sorted(dias, key=lambda d: (d == 0, d))
            ],
        })
    return secciones


def armar_dopashock(vs, aj):
    groups = {}
    for v in vs:
        stem = v["stem"]
        clean = re.sub(r"\bdopa\s*shock\b", "", stem, flags=re.I).strip(" -")
        place = aj.lugar(stem) or (aj.nombre(v["parts"][0]) if v["parts"] else None)
        title = clean
        if not place:
            m = re.search(r"(?:^|\s)EN\s+(.+?)(?:\s+(\d+))?$", clean, re.I)
            if m:
                place = aj.nombre(m[1])
                title = clean[: m.start()].strip()
        v["titulo"] = aj.titulo(stem, pretty(title) if title else "")
        groups.setdefault(place or "", []).append(v)
    keys = sorted(groups, key=lambda k: (k == "", natural_key(k)))
    return [{"titulo": "", "grupos": [
        group(k or ("Más shows" if len(keys) > 1 else ""), groups[k],
              "" if k else "Otros escenarios y temas")
        for k in keys
    ]}]


def armar_bandas(vs, aj):
    groups = {}
    for v in vs:
        band = aj.nombre(v["parts"][0]) if v["parts"] else ""
        auto = auto_title(v["stem"])
        if band and auto.lower().startswith(band.lower()):
            auto = auto[len(band):].strip(" -·")
            auto = auto[:1].upper() + auto[1:]
        v["titulo"] = aj.titulo(v["stem"], auto)
        groups.setdefault(band, []).append(v)
    keys = sorted(groups, key=lambda k: (k == "", natural_key(k)))
    return [{"titulo": "", "grupos": [
        group(k or "Otras formaciones", groups[k]) for k in keys
    ]}]


MODOS = {
    "lugares": armar_lugares, "simple": armar_simple, "juegos": armar_juegos,
    "dopashock": armar_dopashock, "bandas": armar_bandas,
}


def armar_paginas(medios, aj):
    por_carpeta = videos_por_carpeta(medios)
    paginas = []
    usadas = set()
    for p in PAGINAS:
        vs = por_carpeta.get(p["carpeta"], [])
        usadas.add(p["carpeta"])
        if not vs:
            continue
        paginas.append({**p, "videos": vs, "secciones": MODOS[p["modo"]](vs, aj)})
    for carpeta, vs in sorted(por_carpeta.items()):
        if carpeta in usadas:
            continue
        nombre = aj.nombre(vs[0]["folder"])
        paginas.append({
            "carpeta": carpeta, "slug": slug(carpeta), "menu": nombre, "modo": "simple",
            "titulo": nombre, "eyebrow": "Videos", "intro": "",
            "desc": f"{nombre}: videos de Branco tocando el saxo en vivo.",
            "videos": vs, "secciones": armar_simple(vs, aj),
        })
    for p in paginas:
        p["n"] = len(p["videos"])
        portada = p.get("portada_rel") or aj.portadas.get(p["slug"])
        cover = next((v for v in p["videos"] if portada and nfc(v["rel"]).lower() == nfc(portada).lower()), None)
        p["cover"] = cover or p["videos"][0]
        p["grupos_n"] = sum(1 for s in p["secciones"] for g in s["grupos"] if g["titulo"])
    return paginas


def es_lugar(titulo):
    """Los grupos genéricos ("Más shows", "Otros bares") no cuentan como lugar."""
    return bool(titulo) and not titulo.startswith(("Más ", "Otros", "Otras"))


# ---------------------------------------------------------------- HTML
def render_nav(paginas, actual):
    links = []
    for p in paginas:
        cur = ' aria-current="page"' if p["slug"] == actual else ""
        links.append(f'<a href="{p["slug"]}.html"{cur}>{esc(p["menu"])}</a>')
    home_cur = ' aria-current="page"' if actual == "index" else ""
    contacto = "#contacto" if actual == "index" else "index.html#contacto"
    return f"""<nav class="nav" id="nav" aria-label="Principal">
      <a href="index.html" class="nav__brand" aria-label="Branco — Inicio">
        <img src="assets/logos/branco.webp" alt="Branco" width="120" height="120" />
      </a>
      <div class="nav__links" id="navLinks">
        <a href="index.html"{home_cur}>Inicio</a>
        {chr(10).join('        ' + l for l in links).strip()}
        <a href="{contacto}" class="btn btn--gold nav__cta">Contratar</a>
      </div>
      <button class="nav__toggle" id="navToggle" aria-label="Abrir menú" aria-expanded="false" aria-controls="navLinks">
        <span></span><span></span><span></span>
      </button>
    </nav>"""


def render_footer(paginas):
    links = "\n".join(f'<a href="{p["slug"]}.html">{esc(p["menu"])}</a>' for p in paginas)
    return (TPL / "footer.html").read_text(encoding="utf-8").replace("{{FOOTER_LINKS}}", links)


def card(v):
    orient = "h" if v["w"] > v["h"] else "v"
    t = v.get("titulo") or ""
    label = f"Reproducir: {t}" if t else "Reproducir video"
    title_html = f'<span class="vcard__title">{esc(t)}</span>' if t else ""
    return (
        f'<a class="vcard vcard--{orient}" href="{esc(v["src"])}" data-video '
        f'data-title="{esc(t)}" data-poster="{esc(v["poster"])}" aria-label="{esc(label)}">'
        f'<img src="{esc(v["poster"])}" alt="" width="{v["w"]}" height="{v["h"]}" loading="lazy" decoding="async" />'
        f'<span class="vcard__play">{ICON_PLAY}</span>'
        f'<span class="vcard__dur">{fmt_dur(v["dur"])}</span>{title_html}</a>'
    )


def grids(items):
    hs = [v for v in items if v["w"] > v["h"]]
    vs = [v for v in items if v["w"] <= v["h"]]
    out = []
    if hs:
        out.append('<div class="vgrid vgrid--h">' + "".join(card(v) for v in hs) + "</div>")
    if vs:
        out.append('<div class="vgrid vgrid--v">' + "".join(card(v) for v in vs) + "</div>")
    return "\n".join(out)


def render_secciones(p):
    html_out, chips = [], []
    for s in p["secciones"]:
        parts = []
        if s.get("titulo"):
            sid = s.get("id") or slug(s["titulo"])
            chips.append((sid, s["titulo"], True))
            intro = f'<p>{esc(s["intro"])}</p>' if s.get("intro") else ""
            parts.append(
                f'<header class="block__head reveal" id="{sid}"><h2>{esc(s["titulo"])}</h2>{intro}</header>'
            )
        # Grupos con un solo video: van juntos en una grilla, con el nombre
        # arriba de cada video (así no queda una fila casi vacía por lugar).
        singles = [g for g in s["grupos"] if g["titulo"] and len(g["items"]) == 1]
        if len(singles) < 2:
            singles = []
        singles_done = False
        for g in s["grupos"]:
            n = len(g["items"])
            gid = ""
            if g["titulo"]:
                gid = slug((s.get("id") or "") + "-" + g["titulo"]) if s.get("titulo") else slug(g["titulo"])
                chips.append((gid, g["titulo"], False))
            if g in singles:
                if not singles_done:
                    parts.append(render_singles(s, singles))
                    singles_done = True
            elif g["titulo"]:
                sub = g["sub"] or f"{n} {'video' if n == 1 else 'videos'}"
                tag = "h3" if s.get("titulo") else "h2"
                parts.append(
                    f'<section class="group reveal" id="{gid}">'
                    f'<header class="group__head"><{tag}>{esc(g["titulo"])}</{tag}>'
                    f'<span>{esc(sub)}</span></header>{grids(g["items"])}</section>'
                )
            else:
                parts.append(f'<section class="group reveal">{grids(g["items"])}</section>')
        html_out.append('<div class="block">' + "\n".join(parts) + "</div>")
    return "\n".join(html_out), chips


def render_singles(s, singles):
    def labeled(g):
        gid = slug((s.get("id") or "") + "-" + g["titulo"]) if s.get("titulo") else slug(g["titulo"])
        return (f'<div class="lcard" id="{gid}"><h3 class="lcard__name">{esc(g["titulo"])}</h3>'
                f'{card(g["items"][0])}</div>')
    hs = [g for g in singles if g["items"][0]["w"] > g["items"][0]["h"]]
    vs = [g for g in singles if g not in hs]
    out = []
    if hs:
        out.append('<div class="vgrid vgrid--h">' + "".join(labeled(g) for g in hs) + "</div>")
    if vs:
        out.append('<div class="vgrid vgrid--v">' + "".join(labeled(g) for g in vs) + "</div>")
    return '<section class="group group--singles reveal">' + "\n".join(out) + "</section>"


def render_subnav(chips):
    if len(chips) < 2:
        return ""
    links = "".join(
        f'<a href="#{cid}" class="{"is-main" if main else ""}">{esc(t)}</a>' for cid, t, main in chips
    )
    return f'<nav class="subnav" aria-label="Secciones de la página"><div class="subnav__inner wrap">{links}</div></nav>'


def stats_line(p):
    n = p["n"]
    s = [f"{n} {'video' if n == 1 else 'videos'}"]
    g = p["grupos_n"]
    if p["modo"] in ("lugares", "dopashock") and g:
        real = sum(1 for sec in p["secciones"] for gr in sec["grupos"] if es_lugar(gr["titulo"]))
        if real:
            s.append(f"{real} {'lugar' if real == 1 else 'lugares'}")
    if p["modo"] == "bandas" and g:
        real = sum(1 for sec in p["secciones"] for gr in sec["grupos"] if gr["titulo"] != "Otras formaciones")
        s.append(f"{real} {'banda' if real == 1 else 'bandas'}")
    if p["modo"] == "juegos":
        enteras = sum(len(gr["items"]) for sec in p["secciones"] if sec.get("id") == "canciones-enteras" for gr in sec["grupos"])
        if enteras:
            s.append(f"{enteras} canciones enteras")
    return " · ".join(s)


def page_hero(p, medios):
    extra = ""
    bg = p["cover"]["poster"]
    if p.get("tema") == "dopa":
        fotos = medios.get("fotos", {}).get("dopashock") or []
        if fotos:
            bg = fotos[0]["src"]
        extra = (
            '<img class="phero__logo" src="assets/logos/dopashock-wordmark.webp" '
            'alt="DopaShock" width="843" height="296" />'
        )
        title_html = f'<h1 class="visually-hidden">{esc(p["titulo"])}</h1>'
    else:
        title_html = f'<h1>{esc(p["titulo"])}</h1>'
    intro = f'<p class="phero__lead">{esc(p["intro"])}</p>' if p.get("intro") else ""
    return f"""<header class="phero">
        <div class="phero__bg" style="background-image:url('{esc(bg)}')" aria-hidden="true"></div>
        <div class="wrap phero__inner">
          <p class="eyebrow">{esc(p["eyebrow"])}</p>
          {extra}{title_html}
          {intro}
          <p class="phero__stats">{esc(stats_line(p))}</p>
        </div>
      </header>"""


CTA = """<section class="cta">
        <div class="wrap cta__inner reveal">
          <div>
            <p class="eyebrow">Contrataciones</p>
            <h2>¿Querés este show en tu evento?</h2>
            <p>Bares, eventos privados, empresas y festivales. Escribime y armamos la propuesta.</p>
          </div>
          <div class="cta__btns">
            <a class="btn btn--gold" data-wa href="index.html#contacto">Escribime por WhatsApp</a>
            <a class="btn btn--ghost" href="index.html#contacto">Ver contacto</a>
          </div>
        </div>
      </section>"""


def base(nav, footer, content, *, title, desc, path, image, body_class=""):
    url = SITE_URL + ("" if path == "index.html" else path)
    img = SITE_URL + image
    t = (TPL / "base.html").read_text(encoding="utf-8")
    rep = {
        "{{TITLE}}": esc(title), "{{DESC}}": esc(desc), "{{URL}}": esc(url),
        "{{IMAGE}}": esc(img), "{{SITE}}": SITE_URL, "{{NAV}}": nav,
        "{{CONTENT}}": content, "{{FOOTER}}": footer, "{{BODY_CLASS}}": body_class,
    }
    for k, v in rep.items():
        t = t.replace(k, v)
    return t


def render_pagina(p, paginas, medios):
    body, chips = render_secciones(p)
    content = "\n".join([
        page_hero(p, medios),
        render_subnav(chips),
        f'<div class="wrap page">{body}</div>',
        CTA,
    ])
    return base(
        render_nav(paginas, p["slug"]), render_footer(paginas), content,
        title=f'{p["titulo"]} — Branco Saxofonista', desc=p["desc"],
        path=f'{p["slug"]}.html', image=p["cover"]["poster"],
        body_class=f'page-{p["slug"]}' + (f' theme-{p["tema"]}' if p.get("tema") else ""),
    )


def xcols(n):
    """Columnas para las tarjetas del inicio, sin dejar una sola en la última fila."""
    if n <= 5:
        return n
    for c in (4, 3, 5):
        if n % c == 0:
            return c
    return 4 if n % 4 >= 2 else 3


def render_inicio(paginas, medios):
    cards = []
    for p in paginas:
        c = p["cover"]
        cards.append(f"""<a class="xcard reveal" href="{p["slug"]}.html">
            <img src="{esc(c["poster"])}" alt="" width="{c["w"]}" height="{c["h"]}" loading="lazy" decoding="async" />
            <span class="xcard__body">
              <span class="xcard__eyebrow">{esc(p["eyebrow"])}</span>
              <span class="xcard__title">{esc(p["titulo"])}</span>
              <span class="xcard__meta">{esc(stats_line(p))}</span>
            </span>
            <span class="xcard__arrow" aria-hidden="true">→</span>
          </a>""")
    fotos = medios.get("fotos", {}).get("branco") or []
    slides = "\n".join(
        f'<figure class="pslide" role="button" tabindex="0" aria-label="Ampliar foto">'
        f'<img src="{esc(f["src"])}" width="{f["w"]}" height="{f["h"]}" loading="lazy" decoding="async" '
        f'alt="Branco tocando el saxo en vivo" /></figure>'
        for f in fotos
    )
    total = sum(p["n"] for p in paginas)
    lugares = sum(
        1 for p in paginas if p["modo"] in ("lugares", "dopashock")
        for s in p["secciones"] for g in s["grupos"] if es_lugar(g["titulo"])
    )
    bandas = sum(
        1 for p in paginas if p["modo"] == "bandas"
        for s in p["secciones"] for g in s["grupos"] if g["titulo"] != "Otras formaciones"
    )
    stats = [(total, "videos en vivo"), (lugares, "lugares y escenarios"), (bandas, "bandas y proyectos")]
    stats_html = "".join(
        f'<div class="stat"><b data-count="{n}">{n}</b><span>{esc(l)}</span></div>' for n, l in stats if n
    )
    dopa = next((p for p in paginas if p["slug"] == "dopashock"), None)
    dopa_fotos = medios.get("fotos", {}).get("dopashock") or []
    dopa_img = dopa_fotos[0]["src"] if dopa_fotos else (dopa["cover"]["poster"] if dopa else "")

    t = (TPL / "inicio.html").read_text(encoding="utf-8")
    rep = {
        "{{EXPLORAR}}": "\n".join(cards),
        "{{XCOLS}}": str(xcols(len(cards))),
        "{{FOTOS}}": slides,
        "{{STATS}}": stats_html,
        "{{DOPA_IMG}}": esc(dopa_img),
        "{{DOPA_META}}": esc(stats_line(dopa)) if dopa else "",
    }
    for k, v in rep.items():
        t = t.replace(k, v)
    return base(
        render_nav(paginas, "index"), render_footer(paginas), t,
        title="Branco — Saxofonista | Show de saxo en vivo para bares, eventos y festivales",
        desc="Branco, saxofonista. Show de saxo en vivo para bares, eventos privados, empresas y festivales. Mirá los videos en vivo.",
        path="index.html", image="assets/img/hero.jpg", body_class="page-index",
    )


def write(name, text):
    (ROOT / name).write_text(text, encoding="utf-8", newline="\n")


def main():
    medios, aj = cargar()
    paginas = armar_paginas(medios, aj)
    # borrar páginas de categorías que ya no existen
    marca = "<!-- generado por tools/generar_paginas.py -->"
    vigentes = {p["slug"] + ".html" for p in paginas} | {"index.html"}
    for f in ROOT.glob("*.html"):
        if f.name not in vigentes and marca in f.read_text(encoding="utf-8", errors="ignore"):
            f.unlink()
    write("index.html", render_inicio(paginas, medios))
    for p in paginas:
        write(p["slug"] + ".html", render_pagina(p, paginas, medios))
    urls = [SITE_URL] + [SITE_URL + p["slug"] + ".html" for p in paginas]
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n'
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
          + "".join(f"  <url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n")
    write("robots.txt", f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}sitemap.xml\n")
    for p in paginas:
        print(f'  {p["slug"]}.html  ({stats_line(p)})')
    print("Páginas generadas.")


if __name__ == "__main__":
    main()
