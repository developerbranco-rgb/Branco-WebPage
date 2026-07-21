# 🎷 Branco Martín — Portfolio Saxofonista

Landing page / portfolio para mostrar mi trabajo como saxofonista y recibir
contrataciones para casamientos, eventos corporativos, fiestas y bares.

**Sitio en vivo:** https://brancomartin.github.io

## ✏️ Cómo editar mis datos de contacto

Abrí **`script.js`** y editá SOLO el bloque `CONFIG` de arriba de todo:

```js
const CONFIG = {
  WHATSAPP:  "5490000000000",   // tu número, con código de país, sin + ni espacios
  INSTAGRAM: "tu_usuario",       // tu usuario de Instagram, sin la @
  EMAIL:     "brancoantu9@gmail.com"
};
```

- **WhatsApp (Argentina):** `549` + código de área + número. Ej: `5493471234567`
- **Instagram:** solo el usuario, sin `@`.

El botón flotante, el formulario y los enlaces de contacto se actualizan solos.

## 🗂️ Estructura

```
index.html      → la página
styles.css      → estilos
script.js       → interacción + configuración de contacto
assets/
  img/          → fotos optimizadas
  video/        → videos optimizados para web (H.264 .mp4)
  poster/       → miniaturas de los videos
```

Los videos y fotos originales viven fuera del repo (en OneDrive) para mantenerlo liviano.

## 🚀 Cómo verlo localmente

Abrí `index.html` en el navegador (doble clic), o serví la carpeta:

```bash
python -m http.server 8000
# luego abrí http://localhost:8000
```
