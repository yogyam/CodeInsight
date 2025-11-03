# GitHub App Setup Guide

Follow these steps to create and configure your GitHub App for the PR Review Bot.

## Step 1: Create a New GitHub App

1. Navigate to [GitHub Settings → Developer settings → GitHub Apps](https://github.com/settings/apps)
2. Click **"New GitHub App"**

## Step 2: Basic Information

Fill in the following fields:

- **GitHub App name**: `pr-review-bot` (or your preferred name)
- **Homepage URL**: Your repository URL or bot website
- **Webhook URL**: `https://your-domain.com/webhook`
  - For local development: Use [ngrok](https://ngrok.com/) or [smee.io](https://smee.io/)
  - Example: `https://abc123.ngrok.io/webhook`
- **Webhook secret**: Generate a strong secret and save it
  - You can generate one with: `openssl rand -hex 32`

## Step 3: Permissions

### Repository Permissions

Set the following permissions to **Read & write**:
- ✅ **Pull requests**: Read & write (to post reviews)
- ✅ **Contents**: Read (to access code)
- ✅ **Issues**: Read & write (for issue comments)

Set to **Read-only**:
- ✅ **Metadata**: Read-only (required)

### Subscribe to Events

Check these webhook events:
- ✅ **Pull request**
- ✅ **Issue comment**

## Step 4: Installation

- **Where can this GitHub App be installed?**
  - Choose "Any account" for public bot
  - Or "Only on this account" for private use

## Step 5: Generate Private Key

1. After creating the app, scroll to **Private keys**
2. Click **"Generate a private key"**
3. Save the downloaded `.pem` file securely
4. Rename it to `github-app-private-key.pem`
5. Place it in your project root directory

## Step 6: Note Your App Details

From the app settings page, copy:
- **App ID** (you'll need this for `GITHUB_APP_ID`)
- **Webhook secret** (from Step 2)

## Step 7: Install the App

1. Go to the **Install App** tab in your GitHub App settings
2. Click **Install** next to your organization/account
3. Select repositories:
   - Choose "All repositories" OR
   - "Only select repositories" and pick the ones to review
4. Click **Install**

## Step 8: Configure Your Environment

Update your `.env` file:

```bash
GITHUB_APP_ID=123456  # Your App ID
GITHUB_APP_PRIVATE_KEY_PATH=github-app-private-key.pem
GITHUB_WEBHOOK_SECRET=your_webhook_secret_here
```

## Step 9: Test the Integration

1. Start your bot: `docker compose up`
2. Create a test PR in an installed repository
3. Check the logs: `docker compose logs -f api`
4. You should see webhook events being received

## Troubleshooting

### Webhook not working

1. Check Recent Deliveries:
   - Go to your GitHub App settings
   - Click "Advanced" → "Recent Deliveries"
   - Look for failed deliveries and error messages

2. Verify webhook URL is accessible:
   ```bash
   curl https://your-domain.com/health
   ```

3. Check webhook secret matches in `.env`

### Permission Issues

If the bot can't post comments:
- Verify "Pull requests: Read & write" permission
- Reinstall the app on your repository
- Check bot has access to the specific repository

### Private Key Issues

If authentication fails:
- Ensure `.pem` file is in the correct location
- Check file permissions: `chmod 600 github-app-private-key.pem`
- Verify the path in `GITHUB_APP_PRIVATE_KEY_PATH`

## Local Development with ngrok

For testing webhooks locally:

```bash
# Install ngrok
brew install ngrok

# Start ngrok tunnel
ngrok http 8000

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
# Update GitHub App webhook URL to: https://abc123.ngrok.io/webhook
```

## Security Best Practices

1. **Never commit** your private key to git
2. Use strong webhook secrets (32+ characters)
3. Rotate private keys periodically
4. Limit app installation to necessary repositories
5. Use environment variables for all secrets

## Next Steps

Once your GitHub App is configured:

1. ✅ Install dependencies: `pip install -r requirements.txt`
2. ✅ Set up database: `docker compose up -d postgres`
3. ✅ Configure other services (Anthropic API, etc.)
4. ✅ Deploy to production (Render, AWS, etc.)
5. ✅ Test with a real PR

## Useful Links

- [GitHub Apps Documentation](https://docs.github.com/en/developers/apps)
- [Webhook Events](https://docs.github.com/en/developers/webhooks-and-events/webhooks/webhook-events-and-payloads)
- [Testing Webhooks](https://docs.github.com/en/developers/webhooks-and-events/webhooks/testing-webhooks)
