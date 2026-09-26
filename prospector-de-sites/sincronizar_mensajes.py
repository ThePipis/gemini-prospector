#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sincronizador Omnicanal de Comunicaciones y Trazabilidad — Prospector
Monitorea de forma unificada:
1. Bandeja de Borradores de Gmail ([Gmail]/Borradores): detecta propuestas generadas pendientes de revisión humana y envío.
2. Bandeja de Enviados de Gmail ([Gmail]/Enviados): detecta cuándo el usuario realmente envió el correo al cliente.
3. Bandeja de Entrada de Gmail (INBOX):
   - Respuestas directas por email del cliente.
   - Confirmaciones de citas agendadas por Google Calendar / Google Meet.
4. Twilio SMS (si está configurado):
   - Mensajes SMS entrantes de clientes en respuesta al contacto.
Actualiza prospector.db reflejando el estado real del lead (borrador, enviado, respondió).
"""

import os, sys, json, imaplib, email, re, sqlite3, urllib.request, urllib.parse, base64
from datetime import datetime

PASTA = os.path.dirname(os.path.abspath(__file__))
if not os.path.exists(os.path.join(PASTA, 'prospector-config.json')) and os.path.exists(os.path.join(PASTA, '..', 'prospector-config.json')):
    PASTA = os.path.abspath(os.path.join(PASTA, '..'))

CONFIG_FILE = os.path.join(PASTA, 'prospector-config.json')
DB_FILE = os.path.join(PASTA, 'prospector.db')

def ler_config():
    try: return json.load(open(CONFIG_FILE, encoding='utf-8'))
    except Exception: return {}

def conexao():
    c = sqlite3.connect(DB_FILE)
    c.row_factory = sqlite3.Row
    return c

def normalizar_tel(tel):
    if not tel: return ''
    return re.sub(r'\D', '', str(tel))

def parsear_fecha_correo(fecha_str):
    try:
        from email.utils import parsedate_to_datetime
        dt = parsedate_to_datetime(fecha_str)
        return dt.strftime('%Y-%m-%d')
    except Exception:
        return datetime.now().strftime('%Y-%m-%d')

def decodificar_asunto(sub):
    if not sub: return ''
    from email.header import decode_header
    partes = decode_header(sub)
    texto = ''
    for p, enc in partes:
        if isinstance(p, bytes):
            texto += p.decode(enc or 'utf-8', errors='ignore')
        else:
            texto += str(p)
    return texto.strip().replace('\n', ' ').replace('\r', '')

def sincronizar_todo():
    cfg = ler_config()
    envio = cfg.get('envio', {})
    user = envio.get('gmail_user')
    pw = envio.get('gmail_app_password', '').replace(' ', '')

    if not user or not pw:
        return {'ok': False, 'erro': 'Faltan credenciales de Gmail en prospector-config.json'}

    conn = conexao()
    leads = [dict(r) for r in conn.execute('SELECT * FROM leads').fetchall()]

    email_map = {}
    tel_map = {}
    for l in leads:
        if l.get('email'):
            email_map[l['email'].strip().lower()] = l
        if l.get('telefone'):
            d = normalizar_tel(l['telefone'])
            if d:
                tel_map[d] = l
                if len(d) == 10:
                    tel_map['1' + d] = l
                elif len(d) == 11 and d.startswith('1'):
                    tel_map[d[1:]] = l

    resumen = {
        'borradores': 0,
        'enviados': 0,
        'respuestas_email': 0,
        'citas_calendar': 0,
        'sms_recibidos': 0
    }
    actualizados = []

    try:
        imap = imaplib.IMAP4_SSL('imap.gmail.com', 993)
        imap.login(user, pw)

        # Descubrimiento dinámico de carpetas de Gmail (RFC 6154)
        drafts_folder = '[Gmail]/Borradores'
        sent_folder = '[Gmail]/Enviados'
        typ, list_resp = imap.list()
        if typ == 'OK':
            for f in list_resp:
                decoded = f.decode('utf-8', errors='ignore')
                parts = decoded.split(' "/" ')
                if len(parts) > 1:
                    fname = parts[1].strip().strip('"')
                    if '\\Drafts' in decoded:
                        drafts_folder = fname
                    elif '\\Sent' in decoded:
                        sent_folder = fname

        # =========================================================================
        # 1. ESCANEAR BANDEJA DE ENVIADOS (Detectar correos que ya salieron)
        # =========================================================================
        emails_enviados_detectados = {}
        try:
            status, _ = imap.select(f'"{sent_folder}"', readonly=True)
            if status == 'OK':
                typ, data = imap.search(None, 'ALL')
                if typ == 'OK' and data[0]:
                    msg_nums = data[0].split()
                    for num in msg_nums[-80:]: # últimos 80 enviados
                        try:
                            t_f, m_d = imap.fetch(num, '(BODY.PEEK[HEADER.FIELDS (TO CC DATE SUBJECT)])')
                            if t_f != 'OK': continue
                            msg = email.message_from_bytes(m_d[0][1])
                            dest = (msg.get('To', '') + ' ' + msg.get('Cc', '')).lower()
                            dest_emails = set(re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', dest))
                            f_envio = parsear_fecha_correo(msg.get('Date', ''))
                            asunto = decodificar_asunto(msg.get('Subject', ''))

                            for em in dest_emails:
                                if em in email_map and em != user.lower():
                                    emails_enviados_detectados[em] = {
                                        'fecha': f_envio,
                                        'asunto': asunto
                                    }
                        except Exception:
                            pass
        except Exception as e:
            print(f"[!] Error leyendo enviados: {e}")

        # =========================================================================
        # 2. ESCANEAR BANDEJA DE BORRADORES (Detectar borradores listos sin enviar)
        # =========================================================================
        borradores_detectados = {}
        try:
            status, _ = imap.select(f'"{drafts_folder}"', readonly=True)
            if status == 'OK':
                typ, data = imap.search(None, 'ALL')
                if typ == 'OK' and data[0]:
                    msg_nums = data[0].split()
                    for num in msg_nums[-60:]:
                        try:
                            t_f, m_d = imap.fetch(num, '(BODY.PEEK[HEADER.FIELDS (TO SUBJECT DATE)])')
                            if t_f != 'OK': continue
                            msg = email.message_from_bytes(m_d[0][1])
                            dest = (msg.get('To', '')).lower()
                            dest_emails = set(re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', dest))
                            asunto = decodificar_asunto(msg.get('Subject', ''))

                            for em in dest_emails:
                                if em in email_map and em != user.lower():
                                    borradores_detectados[em] = {
                                        'asunto': asunto
                                    }
                        except Exception:
                            pass
        except Exception as e:
            print(f"[!] Error leyendo borradores: {e}")

        # =========================================================================
        # 3. ESCANEAR BANDEJA DE ENTRADA (Respuestas de clientes & Google Calendar)
        # =========================================================================
        respuestas_email_detectadas = {}
        citas_calendar_detectadas = {}
        try:
            status, _ = imap.select('INBOX', readonly=True)
            if status == 'OK':
                # a) Respuestas directas de clientes
                typ, data = imap.search(None, 'ALL')
                if typ == 'OK' and data[0]:
                    msg_nums = data[0].split()
                    for num in msg_nums[-120:]: # últimos 120 correos recibidos
                        try:
                            t_f, m_d = imap.fetch(num, '(RFC822)')
                            if t_f != 'OK': continue
                            msg = email.message_from_bytes(m_d[0][1])
                            de = (msg.get('From', '')).lower()
                            asunto = decodificar_asunto(msg.get('Subject', ''))
                            fecha_recibido = parsear_fecha_correo(msg.get('Date', ''))

                            # Verificar si es de un lead
                            de_emails = set(re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', de))
                            for em in de_emails:
                                if em in email_map and em != user.lower():
                                    respuestas_email_detectadas[em] = {
                                        'fecha': fecha_recibido,
                                        'asunto': asunto
                                    }

                            # b) Notificaciones de Google Calendar
                            es_calendar = any(k in de for k in ['calendar-notification@google.com', 'google.com', 'calendar']) or \
                                          any(k in asunto.lower() for k in ['counseling', 'walkthrough', 'cita', 'booking', 'meet', 'reserva', 'invitation'])
                            if es_calendar:
                                cuerpo = ""
                                if msg.is_multipart():
                                    for part in msg.walk():
                                        if part.get_content_type() in ['text/plain', 'text/html']:
                                            payload = part.get_payload(decode=True)
                                            if payload: cuerpo += payload.decode('utf-8', errors='ignore') + " "
                                else:
                                    payload = msg.get_payload(decode=True)
                                    if payload: cuerpo = payload.decode('utf-8', errors='ignore')

                                todos_textos = f"{de} {msg.get('To','')} {asunto} {cuerpo}".lower()
                                for em in email_map:
                                    if em in todos_textos and em != user.lower():
                                        citas_calendar_detectadas[em] = {
                                            'fecha': fecha_recibido,
                                            'asunto': asunto
                                        }
                        except Exception:
                            pass
        except Exception as e:
            print(f"[!] Error leyendo INBOX: {e}")

        imap.logout()

        # =========================================================================
        # 4. ESCANEAR TWILIO SMS (Si está configurado)
        # =========================================================================
        sms_recibidos_detectados = {}
        twilio_cfg = cfg.get('twilio', {})
        tw_sid = twilio_cfg.get('accountSid', '').strip()
        tw_token = twilio_cfg.get('authToken', '').strip()
        tw_from = twilio_cfg.get('fromNumber', '').strip()

        if tw_sid and tw_token:
            try:
                url = f"https://api.twilio.com/2010-04-01/Accounts/{tw_sid}/Messages.json?PageSize=50"
                req = urllib.request.Request(url)
                auth_str = base64.b64encode(f"{tw_sid}:{tw_token}".encode('utf-8')).decode('ascii')
                req.add_header("Authorization", f"Basic {auth_str}")
                with urllib.request.urlopen(req, timeout=10) as resp:
                    if resp.status == 200:
                        datos_tw = json.loads(resp.read().decode('utf-8'))
                        mensajes = datos_tw.get('messages', [])
                        for m in mensajes:
                            if m.get('direction') == 'inbound':
                                rem = normalizar_tel(m.get('from', ''))
                                if rem in tel_map:
                                    lead_tw = tel_map[rem]
                                    sms_recibidos_detectados[lead_tw['slug']] = {
                                        'fecha': (m.get('date_sent') or m.get('date_created') or '')[:10],
                                        'body': m.get('body', '')[:100]
                                    }
            except Exception as e:
                print(f"[!] Error consultando Twilio: {e}")

        # =========================================================================
        # 5. APLICAR ACTUALIZACIONES EN LA BASE DE DATOS
        # =========================================================================
        for l in leads:
            slug = l['slug']
            em = (l.get('email') or '').strip().lower()
            tel = normalizar_tel(l.get('telefone') or '')
            st_actual = l.get('status') or 'novo'
            obs_actual = l.get('obs') or ''
            email_st_actual = l.get('emailStatus') or 'sin_borrador'
            modificado = False
            notas_nuevas = []

            # Prioridad 1: Cita agendada en Google Calendar / Meet
            if em in citas_calendar_detectadas:
                cita = citas_calendar_detectadas[em]
                resumen['citas_calendar'] += 1
                nota = f"[📅 CITA AGENDADA EN GOOGLE MEET] Reserva confirmada vía Google Calendar ({cita['fecha']})"
                if nota not in obs_actual: notas_nuevas.append(nota)
                conn.execute(
                    "UPDATE leads SET status='respondeu', emailStatus='respondeu', canalRespuesta='calendar', obs=?, atualizado=datetime('now','localtime') WHERE slug=?",
                    ((obs_actual + '\n' + '\n'.join(notas_nuevas)).strip(), slug)
                )
                modificado = True
                actualizados.append({'slug': slug, 'nome': l['nome'], 'accion': 'Cita en Google Meet', 'status': 'respondeu'})

            # Prioridad 2: Respuesta directa por email
            elif em in respuestas_email_detectadas:
                resp = respuestas_email_detectadas[em]
                resumen['respuestas_email'] += 1
                nota = f"[✉️ RESPUESTA POR EMAIL] El cliente respondió al correo ({resp['fecha']}). Asunto: {resp['asunto']}"
                if nota not in obs_actual: notas_nuevas.append(nota)
                conn.execute(
                    "UPDATE leads SET status='respondeu', emailStatus='respondeu', canalRespuesta='email', obs=?, atualizado=datetime('now','localtime') WHERE slug=?",
                    ((obs_actual + '\n' + '\n'.join(notas_nuevas)).strip(), slug)
                )
                modificado = True
                actualizados.append({'slug': slug, 'nome': l['nome'], 'accion': 'Respuesta por Email', 'status': 'respondeu'})

            # Prioridad 3: Respuesta por SMS (Twilio)
            elif slug in sms_recibidos_detectados:
                sms_item = sms_recibidos_detectados[slug]
                resumen['sms_recibidos'] += 1
                nota = f"[💬 RESPUESTA POR SMS] Mensaje recibido vía Twilio ({sms_item['fecha']}): \"{sms_item['body']}\""
                if nota not in obs_actual: notas_nuevas.append(nota)
                conn.execute(
                    "UPDATE leads SET status='respondeu', emailStatus='respondeu', canalRespuesta='sms', obs=?, atualizado=datetime('now','localtime') WHERE slug=?",
                    ((obs_actual + '\n' + '\n'.join(notas_nuevas)).strip(), slug)
                )
                modificado = True
                actualizados.append({'slug': slug, 'nome': l['nome'], 'accion': 'Respuesta por SMS', 'status': 'respondeu'})

            # Prioridad 4: Correo efectivamente enviado al cliente (en [Gmail]/Enviados)
            elif em in emails_enviados_detectados:
                env_item = emails_enviados_detectados[em]
                resumen['enviados'] += 1
                nota = f"[✉️ CORREO ENVIADO] Enviado al cliente el {env_item['fecha']}"
                if nota not in obs_actual: notas_nuevas.append(nota)
                nuevo_st = 'proposta' if st_actual in ['novo', 'redesenhado', 'publicado'] else st_actual
                conn.execute(
                    "UPDATE leads SET emailStatus='enviado', emailEnviadoEm=?, dataProposta=COALESCE(dataProposta, ?), status=?, obs=?, atualizado=datetime('now','localtime') WHERE slug=?",
                    (env_item['fecha'], env_item['fecha'], nuevo_st, (obs_actual + '\n' + '\n'.join(notas_nuevas)).strip(), slug)
                )
                if email_st_actual != 'enviado':
                    modificado = True
                    actualizados.append({'slug': slug, 'nome': l['nome'], 'accion': 'Envío detectado en Gmail', 'status': nuevo_st})

            # Prioridad 5: Borrador listo en Gmail (no enviado aún)
            elif em in borradores_detectados:
                borr = borradores_detectados[em]
                resumen['borradores'] += 1
                nuevo_st = 'proposta' if st_actual in ['novo', 'redesenhado', 'publicado'] else st_actual
                conn.execute(
                    "UPDATE leads SET emailStatus='borrador', draftSubject=?, status=?, atualizado=datetime('now','localtime') WHERE slug=?",
                    (borr['asunto'], nuevo_st, slug)
                )
                if email_st_actual != 'borrador':
                    modificado = True
                    actualizados.append({'slug': slug, 'nome': l['nome'], 'accion': 'Borrador en preparación', 'status': nuevo_st})

        conn.commit()
        conn.close()

        return {
            'ok': True,
            'resumen': resumen,
            'actualizados': actualizados,
            'total_leads': len(leads)
        }

    except Exception as e:
        if 'conn' in locals() and conn: conn.close()
        return {'ok': False, 'erro': str(e)}

if __name__ == '__main__':
    print("=" * 65)
    print("🔄 SINCRONIZADOR OMNICANAL: Gmail (Borradores, Enviados, Inbox) + Calendar + Twilio")
    print("=" * 65)
    res = sincronizar_todo()
    if res.get('ok'):
        r = res.get('resumen', {})
        print(f"\n[✓] Sincronización exitosa:")
        print(f"    📝 Borradores listos en Gmail:   {r.get('borradores', 0)}")
        print(f"    ✉️ Propuestas enviadas:          {r.get('enviados', 0)}")
        print(f"    📬 Respuestas directas por email: {r.get('respuestas_email', 0)}")
        print(f"    📅 Citas de Google Calendar:      {r.get('citas_calendar', 0)}")
        print(f"    💬 Respuestas por SMS (Twilio):   {r.get('sms_recibidos', 0)}")
        if res.get('actualizados'):
            print(f"\n[+] Cambios aplicados en el CRM:")
            for a in res.get('actualizados'):
                print(f"    - {a['nome']}: {a['accion']} -> {a['status']}")
        else:
            print("\n(El CRM ya se encontraba 100% al día)")
    else:
        print(f"\n[!] Error en sincronización: {res.get('erro')}")
