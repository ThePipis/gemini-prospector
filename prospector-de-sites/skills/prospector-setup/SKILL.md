---
name: prospector-setup
description: Configuración inicial del Prospector de Sitios en Antigravity — recolecta firma comercial, nichos, ciudad (California/USA), idioma preferido (EN/ES) y credenciales de Cloudflare, e instala el panel local. Usar cuando el usuario diga "configurar prospector", "setup", "comenzar", "mis datos", o la primera vez que se use el prospector sin un prospector-config.json.
---

# Prospector — Configuración Inicial (Antigravity)

Ejecutar UNA vez. Guarda toda la configuración en `prospector-config.json` en la raíz del proyecto.

## 1. Verificar Configuración Existente

Buscar `prospector-config.json` en la carpeta del proyecto. Si existe, mostrar un resumen (sin tokens sensibles) y preguntar qué desea actualizar. Si no existe, recolectar los datos siguientes.

## 2. Datos del Usuario / Prestador de Servicios (Preguntar en bloques breves)

- **Firma de la propuesta**:
  - Nombre completo / Nombre de agencia.
  - Presentación profesional (ej.: *"High-Converting Web Designer & Conversion Specialist"* / *"Especialista en Diseño Web y Conversión"*).
  - Teléfono / WhatsApp en formato internacional USA: `+1 (XXX) XXX-XXXX` (o `1XXXXXXXXXX` para enlaces `wa.me`).
  - Correo electrónico de contacto profesional.
- **Mercado y Nichos de California / USA**:
  - Sugerir nichos de alta facturación y recurrencia:
    - *Dentists / Dental Clinics* (Dentistas / Clínicas Dentales)
    - *Personal Injury & Immigration Attorneys* (Abogados de Lesiones e Inmigración)
    - *Plastic Surgeons & Med Spas* (Cirujanos Plásticos y Clínicas Estéticas)
    - *CPAs & Tax Consultants* (Contadores y Consultores Fiscales)
    - *HVAC, Roofing & General Contractors* (Contratistas de Climatización, Techos y Construcción)
    - *Chiropractors & Physical Therapy* (Quiroprácticos y Fisioterapia)
  - Ciudad / Región en California (ej.: Los Angeles, San Diego, San Jose, San Francisco, Sacramento, Irvine, Fresno).
- **Idioma predeterminado de contacto**:
  - `en` (English) para negocios mainstream estadounidenses.
  - `es` (Español) para negocios hispanos/latinos en California.
  - `auto` (detectar según el idioma del sitio web actual del cliente).
- **Leads por búsqueda**: estándar 10.
- **Modo de envío de propuesta**: "borrador en Gmail para revisión previa".

## 3. Conexión Cloudflare (Despliegue y CDN)

Se conecta a la cuenta de Cloudflare para publicar las páginas y comparadores instantáneamente con HTTPS global:
- `accountId`: `TU_CLOUDFLARE_ACCOUNT_ID` (el ID de tu cuenta de Cloudflare).
- `apiToken`: Token de API con permisos de Workers / Pages (o leer de `CLOUDFLARE_API_TOKEN`).
- `projectName`: `prospector-sites`.
- `customDomain`: `tudominio.com` (o el dominio propio que se desee).
- `subdomain`: `demos` (para URLs del tipo `https://demos.tudominio.com/[slug]/`).

## 4. Archivo de Configuración Resultante (`prospector-config.json`)

```json
{
  "firma": {
    "nombre": "Tu Nombre",
    "empresa": "Tu Agencia Studio",
    "presentacion_en": "High-Converting Web Designer & Conversion Specialist",
    "presentacion_es": "Especialista en Diseño Web y Conversión para Negocios",
    "telefono": "+1 (000) 000-0000",
    "whatsapp": "10000000000",
    "email": "tu-agencia@gmail.com"
  },
  "prospeccion": {
    "estado": "CA",
    "ciudad": "Los Angeles",
    "nichos": ["dentists", "med spas", "personal injury attorneys", "hvac contractors", "cpas"],
    "idioma_default": "auto",
    "leadsPorBusca": 10
  },
  "envio": {
    "modo": "borrador_gmail",
    "gmail_user": "tu-agencia@gmail.com",
    "gmail_app_password": ""
  },
  "cloudflare": {
    "accountId": "",
    "apiToken": "",
    "projectName": "prospector-sites",
    "customDomain": "tudominio.com",
    "subdomain": "demos"
  },
  "contrato": {
    "prestador_nombre": "Jose Gonzales",
    "prestador_empresa": "AI Sales Radar LLC",
    "prestador_ein": "",
    "prestador_direccion": "California, USA",
    "estado_jurisdiccion": "California"
  }
}
```

## 5. Panel Local (Dashboard)

El panel interactivo se administra con:
- `dashboard-server.py` + `iniciar-dashboard.bat` (Windows).
- Al hacer doble clic en `iniciar-dashboard.bat`, se abre `http://localhost:8765` conectado a `prospector.db`.

## 6. Ciclo de Trabajo en Lenguaje Natural

1. **Prospectar:** *"prospecta dentistas en Los Angeles"* o *"find personal injury attorneys in San Diego"* (skill `prospeccao-maps`).
2. **Rediseñar:** *"rediseña los 3 mejores en inglés"* o *"rediseña para clientes hispanos en español"* (skill `redesign-premium`).
3. **Publicar:** *"publica en cloudflare"* (skill `deploy-cloudflare`).
4. **Propuesta:** *"genera los borradores de propuesta"* (skill `proposta-gmail`).
5. **Cierre:** *"genera el contrato para Dr. Smith"* (skill `contrato-servico`).
