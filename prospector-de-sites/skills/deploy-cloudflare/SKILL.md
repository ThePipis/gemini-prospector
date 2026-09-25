---
name: deploy-cloudflare
description: Esta skill debe ser usada al publicar páginas y demos en Cloudflare (Workers con Static Assets o Cloudflare Pages) — subida atómica instantánea, URLs globales con HTTPS nativo y CDN de borde. Acione cuando el usuario diga "publicar", "subir el sitio", "poner en la web", "deploy", "cloudflare", "subir a cloudflare" o pida publicar (skill deploy-cloudflare).
---

# Deploy en Cloudflare (Workers con Static Assets / Pages)

Publicar páginas estáticas autocontenidas en Cloudflare bajo la carpeta `sites/[slug]/` y garantizar la URL pública con HTTPS nativo de alta velocidad:
- En worker directo: `https://[projectName].[subdomain].workers.dev/[slug]/`
- O en dominio personalizado: `https://demos.[dominio]/[slug]/` (o `https://[dominio]/clientes/[slug]/`)

## Credenciales y Configuración

Todo se lee desde `prospector-config.json` (bloque `cloudflare`):
```json
{
  "cloudflare": {
    "accountId": "TU_ACCOUNT_ID_CLOUDFLARE",
    "apiToken": "TU_API_TOKEN_CLOUDFLARE",
    "projectName": "prospector-sites",
    "customDomain": "tudominio.com",
    "subdomain": "demos"
  }
}
```
*Si `apiToken` está en blanco en el config, se toma de la variable de entorno `CLOUDFLARE_API_TOKEN` ya configurada en el sistema.*

## Método 1 — Publicación Automatizada con Wrangler (Recomendado)

El entorno local cuenta con **Wrangler** instalado globalmente. La publicación sube atómicamente la carpeta `./sites/` al CDN global de Cloudflare.

1. **Asegurar los archivos locales del cliente en `sites/[slug]/`**:
   - `index.html` (o `[slug].html`): la landing page rediseñada.
   - `proposta.html`: la portada interactiva antes/después para el cliente.
2. **Ejecutar el despliegue**:
   - En Windows (PowerShell/CMD):
     ```powershell
     powershell -NoProfile -ExecutionPolicy Bypass -File "prospector-de-sites/skills/deploy-cloudflare/references/publicar-cloudflare.ps1"
     ```
   - O vía Wrangler directo:
     ```powershell
     wrangler deploy
     ```
3. **URL Resultante**:
   - Portada de la propuesta: `https://[projectName].[subdomain].workers.dev/[slug]/proposta.html`
   - Landing page directa: `https://[projectName].[subdomain].workers.dev/[slug]/`
   *(Si se usa el dominio personalizado `aisalesradar.com`, la URL será `https://demos.aisalesradar.com/[slug]/proposta.html`).*

## Método 2 — Purga de Caché (Cloudflare MCP)

Si se actualiza una página ya desplegada para un cliente, se puede purgar la caché de la zona usando la herramienta MCP de Cloudflare:
- Herramienta: `call_mcp_tool` -> `purge_zone_cache` con `zone_id` (para `aisalesradar.com` es `9bc5fff3862d3cfd503f3f3921bca0af`).

## Verificación (Obligatoria tras el despliegue)

1. Abrir la URL de la portada `.../[slug]/proposta.html` y confirmar que renderiza perfectamente en desktop y móvil.
2. Comprobar que cuenta con candado SSL válido (**HTTPS nativo garantizado por Cloudflare**).
3. Actualizar `prospector.db` y `leads.md` con:
   - `status = 'publicado'`
   - `urlNova = 'https://...'`
   *(El CRM y el Dashboard reflejarán inmediatamente el cambio).*
