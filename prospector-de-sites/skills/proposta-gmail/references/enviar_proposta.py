#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generador y Gestor de Propuestas Comerciales por Gmail (Bilingüe EN/ES)
Permite crear borradores directos en la cuenta de Gmail de la agencia,
enviar propuestas o generar enlaces compose pre-cargados.

Uso:
  python enviar_proposta.py --slug "dr-smith-dentistry-los-angeles" --idioma en --modo borrador
  python enviar_proposta.py --slug "clinica-dental-san-diego" --idioma es --modo borrador
  python enviar_proposta.py --slug "dr-smith-dentistry-los-angeles" --followup
"""

import argparse
import datetime
import email.message
import imaplib
import json
import os
import re
import smtplib
import sqlite3
import sys
import time
import urllib.parse

PASTA = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(PASTA, 'prospector.db')
CONFIG_FILE = os.path.join(PASTA, 'prospector-config.json')

def ler_config():
    try:
        return json.load(open(CONFIG_FILE, encoding='utf-8'))
    except Exception:
        return {}

def obter_lead(slug):
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    row = c.execute('SELECT * FROM leads WHERE slug=?', (slug,)).fetchone()
    c.close()
    return dict(row) if row else None

def atualizar_status_proposta(slug):
    c = sqlite3.connect(DB)
    c.execute("UPDATE leads SET status='proposta', dataProposta=date('now','localtime'), atualizado=datetime('now','localtime') WHERE slug=?", (slug,))
    c.commit()
    c.close()
    try:
        from prospector_mcp import f_dashboard
        f_dashboard()
    except Exception:
        pass

def construir_propuesta(lead, cfg, idioma='auto', es_followup=False):
    firma = cfg.get('firma', {})
    mi_nombre = firma.get('nombre', 'Jose Gonzales')
    mi_empresa = firma.get('empresa', 'AI Sales Radar Studio')
    mi_tel = firma.get('telefono', '+1 (555) 019-2834')
    mi_email = firma.get('email', 'aisalesradar.agency@gmail.com')
    mi_web = f"https://{cfg.get('cloudflare', {}).get('customDomain', 'aisalesradar.com')}"

    subdomain = cfg.get('cloudflare', {}).get('subdomain', 'demos')
    domain = cfg.get('cloudflare', {}).get('customDomain', 'aisalesradar.com')
    slug = lead.get('slug', '')
    url_demo = lead.get('urlNova') or f"https://{subdomain}.{domain}/{slug}/proposta.html"

    nombre_negocio = lead.get('nome', 'Business')
    nicho = lead.get('nicho', 'services')
    ciudad = lead.get('cidade', 'California')
    nota = lead.get('nota', 4.8)

    # Detección de idioma
    if idioma == 'auto':
        texto_comb = (nombre_negocio + ' ' + nicho).lower()
        if any(h in texto_comb for h in ['dental', 'abogado', 'clinica', 'sonrisa', 'hispano', 'familia', 'taller']):
            idioma = 'es'
        else:
            idioma = 'en'

    if idioma == 'es':
        titulo_cargo = firma.get('presentacion_es', 'Especialista en Diseño Web y Conversión')
        if es_followup:
            asunto = f"Seguimiento sobre la propuesta web para {nombre_negocio}"
            cuerpo_html = f"""<p>Hola,</p>
<p>Solo quería asegurarme de que mi mensaje anterior no se haya perdido entre sus correos. ¿Tuvieron oportunidad de ver la versión móvil interactiva que diseñé para <b>{nombre_negocio}</b>?</p>
<p>Pueden verla y compararla directamente en su teléfono aquí:<br>
<a href="{url_demo}">{url_demo}</a></p>
<p>Sin ningún compromiso. ¡Que tengan una excelente semana!</p>
<p>Atentamente,<br>
<b>{mi_nombre}</b><br>
{titulo_cargo}<br>
{mi_empresa} · {mi_tel}</p>"""
        else:
            asunto = f"Una propuesta para la página móvil de {nombre_negocio}"
            cuerpo_html = f"""<p>Estimado equipo de {nombre_negocio},</p>
