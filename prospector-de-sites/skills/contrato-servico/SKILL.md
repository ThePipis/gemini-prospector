---
name: contrato-servico
description: Esta skill debe ser usada al generar contratos de prestación de servicios para clientes cerrados en USA (California) — creación/rediseño de landing page, despliegue en Cloudflare y mantenimiento mensual recurrente. Acione cuando el usuario diga "contrato", "generar contrato", "formalizar", "cliente cerró", "enviar contrato", "agreement", "contract" o pida el contrato (skill contrato-servico).
---

# Contrato de Servicios Comerciales (Independent Contractor Agreement - California)

Genera el borrador del acuerdo de servicios profesionales (rediseño web + despliegue en Cloudflare + mantenimiento opcional), listo para imprimirse como PDF o exportarse como documento Word (.docx) protegido.

## 1. Fuentes de Datos (En este orden)

1. **Base de Datos (`prospector.db`)**: nombre del cliente (`nome`), nicho, ciudad, valor acordado (`valor`), URL publicada (`urlNova`).
2. **Configuración (`prospector-config.json`)**: datos del PRESTADOR/CONTRATISTA — nombre, empresa/LLC, dirección, EIN/Tax ID, estado de jurisdicción ("California").
3. **Usuario / Cliente**: EIN/SSN del cliente, dirección fiscal en California/USA, términos de pago (ej. 50% anticipo y 50% al entregar), plazo de entrega (ej. 5 días hábiles) y cuota de mantenimiento mensual (MRR, ej. $100-$300 USD/mes).

## 2. Soporte Bilingüe (Inglés / Español)

La skill detecta automáticamente el idioma preferido según el cliente o la indicación del usuario:
- **Inglés (Standard USA)**: usa `references/contract-template-en.html` y genera `sites/[slug]/contract-[slug].html` (y `.docx`).
- **Español (Mercado Hispano)**: usa `references/contrato-template-es.html` y genera `sites/[slug]/contrato-[slug].html` (y `.docx`).

## 3. Generación en HTML y PDF

1. Reemplazar los marcadores `{{PLACEHOLDERS}}` en el template seleccionado.
2. Guardar en `sites/[slug]/contract-[slug].html`.
3. Exportar a PDF: Abrir en el navegador $\to$ `Ctrl + P` $\to$ Guardar como PDF (formato Letter estándar de EE.UU.).

## 4. Generación en DOCX Protegido (Word)

Script listo para ejecutar: `references/gerar-docx.py` (requiere `python-docx`):
```bash
python references/gerar-docx.py dados.json sites/[slug]/contract-[slug].docx
```
*Genera el documento Word en modo solo lectura (`readOnly`), dejando campos editables destacados en amarillo para que el cliente complete su EIN/SSN, fecha y firma.*
*Nota legal: Para validez electrónica robusta en EE.UU., sugerir herramientas como DocuSign, PandaDoc o HelloSign.*

## 5. Correo de Acompañamiento (Borrador en Gmail)

- **Inglés**:
  - Asunto: `Services Agreement — Web Redesign for [Business Name]`
  - Cuerpo: Agradecer la confianza, resumir en 2 líneas el acuerdo (alcance + valor $ + plazo), solicitar revisión del documento adjunto y respuesta con conformidad o firma.
- **Español**:
  - Asunto: `Contrato de Servicios — Rediseño Web para [Nombre Negocio]`
  - Cuerpo: Mensaje profesional y cordial resumiendo el alcance, honorarios en USD y adjuntando la minuta.
