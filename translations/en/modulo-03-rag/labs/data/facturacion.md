---
doc_id: facturacion
title: Billing and Payments
version: 3.6
effective_from: 2026-05-01
owner: Finance Operations
---

# Billing and Payments

## Cycle and Documents

Monthly plans are billed at the start of each period. Annual plans are billed in advance unless a different Enterprise agreement applies. Invoices are generated in UTC and appear in Billing > Invoices within a maximum of two hours from the charge.

The PDF is the fiscal document. The card receipt does not replace the invoice. Issued invoices are not edited: a fiscal correction is made via credit note and new invoice.

## Fiscal Data

Changes to legal entity name, address, or VAT ID apply to future documents. To correct an already issued invoice, open a billing ticket and specify the number and correct data. Finance verifies the request before issuing a credit note.

EU customers with a valid VAT ID may receive reverse charge when applicable. Validation is not automatically retroactive. Special exemptions require a valid certificate and Finance review.

## Methods and Retries

Starter and Scale accept cards. Enterprise can pay by wire transfer if specified in the contract. When a card fails, retries are performed on days 1, 3, and 7 from the due date. During this period, the account shows status `past_due` but is not suspended immediately.

If payment remains pending after the last retry, the administrator is notified and a seven-day grace period begins. Suspension limits new ingestion but allows exporting existing data during the window. Finance can adapt the process in Enterprise contracts.

## Duplicate and Unrecognized Charges

A duplicate charge is investigated by comparing the invoice ID, payment intent, amount, and timestamp. No refund is promised until it is verified that it is not a temporary bank authorization. An active unrecognized charge is marked as P3 priority for internal support, equivalent to urgent, and escalated to Finance/Security; the user must also contact their financial institution if they suspect card fraud.

NebulaOps never requests the full card number or CVV. Support uses the last four digits and the payment ID.

## Refunds

Starter and Scale can request a refund for a renewal within 14 days if there was no material usage afterward. Initial fees and professional services follow the contracted terms. Enterprise is governed by contract. An approved refund typically takes between 5 and 10 business days to reflect, depending on the banking institution.

## Downloads and Recipients

Administrators and Billing roles can download invoices. A maximum of five additional recipients can be configured in Billing > Notifications. Adding a recipient does not grant them access to the tenant or historical invoices; they only receive new ones via email.
