"""
Servicio de auth. Sin lógica todavía — se implementa junto con
spec/features/003-autenticacion-segura/.

Regla de módulos (no negociable, AGENTS.md): este service es el ÚNICO punto de
entrada que otros módulos pueden llamar para leer/mutar datos de auth.
Ningún otro módulo debe importar auth/repository.py directamente.
"""
