---
name: setup-meta-ads
description: >
  Guide the user through end-to-end Meta Ads CLI setup. Installs the CLI if
  missing, walks through obtaining an access token, validates ad account and
  page access, and surfaces every common configuration failure with the exact
  fix. Run this before any other meta-ads skill.
tags: [ads, meta, setup]
---

## Overview

This skill gets the Meta Ads CLI (`meta`) fully configured and validated so
every downstream workflow works on the first try.

**What it covers:**
- Installing the `meta-ads` Python package
- Obtaining a valid access token (System User or short-lived developer token)
- Writing a `.env` file with `ACCESS_TOKEN` and `AD_ACCOUNT_ID`
- Validating auth, ad account access, and page access
- Verifying Instagram is linked to your Facebook Page
- (Optional) Verifying a Meta Pixel / dataset for conversion campaigns

---

## Prerequisites

| Requirement | Details |
|---|---|
| Python 3.8+ | `python3 --version` to check |
| Meta Business Manager | business.facebook.com |
| Access token | System User (recommended) or short-lived developer token |
| `jq` | `brew install jq` or `apt install jq` |

---

## Step 1 — Detect Current State

Run these checks first so you know exactly what is already done:

```
python3 --version
which meta && meta --version
test -f .env && echo ".env found" || echo ".env missing"
```

If the CLI is installed and `.env` exists with a non-empty token, skip to
Step 5 to validate.

---

## Step 2 — Install the CLI

```
pip install "meta-ads>=0.3"
meta --version
```

If `pip` is not on PATH, use `pip3` or `python3 -m pip install meta-ads`.

---

## Step 3 — Obtain an Access Token

### Option A — System User Token (Recommended)

System User tokens do not expire and are safe for automation.

1. Go to **business.facebook.com → Settings → System Users**
2. Create or select a System User (Admin or Employee role)
3. Click **Generate New Token**, select your app, and grant:
   - `ads_management`
   - `ads_read`
   - `business_management`
   - `pages_read_engagement`
4. Copy the token — it will not be shown again

**Assign System User to your Ad Account:**
Business Settings → Ad Accounts → select account → Assign People → select
System User → role: **Manage ad account**

**Assign System User to your Page:**
Business Settings → Pages → select page → Assign People → select System
User → role: **Advertiser** or higher

### Option B — Short-Lived Developer Token

Short-lived tokens expire in ~1–2 hours. Useful for quick tests only.

1. Go to developers.facebook.com/tools/explorer
2. Select your app (or create one)
3. Click **Generate Access Token**
4. Add permissions: `ads_management`, `ads_read`, `business_management`
5. Copy the token

**Important:** The app must be in **Live mode** (not Development) to access
real ad accounts. See the error table below.

---

## Step 4 — Write the .env File

Create a `.env` file in your project root using `.env.example` as a template:

```
ACCESS_TOKEN=your_m...d
```

- Replace `your_meta_access_token_here` with your token
- Replace `act_your_ad_account_id` with your ad account ID (always prefixed with `act_`)

**Finding your Ad Account ID** — after setting ACCESS_TOKEN in your shell:

```
meta -o json ads adaccount list | jq '.[].id'
```

Or find it in Business Manager → Ad Accounts (prepend `act_` to the number shown).

**Source the file:**

```
source .env
export ACCESS_TOKEN AD_ACCOUNT_ID
```

---

## Step 5 — Validate Everything

Run each check in order and fix any error before moving on.

### 5a. Auth Status

```
meta auth status
```

Expected output: your user ID and list of granted permissions.
If it fails, re-source your `.env` and re-export the variables.

### 5b. Ad Account Access

```
meta -o json ads adaccount list | jq '.[].id'
```

Expected: at least one `act_XXXXXXXX` value.
Empty list means the System User is not assigned to the ad account.

### 5c. Page Access

```
meta -o json ads page list | jq '.[].id'
```

Expected: at least one page ID.
Empty list means the System User is not assigned to the Page.

### 5d. Verify Instagram Linked to Page

Meta requires Instagram to be linked to your Facebook Page for Instagram placements.

```
PAGE_ID=$(meta -o json ads page list | jq -r '.[0].id')
curl -s "https://graph.facebook.com/v20.0/${PAGE_ID}?fields=instagram_business_account&access_token=${ACCESS_TOKEN}" | jq .
```

Expected response includes `instagram_business_account.id`. If absent, link
your Instagram at **Business Settings → Instagram Accounts → Connect**.

### 5e. (Optional) Verify Pixel / Dataset

Required only for conversion campaigns (OUTCOME_SALES):

```
meta -o json ads dataset list | jq '.[].id'
```

Note the Pixel ID — you will need it when creating conversion campaigns.

---

## Error Table

| Symptom | Cause | Fix |
|---|---|---|
| `Not authenticated` | ACCESS_TOKEN not in environment | `source .env && export ACCESS_TOKEN AD_ACCOUNT_ID` |
| `adaccount list` returns `[]` | System User not assigned to ad account | Business Settings → Ad Accounts → Assign People → Manage ad account |
| Permission error creating ads | System User role too low | Upgrade to Manage ad account role |
| `App is in development mode` | App not switched to Live | FB Developers → App Dashboard → set App Mode to **Live** |
| `instagram_actor_id` rejected | Obsolete parameter | Never pass `--instagram-actor-id`; Instagram inferred from Page automatically |
| `page list` returns `[]` | System User not assigned to Page | Business Settings → Pages → Assign People → select System User |
| Token expires in ~1h | Short-lived token in use | Switch to System User token (Option A) |
| AD_ACCOUNT_ID format error | Missing `act_` prefix | Use `act_123456789`, not bare `123456789` |

---

## Notes

- CLI outputs are **JSON arrays**. Parse with `.[0].id`, not `.id`.
- All budgets in the CLI are in **cents** (e.g., $20/day = 2000).
- Use `--force` to skip interactive confirmations in scripts.
- `ads_management` is required for write operations; `ads_read` is read-only.
- After any `.env` change, re-run `source .env && export ACCESS_TOKEN AD_ACCOUNT_ID`.

---

## Quick Reference

```
# Install
pip install "meta-ads>=0.3"

# Auth check
meta auth status

# List ad accounts
meta -o json ads adaccount list | jq '.[].id'

# List pages
meta -o json ads page list | jq '.[].id'

# List pixels / datasets
meta -o json ads dataset list | jq '.[].id'
```
