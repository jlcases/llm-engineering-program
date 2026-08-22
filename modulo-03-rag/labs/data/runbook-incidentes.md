---
doc_id: runbook-incidentes
title: Runbook de incidentes de producción
version: 4.4
effective_from: 2026-07-14
owner: Site Reliability Engineering
---

# Runbook de incidentes

## Severidades

### P1 — crítico

Caída general, pérdida o exposición confirmada de datos, acceso cruzado entre tenants, o función
crítica indisponible sin alternativa para una parte material de clientes. Una sospecha razonable de
exposición se trata como P1 hasta descartarla.

### P2 — alto

Degradación significativa o función importante rota con alternativa parcial. Afecta a varios
clientes o bloquea un flujo importante, pero no hay pérdida/exposición confirmada ni caída general.

### P3 — normal

Impacto limitado, defecto cosmético, consulta o problema con alternativa clara. Se gestiona en el
backlog ordinario.

La severidad describe impacto actual, no dificultad técnica ni importancia comercial del cliente.

## Primeros 15 minutos de un P1

1. La persona on-call reconoce la alerta en un máximo de cinco minutos.
2. Declara el incidente y asigna un Incident Commander en un máximo de diez minutos desde la alerta.
3. Abre canal privado de coordinación y documento cronológico.
4. Designa Communications Lead; el Incident Commander no redacta actualizaciones mientras coordina.
5. Publica la primera actualización externa antes de 15 minutos, aunque la causa siga desconocida.
6. Evalúa contención reversible antes de buscar la causa raíz perfecta.

Si la primaria no responde en cinco minutos, se pagina a la secundaria. Si tampoco responde en
otros cinco, escala al Engineering Manager de guardia.

## Comunicación

Durante un P1 se actualiza la página de estado al menos cada 30 minutos. Cada mensaje incluye
impacto observado, acciones en curso y hora de la próxima actualización. No se publica una causa
sin evidencia. Los clientes Enterprise afectados reciben además actualización por su canal
contractual.

Para P2, la cadencia externa es cada 60 minutos cuando existe impacto visible. P3 no requiere página
de estado.

## Contención y cambios

Cambios de emergencia requieren aprobación del Incident Commander y una segunda persona técnica.
Se registra comando/cambio, autor, hora, resultado y plan de reversión. Las credenciales break-glass
son temporales, se auditan y se revocan al cerrar la fase de respuesta.

No se borran logs, colas ni snapshots durante una investigación. Si hay presión de almacenamiento,
se amplía capacidad o se exporta de forma controlada.

## Cierre y postmortem

Un incidente se resuelve cuando el impacto termina y las métricas confirman estabilidad durante al
menos 30 minutos. El Incident Commander puede ampliar esa ventana. Cerrar la página de estado no
equivale a completar la investigación.

Todo P1 tiene postmortem sin culpa publicado internamente en cinco días laborables. Debe incluir
timeline, impacto, detección, factores contribuyentes, qué funcionó, qué falló y acciones con owner y
fecha. P2 requiere postmortem si duró más de dos horas, se repitió o el Incident Commander lo pide.

## Evidencia mínima

- ID y timestamps en UTC;
- métricas y logs relevantes con enlaces estables;
- decisiones y aprobaciones;
- clientes/tenants afectados sin incluir PII innecesaria;
- cambios y rollback;
- mensajes externos publicados;
- tareas de seguimiento.
