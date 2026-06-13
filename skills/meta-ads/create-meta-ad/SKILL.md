---
name: create-meta-ad
description: >
  Create a complete Meta advertising campaign from scratch — campaign,
  ad set, creative, and ad — through a conversational flow. Supports both
  image and video creatives. Defaults to PAUSED status so you can review
  everything before spending money. Requires setup-meta-ads to be completed first.
tags: [ads, meta, campaign, creative]
---

## Overview

This skill creates a full Meta ad campaign end-to-end:

1. **Campaign** — objective, name
2. **Ad Set** — budget, schedule, targeting, optimization
3. **Creative** — image or video with headline, body, link, CTA
4. **Ad** — ties creative to ad set, starts PAUSED

---

## Prerequisites

- `meta-ads` CLI installed and authenticated (`meta auth status` passes)
- `.env` with `ACCESS_TOKEN` and `AD_ACCOUNT_ID` sourced and exported
- `jq` installed
- For video creatives: `curl` (Graph API calls required)
- For conversion campaigns: a Meta Pixel ID (get it via `meta -o json ads dataset list | jq '.[].id'`)

```
source .env
export ACCESS_TOKEN AD_ACCOUNT_ID
meta auth status
```

---

## Information to Gather (Conversational Batches)

### Batch A — Campaign & Ad Set

Collect these before running any commands:

| Field | Default | Notes |
|---|---|---|
| Campaign name | (required) | e.g. "Summer Sale 2024" |
| Objective | `OUTCOME_TRAFFIC` | See objectives list below |
| Ad set name | (required) | e.g. "US 25-45 Broad" |
| Daily budget | `$20` = `2000` cents | All budgets in cents |
| Optimization goal | `LINK_CLICKS` | Must match objective |
| Billing event | `IMPRESSIONS` | Usually IMPRESSIONS |
| Targeting countries | `US` | Comma-separated ISO codes |
| Bid amount | (optional) | In cents; omit for auto-bidding |
| Pixel ID | (required for OUTCOME_SALES) | From dataset list |

**Supported Objectives:**
- `OUTCOME_TRAFFIC` — drive clicks to a URL
- `OUTCOME_AWARENESS` — reach and brand awareness
- `OUTCOME_ENGAGEMENT` — likes, comments, shares
- `OUTCOME_LEADS` — lead generation forms
- `OUTCOME_SALES` — conversions (requires Pixel)
- `OUTCOME_APP_PROMOTION` — app installs

**Optimization Goal / Billing Event pairings:**

| Objective | Optimization Goal | Billing Event |
|---|---|---|
| OUTCOME_TRAFFIC | LINK_CLICKS | IMPRESSIONS |
| OUTCOME_AWARENESS | REACH | IMPRESSIONS |
| OUTCOME_ENGAGEMENT | POST_ENGAGEMENT | IMPRESSIONS |
| OUTCOME_LEADS | LEAD_GENERATION | IMPRESSIONS |
| OUTCOME_SALES | OFFSITE_CONVERSIONS | IMPRESSIONS |

### Batch B — Creative

| Field | Default | Notes |
|---|---|---|
| Creative type | (image or video) | |
| Image path | (required for image) | Local file path |
| Video path | (required for video) | Local file path |
| Thumbnail path | (required for video) | Image file for video preview |
| Headline | (required) | ~40 chars recommended |
| Body text | (required) | ~125 chars recommended |
| Link URL | (required) | Must be a valid https:// URL |
| CTA button | `LEARN_MORE` | See CTA options below |

**Supported CTA Options:**
`LEARN_MORE`, `SHOP_NOW`, `SIGN_UP`, `DOWNLOAD`, `GET_OFFER`,
`BOOK_TRAVEL`, `CONTACT_US`, `APPLY_NOW`, `GET_QUOTE`, `SUBSCRIBE`

### Batch C — Ad

| Field | Default | Notes |
|---|---|---|
| Page ID | (auto-detect if only one page) | From `meta -o json ads page list` |
| Ad name | (required) | e.g. "Summer Sale — Image v1" |
| Ad status | `PAUSED` | Change to ACTIVE only after review |

Do **not** pass `--instagram-actor-id`. Instagram placement falls back to the
account linked to your Page automatically.

---

## Commands — Image Creative Path

Run these commands in sequence. Each captures the ID output for the next step.

### Step 1 — Create Campaign

```
CAMPAIGN_ID=$(meta -o json ads campaign create \
  --name "Your Campaign Name" \
  --objective OUTCOME_TRAFFIC \
  | jq -r '.[0].id')

echo "Campaign ID: $CAMPAIGN_ID"
```

### Step 2 — Create Ad Set

```
ADSET_ID=$(meta -o json ads adset create $CAMPAIGN_ID \
  --name "Your Ad Set Name" \
  --optimization-goal LINK_CLICKS \
  --billing-event IMPRESSIONS \
  --daily-budget 2000 \
  --targeting-countries US \
  | jq -r '.[0].id')

echo "Ad Set ID: $ADSET_ID"
```

