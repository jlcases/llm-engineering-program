---
doc_id: facturacion
title: Facturación y pagos
version: 3.6
effective_from: 2026-05-01
owner: Finance Operations
---

# Facturación y pagos

## Ciclo y documentos

Los planes mensuales se facturan al inicio de cada periodo. Los anuales se facturan por adelantado
salvo acuerdo Enterprise distinto. Las facturas se generan en UTC y aparecen en Billing > Invoices
en un máximo de dos horas desde el cobro.

El PDF es el documento fiscal. El recibo de tarjeta no sustituye a la factura. Las facturas emitidas
no se editan: una corrección fiscal se realiza mediante abono y nueva factura.

## Datos fiscales

Los cambios de razón social, dirección o VAT ID se aplican a documentos futuros. Para corregir una
factura ya emitida hay que abrir un ticket de facturación e indicar número y dato correcto. Finance
verifica la solicitud antes de emitir abono.

Clientes de la UE con VAT ID válido pueden recibir inversión del sujeto pasivo cuando corresponda.
La validación no es retroactiva automática. Exenciones especiales requieren certificado vigente y
revisión de Finance.

## Métodos y reintentos

Starter y Scale aceptan tarjeta. Enterprise puede pagar por transferencia si figura en contrato.
Cuando una tarjeta falla, se realizan reintentos en los días 1, 3 y 7 desde el vencimiento. Durante
ese periodo la cuenta muestra estado `past_due` pero no se suspende inmediatamente.

Si el pago sigue pendiente después del último reintento, se avisa al administrador y comienza una
ventana de gracia de siete días. La suspensión limita ingestión nueva, pero permite exportar datos
existentes durante la ventana. Finance puede adaptar el proceso en contratos Enterprise.

## Cargos duplicados y no reconocidos

Un cargo duplicado se investiga comparando invoice ID, payment intent, importe y timestamp. No se
promete reembolso hasta verificar que no es una autorización bancaria temporal. Un cargo no
reconocido activo se marca prioridad P3 de soporte interno equivalente a urgente y se escala a
Finance/Security; el usuario debe contactar también con su entidad si sospecha fraude de tarjeta.

NebulaOps nunca solicita el número completo de tarjeta ni CVV. Soporte usa los últimos cuatro
dígitos y el ID del pago.

## Reembolsos

Starter y Scale pueden solicitar reembolso de una renovación dentro de los 14 días si no hubo uso
material posterior. Las altas iniciales y servicios profesionales siguen los términos contratados.
Enterprise se rige por contrato. Un reembolso aprobado tarda normalmente entre 5 y 10 días
laborables en reflejarse, según la entidad bancaria.

## Descarga y destinatarios

Administradores y roles Billing pueden descargar facturas. Se puede configurar un máximo de cinco
destinatarios adicionales en Billing > Notifications. Añadir un destinatario no le concede acceso
al tenant ni a facturas históricas; solo recibe las nuevas por email.
