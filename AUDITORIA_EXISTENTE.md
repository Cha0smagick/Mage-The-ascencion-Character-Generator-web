# Auditoría del código existente — Mage Character Generator

## Resumen
El proyecto actual es una app Streamlit (`app.py` + `data.py`) con generación aleatoria, construcción manual básica, exportación PDF (ReportLab) y HTML. No es una página web estática apta para GitHub Pages ni para GitHub Actions sin servidor.

## Hallazgos (solo problemas reales)

### 1. No es una página web desplegable en GitHub Actions/Pages
- `app.py` depende de Streamlit (servidor Python). No se puede hostear estáticamente en GitHub Pages.
- No hay `index.html`, ni CSS, ni JS del lado del cliente.
- **Consecuencia:** no cumple el requisito "página para GitHub Actions para crear hojas".

### 2. Lógica de puntos incompleta / rota
- `display_character_builder_ui` (líneas 317-369): pestañas de Atributos, Habilidades, Ventajas son **prototipos con sliders libres**. No aplican la regla 7/5/3 ni 13/9/5 ni validan tope de puntos.
- `initialize_character_build` define `Points` pero nunca se usa para limitar gastos.
- **Consecuencia:** el modo manual permite crear personajes ilegales según las reglas de Mage.

### 3. Generación aleatoria no respeta prioridades de facción
- `generate_character` asigna esferas al azar (máx 3) sin respetar la esfera de afinidad obligatoria de la Tradición/Convención.
- No diferencia Tradiciones, Convenios de la Tecnocracia, Crafts, Nephandi, Marauders.
- **Consecuencia:** personajes no apegados al lore.

### 4. Exportación PDF deficiente para impresión
- `generate_pdf_sheet` usa ReportLab con `Helvetica` (sin fuentes góticas/herméticas de Mage).
- Diseño de una sola columna aplastada, sin maquetación de hoja de personaje clásica (cuadrícula, trackers de salud/paradoxa, esferas con puntos).
- No usa `@page` con tamaño fijo A4/Letter; riesgo de páginas en blanco o recortes.
- **Consecuencia:** hojas no imprimibles con calidad de producto editorial.

### 5. Exportación HTML sin estilos de impresión
- `download_html_new` usa fuentes de Google (Cinzel/Lato) vía CDN. Sin conexión a internet, se rompe la estética.
- No tiene `@media print` optimizado; no hay trackers de salud/paradoxa con casillas imprimibles.
- **Consecuencia:** no imprimible offline y sin estética Mage.

### 6. Dependencia de generación de imagen externa no confiable
- `freeGPTFix` + `pollinations`: servicio externo, sin clave, con reintentos ciegos. Puede fallar en producción.
- **Consecuencia:** el retrato es opcional y frágil; no bloquea el núcleo.

### 7. Datos en español e inglés mezclados sin consistencia de lore
- `data.py`: nombres, naturalezas, conductas en inglés; algunos conceptos/objetivos en español ("Recuperar el conocimiento arcano...").
- `affiliations` y `sects` mezclan Tradiciones de Mage con facciones de Vampire (Camarilla, Anarchs, Tremere, Ordo Dracul) y Changeling (Thyrsus, Silver Ladder).
- **Consecuencia:** lore contaminado; no es fiel a Mage: The Ascension.

### 8. Sin pruebas ni CI/CD
- No hay tests, ni `.github/workflows`, ni `requirements.txt` (salvo implícito), ni `package.json`.
- **Consecuencia:** no se puede auditar ni desplegar automáticamente.

## Veredicto
**DO NOT SHIP** como está para el requisito solicitado. El núcleo de datos (`data.py`) es reutilizable tras limpieza; `app.py` debe reemplazarse por una aplicación web estática (HTML/JS) con exportación PDF/impresión y GitHub Actions.

## Reutilizable
- `data.py`: listas de nombres, esferas, naturalezas, trasfondos, virtudes/defectos, posesiones, secretos, metas, paradigmas (tras purgar facciones ajenas a Mage).
- Lógica de `generate_prompt_for_image` para prompts de retrato (opcional).
