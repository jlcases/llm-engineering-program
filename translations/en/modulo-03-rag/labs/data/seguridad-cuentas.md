---
doc_id: seguridad-cuentas
title: Account Security Policy
version: 2.8
effective_from: 2026-06-10
owner: Security
---

# Account Security

## Multi-factor Authentication

TOTP app-based MFA is available on all plans. Recovery codes are displayed only once when MFA is activated; NebulaOps cannot display them again. Generating a new set invalidates the previous one.

If a user loses the second factor, a verified administrator from the same tenant can initiate the reset from the portal. If the affected person is the only administrator, Support applies the enhanced recovery procedure: corporate domain verification and two contractual evidences. Support never asks for the TOTP code or a password.

## SSO

SAML SSO is included in Scale and Enterprise. Enterprise may require SSO for all users; break-glass accounts are excluded, must be no more than two, and must use MFA. Starter does not include SAML SSO.

When enabling enforcement, existing sessions are revoked within a maximum of 15 minutes. Before enabling it, you must test a non-administrator user and a break-glass account.

## Sessions and Passwords

The password recovery link expires after 30 minutes and is single-use. Requesting a new one invalidates previous ones. After changing the password, all other sessions are revoked within a maximum of five minutes.

The standard web session expires after 12 hours of inactivity. An administrator can revoke all sessions for a user from Security > Active sessions.

## API Keys

Keys are displayed only once. Only a non-reversible hash is stored. Each key has an owner, scopes, and a creation date; Enterprise can impose a maximum expiration of 90 days. The UI only displays the last four characters.

In case of exposure, first revoke the key, create a new one with minimal scopes, and review the audit log.
Rotating without revoking leaves the compromised credential active.

## Suspected phishing or unauthorized access

1. Revoke affected sessions and keys.
2. Reset password from a trusted device.
3. Review recent users, roles, webhooks, and integrations.
4. Open a security ticket with approximate hours and IPs if available.
5. Do not delete related emails, logs, or messages.

An unrecognized change by an administrator or evidence of another tenant's data is classified as P1. An internal phishing simulation without actual compromise is managed according to the Security program.

## Audit log

Scale retains 180 days of audit log and Enterprise 365 days. Starter retains 30 days. The audit log
records login, role changes, key creation/revocation, SSO configuration, and integrations.
Events are exported in JSON; they cannot be edited from the product.
