---
name: explain-meta-ad-setup
description: >
  Explain how a Meta campaign / ad set / ad is configured — high-level summary, then
  layered details for each level (settings, status, creative, performance). Skimmable
  with short paragraphs and bullets. Use when you want to understand what a campaign
  is doing, or to audit something before making changes.
tags: [ads, meta, audit]
---

# explain-meta-ad-setup

You're producing a clear, skimmable explanation of a Meta ad setup. The user wants to understand the structure and current state at a glance — enough detail to make decisions, without wading through raw JSON.

## Prerequisites

```bash
meta auth status >/dev/null && echo OK
[[ -f .env ]] && set -a && source .env && set +a
```

If `meta auth status` fails, stop and run the **setup-meta-ads** skill first.

## Step 1: Identify the entity

Ask the user — accept any of:
- A name (e.g., "Summer Sale campaign")
- A direct ID
- "everything in the account" → list all campaigns and recurse

Look up by name:
```bash
meta -o json ads campaign list | jq -r '.[] | "\(.id)  \(.name)  [\(.effective_status)]"'
```

Confirm the match before fetching details.

## Step 2: Walk the tree

For a **campaign**, fetch:
1. The campaign: `meta -o json ads campaign get <ID>`
2. Its ad sets: `meta -o json ads adset list <CAMPAIGN_ID>`
3. For each ad set, its ads: `meta -o json ads ad list <ADSET_ID>`
4. For each ad, its creative: `meta -o json ads creative get <CREATIVE_ID>`

For an **ad set**: skip campaign fetch, start from step 2.
For a single **ad**: fetch the ad + creative + parent ad set + parent campaign for context.

In parallel, pull last-7-day performance:
```bash
meta -o json ads insights get \
  --campaign-id <ID> \
  --date-preset last_7d \
  --fields spend,impressions,clicks,ctr,cpc,reach,frequency,cpm
```

Use `--adset-id` or `--ad-id` when the entity is lower in the tree.

## Step 3: Format the report

Keep paragraphs to 2 sentences max. Lead with a one-sentence elevator pitch of what this campaign is *doing*.

```markdown
# <Campaign Name>

**TL;DR**: <one sentence — what this campaign does, current status, last 7d spend/CTR>

**Overall status**: ACTIVE / PAUSED / IN_PROCESS — <one-line interpretation>

---

## Campaign — <name> (`<id>`)

<2-sentence description: objective, what it's optimizing toward>

- **Objective**: OUTCOME_TRAFFIC (drives link clicks to a destination URL)
- **Status**: ACTIVE
- **Daily budget**: $X (campaign-level CBO) or none
- **Created**: <date>

## Ad set — <name> (`<id>`)

<2-sentence description: who it targets, how it bids>

- **Optimization**: LINK_CLICKS
- **Billing event**: IMPRESSIONS
- **Daily budget**: $X.XX
- **Bid**: $X.XX cap (or "auto-bid" if none set)
- **Targeting**: Countries: US · Age: 18–65 · Advantage+ expansion: ON
- **Status**: ACTIVE

## Ads

| Name | Status | Creative | Spend (7d) | CTR | CPC |
|---|---|---|---|---|---|
| Ad name v1 | ACTIVE | Creative v1 | $X.XX | X.X% | $X.XX |

## Creatives

### Creative v1 (`<creative-id>`)
- **Headline**: "..."
- **Body**: "..."
- **CTA**: LEARN_MORE → https://...
- **Image**: 1200×628 jpg (1.91:1) — fits feed

---

## Performance — last 7 days

**Top-line**: $X spent · X impressions · X clicks · X.X% CTR · $X.XX CPC

<one-paragraph interpretation: is it pacing budget, CTR vs benchmarks, standout, what looks off>

## Watch items
- <flag any concerns — see Step 4>
```

## Step 4: Surface watch items

Auto-flag the following (one bullet each, only if relevant):

**Configuration issues:**
- Campaign ACTIVE but ad set or ad PAUSED → tree won't deliver; note which level is the bottleneck
- All ads in `IN_PROCESS` for >24h → ad review may be stuck; suggest checking Ads Manager for rejection reasons
- Daily budget < $5 → Meta delivery is unstable below this; suggest raising
- Targeting only one country but creative copy references other markets → mismatch

**Performance issues** (only if 7d spend > $20):
- CTR < 0.5% → creative likely failing; suggest a variant test
- CPC > $5 (B2B) or $2 (B2C) → audience too narrow, or creative weak
- Frequency > 3 in 7 days → audience saturating; broaden or refresh creative
- Spend ≈ budget every day → budget-constrained; consider scaling if performance is good

## Step 5: Offer next moves

End the report with 2–3 actionable suggestions tailored to what you found:
- "Add a creative variant" → add-creative-to-adset skill
- "Get a placement-level breakdown" → track-meta-ad-performance with `--breakdown platform_position`
- "Refine targeting" → CLI only supports country targeting; use Ads Manager UI for age/interests/lookalikes

## Gotchas

- `meta -o json` returns arrays; parse with `.[0]` for single-resource gets.
- `effective_status` ≠ `status`. `status: PAUSED` is the user's intent; `effective_status` is Meta's runtime state (`IN_PROCESS`, `DISAPPROVED`, etc.). Show both if they differ.
- The CLI's targeting field is a stringified JSON blob — parse it with jq if you need to surface specifics.
- Don't dump raw JSON. Distill it into plain language.
- Don't editorialize beyond what the data shows. If CTR is 1.2%, say "around the B2B benchmark" — don't call it a winning campaign.