<p>Encontré su negocio mientras investigaba los mejores servicios de {nicho} en {ciudad}, California. Muchas felicidades por su calificación de {nota}★ en Google; se nota la confianza y preferencia de sus clientes.</p>
<p>Al analizar su sitio web desde el teléfono celular, noté que la navegación móvil presenta oportunidades clave de mejora y no cuenta con un botón directo para agendar citas o llamar al instante, lo que puede estar haciendo perder clientes potenciales que buscan desde sus smartphones.</p>
<p>Para mostrarles cómo luciría su presencia digital con una experiencia moderna y orientada a captar clientes, preparé una nueva versión interactiva que ya está en línea en este enlace de demostración:</p>
<p><a href="{url_demo}">{url_demo}</a></p>
<p>Pueden abrirla en su teléfono y comparar el antes y después. Me encantaría saber su opinión cuando tengan un minuto disponible.</p>
<p>Un cordial saludo,<br>
<b>{mi_nombre}</b><br>
{titulo_cargo}<br>
<b>{mi_empresa}</b><br>
{mi_tel} · <a href="{mi_web}">{mi_web}</a></p>"""
    else:
        titulo_cargo = firma.get('presentacion_en', 'High-Converting Web Designer & Conversion Specialist')
        if es_followup:
            asunto = f"Quick follow-up regarding the mobile concept for {nombre_negocio}"
            cuerpo_html = f"""<p>Hi there,</p>
<p>Just wanted to make sure my previous note didn't get buried. Were you able to check out the mobile redesign concept I put together for <b>{nombre_negocio}</b>?</p>
<p>You can preview it side-by-side on your phone here:<br>
<a href="{url_demo}">{url_demo}</a></p>
<p>No pressure at all — if you're completely happy with your current setup, I totally understand. Have a great week!</p>
<p>Best regards,<br>
<b>{mi_nombre}</b><br>
{titulo_cargo}<br>
{mi_empresa} · {mi_tel}</p>"""
        else:
            asunto = f"Quick question regarding {nombre_negocio}'s mobile website"
            cuerpo_html = f"""<p>Hi {nombre_negocio} team,</p>
