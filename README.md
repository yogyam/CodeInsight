# 🤖 Persistent Memory GitHub PR Review Bot

An intelligent, open-source GitHub pull request review bot with persistent user-level memory, contextual inline comments, and codebase retrieval capabilities.

## ✨ Features

- **🧠 Persistent Memory**: Remembers user preferences, coding patterns, and review history
- **💬 Contextual Reviews**: Generates intelligent inline code review comments
- **🔍 RAG-Powered**: Uses retrieval-augmented generation for codebase-aware reviews
- **⚡ Async Processing**: Fast, non-blocking reviews using Celery workers
- **🎯 Multi-Trigger**: Auto-review on PR events or manual `/review` commands
- **📊 Vector Search**: pgvector-powered semantic code search

## 🏗️ Architecture

```
GitHub PR → FastAPI Webhook → Celery Queue → Claude Sonnet 4.5 → Review Comments
                ↓                                    ↑
              Redis                          Supabase (Postgres + pgvector)
                                                     ↓
                                            Persistent Memory & Embeddings
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- GitHub App credentials
- Anthropic API key
- Supabase account (or use local PostgreSQL)

### 1. Clone & Setup

```bash
git clone <your-repo-url>
cd CodeInsight
cp .env.example .env
```

### 2. Configure Environment

Edit `.env` with your credentials:

```bash
# GitHub App
GITHUB_APP_ID=your_app_id
GITHUB_APP_PRIVATE_KEY_PATH=github-app-private-key.pem
GITHUB_WEBHOOK_SECRET=your_webhook_secret

# LLM
ANTHROPIC_API_KEY=your_anthropic_api_key

# Database (local)
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/pr_review_bot

# Redis (local)
REDIS_URL=redis://redis:6379/0
```

### 3. Add GitHub App Private Key

Save your GitHub App private key as `github-app-private-key.pem` in the project root.

### 4. Start Services

```bash
docker compose up -d
```

Services will be available at:
- **API**: http://localhost:8000
- **Health Check**: http://localhost:8000/health

### 5. Configure GitHub App Webhook

In your GitHub App settings:
- **Webhook URL**: `https://your-domain.com/webhook`
- **Webhook Secret**: (same as in `.env`)
- **Permissions**:
  - Pull requests: Read & write
  - Contents: Read
  - Metadata: Read
- **Subscribe to events**:
  - Pull request
  - Issue comment

## 📖 Usage

### Automatic Reviews

When enabled (`AUTO_REVIEW_ENABLED=true`), the bot automatically reviews:
- New PRs
- PR updates (new commits)
- Reopened PRs

### Manual Reviews

Comment `/review` on any PR to trigger a review.

## 🛠️ Development

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run API locally
uvicorn app.main:app --reload --port 8000

# Run Celery worker
celery -A app.celery_app worker --loglevel=info
```

### Running Tests

```bash
pytest tests/
```

## 🚢 Deployment

### Deploy to Render

1. Push code to GitHub
2. Connect repository to Render
3. Render will use `render.yaml` for automatic deployment
4. Set environment variables in Render dashboard
5. Upload GitHub App private key as a secret file

### Deploy to Other Platforms

The application is containerized and can be deployed to:
- AWS ECS/Fargate
- Google Cloud Run
- Azure Container Apps
- Any Kubernetes cluster

## 📊 Database Setup

### Enable pgvector Extension

For Supabase:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

The `init.sql` file will automatically create tables when using Docker Compose.

### Manual Schema Setup

If deploying without Docker, run:
```bash
psql $DATABASE_URL < init.sql
```

## 🔧 Configuration

### Review Behavior

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTO_REVIEW_ENABLED` | `true` | Auto-review new PRs |
| `REVIEW_COMMAND` | `/review` | Command to trigger manual review |
| `MAX_FILES_TO_REVIEW` | `10` | Max files per review |
| `MAX_DIFF_SIZE` | `5000` | Max diff size per file |
| `ENABLE_MEMORY_PERSISTENCE` | `true` | Enable memory features |

### LLM Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_MODEL` | `claude-sonnet-4-20250514` | Claude model to use |
| `ANTHROPIC_API_KEY` | - | Anthropic API key |

## 📝 Creating a GitHub App

1. Go to GitHub Settings → Developer settings → GitHub Apps
2. Click "New GitHub App"
3. Fill in:
   - **Name**: Your bot name
   - **Homepage URL**: Your repo or website
   - **Webhook URL**: Your deployed API URL + `/webhook`
   - **Webhook secret**: Generate a secure secret
4. Set permissions (see Quick Start section)
5. Generate a private key (download `.pem` file)
6. Install the app on your repositories

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🗺️ Roadmap

### v1.1 (Next Release)
- [ ] Advanced PR summarization
- [ ] Reviewer analytics dashboard
- [ ] Multi-model LLM support (OpenAI, Gemini)

### v2.0 (Future)
- [ ] Context-aware conversation threads
- [ ] Organization-level memory
- [ ] Custom review templates
- [ ] Integration with CI/CD pipelines

## 🐛 Troubleshooting

### Webhook not receiving events
- Check webhook URL is publicly accessible
- Verify webhook secret matches
- Check GitHub App permissions

### Review not posting
- Verify GitHub App has write permissions
- Check Celery worker logs
- Ensure database connection is working

### Memory not persisting
- Verify pgvector extension is enabled
- Check database migrations ran successfully
- Ensure `ENABLE_MEMORY_PERSISTENCE=true`

## 📞 Support

- Open an issue on GitHub
- Check documentation in `/docs`
- Review logs: `docker compose logs -f`

## ⭐ Acknowledgments

Built with:
- FastAPI
- Celery
- Claude (Anthropic)
- PostgreSQL + pgvector
- Sentence Transformers

---

Made with ❤️ for better code reviews
