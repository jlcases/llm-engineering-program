---
doc_id: seguridad-cuentas
title: Política de seguridad de cuentas
version: 2.8
effective_from: 2026-06-10
owner: Security
---

# Seguridad de cuentas

## Autenticación multifactor

MFA mediante aplicación TOTP está disponible en todos los planes. Los códigos de recuperación se
muestran una sola vez al activar MFA; NebulaOps no puede volver a mostrar los mismos. Generar un
nuevo conjunto invalida el anterior.

Si un usuario pierde el segundo factor, un administrador verificado del mismo tenant puede iniciar
el reset desde el portal. Si la persona afectada es el único administrador, soporte aplica el
procedimiento de recuperación reforzada: verificación de dominio corporativo y dos evidencias
contractuales. Soporte nunca pide el código TOTP ni una contraseña.

## SSO

SSO SAML está incluido en Scale y Enterprise. Enterprise puede exigir SSO para todos los usuarios;
las cuentas break-glass quedan excluidas, deben ser como máximo dos y usar MFA. Starter no incluye
SSO SAML.

Al activar enforcement, las sesiones existentes se revocan en un máximo de 15 minutos. Antes de
activarlo se debe probar un usuario no administrador y una cuenta break-glass.

## Sesiones y contraseñas

El enlace de recuperación de contraseña caduca a los 30 minutos y es de un solo uso. Solicitar uno
nuevo invalida los anteriores. Tras cambiar contraseña se revocan las demás sesiones en un máximo
de cinco minutos.

La sesión web ordinaria caduca tras 12 horas de inactividad. Un administrador puede revocar todas
las sesiones de un usuario desde Security > Active sessions.

## Claves API

Las claves se muestran una sola vez. Solo se almacena un hash no reversible. Cada clave tiene
owner, scopes y fecha de creación; Enterprise puede imponer expiración máxima de 90 días. La UI
solo muestra los últimos cuatro caracteres.

Ante exposición, revoca primero la clave, crea una nueva con scopes mínimos y revisa el audit log.
Rotar sin revocar deja vigente la credencial filtrada.

## Sospecha de phishing o acceso no autorizado

1. Revocar sesiones y claves afectadas.
2. Restablecer contraseña desde un dispositivo confiable.
3. Revisar usuarios, roles, webhooks e integraciones recientes.
4. Abrir ticket de seguridad con horas aproximadas e IPs si están disponibles.
5. No borrar emails, logs ni mensajes relacionados.

Un cambio no reconocido de administrador o evidencia de datos de otro tenant se clasifica P1. Una
simulación interna de phishing sin compromiso real se gestiona según el programa de Security.

## Audit log

Scale conserva 180 días de audit log y Enterprise 365 días. Starter conserva 30 días. El audit log
registra login, cambios de rol, creación/revocación de claves, configuración SSO e integraciones.
Los eventos se exportan en JSON; no se pueden editar desde el producto.
