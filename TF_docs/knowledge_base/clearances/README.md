# Clearance History

This directory contains historical clearance data for rights negotiations and fee structures.

## File Organization

- `by_artist/` - Clearance history organized by artist
- `by_label/` - Clearance history organized by label/publisher
- `by_usage/` - Clearance history organized by usage type
- `fee_benchmarks.json` - General fee benchmarks by tier

## Clearance Record Format

```json
{
  "id": "CLR-2024-001",
  "date": "2024-01-15",
  "track": {
    "title": "Track Name",
    "artist": "Artist Name",
    "label": "Label Name",
    "publisher": "Publisher Name",
    "year": "Release Year"
  },
  "usage": {
    "client": "Client Name",
    "media": ["TV", "Online"],
    "territory": "North America",
    "term": "1 year",
    "campaign_type": "Product Launch"
  },
  "negotiation": {
    "initial_quote": 50000,
    "final_fee": 42000,
    "sync_fee": 21000,
    "master_fee": 21000,
    "negotiation_rounds": 2,
    "days_to_clear": 5
  },
  "contacts": {
    "rights_holder": "Contact Name",
    "email": "contact@email.com",
    "response_time": "24 hours"
  },
  "notes": "Additional context or special terms"
}
```

## Fee Benchmark Structure

```json
{
  "synch_a": {
    "budget_range": "0-5000",
    "typical_sync": "1000-2500",
    "typical_master": "1000-2500",
    "margin": 0.5
  },
  "synch_b": {
    "budget_range": "5000-50000",
    "typical_sync": "5000-25000",
    "typical_master": "5000-25000",
    "margin": 0.4
  },
  "synch_c": {
    "budget_range": "50000+",
    "typical_sync": "25000+",
    "typical_master": "25000+",
    "margin": 0.3
  }
}
```

## Key Insights to Track

1. **Response Times** - How quickly different rights holders respond
2. **Negotiation Patterns** - Typical discount percentages
3. **Territory Premiums** - Additional costs for worldwide rights
4. **Media Premiums** - Cost differences between TV/Online/Radio
5. **Quick Clearers** - Rights holders who clear quickly
6. **Difficult Clearances** - Artists/labels that are hard to clear