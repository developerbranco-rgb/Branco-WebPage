"""
Procesa los videos e imágenes ORIGINALES y genera versiones livianas para la web.

    videos/   (originales, NO se suben)  ->  media/   (mp4 720p + miniatura .webp)
    imagenes/ (originales, NO se suben)  ->  assets/fotos, assets/logos

Solo procesa lo nuevo o lo que cambió, así que correrlo de nuevo es rápido.
Al final escribe data/medios.json, que usa generar_paginas.py.

No hace falta correrlo a mano: usá actualizar.bat
"""

import json
import os
import re
import subprocess
import sys
import unicodedata
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
VIDEOS = ROOT / "videos"
IMAGENES = ROOT / "imagenes"
MEDIA = ROOT / "media"
FOTOS_OUT = ROOT / "assets" / "fotos"
LOGOS_OUT = ROOT / "assets" / "logos"
MANIFEST = ROOT / "data" / "medios.json"

VIDEO_EXT = {".mp4", ".mov", ".m4v", ".mkv", ".avi", ".webm", ".3gp"}
IMG_EXT = {".jpg", ".jpeg", ".png", ".webp", ".heic"}

# Calidad de los videos para la web: lado corto máx. 720px, ~1.5 Mbps.
# Subir CRF = más liviano / menos calidad. Bajarlo = al revés.
LADO_CORTO = 720
CRF = "27"
MAXRATE = "1800k"


def ffmpeg_exe():
    try:
        import imageio_ffmpeg

        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        return "ffmpeg"


FF = ffmpeg_exe()


def slugify(text, maxlen=60):
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return (text[:maxlen].rstrip("-")) or "video"


def probe(path):
    """Devuelve (ancho, alto, duración, es_hdr) leyendo la salida de ffmpeg -i."""
    out = subprocess.run(
        [FF, "-hide_banner", "-i", str(path)],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
    ).stderr
    dur = 0.0
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", out)
    if m:
        dur = int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])
    vline = next((l for l in out.splitlines() if "Video:" in l), "")
    w = h = 0
    m = re.search(r"\b(\d{2,5})x(\d{2,5})\b", vline)
    if m:
        w, h = int(m[1]), int(m[2])
    rot = re.search(r"rotation of (-?[\d.]+)", out)
    if rot and abs(round(float(rot[1]))) % 180 == 90:
        w, h = h, w
    hdr = "arib-std-b67" in vline or "smpte2084" in vline
    return w, h, dur, hdr


