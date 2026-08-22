---
doc_id: handbook
title: NebulaOps Operations Handbook
version: 3.2
effective_from: 2026-07-01
owner: People Operations
---

# Operations Handbook

## Schedule and Coverage

NebulaOps operates the service 24 hours a day, but standard human support is available Monday through Friday from 08:00 to 18:00 Europe/Madrid time, excluding Spanish national holidays. Priority support for Scale and Enterprise plans adds 24-hour P1 incident response. Business and billing inquiries are not considered P1 and are answered during standard hours.

The primary support language is Spanish. Enterprise can contract English-language support. Response times are measured within the plan's coverage window, except for P1 incidents with 24/7 support.

## First Response Objectives

| Plan | P1 | P2 | P3 |
|---|---:|---:|---:|
| Starter | 4 business hours | 1 business day | 2 business days |
| Scale | 30 min, 24/7 | 4 business hours | 1 business day |
| Enterprise | 15 min, 24/7 | 2 business hours | 8 business hours |

These times are first response objectives, not resolution times. Resolution time depends on the cause and is communicated in each incident update.

## On-Call and Human Escalation

The engineering on-call person handles automatic technical alerts. The Support Lead receives customer escalations and determines whether the case meets P1 or P2 severity according to the incident runbook. A P1 must have an assigned Incident Commander; support does not make direct changes in production.

The primary on-call rotation changes on Mondays at 10:00 Europe/Madrid. A secondary person is available for absences or lack of acknowledgment. If the primary person does not acknowledge a P1 alert within five minutes, the system automatically notifies the secondary person.

## Authorized Channels

- Support portal: recommended channel; preserves identity, tenant, and traceability.
- Email: creates a ticket, but account actions require subsequent verification in the portal.
- Product chat: guidance only; does not accept sensitive attachments.
- Phone: Enterprise-only for P1 incidents; the number appears in the contract.

NebulaOps never requests passwords, MFA codes, full API keys, or full card numbers through any channel.

## Data protection in support

Tickets are retained for 24 months for audit and service improvement purposes. Attachments are
removed after 90 days unless linked to an open security investigation. The customer may request
export or deletion according to contract and regulations; Security reviews
conservation exceptions.

Agents must redact tokens, cookies, passwords, and payment data before escalating a ticket.
Shared logs must not exceed the necessary time window nor include data from other
tenants.

## Changes and maintenance

Planned maintenance is announced at least 72 hours in advance on the status page.
Ordinary windows are Wednesdays between 22:00 and 00:00 Europe/Madrid. An urgent security change
can be performed outside the window with approval from the Incident Commander and the Security
Lead; an explanation is published afterward.
