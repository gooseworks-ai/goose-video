---
name: add-creative-to-adset
description: >
  Add a new creative variant to an existing Meta ad set for A/B testing.
  Supports both image and video creatives. Creates a new creative object and a
  new ad within the target ad set, starting PAUSED for review. Requires
  setup-meta-ads to be completed first.
tags: [ads, meta, creative, a/b testing]
---

## Overview

This skill adds a new creative variant to an existing ad set without touching
the campaign or ad set structure. It is the standard workflow for A/B creative
testing on Meta.

**What it does:**
1. Identifies the target ad set by name or ID
2. Gathers creative assets and copy
3. Creates a new creative object (image or video)
4. Creates a new ad in the ad set pointing to that creative
5. Starts the ad as PAUSED for review

---

## Prerequisites

- `meta-ads` CLI installed and authenticated
- `.env` with `ACCESS_TOKEN` and `AD_ACCOUNT_ID` sourced and exported
- `jq` and `curl` installed
- An existing campaign and ad set to add to

```
source .env
export ACCESS_TOKEN AD_ACCOUNT_ID
meta auth status
```

---

## Step 1 — Confirm Auth

```
meta auth status
source .env && export ACCESS_TOKEN AD_ACCOUNT_ID
```

---

## Step 2 — Identify the Target Ad Set

### List campaigns first:

```
meta -o json ads campaign list | jq '.[] | {id: .id, name: .name, status: .status}'
```

### Then list ad sets for a specific campaign:

```
meta -o json ads adset list $CAMPAIGN_ID | jq '.[] | {id: .id, name: .name, status: .status}'
```

Note the `ADSET_ID` you want to add the new creative to.

---

## Step 3 — Confirm Page ID

```
meta -o json ads page list | jq '.[] | {id: .id, name: .name}'
PAGE_ID=$(meta -o json ads page list | jq -r '.[0].id')
echo "Page ID: $PAGE_ID"
```

Use the Page that is already associated with the existing ads in this ad set
for consistency.

---

## Step 4 — Gather Creative Details

Collect these before running any commands:

| Field | Notes |
|---|---|
| Creative type | `image` or `video` |
| Image path | Local file path (`.jpg`, `.png`) |
| Video path | Local file path (`.mp4`) — video path only |
| Thumbnail path | Image file for video preview — video path only |
| Headline | ~40 chars recommended |
| Body text | ~125 chars recommended |
| Description | Optional — shown below headline in some placements |
| Link URL | Must be a valid `https://` URL |
| CTA button | Default: `LEARN_MORE` |
| Creative name | Internal label, e.g. "Summer — Image v2" |
| Ad name | Internal label, e.g. "Summer Sale US — Image v2" |

**CTA options:** `LEARN_MORE`, `SHOP_NOW`, `SIGN_UP`, `DOWNLOAD`, `GET_OFFER`,
`BOOK_TRAVEL`, `CONTACT_US`, `APPLY_NOW`, `GET_QUOTE`, `SUBSCRIBE`

---

## Step 5a — Create Image Creative and Ad

### Create the creative:

```
CREATIVE_ID=$(meta -o json ads creative create \
  --name "Your Creative Name" \
  --page-id $PAGE_ID \
  --image /path/to/image.jpg \
  --title "Your Headline" \
  --body "Your ad body copy." \
  --link-url "https://yoursite.com/landing" \
  --call-to-action LEARN_MORE \
  | jq -r '.[0].id')

echo "Creative ID: $CREATIVE_ID"
```

### Create the ad in the target ad set:

```
AD_ID=$(meta -o json ads ad create $ADSET_ID \
  --name "Your Ad Name" \
  --creative-id $CREATIVE_ID \
  | jq -r '.[0].id')

echo "Ad ID: $AD_ID"
```

---

## Step 5b — Create Video Creative and Ad (Graph API)

The CLI does not support video creative creation. Use the Graph API.

### Upload the video:

```
VIDEO_ID=$(curl -s \
  -F "name=Your Video Name" \
  -F "source=@/path/to/video.mp4" \
  "https://graph.facebook.com/v20.0/act_${AD_ACCOUNT_ID}/advideos?access_token=${ACCESS_TOKEN}" \
  | jq -r '.id')

echo "Video ID: $VIDEO_ID"
```

### Upload the thumbnail:

```
IMAGE_HASH=$(curl -s \
  -F "filename=@/path/to/thumbnail.jpg" \
  "https://graph.facebook.com/v20.0/act_${AD_ACCOUNT_ID}/adimages?access_token=${ACCESS_TOKEN}" \
  | jq -r '.images[].hash')

echo "Image Hash: $IMAGE_HASH"
```

### Create the video creative:

```
CREATIVE_ID=$(curl -s -X POST \
  "https://graph.facebook.com/v20.0/act_${AD_ACCOUNT_ID}/adcreatives" \
  -F "access_token=${ACCESS_TOKEN}" \
  -F "name=Your Video Creative Name" \
  -F 'object_story_spec={"page_id":"'"$PAGE_ID"'","video_data":{"video_id":"'"$VIDEO_ID"'","image_hash":"'"$IMAGE_HASH"'","title":"Your Headline","message":"Your body copy.","call_to_action":{"type":"LEARN_MORE","value":{"link":"https://yoursite.com/landing"}}}}' \
  | jq -r '.id')

echo "Creative ID: $CREATIVE_ID"
```

### Create the ad:

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

## Step 6 — Confirm and Optionally Activate

### Confirm the new ad was created:

```
meta -o json ads ad list $ADSET_ID | jq '.[] | {id: .id, name: .name, status: .status}'
```

### Activate when ready:

```
meta ads ad update $AD_ID --status ACTIVE
```

Or keep it PAUSED and activate manually in Ads Manager after review.

---

## Creative Review Process

New creatives go through Meta's review process:

- **IN_PROCESS** — under review, typically 15 minutes to 24 hours
- **APPROVED** — cleared, ad can deliver
- **DISAPPROVED** — policy violation; check the rejection reason in Ads Manager

Check review status:

```
meta -o json ads ad list $ADSET_ID | jq '.[] | {id: .id, name: .name, status: .status, review_feedback: .review_feedback}'
```

---

## Gotchas

| Gotcha | Details |
|---|---|
| JSON arrays | CLI always returns arrays — use `.[0].id`, not `.id` |
| No `--instagram-actor-id` | Obsolete flag; rejected by the API. Instagram inferred from Page |
| Video needs thumbnail | Graph API required for video; no CLI shortcut |
| Budget inherited from ad set | You are adding an ad, not changing budget |
| Creative review delay | New creatives may sit in IN_PROCESS for up to 24h |
| Budgets in cents | Reminder: $20/day = 2000. Relevant if you later adjust ad set budget |

---

## Quick Reference

```
# List campaigns
meta -o json ads campaign list | jq '.[] | {id, name, status}'

# List ad sets in a campaign
meta -o json ads adset list $CAMPAIGN_ID | jq '.[] | {id, name, status}'

# List ads in an ad set
meta -o json ads ad list $ADSET_ID | jq '.[] | {id, name, status}'

# Create image creative
CREATIVE_ID=$(meta -o json ads creative create --name "Name" --page-id $PAGE_ID --image /path.jpg --title "Headline" --body "Body" --link-url "https://example.com" --call-to-action LEARN_MORE | jq -r '.[0].id')

# Add ad to ad set
AD_ID=$(meta -o json ads ad create $ADSET_ID --name "Ad Name" --creative-id $CREATIVE_ID | jq -r '.[0].id')

# Activate
meta ads ad update $AD_ID --status ACTIVE
```