def detect_crop(src, dur, w, h):
    """Detecta franjas negras (ej. video vertical guardado en horizontal) y devuelve 'crop=...' o ''."""
    crops = []
    for frac in (0.15, 0.3, 0.5, 0.7, 0.85):
        out = subprocess.run(
            [FF, "-hide_banner", "-ss", f"{dur * frac:.2f}", "-i", str(src), "-t", "1",
             "-vf", "cropdetect=limit=24:round=2:reset=0", "-an", "-f", "null", "-"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        ).stderr
        found = re.findall(r"crop=(\d+):(\d+):(\d+):(\d+)", out)
        if found:
            crops.append(tuple(map(int, found[-1])))
    if len(crops) < 3 or not w or not h:
        return ""
    # el recorte que más se repite; las franjas reales son iguales de los dos lados
    cw, ch, x, y = max(set(crops), key=crops.count)
    if crops.count((cw, ch, x, y)) < 3:
        return ""
    if abs(x - (w - cw - x)) > 8 or abs(y - (h - ch - y)) > 8:
        return ""
    if cw * ch > 0.85 * w * h or cw < w * 0.2 or ch < h * 0.2:
        return ""
    return f"crop={cw}:{ch}:{x}:{y},"


def encode_video(src, dst, hdr, crop=""):
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_suffix(".tmp.mp4")
    scale = (
        f"scale='if(gt(iw,ih),-2,min({LADO_CORTO},iw))':"
        f"'if(gt(iw,ih),min({LADO_CORTO},ih),-2)':flags=lanczos"
    )
    if hdr:  # videos HDR del iPhone -> SDR, para que no se vean lavados
        vf = crop + (
            "zscale=t=linear:npl=100,format=gbrpf32le,zscale=p=bt709,"
            "tonemap=tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv,"
            + scale + ",format=yuv420p"
        )
    else:
        vf = crop + scale + ",format=yuv420p"
    cmd = [
        FF, "-y", "-hide_banner", "-loglevel", "error", "-i", str(src),
        "-map", "0:v:0", "-map", "0:a:0?", "-vf", vf, "-fpsmax", "30",
        "-c:v", "libx264", "-preset", "medium", "-crf", CRF,
        "-maxrate", MAXRATE, "-bufsize", "3600k", "-profile:v", "high",
        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
        "-c:a", "aac", "-b:a", "128k", "-ac", "2",
        "-movflags", "+faststart", "-map_metadata", "-1", str(tmp),
    ]
    subprocess.run(cmd, check=True)
    os.replace(tmp, dst)


def make_poster(video, dst, dur):
    t = min(1.5, max(0.0, dur * 0.2))
    subprocess.run(
        [FF, "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{t:.2f}",
         "-i", str(video), "-frames:v", "1", "-c:v", "libwebp", "-quality", "72",
         str(dst)],
        check=True,
    )


def process_videos(old):
    entries = {}
    files = sorted(
        p for p in VIDEOS.rglob("*")
        if p.is_file() and p.suffix.lower() in VIDEO_EXT
    )
    used = set()
    for i, src in enumerate(files, 1):
        rel = src.relative_to(VIDEOS).as_posix()
        parts = [slugify(x, 40) for x in src.relative_to(VIDEOS).parent.parts]
        base = slugify(src.stem)
        out_rel = "/".join(["media", *parts, base])
        n = 2
        while out_rel in used:  # mismo nombre con distinta extensión
            out_rel = "/".join(["media", *parts, f"{base}-{n}"])
            n += 1
        used.add(out_rel)
        mp4 = ROOT / (out_rel + ".mp4")
        webp = ROOT / (out_rel + ".webp")
        size = src.stat().st_size

        prev = old.get(rel)
        if prev and prev.get("size") == size and mp4.exists() and webp.exists() \
                and prev.get("src") == out_rel + ".mp4":
            entries[rel] = prev
            continue

        print(f"[{i}/{len(files)}] Procesando {rel} ...", flush=True)
        sw, sh, dur, hdr = probe(src)
        crop = detect_crop(src, dur, sw, sh)
        if crop:
            print("   (recortando franjas negras)", flush=True)
        encode_video(src, mp4, hdr, crop)
        w, h, dur, _ = probe(mp4)
        make_poster(mp4, webp, dur)
        entries[rel] = {
            "src": out_rel + ".mp4",
            "poster": out_rel + ".webp",
            "w": w, "h": h, "dur": round(dur, 1),
            "size": size,
            "mb": round(mp4.stat().st_size / 1e6, 1),
        }
    # Borrar archivos web de videos que ya no existen
    keep = {ROOT / e["src"] for e in entries.values()} | {ROOT / e["poster"] for e in entries.values()}
    if MEDIA.exists():
        for f in MEDIA.rglob("*"):
            if f.is_file() and f not in keep:
                print("Eliminando (ya no está el original):", f.relative_to(ROOT))
                f.unlink()
        for d in sorted((d for d in MEDIA.rglob("*") if d.is_dir()), reverse=True):
            if not any(d.iterdir()):
                d.rmdir()
    return entries


def save_image(src, dst, max_side, quality=80):
    from PIL import Image, ImageOps

    dst.parent.mkdir(parents=True, exist_ok=True)
    im = ImageOps.exif_transpose(Image.open(src))
    im.thumbnail((max_side, max_side), Image.LANCZOS)
    if im.mode not in ("RGB", "RGBA"):
        im = im.convert("RGBA" if "A" in im.getbands() else "RGB")
    im.save(dst, "WEBP", quality=quality, method=6)
    return im.size


def process_photos(old):
    """Cada carpeta dentro de imagenes/ que empiece con 'IMAGENES' es una galería."""
    galleries = {}
    if not IMAGENES.exists():
        return old
    for folder in sorted(p for p in IMAGENES.iterdir() if p.is_dir()):
        if not folder.name.upper().startswith("IMAGENES"):
            continue
        key = slugify(folder.name.upper().replace("IMAGENES", "", 1)) or "general"
        prev = {e["orig"]: e for e in old.get(key, [])}
        items = []
        for src in sorted(folder.iterdir()):
            if src.suffix.lower() not in IMG_EXT:
                continue
            dst = FOTOS_OUT / key / (slugify(src.stem) + ".webp")
            rel = dst.relative_to(ROOT).as_posix()
            size = src.stat().st_size
            p = prev.get(src.name)
            if p and p.get("size") == size and dst.exists():
                items.append(p)
                continue
            print("Foto:", src.relative_to(ROOT))
            w, h = save_image(src, dst, 1600, 80)
            items.append({"orig": src.name, "src": rel, "w": w, "h": h, "size": size})
        galleries[key] = items
    return galleries


# Logos elegidos de imagenes/LOGOS  ->  assets/logos
LOGOS = {
    "branco.webp": ("LOGOS/BRANCO/Branco.sax.png", 520),
    "branco-escudo.webp": ("LOGOS/BRANCO/ESCUDO MIO STICKERS.PNG", 520),
    "dopashock-wordmark.webp": ("LOGOS/DOPASHOCK/Logotipo_futurista_DOPASHOCK_neón-removebg-preview.png", 843),
    "dopashock-emblema.webp": ("LOGOS/DOPASHOCK/Emblema neón de D y saxofón.png", 600),
}


def process_logos():
    for name, (rel, side) in LOGOS.items():
        src = IMAGENES / rel
        dst = LOGOS_OUT / name
        if src.exists() and (not dst.exists() or dst.stat().st_mtime < src.stat().st_mtime):
            print("Logo:", name)
            save_image(src, dst, side, 90)
    # favicon / ícono para celulares a partir del logo de Branco
    src = IMAGENES / LOGOS["branco-escudo.webp"][0]
    if src.exists() and not (ROOT / "assets" / "icon-512.png").exists():
        from PIL import Image

        im = Image.open(src).convert("RGBA")
        for s in (512, 180, 32):
            im.resize((s, s), Image.LANCZOS).save(ROOT / "assets" / f"icon-{s}.png")


def main():
    old = {}
    if MANIFEST.exists():
        old = json.loads(MANIFEST.read_text(encoding="utf-8"))

    if VIDEOS.exists():
        videos = process_videos(old.get("videos", {}))
    else:
        print("No encuentro la carpeta 'videos', dejo los videos como estaban.")
        videos = old.get("videos", {})

    fotos = process_photos(old.get("fotos", {}))
    if IMAGENES.exists():
        process_logos()

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(
        json.dumps({"videos": videos, "fotos": fotos}, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    total = sum(e.get("mb", 0) for e in videos.values())
    print(f"\nListo: {len(videos)} videos ({total:.0f} MB en la web).")
    if total > 850:
        print("ATENCION: GitHub Pages permite ~1 GB. Conviene subir CRF o sacar videos.")


if __name__ == "__main__":
    sys.exit(main())
