# GitHub Actions Setup Guide

This guide explains how to set up GitHub Actions to trigger PR reviews using our API instead of webhooks.

## Overview

Instead of using webhooks, we use GitHub Actions workflows that:
1. Trigger automatically on PR events (open, sync, reopen)
2. Allow manual triggering via `/review` comments
3. Call our API with Bearer token authentication
4. Work with private or internal APIs (no public webhook endpoint needed)

## Architecture Benefits

✅ **Simpler Authentication**: Bearer token instead of HMAC signature validation  
✅ **Easier Local Testing**: Use ngrok with GitHub Actions, no webhook config needed  
✅ **No Public Endpoint Required**: API can be internal, GitHub Actions calls it  
✅ **GitHub-Managed Secrets**: Encrypted repository secrets for tokens  
✅ **Better Visibility**: GitHub Actions tab shows all runs and logs  

## Setup Steps

### 1. Get Your GitHub App Installation ID

First, you need to find your GitHub App's installation ID:

**Option A: Using API**
```bash
# Replace with your GitHub App ID and private key path
curl -i -H "Authorization: Bearer $(python3 -c "import jwt, time; print(jwt.encode({'iat': int(time.time()), 'exp': int(time.time()) + 600, 'iss': YOUR_APP_ID}, open('path/to/private-key.pem').read(), algorithm='RS256'))")" \
  https://api.github.com/app/installations
```

**Option B: From GitHub App Settings**
1. Go to your installed GitHub App
2. Click "Configure" next to the repository
3. Look at the URL: `https://github.com/settings/installations/{installation_id}`

**Option C: From a webhook delivery** (if you had webhooks before)
1. Go to your GitHub App settings
2. Recent Deliveries tab
3. Look for `installation.id` in any payload

### 2. Update Workflow Files

Edit `.github/workflows/pr-review.yml` and `.github/workflows/review-command.yml`:

Replace this line:
```yaml
echo "installation_id=YOUR_INSTALLATION_ID" >> $GITHUB_OUTPUT
```

With your actual installation ID:
```yaml
echo "installation_id=12345678" >> $GITHUB_OUTPUT
```

### 3. Set Up Repository Secrets

Go to your repository Settings → Secrets and variables → Actions → New repository secret

Add these secrets:

#### `REVIEW_API_URL`
- **Local testing**: `https://your-ngrok-url.ngrok.io`
- **Production**: `https://your-app.onrender.com` (or your deployment URL)
- **Example**: `https://abc123.ngrok.io`

#### `REVIEW_API_TOKEN`
- This should match your `API_SECRET_KEY` from `.env`
- Generate with: `openssl rand -hex 32`
- **Important**: Must be the same value in both:
  - Repository secret `REVIEW_API_TOKEN`
  - API environment variable `API_SECRET_KEY`

### 4. Test the Setup

#### Test Automatic Reviews:
1. Create a new Pull Request
2. Go to the "Actions" tab in GitHub
3. You should see "AI PR Review" workflow running
4. Check the workflow logs for any errors
5. The bot should post a review comment on your PR

#### Test Manual Reviews:
1. Go to any Pull Request
2. Add a comment: `/review`
3. Go to the "Actions" tab
4. You should see "Manual Review Command" workflow running
5. The bot should post a new review

## Local Testing with ngrok

For local development:

### 1. Start Your API
```bash
docker-compose up -d
```

### 2. Start ngrok
```bash
ngrok http 8000
```

### 3. Update Repository Secret
Copy the ngrok HTTPS URL (e.g., `https://abc123.ngrok.io`) and update the `REVIEW_API_URL` secret in your repository.

### 4. Test with a PR
Create a test PR and watch the GitHub Actions logs and your local API logs:
```bash
docker-compose logs -f api celery_worker
```

## Troubleshooting

### Workflow doesn't trigger
- ✅ Check that workflows are enabled in repository settings
- ✅ Verify workflow files are in `.github/workflows/` directory
- ✅ Check GitHub Actions tab for any disabled workflows
- ✅ Ensure you have the correct repository permissions

### API returns 401 Unauthorized
- ✅ Verify `REVIEW_API_TOKEN` secret matches `API_SECRET_KEY` in API
- ✅ Check API logs: `docker-compose logs api`
- ✅ Ensure Bearer token is being sent correctly

### API returns 404 Not Found
- ✅ Check `REVIEW_API_URL` is correct
- ✅ Ensure API is running and accessible
- ✅ Test with curl: `curl https://your-api.com/health`

### Installation ID issues
- ✅ Verify installation ID is correct
- ✅ Check GitHub App is installed on the repository
- ✅ Ensure App has correct permissions

### No review comments appear
- ✅ Check Celery worker logs: `docker-compose logs celery_worker`
- ✅ Verify GitHub App has "Pull requests: Read & Write" permission
- ✅ Check API logs for any errors
- ✅ Ensure Anthropic API key is valid

## Workflow Customization

### Change which events trigger reviews

Edit `.github/workflows/pr-review.yml`:

```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened]  # Add/remove events here
```

Available events:
- `opened`: PR is created
- `synchronize`: New commits pushed
- `reopened`: Closed PR is reopened
- `edited`: PR title/description changed
- `ready_for_review`: Draft → Ready

### Add custom review commands

Edit `.github/workflows/review-command.yml`:

```yaml
if: |
  github.event.issue.pull_request &&
  (startsWith(github.event.comment.body, '/review') ||
   startsWith(github.event.comment.body, '/analyze'))
```

### Add authentication headers

If you need additional headers:

```yaml
- name: Trigger AI Review
  run: |
    curl -X POST "${{ secrets.REVIEW_API_URL }}/api/review" \
      -H "Authorization: Bearer ${{ secrets.REVIEW_API_TOKEN }}" \
      -H "Content-Type: application/json" \
      -H "X-Custom-Header: value" \
      -d '...'
```

## Security Best Practices

✅ Never commit secrets to the repository  
✅ Use GitHub's encrypted secrets for all sensitive data  
✅ Rotate API tokens periodically  
✅ Use HTTPS for all API endpoints  
✅ Limit GitHub App installation to necessary repositories  
✅ Monitor workflow runs for suspicious activity  
✅ Use environment protection rules for production  

## Production Checklist

- [ ] GitHub App created and installed
- [ ] Installation ID added to workflow files
- [ ] Repository secrets configured (`REVIEW_API_URL`, `REVIEW_API_TOKEN`)
- [ ] API deployed and accessible
- [ ] API token matches between GitHub secrets and API environment
- [ ] Test PR created and reviewed successfully
- [ ] Manual `/review` command tested
- [ ] Monitoring/logging set up
- [ ] Error notifications configured

## Need Help?

- Check workflow logs in the Actions tab
- Review API logs: `docker-compose logs -f api celery_worker`
- See [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- See [DEPLOYMENT.md](DEPLOYMENT.md) for deployment guides
