# 010 · Reportes de asistencia

**Estado:** propuesta

**Traza:** HU-09 · RF-12, RF-13 · RF-05 (fuente inmutable), RF-09 · depende de `003-autenticacion-segura`

## Qué hace

Da al **Administrador** un reporte histórico de asistencias filtrable por **rango de fechas** (Fecha Inicio – Fecha Fin) y la posibilidad de **exportarlo a `.XLSX` y `.CSV`**.

## Por qué

Convierte el histórico inmutable de `CheckIn` en información para decisiones de negocio (aforo, conversión de prospectos, uso por plan). Cierra la trazabilidad HU-09 → RF-12/RF-13.

## Criterios de aceptación

- [ ] Un Administrador filtra por Fecha Inicio–Fecha Fin y obtiene una **tabla consolidada** de asistencias (fecha/hora, usuario, resultado, tipo de membresía, titular si es invitado) (RF-12).
- [ ] El reporte filtrado se puede **exportar a `.XLSX`** y a **`.CSV`** con los mismos datos mostrados (RF-13).
- [ ] Los datos provienen de `CheckIn` (registro **inmutable**, RF-05) y **no** se alteran al reportar.
- [ ] Solo rol **Administrador** puede acceder (RBAC, RF-09).
- [ ] Un rango sin registros devuelve un reporte vacío coherente (no error).

## Fuera de alcance

- **Dashboards** en tiempo real o gráficos → no está en `docs/` (solo tabla + export).
- **Generación** de los check-ins → `001`/`002`/`005`/`006`.
- **Discrepancia de la constitución (marcar con el equipo):** `tech-stack.md` describe un `reports/repository.py` con "lectura agregada sobre `CheckIn`", pero `CheckIn` es propiedad del módulo `checkin` y el **límite duro** prohíbe "queries cruzadas entre tablas de distintos módulos saltándose el service del módulo dueño". Ver la resolución propuesta en el plan.
