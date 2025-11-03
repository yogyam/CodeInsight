# 🚀 Setup Checklist

Use this checklist to get your PR Review Bot up and running.

## 📋 Pre-requisites

- [ ] Docker installed and running
- [ ] Docker Compose installed
- [ ] GitHub account with admin access to repositories
- [ ] Anthropic API key (for Claude)
- [ ] (Optional) Supabase account or Render account

## 🔧 Environment Setup

### 1. Clone & Configure
- [ ] Clone the repository
- [ ] Copy `.env.example` to `.env`
- [ ] Open `.env` in your editor

### 2. GitHub App Setup
- [ ] Go to GitHub Settings → Developer settings → GitHub Apps
- [ ] Click "New GitHub App"
- [ ] Fill in basic information:
  - [ ] App name: `your-pr-review-bot`
  - [ ] Homepage URL: Repository URL
  - [ ] Webhook URL: `https://your-domain.com/webhook` (or ngrok for testing)
  - [ ] Webhook secret: Generate with `openssl rand -hex 32`
- [ ] Set permissions:
  - [ ] Pull requests: Read & Write
  - [ ] Contents: Read
  - [ ] Issues: Read & Write
  - [ ] Metadata: Read-only
- [ ] Subscribe to events:
  - [ ] Pull request
  - [ ] Issue comment
- [ ] Generate private key and download `.pem` file
- [ ] Note your App ID

### 3. Configure Environment Variables
Edit `.env` with your values:
- [ ] `GITHUB_APP_ID=` (your GitHub App ID)
- [ ] `GITHUB_WEBHOOK_SECRET=` (your webhook secret)
- [ ] `GITHUB_APP_PRIVATE_KEY_PATH=github-app-private-key.pem`
- [ ] `ANTHROPIC_API_KEY=` (your Anthropic API key)

### 4. Add Private Key
- [ ] Rename downloaded GitHub App key to `github-app-private-key.pem`
- [ ] Move it to project root
- [ ] Run: `chmod 600 github-app-private-key.pem`

## 🐳 Local Development

### 5. Start Services
Choose one:

**Option A: Quick Start Script**
```bash
./start.sh
```

**Option B: Manual Start**
```bash
docker-compose up -d
```

### 6. Verify Services
- [ ] Check services are running: `docker-compose ps`
- [ ] API health check: http://localhost:8000/health
- [ ] Check logs: `docker-compose logs -f api`

### 7. Test Webhook (Local)
For local testing with ngrok:
- [ ] Install ngrok: `brew install ngrok`
- [ ] Start tunnel: `ngrok http 8000`
- [ ] Copy HTTPS URL (e.g., `https://abc123.ngrok.io`)
- [ ] Update GitHub App webhook URL to: `https://abc123.ngrok.io/webhook`
- [ ] Restart ngrok if needed

### 8. Install GitHub App
- [ ] Go to your GitHub App settings
- [ ] Click "Install App" tab
- [ ] Install on your account/organization
- [ ] Select repositories to review
- [ ] Click "Install"

### 9. Test with a PR
- [ ] Create a test PR in an installed repository
- [ ] Check webhook deliveries in GitHub App settings
- [ ] Check logs: `docker-compose logs -f api celery_worker`
- [ ] Verify bot posts review comments

## 🚀 Production Deployment

### 10. Choose Deployment Platform
- [ ] Render (recommended, easiest)
- [ ] AWS ECS/Fargate
- [ ] Google Cloud Run
- [ ] Azure Container Apps
- [ ] Self-hosted

### 11. Deploy to Render
- [ ] Create Render account
- [ ] Connect GitHub repository
- [ ] Create new "Blueprint" from repository
- [ ] Render detects `render.yaml`
- [ ] Add environment variables in Render dashboard
- [ ] Upload private key as secret file
- [ ] Click "Apply" to deploy
- [ ] Note your service URL

### 12. Update GitHub App
- [ ] Go to GitHub App settings
- [ ] Update webhook URL to your production URL
- [ ] Example: `https://your-app.onrender.com/webhook`
- [ ] Save changes

### 13. Database Setup (Production)
If using Supabase:
- [ ] Create Supabase project
- [ ] Run SQL: `CREATE EXTENSION IF NOT EXISTS vector;`
- [ ] Run `init.sql` script
- [ ] Update `DATABASE_URL` in environment

If using Render PostgreSQL:
- [ ] Connect to database
- [ ] Run init.sql

### 14. Final Verification
- [ ] Test production webhook with a PR
- [ ] Check Render logs for any errors
- [ ] Verify reviews are posted correctly
- [ ] Monitor resource usage

## 🔒 Security Checklist

- [ ] Never commit `.env` file
- [ ] Never commit `.pem` private key
- [ ] Use strong webhook secret (32+ chars)
- [ ] Rotate private keys periodically
- [ ] Use HTTPS for all webhooks
- [ ] Limit GitHub App installation to necessary repos
- [ ] Set up monitoring/alerting

## 📊 Monitoring Setup

- [ ] Set up health check monitoring
- [ ] Configure log aggregation (optional)
- [ ] Set up error tracking (Sentry, etc.)
- [ ] Monitor API response times
- [ ] Track review task completion rate

## 🎯 Optional Enhancements

- [ ] Set up custom domain
- [ ] Configure rate limiting
- [ ] Add caching layer
- [ ] Set up CI/CD pipeline
- [ ] Add integration tests
- [ ] Configure backup strategy
- [ ] Set up staging environment

## 📝 Documentation

- [ ] Read `README.md` for overview
- [ ] Review `docs/GITHUB_APP_SETUP.md` for detailed app setup
- [ ] Check `docs/DEPLOYMENT.md` for platform-specific guides
- [ ] Read `docs/ARCHITECTURE.md` to understand system design
- [ ] Review `CONTRIBUTING.md` if planning to contribute

## 🐛 Troubleshooting

If something doesn't work:

### Webhook Issues
- [ ] Check GitHub App "Recent Deliveries" for errors
- [ ] Verify webhook URL is accessible
- [ ] Check webhook secret matches
- [ ] Review API logs

### Authentication Issues
- [ ] Verify App ID is correct
- [ ] Check private key file path
- [ ] Ensure private key has correct permissions
- [ ] Verify app is installed on repository

### Review Not Posting
- [ ] Check Celery worker logs
- [ ] Verify Anthropic API key
- [ ] Check database connection
- [ ] Ensure app has write permissions

### Database Issues
- [ ] Verify DATABASE_URL is correct
- [ ] Check pgvector extension is enabled
- [ ] Ensure tables are created (run init.sql)
- [ ] Check connection pool settings

## ✅ Success Criteria

You're all set when:
- [ ] Webhook receives PR events successfully
- [ ] Bot posts review comments on PRs
- [ ] Memory is persisted in database
- [ ] All services are healthy
- [ ] Logs show no errors
- [ ] Manual `/review` command works

## 📞 Getting Help

If stuck:
1. Check logs: `docker-compose logs -f`
2. Review documentation in `/docs`
3. Check GitHub App webhook deliveries
4. Verify all environment variables
5. Test individual components
6. Open an issue on GitHub

## 🎉 Next Steps After Setup

Once everything works:
1. Test with various PR types
2. Monitor performance and costs
3. Customize review behavior
4. Add more repositories
5. Gather user feedback
6. Plan enhancements

---

**Congratulations! Your PR Review Bot is ready to make code reviews better! 🚀**
