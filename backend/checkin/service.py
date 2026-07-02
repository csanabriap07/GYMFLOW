"""
Servicio de checkin. Sin lógica todavía — se implementa junto con
spec/features/001, 002, 005, 006/.

Regla de módulos (no negociable, AGENTS.md): este service es el ÚNICO punto de
entrada que otros módulos pueden llamar para leer/mutar datos de checkin.
Ningún otro módulo debe importar checkin/repository.py directamente.
"""