For conversion campaigns, add `--pixel-id YOUR_PIXEL_ID`.
For optional bid cap, add `--bid-amount 150` (in cents).

### Step 3 — Create Creative (Image)

```
PAGE_ID=$(meta -o json ads page list | jq -r '.[0].id')

CREATIVE_ID=$(meta -o json ads creative create \
  --name "Your Creative Name" \
  --page-id $PAGE_ID \
  --image /path/to/your/image.jpg \
  --title "Your Headline Here" \
  --body "Your ad copy body text here." \
  --link-url "https://yoursite.com/landing-page" \
  --call-to-action LEARN_MORE \
  | jq -r '.[0].id')

echo "Creative ID: $CREATIVE_ID"
```

### Step 4 — Create Ad

```
AD_ID=$(meta -o json ads ad create $ADSET_ID \
  --name "Your Ad Name" \
  --creative-id $CREATIVE_ID \
  | jq -r '.[0].id')

echo "Ad ID: $AD_ID"
```

The ad is created as PAUSED by default. Review it in Ads Manager before activating.

---

## Commands — Video Creative Path

The CLI does not support video creative creation directly. Use the Graph API.

### Step 1 — Create Campaign and Ad Set

Same as image path above (Steps 1 and 2).

### Step 2 — Upload Video

```
VIDEO_ID=$(curl -s \
  -F "name=Your Video Name" \
  -F "source=@/path/to/your/video.mp4" \
  "https://graph.facebook.com/v20.0/act_${AD_ACCOUNT_ID}/advideos?access_token=${ACCESS_TOKEN}" \
  | jq -r '.id')

echo "Video ID: $VIDEO_ID"
```

### Step 3 — Upload Thumbnail

```
IMAGE_HASH=$(curl -s \
  -F "filename=@/path/to/thumbnail.jpg" \
  "https://graph.facebook.com/v20.0/act_${AD_ACCOUNT_ID}/adimages?access_token=${ACCESS_TOKEN}" \
  | jq -r '.images[].hash')

echo "Image Hash: $IMAGE_HASH"
```

### Step 4 — Create Video Creative

```
PAGE_ID=$(meta -o json ads page list | jq -r '.[0].id')

CREATIVE_ID=$(curl -s -X POST \
  "https://graph.facebook.com/v20.0/act_${AD_ACCOUNT_ID}/adcreatives" \
  -F "access_token=${ACCESS_TOKEN}" \
  -F "name=Your Video Creative Name" \
  -F 'object_story_spec={"page_id":"'"$PAGE_ID"'","video_data":{"video_id":"'"$VIDEO_ID"'","image_hash":"'"$IMAGE_HASH"'","title":"Your Headline","message":"Your body text.","call_to_action":{"type":"LEARN_MORE","value":{"link":"https://yoursite.com/landing-page"}}}}' \
  | jq -r '.id')

echo "Creative ID: $CREATIVE_ID"
```

### Step 5 — Create Ad

```
AD_ID=$(curl -s -X POST \
  "https://graph.facebook.com/v20.0/act_${AD_ACCOUNT_ID}/ads" \
  -F "access_token=${ACCESS_TOKEN}" \
  -F "name=Your Video Ad Name" \
  -F "adset_id=${ADSET_ID}" \
  -F "creative={\"creative_id\":\"${CREATIVE_ID}\"}" \
  -F "status=PAUSED" \
  | jq -r '.id')

echo "Ad ID: $AD_ID"
```

---

## Activating the Ad

After reviewing in Ads Manager:

```
meta ads ad update $AD_ID --status ACTIVE
```

Or activate the entire campaign:

```
meta ads campaign update $CAMPAIGN_ID --status ACTIVE
```

---

## Gotchas

| Gotcha | Details |
|---|---|
| JSON arrays | CLI always returns arrays — use `.[0].id`, never `.id` |
| Budgets in cents | $20/day = 2000. Always convert. |
| No `--instagram-actor-id` | This flag is rejected; Instagram is inferred from the Page |
| OUTCOME_SALES needs Pixel | Pass `--pixel-id` on ad set creation |
| Video needs thumbnail | Graph API upload only; no CLI shortcut |
| Ad starts PAUSED | Intentional — review before activating |
| App in dev mode | Flip to Live in FB Developers → App Dashboard |

---

## Quick Reference

```
# Auth check
source .env && export ACCESS_TOKEN AD_ACCOUNT_ID
meta auth status

# Get Page ID
meta -o json ads page list | jq -r '.[0].id'

# Get Pixel ID (for conversion campaigns)
meta -o json ads dataset list | jq '.[].id'

# Create campaign (OUTCOME_TRAFFIC)
CAMPAIGN_ID=$(meta -o json ads campaign create --name "Name" --objective OUTCOME_TRAFFIC | jq -r '.[0].id')

# Activate ad
meta ads ad update $AD_ID --status ACTIVE
```
