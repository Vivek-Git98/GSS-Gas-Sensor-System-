# Cloud Platform Cost Analysis — GSS

## Write Volume Calculation

- 8 sensors × 1 reading/second = **691,200 writes/day**
- 6-month deployment = **~124,416,000 total writes**

## Platform Comparison

| Platform             | Free Tier / Month | Paid Option      | 6-Month Verdict       |
|----------------------|-------------------|------------------|-----------------------|
| ThingSpeak Free      | ~246K writes      | Limited scale    | ❌ Far below requirement |
| ThingSpeak Standard  | ~2.7M writes      | Still limited    | ❌ Only 13% of need   |
| AWS IoT Core (Free)  | 500K writes       | ~$18 for 6 mo.  | ✅ Scalable, low cost  |
| Google Firebase Free | 600K writes       | Costly at scale  | ❌ Insufficient       |
| SensorCloud Free     | 25K writes        | 100K/month       | ❌ Far too small       |
| **Local InfluxDB**   | **Unlimited**     | **Hardware only** | ✅ **Recommended**    |

## Recommendation

For long-term, high-frequency deployment:
- **Local InfluxDB on Raspberry Pi** — zero per-write cost, full control
- **AWS IoT Core** — if cloud backup or multi-site aggregation is needed (~$18 for 6 months)
- Avoid free tiers of ThingSpeak / Firebase / SensorCloud for 1-second intervals
