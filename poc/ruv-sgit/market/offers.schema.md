# site/data/offers.json: the catalogue the shop, the business pages and the business-model article all read

```
{ "updated": "2026-10-15", "currency": "GBP", "contact": "agent@riskmandate.ai",
  "assumptions": { "fx_usd_per_gbp": 1.30, "model_prices_usd_per_mtok": {…}, "ec2_usd_per_hour": {…}, "notes": ["…"] },
  "groups": [
    { "id": "runs", "title": "…", "summary": "one or two sentences", "who": "who buys this",
      "map": "runs",                              // id of its Wardley map in site/data/maps.json
      "items": [
        { "id": "run-s", "name": "…", "price": 5, "unit": "per run",   // price in GBP, excl. VAT
          "summary": "one line",
          "details": ["1 queen + 5 workers", "up to 1M tokens (Sonnet 5.5) …", "…"],   // shown as a list
          "options": [ { "id": "key", "label": "Model key",
                         "choices": [ { "id": "ours", "label": "Our key (tokens included)", "delta": 0 },
                                      { "id": "byok", "label": "Bring your own key", "delta": -3 } ] } ],
          "max_qty": 50 } ] } ] }
```
Rules: every price is a number in GBP excluding VAT; "delta" is added to the item price for that choice; an item with "price": null is "priced on request" (the shop still lets it be ordered). The shop does not take payment: it emails the order to "contact".
