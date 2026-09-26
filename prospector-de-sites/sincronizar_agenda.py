#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sincronizador de Agenda y Mensajería Omnicanal (Wrapper de compatibilidad).
Invoca sincronizar_todo() de sincronizar_mensajes.py para mantener sincronizado
Gmail (Borradores, Enviados, Inbox), Google Calendar y Twilio con el CRM.
"""
import os, sys

PASTA = os.path.dirname(os.path.abspath(__file__))
if PASTA not in sys.path:
    sys.path.insert(0, PASTA)

try:
    from sincronizar_mensajes import sincronizar_todo
except ImportError:
    from prospector_de_sites.sincronizar_mensajes import sincronizar_todo

def sincronizar_citas():
    return sincronizar_todo()

if __name__ == '__main__':
    res = sincronizar_citas()
    print(res)
