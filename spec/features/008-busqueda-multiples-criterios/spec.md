# 008 · Búsqueda por múltiples criterios

**Estado:** propuesta

**Traza:** HU-03 · RF-01, RF-02, RF-03

## Qué hace

Permite identificar/buscar a un usuario por **cédula**, **código QR** o **nombre** (coincidencias parciales), tanto en el kiosko como en el backoffice, para que un miembro pueda ingresar aunque olvide alguno de sus datos y para que el staff resuelva incidencias.

## Por qué

Reduce la fricción del check-in y las incidencias de recepción (ej. "el usuario olvidó su número de cédula", §3 de la Propuesta). Alimenta la identificación de los flujos `001`, `002` y `006`.

## Criterios de aceptación

- [ ] Búsqueda por **cédula** exacta → devuelve el usuario correspondiente (RF-01).
- [ ] Búsqueda por **nombre parcial** → devuelve la lista de coincidencias para que el staff seleccione (RF-03).
- [ ] Lectura de **QR** → decodifica el payload e identifica al miembro (RF-02).
- [ ] Los resultados pueden encadenarse al flujo de check-in (identificación → validación).
- [ ] La búsqueda por nombre/documento admite coincidencias **parciales** (no solo exactas).

## Fuera de alcance

- Validación de acceso y descuentos → `001`/`002`/`006`.
- **Duda abierta (importante):** RF-02 pide un **"QR dinámico generado desde la sesión del Miembro"**, pero la misión establece que **el miembro no inicia sesión**. Es una contradicción real. Se propone para el MVP un **QR que codifica la cédula/id del miembro** (emitido por staff), y dejar el "QR dinámico por sesión" como pendiente de aclarar con la profesora. No se implementa sesión de miembro (choca con la constitución).
