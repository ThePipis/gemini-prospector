# Gemini Prospector — Edición Cloudflare & Mercado USA (California Bilingüe)

Plugin profesional para **Google Antigravity** (compatible con Agy 2.0 / CLI / IDE): Prospección B2B semiautomática de clientes con sitio web deficiente, rediseño premium de alta conversión bilingüe (Inglés / Español), despliegue atómico en **Cloudflare** (Workers con Static Assets / CDN global), propuestas comerciales anti-spam por Gmail y CRM local con acuerdos legales adaptados a **California, USA**.

---

## Estructura del Plugin (`prospector-de-sites/`)

```text
prospector-de-sites/
├── dashboard/
│   ├── dashboard-server.py                 # Mini-servidor local en Python (puerto 8765)
│   ├── dashboard-template.html             # Plantilla bilingüe del CRM Kanban [ES | EN]
│   ├── iniciar-dashboard.bat               # Lanzador para Windows
│   └── iniciar-dashboard.command           # Lanzador para macOS / Linux
├── mcp_config.json                         # Configuración de servidores MCP (CRM + Playwright)
├── plugin.json                             # Manifiesto del plugin para Google Antigravity
├── prospectar.py                           # Motor multi-proveedor de prospección segura (Yelp, Apify, Web)
├── prospector-config.template.json         # Plantilla base de configuración
├── prospector-mcp.py                       # Servidor FastMCP de base de datos SQLite
└── skills/
    ├── contrato-servico/
    │   ├── references/
    │   │   ├── contract-template-en.html   # Plantilla de contrato en inglés (California)
    │   │   ├── contrato-template-es.html   # Plantilla de contrato en español
    │   │   ├── contrato-template.html      # Plantilla base
    │   │   └── gerar-docx.py               # Generador de contratos Word (.docx)
    │   └── SKILL.md
    ├── dashboard-leads/
    │   ├── references/
    │   │   ├── dashboard-server.py
    │   │   ├── dashboard-template.html
    │   │   ├── iniciar-dashboard.bat
    │   │   └── iniciar-dashboard.command
    │   └── SKILL.md
    ├── deploy-cloudflare/
    │   ├── references/
    │   │   ├── publicar-cloudflare.bat     # Lanzador de publicación para Windows
    │   │   ├── publicar-cloudflare.ps1     # Script de despliegue a Cloudflare Workers
    │   │   └── wrangler.template.jsonc     # Plantilla de configuración Wrangler
    │   └── SKILL.md
    ├── proposta-gmail/
    │   ├── references/
    │   │   ├── capa-proposta-template.html # Plantilla visual de presentación de propuesta
    │   │   └── enviar_proposta.py          # Script de automatización de borradores Gmail
    │   └── SKILL.md
    ├── prospeccao-maps/
    │   └── SKILL.md
    ├── prospector-setup/
    │   └── SKILL.md
    └── redesign-premium/
        ├── references/
        │   ├── comparador-template.html    # Comparador interactivo antes / después
        │   └── editor-visual.md            # Guía de edición y personalización visual
        └── SKILL.md
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

---

## 📖 Manual de Operaciones y Setup Automatizado con IA

Para ver el manual completo de uso, instructivo de prospección manual y el **Prompt Maestro** para que cualquier agente de IA instale y configure este repositorio automáticamente:
👉 Consulta el archivo **[Doc/MANUAL_DE_USO.md](Doc/MANUAL_DE_USO.md)**.

