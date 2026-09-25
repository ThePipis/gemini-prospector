---
name: proposta-gmail
description: Esta skill debe ser usada al redactar y enviar propuestas comerciales por correo electrónico a un lead prospectado — e-mail de presentación del rediseño, con rapport auténtico, 100% bilingüe (Inglés para mercado estadounidense o Español para negocios hispanos en California/USA), sin precio y anti-spam. Acione cuando el usuario diga "enviar propuesta", "correo para el cliente", "mandar propuesta", "send proposal", "draft email" o pida enviar la propuesta (skill proposta-gmail).
---

# Propuesta por Correo (Mercado USA / California — Bilingüe EN/ES)

El correo electrónico **NO busca vender de golpe**: despierta curiosidad y demuestra trabajo ya realizado. El cierre comercial (precio, alcance, llamada) ocurre tras la respuesta positiva del cliente.
Un correo que parece de venta fría genérica va a spam; un correo que demuestra que te tomaste el tiempo de analizar su negocio y crear una versión mejorada en vivo, se abre y se responde.

## Principios Psicológicos de Alta Conversión

1. **Rapport y Elogio Específico:** Abrir destacando su reputación real (su calificación en Google, una reseña destacada o su trayectoria en California). Cero elogios genéricos.
2. **El Problema Sin Ofensa:** Señalar 1 o 2 puntos objetivos de fricción en su web actual (ej. lentitud en móvil, falta de botón directo de cita o teléfono tapado), siempre como una oportunidad de captar más clientes.
3. **La Prueba Tangible:** El trabajo YA está hecho y en línea en Cloudflare con HTTPS seguro.
4. **Cero Precios de Entrada:** El precio se discute en la respuesta cuando ya validaron el valor.
5. **Cero Presión:** Sin urgencia artificial ("últimos cupos"). Un único llamado a la acción (CTA): revisar la demo en su celular y compartir su opinión.
6. **Brevedad:** 100 a 160 palabras. Los dueños de negocios en California están ocupados.

---

## Plantillas Bilingües (EN / ES)

### Opción A: Negocios en Inglés (US Standard — Dentists, MedSpas, Lawyers, CPAs, Contractors)

**Asunto (Subject Line)**:
* `Dr. [Name], quick question regarding your website`
* `Created a mobile concept for [Business Name]`
* `Noticeable observation regarding [Business Name]'s mobile page`

**Cuerpo del Correo (Body)**:
```html
<p>Hi Dr. [Name] (or [First Name]),</p>

<p>I came across [Business Name] while researching top-rated [niche] in [City/Area, CA]. Congratulations on your [Rating]★ rating on Google — patients clearly love your work.</p>

<p>While looking through your services, I noticed that on smartphones, your current website takes a moment to load and lacks a one-tap booking/call button, which might be costing you calls from mobile visitors.</p>

<p>Since your clinic already has such high patient trust, I put together a clean, modern mobile redesign for your practice, completely live on a demo link:</p>

<p><a href="[URL_CLOUDFLARE_PROPOSTA]">[URL_CLOUDFLARE_PROPOSTA]</a></p>

<p>It's fully interactive so you can compare it side-by-side with your current page on your phone. Would love to hear your thoughts!</p>

<p>Best regards,<br>
<b>[YOUR_NAME]</b><br>
[YOUR_TITLE_EN]<br>
[YOUR_PHONE] · [YOUR_WEBSITE]</p>
```

**Follow-Up en Inglés (Día 3-4 si no hay respuesta)**:
```html
<p>Hi [First Name],</p>

<p>Just wanted to make sure my previous note didn't get buried. Were you able to check out the mobile redesign demo for [Business Name]?</p>

<p><a href="[URL_CLOUDFLARE_PROPOSTA]">[URL_CLOUDFLARE_PROPOSTA]</a></p>

<p>No pressure at all — if you're happy with your current setup, completely understand. Have a great week!</p>

<p>Best,<br>
<b>[YOUR_NAME]</b></p>
```

---

### Opción B: Negocios Hispanos en California (Español Profesional y Cálido)

**Asunto**:
* `Dr./Dra. [Nombre], preparé algo para el sitio web de [Negocio]`
* `Una propuesta para la página móvil de [Negocio]`
* `Pregunta rápida sobre la web de [Negocio] en [Ciudad]`

**Cuerpo del Correo**:
```html
<p>Estimado/a Dr./Dra. [Apellido] (o [Nombre]),</p>

<p>Encontré el perfil de [Nombre Negocio] buscando los mejores servicios de [nicho] en [Ciudad, California]. Muchas felicidades por su calificación de [Nota]★ en Google; se nota el excelente trato y la confianza de sus clientes.</p>

<p>Al revisar su sitio web desde el teléfono, noté que la navegación móvil se dificulta un poco y no cuenta con un botón directo para agendar cita o llamar al instante, lo que puede estar haciendo perder pacientes/clientes que buscan desde el celular.</p>

<p>Para mostrarles cómo luciría su presencia digital al nivel de su reputación, preparé una nueva versión interactiva que ya está activa en este enlace de demostración:</p>

<p><a href="[URL_CLOUDFLARE_PROPOSTA]">[URL_CLOUDFLARE_PROPOSTA]</a></p>

<p>Pueden verla directamente en su teléfono y comparar el antes y después. Me encantaría saber su opinión cuando tengan un minuto.</p>

<p>Un cordial saludo,<br>
<b>[TU_NOMBRE]</b><br>
[TU_TITULO_ES]<br>
[TU_TELEFONO] · [TU_WEB]</p>
```

**Follow-Up en Español (Día 3-4)**:
```html
<p>Hola [Nombre],</p>

<p>Solo quería asegurarme de que mi mensaje anterior no se haya perdido entre sus correos. ¿Pudo ver la propuesta de rediseño para [Nombre Negocio]?</p>

<p><a href="[URL_CLOUDFLARE_PROPOSTA]">[URL_CLOUDFLARE_PROPOSTA]</a></p>

<p>Sin ningún compromiso. ¡Que tenga una excelente semana!</p>

<p>Saludos cordiales,<br>
<b>[TU_NOMBRE]</b></p>
```

---

## Lista de Verificación Anti-Spam y CAN-SPAM (Bloqueante)

Revisar el correo antes de enviar o crear el borrador:
- [ ] **Un solo enlace**: Dirigido a la portada comparadora (`https://demos.aisalesradar.com/[slug]/proposta.html` o Cloudflare Worker).
- [ ] **Sin acortadores**: Jamás usar bit.ly ni redirects sospechosos.
- [ ] **Enlace limpio en HTML**: Texto visible idéntico al href para evitar falsos positivos de phishing.
- [ ] **Sin palabras prohibidas**: Cero "gratis", "promoción", "descuento", "oferta única", "urgente", "garantizado 100%".
- [ ] **Sin mayúsculas en el asunto** y sin signos de exclamación múltiples (`!!`).
- [ ] **Remitente legítimo**: Cuenta personal activa de Gmail (cuenta con SPF y DKIM validados por Google).
- [ ] **Frecuencia humana**: Envíos espaciados 1 a 1 (no blast masivo).

## Modos de Creación

1. **Modo Borrador en Gmail (Recomendado)**: Se genera como borrador en la cuenta de Gmail del usuario para que pueda darle una última revisión humana antes de pulsar Enviar.
2. **Enlace Directo de Compose**: Fallback con `https://mail.google.com/mail/?view=cm&fs=1&to=...&su=...&body=...` con todo precargado.
