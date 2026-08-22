---
doc_id: handbook
title: Handbook de operaciones de NebulaOps
version: 3.2
effective_from: 2026-07-01
owner: People Operations
---

# Handbook de operaciones

## Horario y cobertura

NebulaOps opera el servicio las 24 horas, pero el soporte humano ordinario atiende de lunes a
viernes de 08:00 a 18:00, hora de Europa/Madrid, excepto festivos nacionales de España. El soporte
Priority de los planes Scale y Enterprise añade atención de incidentes P1 las 24 horas. Las
consultas comerciales y de facturación no se consideran P1 y se responden en horario ordinario.

El idioma principal de soporte es español. Enterprise puede contratar atención en inglés. Los
tiempos se miden dentro de la ventana de cobertura del plan salvo los P1 con soporte 24/7.

## Objetivos de primera respuesta

| Plan | P1 | P2 | P3 |
|---|---:|---:|---:|
| Starter | 4 h laborables | 1 día laborable | 2 días laborables |
| Scale | 30 min, 24/7 | 4 h laborables | 1 día laborable |
| Enterprise | 15 min, 24/7 | 2 h laborables | 8 h laborables |

Estos tiempos son objetivos de primera respuesta, no de resolución. El tiempo de resolución depende
de la causa y se comunica en cada actualización del incidente.

## Guardia y escalado humano

La persona on-call de ingeniería atiende alertas técnicas automáticas. El Support Lead recibe
escalados de clientes y decide si el caso cumple severidad P1 o P2 según el runbook de incidentes.
Un P1 debe tener Incident Commander asignado; soporte no realiza cambios directos en producción.

La rotación primaria cambia los lunes a las 10:00 Europe/Madrid. Existe una persona secundaria para
ausencias o falta de acuse. Si la persona primaria no reconoce una alerta P1 en cinco minutos, el
sistema avisa automáticamente a la secundaria.

## Canales autorizados

- Portal de soporte: canal recomendado; conserva identidad, tenant y trazabilidad.
- Email: crea un ticket, pero las acciones de cuenta requieren verificación posterior en el portal.
- Chat de producto: solo orientación; no admite adjuntos sensibles.
- Teléfono: exclusivo de Enterprise para incidentes P1; el número aparece en el contrato.

NebulaOps nunca solicita contraseñas, códigos MFA, claves API completas ni números completos de
tarjeta por ningún canal.

## Protección de datos en soporte

Los tickets se conservan 24 meses por motivos de auditoría y mejora del servicio. Los adjuntos se
eliminan a los 90 días salvo que estén vinculados a una investigación de seguridad abierta. El
cliente puede solicitar exportación o borrado según contrato y normativa; Security revisa las
excepciones de conservación.

Los agentes deben redactar tokens, cookies, contraseñas y datos de pago antes de escalar un ticket.
Los logs compartidos no deben superar la ventana temporal necesaria ni incluir datos de otros
tenants.

## Cambios y mantenimiento

El mantenimiento planificado se anuncia con al menos 72 horas de antelación en la página de estado.
Las ventanas ordinarias son los miércoles entre 22:00 y 00:00 Europe/Madrid. Un cambio urgente de
seguridad puede realizarse fuera de ventana con aprobación del Incident Commander y del Security
Lead; se publica una explicación posterior.
