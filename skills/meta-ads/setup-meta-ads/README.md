# setup-meta-ads

This skill walks you through the complete setup of the Meta Ads CLI — from
installation to full validation. It handles the two most common token
workflows (System User for automation, short-lived token for quick tests),
helps you write your `.env` file, and verifies that your ad account, Facebook
Page, and Instagram account are all correctly linked and accessible.

Use this skill at the start of any Meta advertising project. It surfaces every
common configuration pitfall — wrong token scope, missing ad-account role, app
stuck in development mode, missing Instagram connection — and gives you the
exact steps to fix each one before you touch a campaign.

You need Python 3.8+, a Meta Business Manager account, an access token with
`ads_management` and `ads_read` permissions, and `jq` for JSON parsing.

## Quick Start

```
# 1. Install the CLI
pip install "meta-ads>=0.3"

# 2. Copy the env template and fill in your values
cp .env.example .env
# Edit .env: set ACCESS_TOKEN and AD_ACCOUNT_ID

# 3. Source and validate
source .env
export ACCESS_TOKEN AD_ACCOUNT_ID
meta auth status
meta -o json ads adaccount list | jq '.[].id'
meta -o json ads page list | jq '.[].id'
```

Open `SKILL.md` or paste the prompt from `examples/kickoff.md` into Claude Code
for a fully guided, step-by-step walkthrough.
