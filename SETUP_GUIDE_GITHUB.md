# GitHub Actions Setup Guide - Step by Step

## Overview

This integration uses:
1. **GitHub Actions** - Runs the Confluence update script (free)
2. **smee.io** - Free webhook relay service
3. **Webhook relay script** - Forwards Jira webhooks to GitHub Actions

## Complete Setup (20 minutes)

### Step 1: Add GitHub Secrets

1. Go to your repository → **Settings** → **Secrets and variables** → **Actions**
2. Click **"New repository secret"**

Add these two secrets:

**Secret 1:**
- Name: `ATLASSIAN_EMAIL`
- Value: Your Atlassian account email

**Secret 2:**
- Name: `ATLASSIAN_API_TOKEN`
- Value: Get your API token from https://id.atlassian.com/manage-profile/security/api-tokens

### Step 2: Create smee.io Channel

1. Go to https://smee.io/
2. Click **"Start a new channel"**
3. You'll get a unique URL like: `https://smee.io/abc123def456`
4. **Copy this URL** - you'll need it next

### Step 3: Create GitHub Personal Access Token

1. Go to https://github.com/settings/tokens
2. Click **"Generate new token"** → **"Generate new token (classic)"**
3. Give it a name: "Jira Webhook Relay"
4. Set expiration: 90 days (or No expiration)
5. Select scopes:
   - ✅ `repo` (Full control of private repositories)
6. Click **"Generate token"**
7. **Copy the token** immediately

### Step 4: Configure Webhook Relay Locally

You need to run the webhook relay on your computer. Here's how:

1. **Clone your repository** (if you haven't already):
```bash
