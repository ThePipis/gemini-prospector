#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sincronizador de Citas Google Calendar / Google Meet con el CRM de Prospector.
Escanea la bandeja de entrada de aisalesradar.agency@gmail.com buscando confirmaciones
de citas reservadas en Google Calendar. Al detectar una cita con un prospecto,
mueve automáticamente el lead a la columna 'respondeu' (Respondió / Cita Agendada)
en prospector.db.
"""

import os, sys, json, imaplib, email, re, sqlite3
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
    return sqlite3.connect(DB_FILE)

def sincronizar_citas():
    cfg = ler_config()
    envio = cfg.get('envio', {})
    user = envio.get('gmail_user')
    pw = envio.get('gmail_app_password', '').replace(' ', '')

    if not user or not pw:
        return {'ok': False, 'erro': 'Faltan credenciales de Gmail en prospector-config.json'}

    # Cargar leads activos desde la base de datos
    conn = conexao()
    conn.row_factory = sqlite3.Row
    leads = [dict(r) for r in conn.execute('SELECT slug, nome, email, telefone, status, obs FROM leads').fetchall()]

    # Mapa de emails conocidos a lead
    email_map = {}
    for l in leads:
        if l.get('email'):
            email_map[l['email'].strip().lower()] = l

    actualizados = []

    try:
        imap = imaplib.IMAP4_SSL('imap.gmail.com', 993)
        imap.login(user, pw)
        imap.select('INBOX')

        # Buscar correos relacionados con Google Calendar o citas
        criterios = [
            '(FROM "calendar-notification@google.com")',
            '(FROM "google.com" SUBJECT "Walkthrough")',
            '(FROM "google.com" SUBJECT "cita")',
            '(FROM "google.com" SUBJECT "booking")',
            '(FROM "google.com" SUBJECT "reserva")'
        ]

        uids_encontrados = set()
        for crit in criterios:
            try:
                typ, data = imap.search(None, crit)
                if typ == 'OK' and data[0]:
                    for num in data[0].split():
                        uids_encontrados.add(num)
            except Exception:
                pass

        print(f"[*] Escaneando {len(uids_encontrados)} correos de citas en INBOX...")

        for num in uids_encontrados:
            try:
                typ, msg_data = imap.fetch(num, '(RFC822)')
                if typ != 'OK': continue
                msg = email.message_from_bytes(msg_data[0][1])

                # Extraer cuerpo del correo
                cuerpo = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() in ['text/plain', 'text/html']:
                            try:
                                payload = part.get_payload(decode=True)
                                if payload: cuerpo += payload.decode('utf-8', errors='ignore') + " "
                            except Exception: pass
                else:
                    payload = msg.get_payload(decode=True)
                    if payload: cuerpo = payload.decode('utf-8', errors='ignore')

                # Extraer todos los emails presentes en el cuerpo y encabezados
                todos_textos = f"{msg.get('From', '')} {msg.get('To', '')} {msg.get('Subject', '')} {cuerpo}"
                emails_encontrados = set(re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', todos_textos.lower()))

                for em in emails_encontrados:
                    if em in email_map and em != user.lower():
                        lead = email_map[em]
                        slug = lead['slug']

                        # Si el lead aún no estaba marcado como que agendó / respondió
                        if lead['status'] in ['novo', 'redesenhado', 'publicado', 'proposta']:
                            timestamp_ahora = datetime.now().strftime('%Y-%m-%d %H:%M')
                            nueva_obs = (lead.get('obs') or '').strip()
                            nota_cita = f"[📅 CITA AGENDADA EN GOOGLE MEET] Reserva confirmada vía Google Calendar ({timestamp_ahora})"
                            if nota_cita not in nueva_obs:
                                nueva_obs = f"{nueva_obs}\n{nota_cita}".strip()

                            conn.execute(
                                'UPDATE leads SET status = ?, obs = ?, atualizado = datetime("now","localtime") WHERE slug = ?',
                                ('respondeu', nueva_obs, slug)
                            )
                            conn.commit()
                            actualizados.append({
                                'slug': slug,
                                'nome': lead['nome'],
                                'email': em,
                                'status_anterior': lead['status'],
                                'status_nuevo': 'respondeu'
                            })
                            print(f"[✓] Lead actualizado en CRM: {lead['nome']} -> respondeu (Cita agendada)")
            except Exception as e:
                print(f"[!] Error procesando correo de cita: {e}")

        imap.logout()
        conn.close()
        return {'ok': True, 'actualizados': actualizados, 'total_escaneados': len(uids_encontrados)}

    except Exception as e:
        if 'conn' in locals() and conn: conn.close()
        return {'ok': False, 'erro': str(e)}

if __name__ == '__main__':
    print("=" * 60)
    print("🔄 SINCRONIZADOR DE CITAS: Google Calendar / Meet -> CRM")
    print("=" * 60)
    res = sincronizar_citas()
    if res.get('ok'):
        print(f"\n[✓] Sincronización exitosa. Citas encontradas/actualizadas: {len(res.get('actualizados', []))}")
        for act in res.get('actualizados', []):
            print(f"    - {act['nome']} ({act['email']}): {act['status_anterior']} -> {act['status_nuevo']}")
    else:
        print(f"\n[!] Error en sincronización: {res.get('erro')}")
