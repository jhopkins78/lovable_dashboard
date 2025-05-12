# Connector Prioritization Roadmap

This roadmap prioritizes third-party platforms for connector development based on data value (LTV, funnel insights, spend signals), industry adoption, and API accessibility.

| Rank | Platform         | API Link                                              | Data Type(s)                        | Suggested Use Case in Lead Commander/Samaritan AI         |
|------|------------------|------------------------------------------------------|-------------------------------------|-----------------------------------------------------------|
| 1    | HubSpot          | https://developers.hubspot.com/docs/api/overview     | CRM, contacts, deals, activities    | Lead enrichment, funnel analytics, LTV estimation         |
| 2    | Stripe           | https://stripe.com/docs/api                          | Payments, subscriptions, invoices   | Revenue tracking, churn prediction, LTV, spend signals    |
| 3    | Shopify          | https://shopify.dev/docs/api                         | Orders, customers, products         | E-commerce funnel, cohort analysis, LTV, segmentation     |
| 4    | Facebook Ads     | https://developers.facebook.com/docs/marketing-api/  | Ad spend, leads, campaign metrics   | Ad ROI, lead source attribution, spend optimization       |
| 5    | Google Ads       | https://developers.google.com/google-ads/api/docs    | Ad spend, conversions, keywords     | Ad ROI, funnel attribution, spend optimization            |
| 6    | Salesforce       | https://developer.salesforce.com/docs/apis           | CRM, opportunities, activities      | Enterprise lead scoring, pipeline analytics               |
| 7    | QuickBooks       | https://developer.intuit.com/app/developer/qbo/docs  | Invoices, payments, expenses        | Financial health, LTV, spend signals                      |
| 8    | Intercom         | https://developers.intercom.com/intercom-api         | Conversations, users, events        | Engagement scoring, support funnel, retention analysis    |
| 9    | Zendesk          | https://developer.zendesk.com/api-reference/         | Tickets, users, satisfaction        | Support funnel, churn signals, customer health            |
| 10   | Marketo          | https://developers.marketo.com/rest-api/             | Leads, campaigns, engagement        | Marketing funnel, lead nurturing, attribution             |

**Selection Criteria:**
- **Data Value:** Platforms that provide high-value signals for LTV, funnel progression, or spend.
- **Industry Adoption:** Widely used in B2B/B2C SaaS, e-commerce, and marketing.
- **API Access:** Public, well-documented APIs with robust data models.

**Next Steps:**
- Start with HubSpot, Stripe, Shopify, Facebook Ads, and Google Ads for maximum impact.
- Build modular connector agents for each, following the pattern established in `connector_agent.py`.
- Expand to Salesforce, QuickBooks, Intercom, Zendesk, and Marketo as roadmap progresses.
