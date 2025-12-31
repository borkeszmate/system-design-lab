#!/bin/bash
# Setup script for microservices environment

echo "🚀 Setting up E-commerce Microservices..."

# Create .env files from examples
echo "📝 Creating environment files..."
for service in product-service user-service cart-service order-service payment-service email-service; do
  if [ -f "$service/.env.example" ] && [ ! -f "$service/.env" ]; then
    cp "$service/.env.example" "$service/.env"
    echo "✅ Created $service/.env"
  fi
done

# Build and start services
echo "🐳 Building Docker images..."
docker compose build

echo "✅ Setup complete!"
echo "Run 'docker compose up -d' to start all services"
