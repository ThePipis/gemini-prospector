#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prospector — servidor local do dashboard (SQLite + Cloudflare). Sem dependências: só Python padrão.
Uso: python dashboard-server.py  (ou duplo clique em iniciar-dashboard.bat)
Abre em http://localhost:8765 — edições, exclusões e drag&drop salvam no prospector.db"""
import json, sqlite3, os, sys, webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

PASTA = os.path.dirname(os.path.abspath(__file__))
# Si se ejecuta desde subcarpeta dashboard, subir a raíz si prospector.db / config están arriba
if not os.path.exists(os.path.join(PASTA, 'prospector-config.json')) and os.path.exists(os.path.join(PASTA, '..', 'prospector-config.json')):
    PASTA = os.path.abspath(os.path.join(PASTA, '..'))
elif not os.path.exists(os.path.join(PASTA, 'prospector-config.json')) and os.path.exists(os.path.join(PASTA, '..', '..', 'prospector-config.json')):
    PASTA = os.path.abspath(os.path.join(PASTA, '..', '..'))

os.chdir(PASTA)
DB = os.path.join(PASTA, 'prospector.db')
CONFIG = os.path.join(PASTA, 'prospector-config.json')

def ler_config():
    try: return json.load(open(CONFIG, encoding='utf-8'))
    except Exception: return {}

PORTA = 8765
CAMPOS = ['slug','nome','nicho','cidade','nota','avaliacoes','email','telefone','whatsapp',
          'siteAntigo','motivo','status','urlNova','dataProposta','valor','obs',
          'contratoStatus','contratoEm','manutencao','pago','docCliente','endCliente']

def conexao():
    c = sqlite3.connect(DB)
    c.execute('''CREATE TABLE IF NOT EXISTS leads(
        slug TEXT PRIMARY KEY, nome TEXT, nicho TEXT, cidade TEXT, nota REAL, avaliacoes INTEGER,
        email TEXT, telefone TEXT, whatsapp TEXT, siteAntigo TEXT, motivo TEXT,
        status TEXT DEFAULT 'novo', urlNova TEXT, dataProposta TEXT, valor REAL, obs TEXT,
        contratoStatus TEXT DEFAULT 'pendente', contratoEm TEXT, manutencao REAL, pago INTEGER DEFAULT 0,
        atualizado TEXT DEFAULT (datetime('now','localtime')))''')
    for col, tipo in [('contratoStatus',"TEXT DEFAULT 'pendente'"),('contratoEm','TEXT'),('manutencao','REAL'),('pago','INTEGER DEFAULT 0'),('docCliente','TEXT'),('endCliente','TEXT')]:
        try: c.execute('ALTER TABLE leads ADD COLUMN %s %s' % (col, tipo))
        except sqlite3.OperationalError: pass
    return c

def importar_snapshot():
    """Primeira execução sem banco: importa os leads embutidos no dashboard.html."""
    try:
        html = open(os.path.join(PASTA, 'dashboard.html'), encoding='utf-8').read()
        ini = html.index('<script id="dados" type="application/json">') + len('<script id="dados" type="application/json">')
        fim = html.index('</script>', ini)
        dados = json.loads(html[ini:fim])
        c = conexao()
        for l in dados.get('leads', []):
            c.execute('INSERT OR IGNORE INTO leads (%s) VALUES (%s)' % (','.join(CAMPOS), ','.join('?'*len(CAMPOS))),
                      [l.get(k) for k in CAMPOS])
        c.commit(); c.close()
        print('Snapshot importado do dashboard.html para o prospector.db')
    except Exception as e:
        print('(sem snapshot para importar: %s)' % e)

