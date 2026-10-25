@echo off
chcp 65001 >nul
title Actualizar pagina de Branco
cd /d "%~dp0"

echo.
echo  ==========================================================
echo    ACTUALIZAR PAGINA WEB
echo    1) Procesa videos y fotos nuevos (puede tardar)
echo    2) Rearma todas las paginas
echo    3) Sube los cambios a internet
echo  ==========================================================
echo.

set "PY=python"
where python >nul 2>nul || set "PY=py"

%PY% -c "import imageio_ffmpeg, PIL" 2>nul || (
  echo Instalando herramientas necesarias (solo la primera vez)...
  %PY% -m pip install --user imageio-ffmpeg pillow || goto :error
)

%PY% tools\procesar_medios.py || goto :error
%PY% tools\generar_paginas.py || goto :error

echo.
set /p SUBIR="Subir los cambios a internet ahora? (S/N): "
if /i not "%SUBIR%"=="S" goto :fin

git add -A || goto :error
git commit -m "Actualizacion de videos y paginas" || echo (No habia cambios nuevos para subir)
git push || goto :error
echo.
echo  Listo! En 1 o 2 minutos se ve en internet.
goto :fin

:error
echo.
echo  Hubo un error. Revisa el mensaje de arriba.

:fin
echo.
pause
