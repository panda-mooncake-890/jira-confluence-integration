# Jira → Confluence Webhook Integration (GitHub Actions)

## How It Works (Event-Driven with GitHub Actions)
```
1. Developer moves ticket to DONE in Jira
        ↓
2. Jira sends webhook to smee.io relay
        ↓
3. Webhook relay forwards to GitHub Actions
        ↓
4. GitHub Actions workflow runs Python script
        ↓
5. Script checks: Is this ticket under epic SCRUM-5?
        ↓
6. If YES → Extract ticket title & current date
        ↓
7. Update Confluence table with new row
        ↓
8. Done! ✓
```

## What Gets Updated

**Confluence Table:** "MCP/Connector Inventory Simulator"  
**Page:** https://panda-mooncake.atlassian.net/wiki/spaces/~622e38dc73c8ec00699b8c44/pages/163975/MCP+Connector+Inventory+Simulator

**Columns filled automatically:**
- **Connector/MCP**: Ticket Key (e.g., SCRUM-123)
- **Title**: Ticket Summary/Title
- **Enablement Date**: Date ticket moved to DONE
- **Access Notes**: Left blank (as requested)

## Quick Start

### 1. Add GitHub Secrets

Go to **Settings** → **Secrets and variables** → **Actions**

Add these secrets:
- `ATLASSIAN_EMAIL`: Your Atlassian account email
- `ATLASSIAN_API_TOKEN`: Your API token from https://id.atlassian.com/manage-profile/security/api-tokens

### 2. Create a smee.io channel

1. Go to https://smee.io/
2. Click "Start a new channel"
3. Copy your unique smee URL

### 3. Create a GitHub Personal Access Token

1. Go to https://github.com/settings/tokens
2. Generate new token (classic) with `repo` scope
3. Copy the token

### 4. Run the webhook relay locally
```bash
# Clone this repo
git clone https://github.com/panda-mooncake-890/jira-confluence-integration.git
cd jira-confluence-integration

# Install dependencies
npm install

# Create .env file with your values
echo "SMEE_URL=https://smee.io/YOUR_CHANNEL" > .env
echo "GITHUB_TOKEN=ghp_YOUR_TOKEN" >> .env
echo "GITHUB_REPO=panda-mooncake-890/jira-confluence-integration" >> .env

# Install dotenv
npm install dotenv

# Start the relay
npm start
```

### 5. Configure Jira webhook

1. Go to https://panda-mooncake.atlassian.net/plugins/servlet/webhooks
2. Create a new webhook
3. URL: Your smee.io URL
4. Events: Issue → updated
5. Save

### 6. Test it!

Move a ticket under SCRUM-5 to DONE and watch the magic happen!

## Files in This Repo

- `.github/workflows/jira-webhook.yml` - GitHub Actions workflow
- `.github/scripts/update_confluence.py` - Python script to update Confluence
- `webhook-relay.js` - Node.js relay script
- `package.json` - Node.js dependencies
- `SETUP_GUIDE_GITHUB.md` - Detailed setup instructions

## Trigger Condition

**ONLY triggers when:**
- A ticket under epic SCRUM-5
- Has its status changed to "DONE"

## Architecture

GitHub Actions (free) + smee.io (free) + lightweight webhook relay = $0/month! 🎉

For detailed setup instructions, see [SETUP_GUIDE_GITHUB.md](SETUP_GUIDE_GITHUB.md)
