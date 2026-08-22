---
doc_id: faq
title: Preguntas frecuentes de NebulaOps
version: 6.0
effective_from: 2026-08-01
owner: Customer Education
---

# Preguntas frecuentes

## ¿Puedo probar NebulaOps?

Existe una prueba de 14 días del plan Scale, limitada a 20 usuarios y 500.000 eventos diarios. No
requiere tarjeta. Al terminar, el tenant pasa a modo solo lectura durante siete días; después se
elimina si no se contrata un plan.

## ¿Cómo compruebo un webhook?

Usa la entrega de prueba desde Integrations > Webhooks. Verifica `X-Nebula-Signature` sobre el cuerpo
sin modificar y responde 2xx en menos de cinco segundos. El receptor debe deduplicar por `event_id`
porque la entrega es al menos una vez.

## ¿Qué zona horaria usa el producto?

Los eventos se almacenan en UTC. Cada usuario puede elegir zona de visualización; esto no altera el
timestamp original ni los límites diarios de ingestión, que se reinician a las 00:00 UTC.

## ¿Cómo exporto más de 100.000 filas?

Selecciona exportación asíncrona. Recibirás una notificación cuando el job termine y un enlace
firmado válido durante 24 horas. Scale y Enterprise pueden elegir CSV o Parquet.

## ¿Se puede recuperar información tras reducir retención?

Durante la ventana de gracia de siete días se puede cancelar el cambio. Después de la eliminación,
aumentar la retención no recupera datos. Un backup no funciona como archivo consultable por el
cliente.

## ¿Dónde veo cambios administrativos?

Security > Audit log muestra logins, roles, claves, SSO e integraciones. La retención depende del
plan: 30 días Starter, 180 Scale y 365 Enterprise.

## ¿Qué hago si el dashboard está lento?

Comprueba la página de estado y reduce temporalmente el rango temporal. Si persiste, abre un ticket
con URL del dashboard, rango, región y hora aproximada. No adjuntes tokens ni cookies.

## ¿NebulaOps ofrece aplicación móvil nativa?

No. La interfaz web es responsive y las alertas se reciben mediante integraciones. La documentación
no anuncia fecha para una aplicación móvil.
