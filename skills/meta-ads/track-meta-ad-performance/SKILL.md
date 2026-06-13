---
name: track-meta-ad-performance
description: >
  Pull Meta ad performance data and present a readable report. Asks scope (account /
  campaign / ad set / ad), date range, metrics, and optional breakdowns. Outputs a
  human-friendly summary with totals, per-row metrics, efficiency signals (CTR, CPC,
  frequency) and flagged anomalies. Run after any campaign has been live for at least
  a few hours.
tags: [ads, meta, analytics]
---

# track-meta-ad-performance

You're pulling and presenting Meta ad insights. The user shouldn't have to think about API field names or formatting — your job is to ask the right scope/date/metric questions, run the right `meta ads insights get` query, and turn the raw JSON into a clean readable report.

## Prerequisites

```bash
meta auth status >/dev/null && echo OK
[[ -f .env ]] && set -a && source .env && set +a
```

If `meta auth status` fails, stop and run the **setup-meta-ads** skill first.

## Step 1: Determine scope

Ask the user — accept any of:
- "the whole account" → no entity filter
- A campaign / ad set / ad name → look up the ID and confirm match
- A direct ID → use as-is

Look up by name when needed:
```bash
meta -o json ads campaign list | jq -r '.[] | "\(.id)  \(.name)  [\(.effective_status)]"'
```

Don't make the user copy-paste IDs. Do the lookup yourself.

## Step 2: Determine date range

Default: `last_7d`. Offer these presets:
- `today`, `yesterday`
- `last_3d`, `last_7d` (default), `last_14d`, `last_30d`, `last_90d`
- `this_month`, `last_month`
- Custom: `--since YYYY-MM-DD --until YYYY-MM-DD`

## Step 3: Determine metrics

Default fields (good for most campaigns):
```
spend,impressions,clicks,ctr,cpc,reach,frequency
```

Add based on campaign objective:
- Traffic / link-click campaigns: `inline_link_clicks,cost_per_inline_link_click`
- Conversion campaigns: `actions,action_values,cost_per_action_type`
- Awareness: `cpm`
- Video campaigns: `video_thruplay_watched_actions,video_avg_time_watched_actions`

Fetch the objective automatically: `meta -o json ads campaign get <ID>`

## Step 4: Breakdown (optional)

Only ask if the user wants to slice the data. Available breakdowns:
- `age`, `gender`, `country`
- `publisher_platform` (Facebook vs Instagram vs Audience Network vs Messenger)
- `platform_position` (feed, stories, reels — most useful for Advantage+ campaigns)
- `device_platform`, `impression_device`

## Step 5: Time granularity

Default `all_days` (one total row). Options:
- `daily` — one row per day, good for trends
- `weekly`, `monthly` — for longer date ranges

## Step 6: Run the query

```bash
meta -o json ads insights get \
  [--campaign-id <ID> | --adset-id <ID> | --ad-id <ID>] \
  --date-preset <preset> \
  --fields spend,impressions,clicks,ctr,cpc,reach,frequency \
  [--breakdown <dim>] \
  [--time-increment <gran>] \
  --sort spend_descending \
  --limit 50 \
  > /tmp/insights.json
```

Show headline numbers immediately, then dive into details.

## Step 7: Format the report

Lead with the **summary**, then detail. Use tables for multi-row data. Format numbers cleanly:
- Spend: `$X.XX`
- Impressions: thousand separators (`12,345`)
- CTR: `X.XX%`
- CPC: `$X.XX`
- CPM: `$X.XX`

### Report template

```
# <Entity name> — <date range>

**Summary**: $X.XX spent · X impressions · X clicks · X.X% CTR · $X.XX CPC
<one-sentence interpretation>

## Detail

[table or per-row summary]

## Notes
- <flagged anomalies — see Step 8>
```

## Step 8: Surface anomalies

Auto-flag the following (one short bullet each, only if relevant):

- **No spend** despite ACTIVE → ad still in `IN_PROCESS` review, or budget too low
- **CTR < 0.5%** → creative likely not resonating; suggest a variant test
- **CTR > 2.5%** → creative working well; suggest scaling budget
- **CPC > $5** (B2B) or **> $2** (consumer) → audience too narrow, or creative weak
- **Frequency > 3** in a 7-day window → audience saturating; broaden or refresh creative
- **Spend ≈ budget every day** → budget-constrained; consider raising if performance is good
- **All spend on one placement** (only visible with `--breakdown platform_position`) → consider whether to split-test or add platform-specific creative

## Step 9: Offer follow-ups

After the report, suggest 2–3 next moves:
- "Want me to break this down by placement (IG vs FB vs Reels)?"
- "Want to compare last 7 days vs the prior 7?"
- "Want to add a creative variant?"

## Gotchas

- Insights data has a **30–60 minute lag** for live campaigns; today's numbers are always partial.
- `effective_status: IN_PROCESS` ads have $0 spend — that's expected while Meta reviews them.
- `--fields` takes a comma-separated string, not repeated flags.
- Output is a JSON array. `all_days` + no breakdown = one row. Breakdowns or daily = multiple rows.
- Parse IDs with `.[0].id` — the CLI always returns arrays.