<p>I came across your practice while researching top-rated {nicho} in {ciudad}, CA. Congratulations on your {nota}★ rating on Google — clients and patients clearly love your work.</p>
<p>While looking through your services on my phone, I noticed that your current website takes a moment to load and lacks a one-tap appointment booking button, which might be costing you calls and conversions from mobile visitors.</p>
<p>Since your business already has such high trust, I put together a clean, high-converting mobile redesign concept, completely live on this interactive demo link:</p>
<p><a href="{url_demo}">{url_demo}</a></p>
<p>It's fully responsive so you can compare it side-by-side with your current page directly on your phone. Would love to hear your thoughts!</p>
<p>Best regards,<br>
<b>{mi_nombre}</b><br>
{titulo_cargo}<br>
<b>{mi_empresa}</b><br>
{mi_tel} · <a href="{mi_web}">{mi_web}</a></p>"""

    return {
        'asunto': asunto,
        'cuerpo_html': cuerpo_html,
        'url_demo': url_demo,
        'idioma': idioma,
        'destinatario': lead.get('email', '')
    }

def crear_borrador_imap(cfg, destinatario, asunto, cuerpo_html):
    envio = cfg.get('envio', {})
    user = envio.get('gmail_user')
    pw = envio.get('gmail_app_password', '').replace(' ', '')
    if not user or not pw:
        return {'ok': False, 'erro': 'Faltan credenciales de Gmail en prospector-config.json'}

    msg = email.message.EmailMessage()
    msg['From'] = user
    msg['To'] = destinatario or 'client@example.com'
    msg['Subject'] = asunto
    msg.set_content(re.sub(r'<[^>]+>', '', cuerpo_html))
    msg.add_alternative(cuerpo_html, subtype='html')

    try:
        imap = imaplib.IMAP4_SSL('imap.gmail.com', 993)
        imap.login(user, pw)

        # Detectar carpeta de borradores de Gmail (inglés o español)
        folder = '[Gmail]/Drafts'
        typ, list_resp = imap.list()
        for f in list_resp:
            decoded = f.decode('utf-8', errors='ignore')
            if 'Drafts' in decoded:
                m = re.search(r'Drafts', decoded)
                folder = '[Gmail]/Drafts'
                break
            elif 'Borradores' in decoded:
                folder = '[Gmail]/Borradores'
                break

        imap.select(folder)
        imap.append(folder, '\\Draft', imaplib.Time2Internaldate(time.time()), msg.as_bytes())
        imap.logout()
        return {'ok': True, 'msg': f'Borrador creado exitosamente en tu Gmail ({folder})'}
    except Exception as e:
        return {'ok': False, 'erro': str(e)}

def enviar_correo_smtp(cfg, destinatario, asunto, cuerpo_html):
    envio = cfg.get('envio', {})
    user = envio.get('gmail_user')
    pw = envio.get('gmail_app_password', '').replace(' ', '')
    if not user or not pw:
        return {'ok': False, 'erro': 'Faltan credenciales de Gmail'}
    if not destinatario or '@' not in destinatario:
        return {'ok': False, 'erro': f'Dirección de correo inválida: {destinatario}'}

    msg = email.message.EmailMessage()
    msg['From'] = user
    msg['To'] = destinatario
    msg['Subject'] = asunto
    msg.set_content(re.sub(r'<[^>]+>', '', cuerpo_html))
    msg.add_alternative(cuerpo_html, subtype='html')

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587, timeout=12)
        server.starttls()
        server.login(user, pw)
        server.send_message(msg)
        server.quit()
        return {'ok': True, 'msg': f'Correo enviado con éxito a {destinatario}'}
    except Exception as e:
        return {'ok': False, 'erro': str(e)}

def generar_link_compose(destinatario, asunto, cuerpo_html):
    cuerpo_texto = re.sub(r'<[^>]+>', '', cuerpo_html)
    params = urllib.parse.urlencode({
        'view': 'cm',
        'fs': '1',
        'to': destinatario or '',
        'su': asunto,
        'body': cuerpo_texto
    })
    return f"https://mail.google.com/mail/?{params}"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Envío y Gestión de Propuestas por Gmail")
    parser.add_argument('--slug', required=True, help="Slug del lead (ej. dr-smith-los-angeles)")
    parser.add_argument('--idioma', default='auto', choices=['auto', 'en', 'es'], help="Idioma de la propuesta")
    parser.add_argument('--modo', default='borrador', choices=['borrador', 'enviar', 'link'], help="Modo: borrador en Gmail, enviar o enlace web")
    parser.add_argument('--followup', action='store_true', help="Generar correo de seguimiento (día 3-4)")

    args = parser.parse_args()

    lead = obter_lead(args.slug)
    if not lead:
        print(f"[!] Error: No se encontró ningún lead con slug '{args.slug}' en prospector.db")
        sys.exit(1)

    cfg = ler_config()
    prop = construir_propuesta(lead, cfg, idioma=args.idioma, es_followup=args.followup)

    print(f"\n============================================================")
    print(f"📧 PROPUESTA PARA: {lead['nome']} ({prop['idioma'].upper()})")
    print(f"📬 Destinatario: {prop['destinatario'] or '(Sin email registrado aún)'}")
    print(f"📌 Asunto: {prop['asunto']}")
    print(f"🔗 Enlace Demo: {prop['url_demo']}")
    print(f"============================================================\n")

    if args.modo == 'borrador':
        print("[*] Guardando borrador directamente en tu bandeja de Gmail...")
        res = crear_borrador_imap(cfg, prop['destinatario'], prop['asunto'], prop['cuerpo_html'])
        if res.get('ok'):
            print(f"[✓] {res['msg']}")
            atualizar_status_proposta(args.slug)
            print("[✓] Estado del lead actualizado a 'proposta' en el CRM.")
        else:
            print(f"[!] Error creando borrador: {res.get('erro')}")
            print("\nFallback: Enlace de redacción rápida en navegador:")
            print(generar_link_compose(prop['destinatario'], prop['asunto'], prop['cuerpo_html']))
    elif args.modo == 'enviar':
        print(f"[*] Enviando correo a {prop['destinatario']} desde {cfg.get('envio',{}).get('gmail_user')}...")
        res = enviar_correo_smtp(cfg, prop['destinatario'], prop['asunto'], prop['cuerpo_html'])
        if res.get('ok'):
            print(f"[✓] {res['msg']}")
            atualizar_status_proposta(args.slug)
        else:
            print(f"[!] Error al enviar: {res.get('erro')}")
    else:
        link = generar_link_compose(prop['destinatario'], prop['asunto'], prop['cuerpo_html'])
        print("[✓] Enlace directo de Gmail generado:")
        print(link)
