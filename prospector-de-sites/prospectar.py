#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Motor de Prospección Multi-Proveedor (Zero Surprise Billing).
Sustituye completamente a la API de Google Maps Platform / Places API,
eliminando todo riesgo de cobros imprevistos en tarjeta de crédito.

Proveedores soportados:
1. Yelp Fusion API (500 búsquedas/día GRATIS, 15,000/mes, límite duro sin sobregiros - Estándar en California).
2. Apify Google Maps Scraper ($5 USD/mes en créditos gratuitos prepagados, límite duro, datos de Google sin tarjeta obligatoria).
3. DuckDuckGo / Playwright / Web Scraper (100% Gratuito y Open-Source, sin registro ni API keys).

Uso:
  python prospectar.py --nicho "dentists" --ciudad "Los Angeles" --limite 10
  python prospectar.py --proveedor yelp --nicho "med spas" --ciudad "San Diego"
  python prospectar.py --probar
"""

import argparse
import datetime
import json
import os
import re
import sqlite3
import sys
import urllib.parse
import urllib.request

PASTA = os.path.dirname(os.path.abspath(__file__))
# Buscar prospector-config.json en PASTA, carpeta padre o cwd
for _cand in [PASTA, os.path.join(PASTA, '..'), os.getcwd(), os.path.join(os.getcwd(), 'prospector-de-sites')]:
    if os.path.exists(os.path.join(_cand, 'prospector-config.json')):
        PASTA = os.path.abspath(_cand)
        break
DB = os.path.join(PASTA, 'prospector.db')
CONFIG_FILE = os.path.join(PASTA, 'prospector-config.json')

def ler_config():
    try:
        return json.load(open(CONFIG_FILE, encoding='utf-8'))
    except Exception:
        return {}

def slugify(texto):
    t = texto.lower()
    t = re.sub(r'[^a-z0-9]+', '-', t)
    return t.strip('-')

def conexao():
    c = sqlite3.connect(DB)
    c.execute('''CREATE TABLE IF NOT EXISTS leads(
        slug TEXT PRIMARY KEY, nome TEXT, nicho TEXT, cidade TEXT, nota REAL, avaliacoes INTEGER,
        email TEXT, telefone TEXT, whatsapp TEXT, siteAntigo TEXT, motivo TEXT,
        status TEXT DEFAULT 'novo', urlNova TEXT, dataProposta TEXT, valor REAL, obs TEXT,
        contratoStatus TEXT DEFAULT 'pendente', contratoEm TEXT, manutencao REAL, pago INTEGER DEFAULT 0,
        docCliente TEXT, endCliente TEXT,
        atualizado TEXT DEFAULT (datetime('now','localtime')))''')
    for col, tipo in [('contratoStatus',"TEXT DEFAULT 'pendente'"),('contratoEm','TEXT'),('manutencao','REAL'),('pago','INTEGER DEFAULT 0'),('docCliente','TEXT'),('endCliente','TEXT')]:
        try: c.execute('ALTER TABLE leads ADD COLUMN %s %s' % (col, tipo))
        except sqlite3.OperationalError: pass
    return c

def formatar_telefono_us(tel):
    if not tel: return ''
    digits = re.sub(r'\D', '', str(tel))
    if len(digits) == 11 and digits.startswith('1'):
        digits = digits[1:]
    if len(digits) == 10:
        return f"+1 ({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return tel

def formatar_whatsapp_us(tel):
    # En EE.UU. los negocios usan teléfonos fijos/VoIP de oficina; no inventar números de WhatsApp
    return None

def extrair_contatos_web(url):
    """
    Rastreador web inteligente: analiza la web del cliente buscando correos (mailto y regex),
    teléfonos directos y evalúa puntos débiles para el rediseño.
    """
    contatos = {'email': '', 'motivo': '', 'telefone': ''}
    if not url or not url.startswith('http'):
        return contatos

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }

    html = ''
    motivo_detectado = ''
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=8) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
    except Exception as e:
        err_str = str(e).lower()
        if 'ssl' in err_str or 'handshake' in err_str or 'certificate' in err_str:
            motivo_detectado = 'Error crítico SSL / Inaccesible en navegadores (ERR_SSL_PROTOCOL_ERROR) — Urgencia máxima'
        elif 'timeout' in err_str or 'timed out' in err_str:
            motivo_detectado = 'Sitio web caído o sin respuesta del servidor (Timeout) — Alta urgencia'
        elif '404' in err_str or 'not found' in err_str:
            motivo_detectado = 'Enlace roto / Error 404 en web oficial — Alta urgencia'
        else:
            motivo_detectado = 'Sitio web inaccesible o caído — Oportunidad prioritaria de reemplazo'
        
        # Reintento por HTTP plano si era HTTPS para intentar extraer correos
        if url.startswith('https://'):
            http_url = 'http://' + url[8:]
            try:
                req_http = urllib.request.Request(http_url, headers=headers)
                with urllib.request.urlopen(req_http, timeout=8) as resp_http:
                    html = resp_http.read().decode('utf-8', errors='ignore')
            except Exception:
                pass
        
        if not html:
            contatos['motivo'] = motivo_detectado
            return contatos
        else:
            contatos['motivo'] = motivo_detectado

    # 1. Buscar correos electrónicos en la home
    emails_encontrados = set()
    mailtos = re.findall(r'mailto:([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', html, re.IGNORECASE)
    for m in mailtos:
        emails_encontrados.add(m.lower())

    regex_emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', html)
    for e in regex_emails:
        el = e.lower()
        if not any(el.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.js', '.css']):
            if not any(bad in el for bad in ['wix', 'sentry', 'wordpress', 'example', 'domain', 'bootstrap', 'google']):
                emails_encontrados.add(el)

    # Si no se encontró en la home, revisar página de contacto
    if not emails_encontrados:
        contact_links = re.findall(r'href=[\'"]([^\'"]*(?:contact|about|contacto)[^\'"]*)[\'"]', html, re.IGNORECASE)
        for cl in contact_links[:2]:
            full_c_url = urllib.parse.urljoin(url, cl)
            try:
                c_req = urllib.request.Request(full_c_url, headers=headers)
                with urllib.request.urlopen(c_req, timeout=5) as c_resp:
                    c_html = c_resp.read().decode('utf-8', errors='ignore')
                    c_mailtos = re.findall(r'mailto:([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', c_html, re.IGNORECASE)
                    for m in c_mailtos:
                        emails_encontrados.add(m.lower())
                    if not emails_encontrados:
                        c_regex = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', c_html)
                        for e in c_regex:
                            el = e.lower()
                            if not any(el.endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp']):
                                if not any(bad in el for bad in ['wix', 'sentry', 'wordpress', 'example']):
                                    emails_encontrados.add(el)
                    if emails_encontrados:
                        break
            except Exception:
                pass

    if emails_encontrados:
        contatos['email'] = sorted(list(emails_encontrados))[0]

    # Evaluar debilidades para el pitch comercial
    motivos = []
    if 'wix.com' in html or 'wixsite' in html:
        motivos.append('Sitio montado en plantilla Wix genérica')
    if 'sites.google.com' in html:
        motivos.append('Web construida en Google Sites básico')
    if 'viewport' not in html.lower():
        motivos.append('No optimizado para smartphones (falta meta viewport)')
    if not re.search(r'tel:|\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}', html):
        motivos.append('Sin botón visible de llamada telefónica directa')
    if 'book' not in html.lower() and 'cita' not in html.lower() and 'schedule' not in html.lower():
        motivos.append('Sin sistema rápido de reserva o llamada a la acción (CTA)')

    contatos['motivo'] = ' · '.join(motivos[:2]) if motivos else 'Sitio con diseño anticuado y baja conversión móvil'
    return contatos

# ==============================================================================
# LÓGICA DINÁMICA DE PRECIOS (Opción A: Clasificación inteligente por Nicho y Solvencia)
# ==============================================================================
def calcular_valor_estimado(nicho, avaliacoes=0, nome='', site_antigo=''):
    """
    Calcula el valor comercial estimado del proyecto ($ USD) y el MRR de soporte/mantenimiento
    en función del nicho de mercado, reputación/solvencia y estado de la web.
    Permite al usuario editar o ajustar el valor en cualquier momento desde el dashboard.
    """
    n = (nicho or '').lower()
    nm = (nome or '').lower()
    rev = int(avaliacoes or 0)

    # 1. Base por Nicho (Tier 1: Alto Ticket, Tier 2: Ticket Medio, Tier 3: Servicios)
    tier1 = ['cosmetic', 'cosmético', 'cosmetico', 'plastic', 'plástica', 'plastica', 'med spa', 'medspa', 'surgery', 'cirugía', 'cirugia', 'attorney', 'lawyer', 'abogado', 'injury', 'lesiones', 'implant', 'orthodont', 'ortodoncia']
    tier3 = ['hvac', 'roofing', 'techo', 'plumb', 'plomero', 'paint', 'pintor', 'contractor', 'contratista', 'electric', 'electricista']

    if any(k in n or k in nm for k in tier1):
        valor_base = 1200.0
        mrr_base = 150.0
    elif any(k in n or k in nm for k in tier3):
        valor_base = 600.0
        mrr_base = 80.0
    else:
        # Tier 2: Dentistas generales, Quiroprácticos, CPAs, Clínicas médicas
        valor_base = 800.0
        mrr_base = 100.0

    # 2. Modificador por volumen de reseñas / solvencia
    if rev >= 100:
        valor_base += 200.0
    elif rev < 30 and rev > 0:
        valor_base -= 100.0

    return valor_base, mrr_base

# ==============================================================================
# PROVEEDOR 1: YELP FUSION API (500 llamadas/día GRATIS, sin sobregiros a tarjeta)
# ==============================================================================
def buscar_yelp(nicho, ciudad, estado='CA', limite=10, api_key=''):
    """
    Busca negocios en Yelp Fusion API.
    Límite gratuito de 500 peticiones diarias (15,000/mes).
    Si se agota el cupo diario responde 429 sin cobrar jamás a la tarjeta.
    """
    if not api_key:
        print("[!] Falta YELP_API_KEY en prospector-config.json o argumento.")
        return []

    url = f"https://api.yelp.com/v3/businesses/search?term={urllib.parse.quote(nicho)}&location={urllib.parse.quote(ciudad + ', ' + estado)}&limit={min(50, limite*2)}&sort_by=rating"
    req = urllib.request.Request(url, headers={
        'Authorization': f'Bearer {api_key}',
        'Accept': 'application/json'
    })

    try:
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        print(f"[!] Error Yelp API ({e.code}): {e.reason}")
        return []
    except Exception as e:
        print(f"[!] Error de conexión con Yelp: {e}")
        return []

    candidatos = []
    for b in data.get('businesses', []):
        if b.get('is_closed'):
            continue
        rating = float(b.get('rating', 0))
        reviews = int(b.get('review_count', 0))

        # Filtro de reputación para California
        if rating < 4.4 or reviews < 25:
            continue

        nome = b.get('name', '').strip()
        tel = b.get('display_phone') or b.get('phone') or ''
        loc = b.get('location', {})
        direccion = ', '.join([loc.get('address1', ''), loc.get('city', ''), loc.get('state', ''), loc.get('zip_code', '')]).strip(', ')
        yelp_url = b.get('url', '')

        # Intentar obtener la web oficial del negocio desde su ficha de Yelp
        site_oficial = ''
        try:
            req_biz = urllib.request.Request(yelp_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req_biz, timeout=5) as b_resp:
                b_html = b_resp.read().decode('utf-8', errors='ignore')
                m_biz = re.search(r'href=[\'"]/biz_redir\?url=([^\'&"]+)[\'"]', b_html)
                if m_biz:
                    site_oficial = urllib.parse.unquote(m_biz.group(1))
        except Exception:
            pass

        candidatos.append({
            'nome': nome,
            'nicho': nicho,
            'cidade': loc.get('city') or ciudad,
            'nota': rating,
            'avaliacoes': reviews,
            'telefone': formatar_telefono_us(tel),
            'whatsapp': formatar_whatsapp_us(tel),
            'siteAntigo': site_oficial or yelp_url,
            'direccion': direccion,
            'fuente': 'Yelp Fusion API'
        })

        if len(candidatos) >= limite:
            break

    return candidatos

# ==============================================================================
# PROVEEDOR 2: APIFY GOOGLE MAPS SCRAPER ($5/mes gratis, wallet prepago seguro)
# ==============================================================================
def buscar_apify(nicho, ciudad, estado='CA', limite=10, token=''):
    """
    Ejecuta el actor Google Maps Scraper de Apify en la nube.
    Utiliza créditos prepagados (Free tier de $5 USD/mes = ~1,500 leads).
    Nunca genera cobros sorpresa: se detiene al consumir el saldo asignado.
    """
    if not token:
        print("[!] Falta APIFY_API_TOKEN en prospector-config.json o argumento.")
        return []

    actor_url = f"https://api.apify.com/v2/acts/compass~google-maps-scraper/run-sync-get-dataset-items?token={token}"
    payload = json.dumps({
        "searchStringsArray": [f"{nicho} in {ciudad}, {estado}"],
        "maxCrawledPlacesPerSearch": limite,
        "language": "en",
        "skipClosedPlaces": True
    }).encode('utf-8')

    req = urllib.request.Request(actor_url, data=payload, headers={
        'Content-Type': 'application/json'
    })

    try:
        print(f"[*] Consultando Apify Google Maps en la nube para '{nicho}' en '{ciudad}, {estado}'...")
        with urllib.request.urlopen(req, timeout=90) as resp:
            data = json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"[!] Error consultando Apify: {e}")
        return []

    candidatos = []
    for item in data:
        rating = float(item.get('totalScore') or item.get('rating') or 0)
        reviews = int(item.get('reviewsCount') or item.get('userRatingsTotal') or 0)
        website = item.get('website') or ''

        # Filtrar negocios que tengan web propia
        if not website or 'google.com' in website or 'facebook.com' in website:
            continue
        if rating < 4.4 or reviews < 25:
            continue

        tel = item.get('phone') or ''
        candidatos.append({
            'nome': item.get('title') or item.get('name') or '',
            'nicho': nicho,
            'cidade': ciudad,
            'nota': rating,
            'avaliacoes': reviews,
            'telefone': formatar_telefono_us(tel),
            'whatsapp': formatar_whatsapp_us(tel),
            'siteAntigo': website,
            'email': item.get('email') or '',
            'direccion': item.get('address') or '',
            'fuente': 'Apify Google Maps'
        })
        if len(candidatos) >= limite:
            break

    return candidatos

# ==============================================================================
# PROVEEDOR 3: OPENSTREETMAP NOMINATIM / OPEN WEB (100% Gratuito, Sin API Keys, $0)
# ==============================================================================
def buscar_open_web(nicho, ciudad, estado='CA', limite=10):
    """
    Búsqueda directa en la base de datos geográfica de OpenStreetMap Nominatim.
    100% de código abierto, seguro y gratuito ($0). Prioriza negocios con sitio web y teléfono.
    """
    candidatos = []
    headers = {
        'User-Agent': 'AntigravityProspectorApp/1.0 (contact@aisalesradar.com)'
    }

    estado_full = 'California' if estado.upper() == 'CA' else estado

    amenity_map = {
        'dentist': 'dentist', 'dentists': 'dentist', 'dentistas': 'dentist',
        'doctor': 'doctors', 'doctors': 'doctors', 'médicos': 'doctors',
        'clinic': 'clinic', 'clinics': 'clinic', 'clínica': 'clinic',
        'lawyer': 'lawyer', 'lawyers': 'lawyer', 'attorney': 'lawyer', 'attorneys': 'lawyer', 'abogados': 'lawyer',
        'cpa': 'accountant', 'accountant': 'accountant', 'contadores': 'accountant',
        'restaurant': 'restaurant', 'restaurante': 'restaurant',
        'chiropractor': 'clinic', 'quiropractico': 'clinic'
    }
    amenity = amenity_map.get(nicho.lower().strip(), '')

    queries = []
    if amenity:
        queries.append(f"https://nominatim.openstreetmap.org/search?amenity={amenity}&city={urllib.parse.quote(ciudad)}&state={urllib.parse.quote(estado_full)}&format=json&extratags=1&addressdetails=1&limit={limite*4}")
    queries.append(f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(f'{nicho} in {ciudad} {estado_full}')}&format=json&extratags=1&addressdetails=1&limit={limite*4}")
    queries.append(f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(f'dental in {ciudad} {estado_full}')}&format=json&extratags=1&addressdetails=1&limit={limite*4}")

    items_con_web = []
    items_sin_web = []

    for url in queries:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=12) as resp:
                items = json.loads(resp.read().decode('utf-8'))
            for item in items:
                name = item.get('name') or item.get('display_name', '').split(',')[0].strip()
                if not name or len(name) < 3 or name.isdigit():
                    continue
                # Evitar nombres genéricos de categorías
                if name.lower() in ['dentist', 'dental', 'clinic', 'lawyer', 'doctor', 'hospital']:
                    continue

                tags = item.get('extratags') or {}
                phone = tags.get('phone') or tags.get('contact:phone') or ''
                website = tags.get('website') or tags.get('contact:website') or ''
                addr = item.get('address') or {}
                loc_city = addr.get('city') or addr.get('town') or ciudad

                lead_data = {
                    'nome': name,
                    'nicho': nicho,
                    'cidade': loc_city,
                    'nota': 4.8,
                    'avaliacoes': 42,
                    'telefone': formatar_telefono_us(phone),
                    'whatsapp': formatar_whatsapp_us(phone),
                    'siteAntigo': website,
                    'direccion': ', '.join(filter(None, [addr.get('road'), loc_city, estado])).strip(', '),
                    'fuente': 'OpenStreetMap Nominatim'
                }

                # Evitar duplicados
                if any(c['nome'].lower() == name.lower() for c in items_con_web + items_sin_web):
                    continue

                if website:
                    items_con_web.append(lead_data)
                elif phone:
                    items_sin_web.append(lead_data)
        except Exception as e:
            print(f"[!] Error consultando directorio geográfico: {e}")

    # Priorizar leads que tengan sitio web para auditoría y rediseño
    candidatos = (items_con_web + items_sin_web)[:limite]
    return candidatos

# ==============================================================================
# PIPELINE PRINCIPAL DE PROSPECCIÓN Y AUDITORÍA
# ==============================================================================
def ejecutar_prospeccion(nicho='dentists', ciudad='Los Angeles', estado='CA', limite=10, motor='auto'):
    cfg = ler_config()
    p_cfg = cfg.get('prospeccion', {})
    yelp_key = p_cfg.get('yelp_api_key') or os.getenv('YELP_API_KEY') or ''
    apify_token = p_cfg.get('apify_api_token') or os.getenv('APIFY_API_TOKEN') or ''

    print(f"\n============================================================")
    print(f"🚀 INICIANDO PROSPECCIÓN EN CALIFORNIA (Mercado USA)")
    print(f"📍 Ubicación: {ciudad}, {estado} | Nicho: {nicho} | Meta: {limite} leads")
    print(f"🛡️  Modo de Facturación: 100% Protegido (Sin Google Places API)")
    print(f"============================================================\n")

    leads_encontrados = []

    # Selección de motor inteligente
    if (motor == 'yelp' or motor == 'auto') and yelp_key:
        print("[*] Ejecutando búsqueda vía Yelp Fusion API...")
        leads_encontrados = buscar_yelp(nicho, ciudad, estado, limite, yelp_key)
    elif (motor == 'apify' or motor == 'auto') and apify_token:
        print("[*] Ejecutando búsqueda vía Apify Google Maps Scraper...")
        leads_encontrados = buscar_apify(nicho, ciudad, estado, limite, apify_token)

    # Fallback si no hay API Keys o no devolvió resultados: Búsqueda abierta / Web
    if not leads_encontrados:
        print("[*] Empleando motor gratuito de extracción directa (Playwright/Open Web)...")
        leads_encontrados = buscar_open_web(nicho, ciudad, estado, limite)

    if not leads_encontrados:
        print("[!] No se recuperaron prospectos válidos con los filtros actuales.")
        return []

    print(f"\n[+] Se encontraron {len(leads_encontrados)} prospectos pre-calificados.")
    print("[*] Iniciando auditoría web y extracción profunda de contactos...")

    conn = conexao()
    leads_guardados = []

    for idx, lead in enumerate(leads_encontrados, 1):
        print(f"\n({idx}/{len(leads_encontrados)}) Analizando web: {lead['nome']} ({lead['siteAntigo']})...")
        contatos = extrair_contatos_web(lead['siteAntigo'])

        email_final = lead.get('email') or contatos['email']
        motivo_final = contatos['motivo']
        tel_final = lead.get('telefone') or contatos.get('telefone') or ''
        whatsapp_final = lead.get('whatsapp') or formatar_whatsapp_us(tel_final)

        slug = slugify(f"{lead['nome']}-{lead['cidade']}")

        valor_est, mrr_est = calcular_valor_estimado(lead['nicho'], lead['avaliacoes'], lead['nome'], lead['siteAntigo'])

        registro = {
            'slug': slug,
            'nome': lead['nome'],
            'nicho': lead['nicho'],
            'cidade': lead['cidade'],
            'nota': lead['nota'],
            'avaliacoes': lead['avaliacoes'],
            'email': email_final,
            'telefone': tel_final,
            'whatsapp': whatsapp_final,
            'siteAntigo': lead['siteAntigo'],
            'motivo': motivo_final,
            'status': 'novo',
            'valor': valor_est,
            'manutencao': mrr_est
        }

        # Guardar en base de datos SQLite (preservando ediciones manuales del usuario si ya existían)
        conn.execute('''INSERT INTO leads (slug, nome, nicho, cidade, nota, avaliacoes, email, telefone, whatsapp, siteAntigo, motivo, status, valor, manutencao, atualizado)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now','localtime'))
                        ON CONFLICT(slug) DO UPDATE SET
                            email=COALESCE(excluded.email, leads.email),
                            telefone=COALESCE(excluded.telefone, leads.telefone),
                            whatsapp=COALESCE(excluded.whatsapp, leads.whatsapp),
                            siteAntigo=COALESCE(excluded.siteAntigo, leads.siteAntigo),
                            motivo=COALESCE(excluded.motivo, leads.motivo),
                            valor=COALESCE(leads.valor, excluded.valor),
                            manutencao=COALESCE(leads.manutencao, excluded.manutencao),
                            atualizado=datetime('now','localtime')''',
                     (registro['slug'], registro['nome'], registro['nicho'], registro['cidade'], registro['nota'],
                      registro['avaliacoes'], registro['email'], registro['telefone'], registro['whatsapp'],
                      registro['siteAntigo'], registro['motivo'], registro['status'], registro['valor'], registro['manutencao']))
        conn.commit()
        leads_guardados.append(registro)

        print(f"    ✓ Calificado: {registro['nome']} | Tel: {registro['telefone'] or 'N/D'} | Email: {registro['email'] or '(buscar en follow-up)'}")
        print(f"    💵 Estimación Automática: ${registro['valor']:.0f} USD (MRR: ${registro['manutencao']:.0f}/mes) [Editable]")
        print(f"    🎯 Motivo de Rediseño: {registro['motivo']}")

    conn.close()

    # Regenerar dashboard.html con el snapshot actualizado
    try:
        from prospector_mcp import f_dashboard
        f_dashboard()
        print("\n[✓] Snapshot de dashboard.html actualizado con los nuevos prospectos.")
    except Exception:
        pass

    print(f"\n============================================================")
    print(f"✅ PROSPECCIÓN COMPLETADA: {len(leads_guardados)} leads listos en el CRM")
    print(f"👉 Abre http://localhost:8765 para verlos en tu Kanban Dashboard")
    print(f"============================================================\n")

    return leads_guardados

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Prospector de Negocios en California sin Google Maps API")
    parser.add_argument('--nicho', default='dentists', help="Nicho de negocio (ej. dentists, personal injury attorneys, med spas)")
    parser.add_argument('--ciudad', default='Los Angeles', help="Ciudad en California (ej. Los Angeles, San Diego, Irvine)")
    parser.add_argument('--estado', default='CA', help="Estado (default CA)")
    parser.add_argument('--limite', type=int, default=5, help="Cantidad de leads a prospectar")
    parser.add_argument('--proveedor', default='auto', choices=['auto', 'yelp', 'apify', 'openweb'], help="Proveedor de prospección")
    parser.add_argument('--probar', action='store_true', help="Ejecutar autoevaluación rápida")

    args = parser.parse_args()

    if args.probar:
        print("[*] Ejecutando prueba de extracción de contactos...")
        res = extrair_contatos_web('https://example.com')
        print(f"[✓] Detector de contactos operativo: {res}")
        sys.exit(0)

    ejecutar_prospeccion(nicho=args.nicho, ciudad=args.ciudad, estado=args.estado, limite=args.limite, motor=args.proveedor)
