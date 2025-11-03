# Contributing to PR Review Bot

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## 🤝 How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Docker version, etc.)
- Relevant logs

### Suggesting Features

Feature requests are welcome! Please:
- Check if the feature is already requested
- Explain the use case
- Describe the proposed solution
- Consider backward compatibility

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Test thoroughly**
   ```bash
   # Run tests
   pytest tests/
   
   # Test with Docker
   docker-compose up --build
   ```
5. **Commit with clear messages**
   ```bash
   git commit -m "Add amazing feature"
   ```
6. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```
7. **Open a Pull Request**

## 📝 Code Style

### Python

We follow PEP 8 with some modifications:
- Line length: 100 characters
- Use type hints where possible
- Document functions with docstrings

```python
def example_function(param: str) -> Dict[str, Any]:
    """
    Brief description.
    
    Args:
        param: Description of parameter
        
    Returns:
        Description of return value
    """
    pass
```

### Formatting

Use `black` for code formatting:
```bash
pip install black
black app/
```

### Linting

Use `flake8` for linting:
```bash
pip install flake8
flake8 app/
```

## 🧪 Testing

### Writing Tests

- Place tests in `tests/` directory
- Use pytest fixtures for common setup
- Aim for >80% code coverage
- Test both success and error cases

```python
def test_review_generation():
    """Test that review generation works correctly."""
    # Arrange
    diff = "sample diff"
    
    # Act
    result = generate_review(diff)
    
    # Assert
    assert result is not None
    assert "issues" in result
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test
pytest tests/test_llm_service.py::test_review_generation
```

## 📚 Documentation

- Update README.md for user-facing changes
- Update docstrings for code changes
- Add examples for new features
- Update deployment docs if needed

## 🏗️ Project Structure

```
CodeInsight/
├── app/                    # Application code
│   ├── main.py            # FastAPI app
│   ├── tasks.py           # Celery tasks
│   ├── config.py          # Configuration
│   ├── database.py        # Database models
│   ├── github_auth.py     # GitHub authentication
│   ├── github_service.py  # GitHub API client
│   ├── llm_service.py     # LLM integration
│   ├── memory_service.py  # Memory management
│   ├── embedding_service.py  # Vector embeddings
│   └── rag_service.py     # RAG pipeline
├── tests/                 # Test files
├── docs/                  # Documentation
├── docker-compose.yml     # Local development
├── Dockerfile            # Container image
└── requirements.txt      # Python dependencies
```

## 🔧 Development Setup

1. **Clone and setup**
   ```bash
   git clone https://github.com/yourusername/CodeInsight.git
   cd CodeInsight
   python -m venv venv
   source venv/bin/activate  # or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Start dependencies**
   ```bash
   docker-compose up -d postgres redis
   ```

4. **Run locally**
   ```bash
   # Terminal 1: API
   uvicorn app.main:app --reload
   
   # Terminal 2: Celery worker
   celery -A app.celery_app worker --loglevel=info
   ```

## 🚀 Release Process

1. Update version in `app/__init__.py`
2. Update CHANGELOG.md
3. Create a new tag
   ```bash
   git tag -a v1.0.0 -m "Release v1.0.0"
   git push origin v1.0.0
   ```
4. GitHub Actions will build and release

## 💡 Tips

- Keep PRs focused and small
- Write meaningful commit messages
- Add tests for new features
- Update documentation
- Be patient with reviews
- Follow the code of conduct

## 🐛 Debugging

### Local Development

```bash
# API logs
uvicorn app.main:app --reload --log-level debug

# Celery logs
celery -A app.celery_app worker --loglevel=debug

# Docker logs
docker-compose logs -f api
docker-compose logs -f celery_worker
```

### Database

```bash
# Connect to local database
docker-compose exec postgres psql -U postgres -d pr_review_bot

# Run queries
SELECT * FROM user_memory LIMIT 10;
```

## 📞 Getting Help

- Open a discussion on GitHub
- Check existing issues and PRs
- Read the documentation in `/docs`
- Ask in community channels

## 🎯 Good First Issues

Look for issues labeled `good first issue` - these are great starting points for new contributors!

## 📜 Code of Conduct

Be respectful, inclusive, and constructive. We're all here to build something great together.

## ⭐ Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- GitHub insights

Thank you for contributing! 🎉
