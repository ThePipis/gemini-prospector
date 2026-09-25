---
name: redesign-premium
description: Esta skill debe ser usada al rediseñar el sitio web de un cliente prospectado — crear una versión nueva, premium y de alta conversión de la página existente, manteniendo contenido, logo y paleta del cliente, adaptado al idioma del negocio (Inglés o Español para California/USA). Acione cuando el usuario diga "rediseñar sitio", "mejorar página", "rehacer web", "redesign" o pida rediseñar (skill redesign-premium).
---

# Rediseño Premium de Páginas (Mercado USA / California)

Crear una **NUEVA VERSIÓN DE ALTA CONVERSIÓN** del sitio web del cliente — no un sitio inventado. El dueño del negocio debe reconocer su identidad, logotipo y servicios inmediatamente, pero elevados al nivel estético que su facturación merece.

## Reglas Inviolables de Calidad

1. **Cero Hechos Inventados — Texto Aprimorado con Copywriting Senior:**
   * Todos los servicios, credenciales, certificaciones, direcciones y números telefónicos provienen del sitio original o de su perfil de Google Maps.
   * Sin embargo, el texto **se reescribe con técnica**: titulares magnéticos, beneficios claros, estructura PAS (Problema-Agitación-Solución) y lectura fluida, ya sea en **Inglés** o **Español** según el idioma del cliente.
2. **Fotografías y Logotipo Originales Mandatorios:**
   * Extraer las imágenes reales del sitio actual (`img.currentSrc` mediante Playwright) y logos. El cliente debe reconocer a su equipo y consultorio al instante.
3. **Identidad Visual Preservada y Refinada:**
   * Mantener los colores de marca. Si la paleta original es tosca o saturada, refinar los tonos (ej. azul marino profundo, acentos en oro o azul cobalto), nunca cambiar drásticamente la familia de colores.
4. **Archivo Único Autocontenido:**
   * `sites/[slug]/[slug].html` autocontenido: CSS inline en el `<head>`, tipografía Google Fonts (`Inter`, `Plus Jakarta Sans`, `Playfair Display`), sin builds complejos ni frameworks pesados para que cargue en milisegundos en Cloudflare.
5. **Responsividad Total (Mobile-First):**
   * El cliente evaluará la propuesta en su teléfono. La página debe ser impecable en 360px, 375px (iPhone), 768px (iPad) y pantallas de escritorio (1440px). Cero desbordes horizontales. Tipografía fluida con `clamp()`.
6. **Editor Visual Integrado:**
   * Todo rediseño genera automáticamente `sites/[slug]/[slug]-editor.html` (con la barra de edición visual de `references/editor-visual.md`).
7. **Comparador Antes / Después:**
   * Todo lote de rediseño actualiza `comparar.html` en la raíz del proyecto para visualizar el sitio original vs. el nuevo lado a lado.

## Estructura de la Landing Page

1. **Hero**: Nombre del negocio + especialidad + propuesta de valor clara en 1 línea + CTA directo visible sin hacer scroll (Botón de Llamar `tel:+1...` y WhatsApp / Agendar).
2. **Prueba Social Inmediata**: Calificación de Google en grande (*"5.0 ★ · 140+ Google Reviews"*) y 2-3 citas textuales reales de pacientes o clientes.
3. **Servicios / Áreas de Práctica**: Tarjetas limpias con llamada a la acción contextual pre-llenada:
   - En inglés: `https://wa.me/1XXXXXXXXXX?text=Hi%20there!%20I'm%20interested%20in%20[Service]`
   - En español: `https://wa.me/1XXXXXXXXXX?text=Hola,%20quisiera%20información%20sobre%20[Servicio]`
4. **Acerca del Profesional / Equipo**: Trayectoria, licencias en California (State Bar, Medical Board, Dental Board si aparecen en el original).
5. **Ubicación y Horarios**: Dirección física en California, mapa incrustado, horarios de atención y teléfono click-to-call.
6. **Botón Flotante Fijo**: Botón de contacto directo en la esquina inferior derecha.

## Entregables por Cliente

Cada lead rediseñado debe tener en `sites/[slug]/`:
1. `[slug].html`: La landing page de alta conversión.
2. `[slug]-editor.html`: La versión con capa de edición en vivo.
3. `proposta.html`: La portada interactiva con el comparador y CTA hacia el prestador (copiada de `references/capa-proposta-template.html`).
