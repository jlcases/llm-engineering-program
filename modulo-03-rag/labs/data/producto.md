---
doc_id: producto
title: Catálogo y límites de NebulaOps
version: 5.1
effective_from: 2026-08-01
owner: Product Operations
---

# Producto, planes y límites

## Plan Starter

Starter incluye hasta 10 usuarios, 30 días de retención de métricas, cinco dashboards y 100.000
eventos ingeridos al día. Permite una integración de alertas por email. No incluye SSO SAML,
entornos privados ni soporte de incidentes 24/7.

## Plan Scale

Scale incluye hasta 100 usuarios, 180 días de retención, dashboards ilimitados y cinco millones de
eventos al día. Incluye SSO SAML, webhooks, Slack, Microsoft Teams, PagerDuty y soporte P1 24/7. La
API permite 600 requests por minuto por tenant con ráfagas de hasta 60 requests en un segundo.

## Plan Enterprise

Enterprise no fija límite contractual de usuarios: se acuerda capacidad y precio. Ofrece retención
configurable entre 365 y 730 días, regiones dedicadas, PrivateLink, claves gestionadas por el
cliente y soporte P1 24/7 con objetivo de primera respuesta de 15 minutos. La cuota API se define
en contrato y puede superar la de Scale tras una prueba de carga.

## Regiones y residencia

El servicio multi-tenant estándar está disponible en `eu-west-1` (Irlanda) y `us-east-1`
(Virginia). Un tenant elige región al crearse y NebulaOps no replica sus datos de telemetría entre
regiones. Cambiar de región requiere un proyecto de migración; no existe un botón de autoservicio.

Los backups permanecen en la misma región lógica del tenant. Enterprise puede contratar una región
dedicada entre las ofertadas en su contrato. La documentación pública no promete disponibilidad en
Asia-Pacífico.

## Ingestión y retención

Los límites diarios se calculan en UTC. Los eventos que superan el límite se rechazan con HTTP 429
y no se ponen en cola para el día siguiente. La respuesta incluye `Retry-After` cuando el límite es
temporal; al agotar la cuota diaria, el dashboard muestra la fecha de reinicio.

La reducción de retención elimina primero los datos que exceden el nuevo periodo tras una ventana
de gracia de siete días. Aumentar la retención no recupera datos ya eliminados.

## Exportaciones

CSV síncrono admite un máximo de 100.000 filas. Exportaciones mayores se ejecutan como job y generan
un enlace firmado válido durante 24 horas. Los enlaces no se pueden renovar; hay que repetir el job.
El formato Parquet está disponible en Scale y Enterprise.

## Integraciones

Los webhooks se entregan al menos una vez, por lo que el receptor debe deduplicar por `event_id`.
NebulaOps reintenta respuestas 5xx o timeouts durante 24 horas con backoff exponencial. No reintenta
respuestas 2xx ni 4xx, excepto 429 cuando contiene `Retry-After` válido.

Cada endpoint de webhook puede configurar un secreto de firma. La cabecera `X-Nebula-Signature`
contiene HMAC-SHA256 del cuerpo exacto; se debe verificar antes de parsear JSON.

## Disponibilidad

El SLA contractual mensual es 99,9 % para Scale y 99,95 % para Enterprise. Starter no tiene SLA
económico. Mantenimiento anunciado con 72 horas y exclusiones contractuales no computa según los
términos de cada plan.
