# Sefa Beach — local smoke test (2026-11-13)

## Scope
- Source: locally generated `index.html`, based on the available older HTML snapshot (07.11.2026), not a verified mirror of the 08.11.2026 live site.
- Engine: locally installed Chromium, Playwright, `page.set_content` with external network resources blocked.
- Viewports: 320×640, 390×844, 1440×900.
- 53 discrete assertions PASS: initial 12 cards, language EN→RU→TR, category and quick filters, paging, search, missing-price disablement, non-overflow at each viewport, local cart total, recommendation visibility, copy feedback, no runtime script errors; offline revenue dashboard validated against a **test fixture**, not actual sales.

## Verification limits
- Browser navigation to both `127.0.0.1` and `file://` was blocked by the testing environment. Testing therefore used DOM HTML insertion, **not deployment smoke**.
- External font and Unsplash image requests were blocked, so actual remote asset loading and image visual correctness are not verified.
- Firefox, Safari, Microsoft Edge, iOS devices, Android devices, POS and payments have not been tested.
- The dashboard test fixture was: 2 orders, TRY 270 net revenue, TRY 135 average order value, TRY 185 contribution after explicitly entered variable costs. These are **synthetic QA numbers**, not business metrics.

## Open release blockers
1. GitHub repository `safal207/sefa-beach` is currently not found; cannot claim remote publication.
2. Photographer/source rights and matching food photos not confirmed.
3. Five menu prices, current stock, allergens and owner approval not confirmed.
4. Official site and public map disagree on neighborhood/opening hours; verify directly with restaurant.
5. Real analytics require POS transaction data and cost inputs.