"""
Servicio de members. Sin lógica todavía — se implementa junto con
spec/features/001, 004, 005, 006/.

Regla de módulos (no negociable, AGENTS.md): este service es el ÚNICO punto de
entrada que otros módulos pueden llamar para leer/mutar datos de members.
Ningún otro módulo debe importar members/repository.py directamente.
"""
