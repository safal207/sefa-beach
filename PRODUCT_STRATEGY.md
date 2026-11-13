# Sefa Beach — product/revenue plan | 2026-11-13

## Decision
Improve the guest's path through a digital QR menu without pretending that the demo already takes payments or records completed orders. Optimize real restaurant contribution profit only once the owner provides POS order lines and verified variable costs.

## Product lenses

| Lens | Borrow the pattern | Sefa Beach implementation / next step | Measure when connected to POS |
| --- | --- | --- | --- |
| ClickFunnels | One clear action per step | Discover menu → find a dish → select → show selection to waiter; avoid mock payment screen | QR scans → POS-confirmed orders (needs correlation) |
| SamCart | Relevant optional order bump | One-tap non-discount additions in cart, never auto-insert or fake scarcity; show actual final price | Add-on attach rate and contribution profit after COGS |
| Duolingo | Small guided choices, immediate feedback | Quick choice by occasion: breakfast, seafood, kids, drinks, pizza; search and favourites remain available | Search success, menu navigation, abandonment |
| Dodo Pizza | Product operations and trustworthy menu | Owner-approved prices, photos, availability, food cost and POS linkage | Contribution per dish, AOV, production capacity, refunds |

These are adaptations, not proprietary design copies, results from A/B tests, or revenue guarantees.

## Measurement contract

1. **Actual order:** only an accepted/paid order in restaurant POS or reconciled sales book. A click on `copy order` is not a sale.
2. **Order value (AOV):** sum of net paid revenue after discounts/refunds / count of distinct completed orders.
3. **Dish contribution:** `qty × paid_unit_price - line_discount - line_refund - qty × (ingredient_cost + packaging_cost) - payment_fee`. For true profit add tax, payroll, rent, utilities, overhead allocation, waste and operational details.
4. **Add-on attach rate:** completed orders with the relevant add-on / completed orders eligible for that add-on. Show absolute order counts next to rate.
5. **Uplift experiment:** compare before/after or randomize suggestion type while controlling for time-of-day/week, channel and relevant traffic; do not claim causality from raw percentage changes.
6. **Funnel diagnostics:** QR opens → menu item views → add-to-list → list presented to staff → POS order accepted. Presentation and POS order need reconciliation; otherwise report separate proxy and sales metrics.

## Prioritization

**P0: trust + content.** Confirm 5 missing prices, 123 items, real photos/licenses, allergens, address. Using 14 illustrative photo buckets for 123 dishes does not support item-level product trust.

**P1: discovery & optional pairing.** Already implemented in refreshed `index.html`: five quick options, contextual pairing, no fake discounts, incremental 12-item loading, TR/EN/RU.

**P2: economics.** Import actual sales lines into `revenue-dashboard-local.html`, verify order IDs and variable costs. No simulated revenue is treated as observed.

**P3: owner operations.** Add photo/price/availability admin and POS export/import only after owner agreement. Set up analytics respecting Turkish KVKK, explicit data minimization and retention rules.

## Release guardrail
Do not call the menu an official Sefa Beach site, post real sales files publicly, activate payment, or claim sales/performance improvement without verified authority, POS integration and tests. Preserve `noindex,nofollow` until the business approves.