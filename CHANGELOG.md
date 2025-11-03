# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-01

### Added
- 🎉 Initial release of Persistent Memory PR Review Bot
- ✅ FastAPI webhook server for GitHub events
- ✅ Celery async task processing
- ✅ PostgreSQL + pgvector for persistent memory
- ✅ Claude Sonnet 4.5 integration for code reviews
- ✅ User-level memory persistence
- ✅ RAG-powered codebase context retrieval
- ✅ Automatic PR reviews on open/update
- ✅ Manual `/review` command support
- ✅ Docker Compose for local development
- ✅ Render deployment configuration
- ✅ GitHub App authentication
- ✅ Inline review comments
- ✅ Vector similarity search for code
- ✅ Comprehensive documentation
- ✅ Setup scripts and guides

### Documentation
- README with quick start guide
- GitHub App setup instructions
- Deployment guide for multiple platforms
- Contributing guidelines
- Architecture diagrams

### Infrastructure
- Docker containerization
- PostgreSQL with pgvector extension
- Redis for Celery queue
- Multi-service orchestration
- Health check endpoints

## [Unreleased]

### Planned for v1.1
- Advanced PR summarization
- Reviewer analytics dashboard
- Multi-model LLM support (OpenAI, Gemini)
- Web UI for configuration
- Improved error handling
- Rate limiting
- Caching layer

### Planned for v2.0
- Context-aware conversation threads
- Organization-level memory
- Custom review templates
- CI/CD pipeline integration
- Slack/Discord notifications
- Review quality metrics
