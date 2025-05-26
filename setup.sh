#!/bin/bash

# Prefect Docker Setup Script
# This script sets up a complete Prefect environment with Docker

set -e

echo "🚀 Starting Prefect Docker Setup..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

print_success "Docker is running"

# Check if Docker Compose is available
if ! docker compose version > /dev/null 2>&1; then
    print_error "Docker Compose is not available. Please install Docker and try again."
    exit 1
fi

print_success "Docker Compose is available"

# Start the Docker Compose stack
print_status "Starting Docker Compose stack..."
docker compose up -d

# Wait for services to be ready
print_status "Waiting for services to start..."
sleep 30

# Check if Prefect server is healthy
print_status "Checking Prefect server health..."
max_attempts=30
attempt=1

while [ $attempt -le $max_attempts ]; do
    if curl -s http://localhost:4200/api/health > /dev/null; then
        print_success "Prefect server is healthy"
        break
    else
        print_warning "Attempt $attempt/$max_attempts: Prefect server not ready yet..."
        sleep 5
        ((attempt++))
    fi
done

if [ $attempt -gt $max_attempts ]; then
    print_error "Prefect server failed to start within expected time"
    exit 1
fi

# Set Prefect API URL for local commands
export PREFECT_API_URL="http://localhost:4200/api"

# Create work pool (this will be created automatically by the worker, but we can verify)
print_status "Checking work pool status..."
sleep 10

# Build the Docker image for our flows
print_status "Building Docker image for flows..."
docker build -t prefect-flows:latest .

print_success "Docker image built successfully"

# Install Python dependencies locally for deployment
print_status "Installing Python dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    pip install prefect httpx requests
fi

# Deploy the flows
print_status "Deploying flows..."
python deploy_flows.py

print_success "Setup completed successfully!"

echo ""
echo "🎉 Prefect environment is ready!"
echo ""
echo "📊 Access the Prefect UI at: http://localhost:4200"
echo ""
echo "🔧 Useful commands:"
echo "  - View logs: docker compose logs -f"
echo "  - Stop services: docker compose down"
echo "  - Restart services: docker compose restart"
echo "  - View work pools: docker compose exec prefect-server prefect work-pool ls"
echo "  - View deployments: docker compose exec prefect-server prefect deployment ls"
echo ""
echo "🚀 Your flows are now deployed and will run according to their schedules!"
echo "   - GitHub Stars: Every 6 hours"
echo "   - Data Processing: Every 4 hours"
echo ""
echo "💡 You can also trigger manual runs from the UI or CLI" 