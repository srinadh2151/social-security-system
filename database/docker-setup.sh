#!/bin/bash

# Docker Setup for PostgreSQL Demo
# This script sets up PostgreSQL using Docker for easy demo setup

echo "🐳 Setting up PostgreSQL with Docker for Demo"
echo "=============================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed!"
    echo "📦 Please install Docker first:"
    echo "  macOS: https://docs.docker.com/desktop/mac/"
    echo "  Windows: https://docs.docker.com/desktop/windows/"
    echo "  Linux: https://docs.docker.com/engine/install/"
    exit 1
fi

echo "✅ Docker is installed"

# Check if container already exists
if docker ps -a --format 'table {{.Names}}' | grep -q "postgres-demo"; then
    echo "📦 PostgreSQL container already exists"
    
    # Check if it's running
    if docker ps --format 'table {{.Names}}' | grep -q "postgres-demo"; then
        echo "✅ PostgreSQL container is already running"
    else
        echo "🚀 Starting existing PostgreSQL container..."
        docker start postgres-demo
    fi
else
    echo "📦 Creating new PostgreSQL container..."
    docker run --name postgres-demo \
        -e POSTGRES_PASSWORD=postgres \
        -e POSTGRES_USER=postgres \
        -e POSTGRES_DB=postgres \
        -p 5432:5432 \
        -d postgres:15
    
    echo "⏳ Waiting for PostgreSQL to start..."
    sleep 5
fi

# Test connection
echo "🔍 Testing PostgreSQL connection..."
if docker exec postgres-demo pg_isready -U postgres; then
    echo "✅ PostgreSQL is ready!"
    echo ""
    echo "📝 Connection Details:"
    echo "  Host: localhost"
    echo "  Port: 5432"
    echo "  User: postgres"
    echo "  Password: postgres"
    echo "  Database: postgres"
    echo ""
    echo "🚀 Now you can run the database setup:"
    echo "  python setup.py"
    echo ""
    echo "🛑 To stop PostgreSQL later:"
    echo "  docker stop postgres-demo"
    echo ""
    echo "🗑️  To remove PostgreSQL container:"
    echo "  docker stop postgres-demo && docker rm postgres-demo"
else
    echo "❌ PostgreSQL failed to start"
    echo "📋 Check container logs:"
    echo "  docker logs postgres-demo"
    exit 1
fi