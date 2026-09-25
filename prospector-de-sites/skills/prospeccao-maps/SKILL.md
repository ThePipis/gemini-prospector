---
name: prospeccao-maps
description: Esta skill debe ser usada al prospectar clientes en California/USA — buscar negocios locales con alta calificación pero sitios web débiles mediante Yelp Fusion API, Apify o Playwright/Scraping (cero riesgo de cobros imprevistos de Google Cloud), calificar leads, auditar sitios y alimentar el CRM. Acione cuando el usuario diga "prospectar", "buscar clientes", "encontrar leads", "find leads", "leads California" o pida prospectar (skill prospeccao-maps).
---

# Prospección de Clientes (Mercado USA / California — Zero Billing Risk)

Objetivo: Encontrar el "cliente de oro" — negocios locales solventes que ya facturan alto (calificación alta $\ge 4.5$, 30+ reseñas positivas) pero pierden clientes debido a un sitio web desactualizado, no optimizado para móviles o sin llamadas a la acción.

**Protección Financiera Activa**: Este sistema **NO requiere Google Maps API Key ni vinculación forzada de tarjetas de crédito**. Utiliza un motor multi-fuente blindado contra cobros sorpresa:
1. **Yelp Fusion API** (Recomendado para California): 500 llamadas/día GRATIS (15,000/mes). Límite duro: si se alcanza, se detiene con código 429 sin cobrar jamás un centavo.
2. **Apify Google Maps Scraper**: $5 USD/mes de saldo gratuito prepagado (~1,500 leads). Saldo cerrado sin sobregiros.
3. **Playwright / Open Web Scraper**: Extracción directa de código abierto, $0.00 de por vida, sin cuentas ni API keys.

---

## Nichos de Alto Rendimiento en California

* **Salud y Estética**: *Dentists / Cosmetic Dentistry, Plastic Surgeons, Med Spas, Dermatologists, Chiropractors*.
* **Servicios Legales y Financieros**: *Personal Injury Attorneys, Immigration Lawyers, CPAs & Tax Advisors*.
* **Servicios del Hogar de Alto Ticket**: *HVAC Contractors, Roofing Contractors, Solar Installers, Remodeling Contractors*.

---

## Flujo Operativo de Prospección

1. **Búsqueda Multi-Fuente (`prospectar.py`)**:
   * Ejecutable por CLI o Claude: `python prospectar.py --nicho "dentists" --ciudad "Los Angeles" --limite 10`
   * Devuelve: `name`, `rating`, `user_ratings_total`, `website`, `formatted_phone_number`, `address`.
   * **Filtro 1 — Solvencia / Reputación**: `rating` $\ge 4.5$ y `user_ratings_total` $\ge 30$.
   * **Filtro 2 — Web Propia**: Debe tener URL de sitio propio (descartar si es solo Facebook, Instagram o directorios).

2. **Auditoría Web y Extracción de Contacto**:
   * Abrir el `website` y evaluar los criterios de web débil:
     - Diseño anticuado (aspecto de hace 10+ años, maquetación rígida).
     - Sin llamada a la acción (CTA) visible para agendar o llamar en la primera pantalla móvil.
     - Sitio en plataforma gratuita (Google Sites, Wix básico con banner, subdominios).
     - Roto o no responsivo en pantalla móvil de 375px.
     - Contenido disperso, sin jerarquía ni testimonios destacados.

3. **Detección de Idioma del Negocio**:
   * Identificar si la web o el perfil atienden principalmente en **Inglés** o **Español** (o bilingüe) para enviar la propuesta en el idioma correspondiente.

4. **Extracción de Teléfono y Correo Electrónico**:
   * **Teléfono USA**: Formato estándar `+1 (XXX) XXX-XXXX` (click-to-call nativo).
   * **Canales de Mensajería**: En EE.UU., priorizar **Llamada telefónica a recepción** y **SMS / Business Texting** (iMessage/SMS bidireccional de clínicas). WhatsApp es secundario y rara vez utilizado en líneas fijas de negocios en USA.
   * **Correo Electrónico (Mandatorio — Protocolo de Enriquecimiento OSINT Autónomo)**:
     - *Nivel 1 (Web Oficial)*: Escaneo de home y página `/contact` (con reintento por HTTP e ignorado de certificados si HTTPS falla por SSL).
     - *Nivel 2 (OSINT Autónomo Obligatorio)*: **CERO LEADS INCOMPLETOS**. Si el sitio web está caído, bloqueado por antivirus/ISP o no expone el email, el agente o script DEBE ejecutar de forma autónoma una búsqueda OSINT profunda (`"[Nombre]" "[Ciudad]" email OR contact OR receptionist`) para localizar el correo directo de la clínica o de la red médica. Ningún prospecto calificado debe quedar como 'sin email' si existe información pública en internet.

5. **Límite**: Detener al alcanzar la meta de leads calificados (padrón 10).

---

## Registro de Datos (CRM Local y leads.md)

1. **Upsert en Base de Datos (`prospector.db`)** vía servidor MCP o `prospectar.py`.
2. **Archivo de seguimiento `leads.md`**:
```markdown
| # | Nombre | Nota | Reseñas | Idioma | E-mail | Teléfono | Web Actual | Motivo de Calificación | Status | URL Cloudflare |
```
Estados: `novo` $\to$ `redesenhado` $\to$ `publicado` $\to$ `proposta` $\to$ `respondeu` $\to$ `fechado`.

Al finalizar la prospección, informar la tabla de resultados y sugerir avanzar a: *"¿Deseas que rediseñemos los 3 mejores prospectos?"* (skill `redesign-premium`).