class App(SimpleHTTPRequestHandler):
    def _json(self, code, obj):
        corpo = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store')
        self.send_header('Content-Length', str(len(corpo)))
        self.end_headers(); self.wfile.write(corpo)

    def _corpo(self):
        n = int(self.headers.get('Content-Length', 0))
        return json.loads(self.rfile.read(n).decode('utf-8')) if n else {}

    def do_GET(self):
        if self.path.split('?')[0] == '/api/config':
            cfg = ler_config()
            cf = dict(cfg.get('cloudflare', {}))
            cf['tokenDefinido'] = bool(cf.get('apiToken') or os.getenv('CLOUDFLARE_API_TOKEN'))
            cf.pop('apiToken', None)  # El token NUNCA sale hacia el frontend

            contrato = dict(cfg.get('contrato', {}))
            contratante = dict(cfg.get('contratante', {}))
            firma = dict(cfg.get('firma', {}))

            # Consolidar campos para que el dashboard reciba siempre la información completa
            for k in ['prestador_nombre', 'prestador_empresa', 'prestador_ein', 'prestador_direccion', 'estado_jurisdiccion', 'email', 'telefono']:
                val = contrato.get(k) or contratante.get(k) or ''
                if not val and k == 'email':
                    val = firma.get('email', '')
                if not val and k == 'telefono':
                    val = firma.get('telefono', '')
                if not val and k == 'prestador_nombre':
                    val = firma.get('nombre', '')
                if not val and k == 'prestador_empresa':
                    val = firma.get('empresa', '')
                contrato[k] = val

            return self._json(200, {
                'contrato': contrato,
                'contratante': contrato,
                'firma': firma,
                'cloudflare': cf,
                'prospeccion': cfg.get('prospeccion', {})
            })
        if self.path.split('?')[0] == '/api/leads':
            c = conexao(); c.row_factory = sqlite3.Row
            rows = [dict(r) for r in c.execute('SELECT * FROM leads').fetchall()]; c.close()
            return self._json(200, rows)
        if self.path in ('/', '', '/dashboard.html', '/dashboard-template.html'):
            for cand in ['dashboard.html', 'dashboard-template.html', os.path.join('dashboard', 'dashboard-template.html'), os.path.join('dashboard', 'dashboard.html')]:
                p = os.path.join(PASTA, cand)
                if os.path.exists(p):
                    conteudo = open(p, 'rb').read()
                    self.send_response(200)
                    self.send_header('Content-Type', 'text/html; charset=utf-8')
                    self.send_header('Content-Length', str(len(conteudo)))
                    self.end_headers()
                    self.wfile.write(conteudo)
                    return
        return SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path.split('?')[0] == '/api/leads':
            l = self._corpo(); c = conexao()
            c.execute('INSERT OR REPLACE INTO leads (%s) VALUES (%s)' % (','.join(CAMPOS), ','.join('?'*len(CAMPOS))),
                      [l.get(k) for k in CAMPOS])
            c.commit(); c.close(); return self._json(200, {'ok': True})
        return self._json(404, {'erro': 'rota'})

    def do_PUT(self):
        if self.path.split('?')[0] == '/api/config':
            cfg = ler_config(); corpo = self._corpo()
            for key in ['contrato', 'firma', 'cloudflare', 'prospeccion', 'contratante', 'hostgator']:
                if key in corpo and isinstance(corpo[key], dict):
                    sub = cfg.get(key, {})
                    for k, v in corpo[key].items():
                        if key == 'cloudflare' and k == 'apiToken' and v == '':
                            continue
                        sub[k] = v
                    cfg[key] = sub

            # Sincronizar datos del contratista/prestador en contrato y firma
            datos_prestador = corpo.get('contrato') or corpo.get('contratante')
            if datos_prestador and isinstance(datos_prestador, dict):
                cfg_contrato = cfg.setdefault('contrato', {})
                cfg_contratante = cfg.setdefault('contratante', {})
                cfg_firma = cfg.setdefault('firma', {})
                for k, v in datos_prestador.items():
                    cfg_contrato[k] = v
                    cfg_contratante[k] = v
                    if k == 'email':
                        cfg_firma['email'] = v
                    elif k == 'telefono':
                        cfg_firma['telefono'] = v
                    elif k == 'prestador_nombre' and v:
                        cfg_firma['nombre'] = v
                    elif k == 'prestador_empresa' and v:
                        cfg_firma['empresa'] = v

            json.dump(cfg, open(CONFIG, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
            return self._json(200, {'ok': True})
        partes = self.path.split('?')[0].split('/')
        if len(partes) == 4 and partes[1] == 'api' and partes[2] == 'leads':
            slug, ch = partes[3], self._corpo()
            sets = [k for k in ch if k in CAMPOS and k != 'slug']
            if sets:
                c = conexao()
                c.execute('UPDATE leads SET %s, atualizado=datetime("now","localtime") WHERE slug=?' %
                          ','.join('%s=?' % k for k in sets), [ch[k] for k in sets] + [slug])
                c.commit(); c.close()
            return self._json(200, {'ok': True})
        return self._json(404, {'erro': 'rota'})

    def do_DELETE(self):
        partes = self.path.split('?')[0].split('/')
        if len(partes) == 4 and partes[1] == 'api' and partes[2] == 'leads':
            c = conexao(); c.execute('DELETE FROM leads WHERE slug=?', (partes[3],)); c.commit(); c.close()
            return self._json(200, {'ok': True})
        return self._json(404, {'erro': 'rota'})

    def log_message(self, *a): pass

if __name__ == '__main__':
    novo = not os.path.exists(DB)
    conexao().close()
    if novo: importar_snapshot()
    print('Prospector Dashboard activo en http://localhost:%d  (Ctrl+C para detener)' % PORTA)
    try: webbrowser.open('http://localhost:%d' % PORTA)
    except Exception: pass
    try: ThreadingHTTPServer(('127.0.0.1', PORTA), App).serve_forever()
    except KeyboardInterrupt: print('\nEncerrado.')
