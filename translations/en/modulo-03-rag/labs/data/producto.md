---
doc_id: producto
title: NebulaOps Catalog and Limits
version: 5.1
effective_from: 2026-08-01
owner: Product Operations
---

# Product, Plans, and Limits

## Starter Plan

The Starter plan includes up to 10 users, 30 days of metrics retention, five dashboards, and 100,000
ingested events per day. It allows for email alert integration. It does not include SSO SAML,
private environments, or 24/7 incident support.

## Scale Plan

The Scale plan includes up to 100 users, 180 days of retention, unlimited dashboards, and five million
events per day. It includes SSO SAML, webhooks, Slack, Microsoft Teams, PagerDuty, and P1 24/7 support. The
API allows 600 requests per minute per tenant with bursts of up to 60 requests in one second.

## Enterprise Plan

The Enterprise plan does not set a contractual user limit: capacity and price are agreed upon. It offers configurable
retention between 365 and 730 days, dedicated regions, PrivateLink, customer-managed keys, and P1 24/7 support
with a first response time target of 15 minutes. The API quota is defined in the contract and may exceed
that of the Scale plan after a load test.

## Regions and Residency

The standard multi-tenant service is available in `eu-west-1` (Ireland) and `us-east-1`
(Virginia). A tenant chooses a region upon creation, and NebulaOps does not replicate its telemetry data between
regions. Changing regions requires a migration project; there is no self-service button.

Backups remain in the tenant's same logical region. Enterprise can contract a dedicated
region among those offered in its contract. Public documentation does not promise availability in
Asia-Pacific.

## Ingestion and Retention

Daily limits are calculated in UTC. Events that exceed the limit are rejected with HTTP 429
and are not queued for the next day. The response includes `Retry-After` when the limit is
temporary; upon exhausting the daily quota, the dashboard displays the reset date.

Retention reduction first removes data that exceeds the new period after a
seven-day grace window. Increasing retention does not recover already deleted data.

## Exports

Synchronous CSV supports a maximum of 100,000 rows. Larger exports run as a job and generate
a signed link valid for 24 hours. Links cannot be renewed; you must rerun the job.
The Parquet format is available on Scale and Enterprise.

## Integrations

Webhooks are delivered at least once, so the receiver must deduplicate by `event_id`.
NebulaOps retries 5xx responses or timeouts for 24 hours with exponential backoff. It does not retry
2xx or 4xx responses, except 429 when it contains a valid `Retry-After`.

Each webhook endpoint can configure a signature secret. The `X-Nebula-Signature`
header contains the HMAC-SHA256 of the exact body; you must verify it before parsing JSON.

## Availability

The monthly contractual SLA is 99.9% for Scale and 99.95% for Enterprise. Starter has no economic SLA.
Maintenance announced with 72 hours and contractual exclusions do not count according to the
terms of each plan.
