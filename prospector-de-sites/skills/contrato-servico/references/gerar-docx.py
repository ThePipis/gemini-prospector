#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera contrato .docx para USA/California (EN/ES) protegido com regiões editáveis para o cliente.
Uso: python gerar-docx.py dados.json saida.docx
dados.json suporta chaves em inglês e espanhol com fallback automático."""
import json, sys
from docx import Document
from docx.shared import Pt, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

d = json.load(open(sys.argv[1], encoding='utf-8'))
lang = d.get('LANGUAGE', d.get('idioma', 'en')).lower()
is_es = lang.startswith('es')
PID = [100]

def par(doc, texto='', bold=False, center=False, size=11, antes=6):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(antes)
    p.paragraph_format.space_after = Pt(6)
    if center: p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    else: p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if texto:
        r = p.add_run(texto); r.bold = bold; r.font.size = Pt(size); r.font.name = 'Georgia'
    return p

def run(p, texto, bold=False, size=11):
    r = p.add_run(texto); r.bold = bold; r.font.size = Pt(size); r.font.name = 'Georgia'
    return r

def editavel(p, texto):
    """Insere trecho que o cliente pode editar (permStart/permEnd, grupo everyone)."""
    PID[0] += 1; pid = str(PID[0])
    ps = OxmlElement('w:permStart'); ps.set(qn('w:id'), pid); ps.set(qn('w:edGrp'), 'everyone')
    p._p.append(ps)
    r = run(p, texto); r.font.highlight_color = 7  # amarelo
    pe = OxmlElement('w:permEnd'); pe.set(qn('w:id'), pid)
    p._p.append(pe)

def campo(p, valor, rotulo):
    if 'preencher' in (valor or '').lower() or 'fill' in (valor or '').lower() or not valor:
        editavel(p, ' [' + rotulo + ': ' + ('completar aquí' if is_es else 'fill in here') + '] ')
    else:
        run(p, str(valor))

doc = Document()
for s in doc.sections:
    s.top_margin = s.bottom_margin = Cm(2.2); s.left_margin = s.right_margin = Cm(2.2)

client_name = d.get('CLIENT_NAME', d.get('NOME_CLIENTE', 'Client'))
client_biz = d.get('CLIENT_BUSINESS', d.get('NOME_NEGOCIO', client_name))
contractor_name = d.get('CONTRACTOR_NAME', d.get('NOME_PRESTADOR', 'Jose Gonzales'))
contractor_co = d.get('CONTRACTOR_COMPANY', d.get('EMPRESA_PRESTADOR', 'AI Sales Radar Studio'))
effective_date = d.get('EFFECTIVE_DATE', d.get('DATA_CONTRATO', ''))

if is_es:
    par(doc, 'CONTRATO DE PRESTACIÓN DE SERVICIOS INDEPENDIENTES', bold=True, center=True, size=13)
    par(doc, 'DISEÑO WEB, OPTIMIZACIÓN Y DESPLIEGUE EN LA NUBE', bold=True, center=True, size=11)
    
    p = par(doc, antes=12); run(p, 'Fecha efectiva: ', bold=True)
    if effective_date: run(p, effective_date)
    else: editavel(p, ' [Fecha] ')

    p = par(doc); run(p, 'EL CLIENTE: ', bold=True); run(p, client_name + ', operando como ' + client_biz + ', con EIN/Tax ID: ')
    campo(p, d.get('CLIENT_EIN_SSN'), 'EIN/SSN')
    run(p, ', con domicilio en ')
    campo(p, d.get('CLIENT_ADDRESS'), 'Dirección')
    run(p, ', ' + d.get('CLIENT_CITY_STATE_ZIP', 'California, USA') + '.')

    p = par(doc); run(p, 'EL CONTRATISTA: ', bold=True); run(p, contractor_name + ', operando como ' + contractor_co + ', con domicilio en ' + d.get('CONTRACTOR_ADDRESS', 'California, USA') + '.')

    par(doc, 'Las partes celebran el presente contrato de servicios profesionales que se regirá bajo las leyes del Estado de California y las siguientes estipulaciones:')

    def clausula(n, tit, txt):
        par(doc, 'Cláusula %d — %s' % (n, tit), bold=True, antes=10)
        par(doc, txt)

    clausula(1, 'Alcance del Trabajo', 'El Contratista diseñará y desarrollará una nueva versión de alta conversión de la página web del Cliente a partir de su web actual (%s), incluyendo rediseño responsivo para móviles, mejora de copywriting y publicación en Cloudflare en %s.' % (d.get('URL_CURRENT_SITE', d.get('URL_SITE_ANTIGO', 'N/A')), d.get('URL_PUBLICADA', 'Cloudflare')))
    clausula(2, 'Honorarios y Forma de Pago', 'Por los servicios descritos, el Cliente pagará un monto total de $%s USD (%s). Forma de pago: %s.' % (d.get('VALOR', '0'), d.get('VALOR_EXTENSO', ''), d.get('PAYMENT_TERMS', d.get('FORMA_PAGAMENTO', '50% anticipo, 50% entrega'))))
    clausula(3, 'Plazos y Revisiones', 'Entrega en un plazo de %s a partir de la firma y entrega de materiales. Incluye %s ronda(s) de ajustes menores.' % (d.get('TIMELINE_DAYS', d.get('PRAZO_ENTREGA', '5 días laborables')), d.get('ROUNDS_OF_REVISIONS', d.get('RODADAS_AJUSTES', '2'))))
    
    n = 4
    if d.get('MANUTENCAO') or d.get('MONTHLY_MAINTENANCE'):
        val_m = d.get('VALOR_MANUTENCAO', d.get('MONTHLY_MAINTENANCE_FEE', '100'))
        clausula(4, 'Mantenimiento Mensual y Hospedaje', 'El Cliente contrata servicio de mantenimiento, actualizaciones y soporte por $%s USD/mes, renovable mensualmente y cancelable con aviso de 30 días.' % val_m)
        n = 5

    clausula(n, 'Propiedad Intelectual', 'El Cliente conserva todos los derechos sobre sus marcas y logos. Al cancelarse el monto en su totalidad, los derechos sobre el diseño final son transferidos al Cliente.')
    clausula(n+1, 'Hospedaje e Infraestructura', 'El sitio web es alojado sobre la infraestructura perimetral de Cloudflare con certificado SSL/TLS (HTTPS) nativo y alta velocidad.')
    clausula(n+2, 'Ley Aplicable', 'El presente acuerdo se rige por las leyes del Estado de California, Estados Unidos.')

    par(doc, '', antes=18)
    p = par(doc, antes=14); run(p, '__________________________________________'); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = par(doc, antes=0); run(p, client_name + ' — Por el Cliente', bold=True); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    editavel(p, ' [firmar aquí] ')
    p = par(doc, antes=14); run(p, '__________________________________________'); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = par(doc, antes=0, center=True); run(p, contractor_name + ' — Por el Contratista', bold=True)

else:
    par(doc, 'INDEPENDENT CONTRACTOR AGREEMENT', bold=True, center=True, size=13)
    par(doc, 'WEB DESIGN, OPTIMIZATION & CLOUD DEPLOYMENT SERVICES', bold=True, center=True, size=11)
    
    p = par(doc, antes=12); run(p, 'Effective Date: ', bold=True)
    if effective_date: run(p, effective_date)
    else: editavel(p, ' [Date] ')

    p = par(doc); run(p, 'CLIENT: ', bold=True); run(p, client_name + ', operating as ' + client_biz + ', Tax ID/EIN: ')
    campo(p, d.get('CLIENT_EIN_SSN'), 'EIN/SSN')
    run(p, ', located at ')
    campo(p, d.get('CLIENT_ADDRESS'), 'Address')
    run(p, ', ' + d.get('CLIENT_CITY_STATE_ZIP', 'California, USA') + '.')

    p = par(doc); run(p, 'CONTRACTOR: ', bold=True); run(p, contractor_name + ', operating as ' + contractor_co + ', located at ' + d.get('CONTRACTOR_ADDRESS', 'California, USA') + '.')

    par(doc, 'This Independent Contractor Agreement is entered into under the laws of the State of California, subject to the following terms:')

    def section(n, tit, txt):
        par(doc, 'Section %d — %s' % (n, tit), bold=True, antes=10)
        par(doc, txt)

    section(1, 'Scope of Work', 'Contractor shall design, optimize, and deploy a responsive, high-converting web landing page based on Client\'s existing site (%s), with enhanced copywriting, authentic imagery, and deployment to Cloudflare at %s.' % (d.get('URL_CURRENT_SITE', d.get('URL_SITE_ANTIGO', 'N/A')), d.get('URL_PUBLICADA', 'Cloudflare')))
    section(2, 'Compensation & Payment Terms', 'Client agrees to pay Contractor a total project fee of $%s USD (%s). Payment terms: %s.' % (d.get('VALOR', '0'), d.get('VALOR_EXTENSO', ''), d.get('PAYMENT_TERMS', d.get('FORMA_PAGAMENTO', '50% deposit, 50% upon deployment'))))
    section(3, 'Timeline and Revisions', 'Delivery within %s following receipt of deposit and approvals. Includes %s round(s) of minor revisions.' % (d.get('TIMELINE_DAYS', d.get('PRAZO_ENTREGA', '5 business days')), d.get('ROUNDS_OF_REVISIONS', d.get('RODADAS_AJUSTES', '2'))))
    
    n = 4
    if d.get('MANUTENCAO') or d.get('MONTHLY_MAINTENANCE'):
        val_m = d.get('VALOR_MANUTENCAO', d.get('MONTHLY_MAINTENANCE_FEE', '100'))
        section(4, 'Monthly Maintenance & Hosting Support', 'Client retains Contractor for monthly hosting, maintenance, and support at $%s USD/month, cancellable with 30 days notice.' % val_m)
        n = 5

    section(n, 'Intellectual Property Rights', 'Client retains pre-existing IP. Upon full payment, rights in the customized design layout transfer to Client.')
    section(n+1, 'Cloudflare Hosting & Infrastructure', 'Website is hosted on Cloudflare\'s edge network with automated SSL/TLS encryption (HTTPS) and global caching.')
    section(n+2, 'Governing Law', 'This Agreement shall be governed by and construed in accordance with the laws of the State of California, USA.')

    par(doc, '', antes=18)
    p = par(doc, antes=14); run(p, '__________________________________________'); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = par(doc, antes=0); run(p, client_name + ' — Client Authorized Signer', bold=True); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    editavel(p, ' [sign here] ')
    p = par(doc, antes=14); run(p, '__________________________________________'); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = par(doc, antes=0, center=True); run(p, contractor_name + ' — Contractor', bold=True)

par(doc, 'Standard legal template generated for California commercial services. Consultation with legal counsel recommended. Generated by Gemini Prospector.', size=8, antes=20)

# Protection: read-only except editable regions
dp = OxmlElement('w:documentProtection')
dp.set(qn('w:edit'), 'readOnly'); dp.set(qn('w:enforcement'), '1')
doc.settings.element.append(dp)

doc.save(sys.argv[2])
print('Generated docx:', sys.argv[2])
