"""
Servicio de reports. Sin lógica todavía — se implementa junto con
spec/features/010-reportes-asistencia/.

Regla de módulos (no negociable, AGENTS.md): este service es el ÚNICO punto de
entrada que otros módulos pueden llamar para leer/mutar datos de reports.
Ningún otro módulo debe importar reports/repository.py directamente.
"""
