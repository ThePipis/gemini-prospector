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

## 🚀 Instalación Universal con Agentes de IA

Puedes delegar la instalación y configuración completa a tu agente de IA preferido (**Google Antigravity, Claude Code, Cursor, Windsurf o Codex**) enviándole en el chat:

> *"Instala y configura este plugin en mi proyecto actual: https://github.com/ThePipis/gemini-prospector"*

---

### Protocolo de Instalación para Agentes de IA

Si eres un **Agente de IA**, ejecuta de forma autónoma el siguiente protocolo estándar al recibir la solicitud:

1. **Dependencias del Entorno**:
   - Valida Python 3.8+ y Node.js/npx en el sistema.
   - Instala librerías en Python:
     ```powershell
     pip install "mcp[cli]" python-docx requests httpx
     ```
   - Verifica Wrangler para Cloudflare:
     ```powershell
     npx wrangler --version
     ```

2. **Registro del Plugin según tu Entorno**:
   - **Google Antigravity (Recomendado Local)**: Copia o enlaza la carpeta `prospector-de-sites/` dentro de `.agents/plugins/prospector-de-sites/` en la raíz del workspace (o en `~/.gemini/config/plugins/prospector-de-sites/` para uso global).
   - **Claude Code**: Conecta el servidor MCP ejecutando:
     ```bash
     claude mcp add prospector-crm python prospector-de-sites/prospector-mcp.py --pasta .
     ```
     o referencia `prospector-de-sites/mcp_config.json`.
   - **Cursor / Windsurf / Codex**: Añade el servidor MCP en Settings (`settings.json` o `.cursor/mcp.json`) apuntando a `python prospector-de-sites/prospector-mcp.py` con argumento `--pasta .`.

3. **Asistente Interactivo de Credenciales**:
   - **No inventes claves ni uses credenciales ficticias**. Solicita al usuario de forma clara y paso a paso sus datos para crear `prospector-de-sites/prospector-config.json` a partir de `prospector-de-sites/prospector-config.template.json`:
     - *Datos de Agencia*: Nombre, Agencia, Teléfono (+1 USA), Email de contacto comercial.
     - *Mercado Objetivo*: Nichos en California (ej. Dentistas, Med Spas, Abogados) y Ciudad principal.
     - *Conexión Cloudflare*: Account ID, Dominio (`ej. aisalesradar.com`), Subdominio (`demos`) y Token.
     - *Conexión Gmail*: Email oficial y Contraseña de Aplicación de 16 letras (App Password de Google).
     - *Opcional*: Yelp Fusion API Key (500 búsquedas gratuitas diarias sin tarjeta).
   - Verifica que `prospector-config.json` y `prospector.db` permanezcan protegidos en `.gitignore`.

4. **Batería de Pruebas Automatizada**:
   - Ejecuta: `python prospector-de-sites/prospector-mcp.py --teste`
   - Ejecuta: `python prospector-de-sites/prospectar.py --probar`
   - Valida la autenticación de Gmail para confirmar el envío de propuestas.
   - Informa al usuario que el sistema está 100% listo para operar.

---

## Flujo de Trabajo en Lenguaje Natural

Una vez instalado, opera el sistema escribiendo en el chat:

1. **"configurar el prospector"** $\to$ Valida o actualiza datos personales, nichos de California y conexión Cloudflare.
2. **"prospecta dentistas en Los Angeles"** (o en San Diego, San Jose, etc.) $\to$ Búsqueda segura de leads, calificación de web débil y extracción de contactos.
3. **"rediseña los 3 mejores en inglés"** (o en español) $\to$ Genera landing pages mobile-first de alta conversión y comparador interactivo.
4. **"publica en cloudflare"** $\to$ Despliega la carpeta `sites/` a Cloudflare y verifica URLs con HTTPS.
5. **"genera la propuesta para Dr. Smith"** $\to$ Crea el borrador en Gmail con el enlace de la demo.
6. **"genera el contrato para Dr. Smith"** $\to$ Crea el acuerdo legal en HTML (para PDF) y DOCX protegido listo para firmar.
7. **Doble clic en `iniciar-dashboard.bat`** $\to$ Abre el panel de control Kanban en `http://localhost:8765` para monitorear el pipeline y la facturación en USD.

---

## 📖 Manual de Operaciones y Estrategia Comercial

Para ver la guía completa de prospección en frío, plantillas anti-spam (CAN-SPAM), contratos adaptados a las leyes de California, gestión de subdominios y uso del CRM Kanban:
👉 Consulta el archivo **[Doc/MANUAL_DE_USO.md](Doc/MANUAL_DE_USO.md)**.


