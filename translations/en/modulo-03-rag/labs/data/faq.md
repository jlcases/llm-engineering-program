---
doc_id: faq
title: NebulaOps Frequently Asked Questions
version: 6.0
effective_from: 2026-08-01
owner: Customer Education
---

# Frequently Asked Questions

## Can I try NebulaOps?

There is a 14-day trial of the Scale plan, limited to 20 users and 500,000 daily events. No credit card is required. Upon expiration, the tenant enters read-only mode for seven days; it is then deleted if a plan is not purchased.

## How do I verify a webhook?

Use the test delivery from Integrations > Webhooks. Verify `X-Nebula-Signature` on the unmodified body and respond with a 2xx status code in less than five seconds. The receiver must deduplicate by `event_id` because delivery is at-least-once.

## What time zone does the product use?

Events are stored in UTC. Each user can choose a display time zone; this does not alter the original timestamp or the daily ingestion limits, which reset at 00:00 UTC.

## How do I export more than 100,000 rows?

Select asynchronous export. You will receive a notification when the job completes and a signed link valid for 24 hours. Scale and Enterprise plans can choose CSV or Parquet.

## Can information be recovered after reducing retention?

During the seven-day grace window, you can cancel the change. After deletion, increasing retention does not recover data. A backup does not function as a client-queryable archive.

## Where do I see administrative changes?

Security > Audit log shows logins, roles, keys, SSO, and integrations. Retention depends on the plan: 30 days for Starter, 180 for Scale, and 365 for Enterprise.

## What do I do if the dashboard is slow?

Check the status page and temporarily reduce the time range. If it persists, open a ticket with the dashboard URL, time range, region, and approximate time. Do not attach tokens or cookies.

## Does NebulaOps offer a native mobile app?

No. The web interface is responsive, and alerts are received via integrations. The documentation does not announce a date for a mobile app.
