# Gemini Prospector — Edición Cloudflare & Mercado USA (California Bilingüe)

Plugin profesional para **Google Antigravity** (compatible con Agy 2.0 / CLI / IDE): Prospección B2B semiautomática de clientes con sitio web deficiente, rediseño premium de alta conversión bilingüe (Inglés / Español), despliegue atómico en **Cloudflare** (Workers con Static Assets / CDN global), propuestas comerciales anti-spam por Gmail y CRM local con acuerdos legales adaptados a **California, USA**.

---

## Estructura del Proyecto

```
d:/GenWebSite/
├── prospector-config.json     ← Configuración central (Cloudflare, firma, nichos USA)
├── wrangler.jsonc             ← Configuración de despliegue atómico en Cloudflare
├── iniciar-dashboard.bat      ← Lanzador del panel local (http://localhost:8765)
├── dashboard-server.py        ← Servidor HTTP local (SQLite)
├── dashboard.html             ← Frontend reactivo del CRM Kanban
├── sites/                     ← Landing pages generadas por cliente
│   └── [slug]/
│       ├── [slug].html        (página de alta conversión)
│       ├── [slug]-editor.html (editor visual en vivo)
│       ├── proposta.html      (portada interactiva bilingüe antes/después)
│       └── contract-[slug].html (contrato para California)
└── prospector-de-sites/       ← Plugin para Antigravity
    ├── plugin.json            (manifiesto del plugin)
    ├── mcp_config.json        (servidores MCP: CRM + Playwright)
    ├── prospector-mcp.py      (servidor FastMCP de base de datos)
    ├── dashboard/             (fuentes del dashboard)
    └── skills/                (las 7 skills en lenguaje natural)
        ├── prospector-setup/  (asistente de configuración)
        ├── prospeccao-maps/   (búsqueda en Google Maps / Places en California)
        ├── redesign-premium/  (motor de rediseño bilingüe EN/ES)
        ├── deploy-cloudflare/ (despliegue en Cloudflare Workers con Assets)
        ├── proposta-gmail/    (propuestas anti-spam en inglés y español)
        ├── dashboard-leads/   (gestión de CRM y métricas MRR)
        └── contrato-servico/  (acuerdos legales para el Estado de California)
```

---

## Puntos Clave de la Migración a Cloudflare

1. **Despliegue Atómico y de Cero Fricción**: Reemplazo total de cPanel/FTP por **Cloudflare Workers con Static Assets** y **Wrangler CLI**.
2. **HTTPS y CDN Global Instantáneo**: Cada página se publica en milisegundos con certificado SSL universal activo y caché global en el borde de Cloudflare.
3. **URLs Limpias**:
   - Vía worker: `https://[projectName].[subdomain].workers.dev/[slug]/proposta.html`
   - Vía dominio personalizado: `https://demos.aisalesradar.com/[slug]/proposta.html`
4. **Purga de Caché Integrada**: Mediante el MCP de Cloudflare preconfigurado.

---

## Adaptación al Mercado de California / USA (Bilingüe EN / ES)

* **Enfoque Bilingüe**:
  * **Inglés**: Dirigido al mercado general estadounidense (dentistas, cirujanos cosméticos, abogados de lesiones, contratistas de climatización).
  * **Español**: Dirigido a negocios locales hispanos/latinos de alto volumen en California.
* **Formato Telefónico**: Estándar estadounidense `+1 (XXX) XXX-XXXX` y enlaces `wa.me/1...` / `tel:+1...`.
* **Cumplimiento Anti-Spam (CAN-SPAM Act)**: Correos hiperpersonalizados de 100 a 160 palabras, 1 solo enlace directo a la demo interactiva, sin palabras gatillo comerciales.
* **Contratos Adaptados a California**: *Independent Contractor Agreement* bajo las leyes del Estado de California, con desglose de honorarios de proyecto ($ USD) y cuota de mantenimiento mensual (MRR).

---

## Requisitos de Instalación

1. **Python 3.8+** en el PATH del sistema.
2. **Node.js (v20+) y Wrangler**:
   ```powershell
   npm install -g wrangler
   pip install "mcp[cli]" python-docx
   ```
3. **Credenciales de Cloudflare**:
   - Variables de entorno o pre-configuradas en `prospector-config.json`:
     - `CLOUDFLARE_API_TOKEN`
     - `CLOUDFLARE_ACCOUNT_ID` (`TU_ACCOUNT_ID_AQUI`)

---

## Flujo de Trabajo en Lenguaje Natural

1. **"configurar el prospector"** $\to$ Valida o actualiza datos personales, nichos de California y conexión Cloudflare.
2. **"prospecta dentistas en Los Angeles"** (o en San Diego, San Jose, etc.) $\to$ Búsqueda en Google Maps Places, calificación de web débil y extracción de correos/teléfonos.
3. **"rediseña los 3 mejores en inglés"** (o en español) $\to$ Genera las landing pages de alta conversión, el editor visual y el comparador antes/después.
4. **"publica en cloudflare"** $\to$ Despliega la carpeta `sites/` a Cloudflare y verifica las URLs activas con HTTPS.
5. **"genera la propuesta para Dr. Smith"** $\to$ Crea el borrador en Gmail con el enlace de la demo.
6. **"genera el contrato para Dr. Smith"** $\to$ Crea el acuerdo legal en HTML (para PDF) y DOCX protegido listo para firmar.
7. **Doble clic en `iniciar-dashboard.bat`** $\to$ Abre el panel de control Kanban en `http://localhost:8765` para monitorear el pipeline y la facturación en USD.
