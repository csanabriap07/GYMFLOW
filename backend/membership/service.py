"""
Servicio de membership. Sin lógica todavía — se implementa junto con
spec/features/001, 007, 009/.

Regla de módulos (no negociable, AGENTS.md): este service es el ÚNICO punto de
entrada que otros módulos pueden llamar para leer/mutar datos de membership.
Ningún otro módulo debe importar membership/repository.py directamente.
"""
