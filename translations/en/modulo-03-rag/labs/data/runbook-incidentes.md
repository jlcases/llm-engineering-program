---
doc_id: runbook-incidentes
title: Production Incident Runbook
version: 4.4
effective_from: 2026-07-14
owner: Site Reliability Engineering
---

# Incident Runbook

## Severities

### P1 — Critical

General outage, confirmed data loss or exposure, cross-tenant access, or a critical function unavailable without an alternative for a material portion of customers. A reasonable suspicion of exposure is treated as P1 until ruled out.

### P2 — High

Significant degradation or a major feature broken with a partial workaround. Affects multiple customers or blocks a major workflow, but there is no confirmed loss/exposure or general outage.

### P3 — Normal

Limited impact, cosmetic defect, inquiry, or issue with a clear workaround. Managed in the standard backlog.

Severity describes current impact, not technical difficulty or the customer's commercial importance.

## First 15 Minutes of a P1

1. The on-call person acknowledges the alert within five minutes.
2. Declares the incident and assigns an Incident Commander within ten minutes of the alert.
3. Opens a private coordination channel and a chronological document.
4. Designates a Communications Lead; the Incident Commander does not draft updates while coordinating.
5. Publishes the first external update within 15 minutes, even if the cause is still unknown.
6. Evaluates reversible containment before seeking the perfect root cause.

If the primary does not respond within five minutes, page the secondary. If they still do not respond within another five minutes, escalate to the on-call Engineering Manager.

## Communication

During a P1, the status page is updated at least every 30 minutes. Each message includes observed impact, ongoing actions, and the time of the next update. Do not publish a cause without evidence. Affected Enterprise customers also receive an update via their contractual channel.

For P2, the external cadence is every 60 minutes when there is visible impact. P3 does not require a status page.

## Containment and changes

Emergency changes require approval from the Incident Commander and a second technical person. Log the command/change, author, time, result, and rollback plan. Break-glass credentials are temporary, audited, and revoked when closing the response phase.

Do not delete logs, queues, or snapshots during an investigation. If there is storage pressure, expand capacity or export in a controlled manner.

## Closure and postmortem

An incident is resolved when the impact ends and metrics confirm stability for at least 30 minutes. The Incident Commander may extend this window. Closing the status page does not equate to completing the investigation.

Every P1 has a blameless postmortem published internally within five business days. It must include timeline, impact, detection, contributing factors, what worked, what failed, and actions with owner and date. P2 requires a postmortem if it lasted more than two hours, repeated, or the Incident Commander requests it.

## Minimum evidence

- ID and UTC timestamps;
- relevant metrics and logs with stable links;
- decisions and approvals;
- affected customers/tenants without including unnecessary PII;
- changes and rollback;
- published external messages;
- follow-up tasks.
