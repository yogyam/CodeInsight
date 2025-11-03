#!/bin/bash

# Quick start script for PR Review Bot
# This script helps you get started quickly

set -e

echo "🤖 PR Review Bot - Quick Start Setup"
echo "===================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created"
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env file with your credentials:"
    echo "   - GITHUB_APP_ID"
    echo "   - API_SECRET_KEY (generate with: openssl rand -hex 32)"
    echo "   - ANTHROPIC_API_KEY"
    echo ""
    read -p "Press Enter after you've updated the .env file..."
else
    echo "✅ .env file already exists"
fi

# Check if GitHub App private key exists
if [ ! -f github-app-private-key.pem ]; then
    echo ""
    echo "⚠️  GitHub App private key not found!"
    echo "   Please save your GitHub App private key as: github-app-private-key.pem"
    echo "   Follow the guide: docs/GITHUB_APP_SETUP.md"
    echo ""
    read -p "Press Enter after you've added the private key file..."
fi

if [ -f github-app-private-key.pem ]; then
    echo "✅ GitHub App private key found"
    chmod 600 github-app-private-key.pem
    echo "   Set correct permissions on private key"
fi

echo ""
echo "🚀 Starting services with Docker Compose..."
echo ""

docker-compose up -d

echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Services are running!"
    echo ""
    echo "📊 Service Status:"
    docker-compose ps
    echo ""
    echo "🌐 API is available at: http://localhost:8000"
    echo "🏥 Health check: http://localhost:8000/health"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Set up GitHub Actions workflows (see docs/GITHUB_ACTIONS_SETUP.md)"
    echo "   2. Add repository secrets (REVIEW_API_URL, REVIEW_API_TOKEN)"
    echo "   3. Test with a PR in your repository"
    echo "   4. Check logs: docker-compose logs -f"
    echo ""
    echo "📚 Documentation:"
    echo "   - README.md - General overview"
    echo "   - docs/GITHUB_APP_SETUP.md - GitHub App configuration"
    echo "   - docs/DEPLOYMENT.md - Production deployment"
    echo ""
    
    # Open browser to health check
    if command -v open &> /dev/null; then
        echo "Opening health check in browser..."
        open http://localhost:8000/health
    elif command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:8000/health
    fi
else
    echo "❌ Some services failed to start. Check logs:"
    echo "   docker-compose logs"
fi
