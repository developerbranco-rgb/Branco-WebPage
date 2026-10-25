# 🎷 Branco — Portfolio Saxofonista

Carta de presentación para bares, eventos, empresas y festivales.

**Sitio en vivo:** https://developerbranco-rgb.github.io/Branco-WebPage/

## ➕ Cómo agregar videos (lo único que vas a hacer seguido)

1. Copiá el video a la carpeta que corresponda dentro de `videos/`:

   | Carpeta                         | Página                | Cómo se agrupa                                              |
   | ------------------------------- | --------------------- | ----------------------------------------------------------- |
   | `videos/lugares/`               | Lugares               | Una **subcarpeta por lugar** (ej. `lugares/Complejo Forest/`). El nombre de la carpeta es el título. |
   | `videos/Eventos/`               | Eventos               | Todos juntos (o en subcarpetas si querés grupos).           |
   | `videos/Juegos suramericanos/`  | Juegos Suramericanos  | Si el nombre dice **ENTERO** va a "Canciones enteras", separado por **DIA 3**, **DIA 7**, etc. |
   | `videos/DopaShock/`             | DopaShock             | Por lugar, según el nombre: `DOPASHOCK EN <LUGAR> 1.mp4` (o una subcarpeta por lugar). |
   | `videos/bandas/`                | Bandas                | Una **subcarpeta por banda** (ej. `bandas/FUNKLOPA/`).       |
   | `videos/<Carpeta nueva>/`       | ¡Página nueva sola!   | Aparece en el menú automáticamente.                         |

2. Hacé doble clic en **`actualizar.bat`**. Comprime los videos nuevos, rearma
   las páginas y (si le decís que sí) los sube a internet.

Fotos: poné las imágenes en `imagenes/IMAGENES BRANCO/` (carrusel del inicio) o
`imagenes/IMAGENES DOPASHOCK/` (fondo de DopaShock) y corré `actualizar.bat`.

### Cambiar títulos o lugares

Por defecto el título sale del nombre del archivo. Para corregir uno (tildes,
mayúsculas, sacar un título), editá **`tools/ajustes.json`**. La clave es el
nombre del archivo sin extensión.

## ✏️ Datos de contacto

En **`script.js`**, bloque `CONFIG` de arriba de todo (WhatsApp, Instagram, email).

## 🗂️ Estructura

```
index.html, lugares.html, ...  → páginas (GENERADAS: no editarlas a mano)
styles.css / script.js         → diseño e interacción
tools/plantillas/              → textos del inicio, pie de página, <head>
tools/generar_paginas.py       → arma las páginas (textos de cada sección arriba de todo)
tools/procesar_medios.py       → comprime videos/fotos (720p H.264, ~1.5 Mbps)
tools/ajustes.json             → títulos/lugares a mano
media/                         → videos web + miniaturas (generados)
assets/                        → logos, fotos y video del inicio
videos/, imagenes/             → ORIGINALES (no se suben a internet)
```

> GitHub Pages permite ~1 GB de sitio. `actualizar.bat` avisa si te acercás al
> límite. La URL del sitio está en `SITE_URL` dentro de `tools/generar_paginas.py`.

## 🚀 Verlo en la compu

```bash
python -m http.server 8000
# abrí http://localhost:8000
```
