# Product Service

Product catalog management microservice following clean architecture principles.

## Architecture

```
app/
├── api/                   # API Layer - HTTP routes
├── core/                  # Business Logic Layer
├── domain/                # Domain Layer - Models & Schemas
└── infrastructure/        # Infrastructure Layer - DB, External Services
```

## Patterns Implemented

- **Layered Architecture**: Separation of concerns across layers
- **Repository Pattern**: Abstract data access
- **Service Layer**: Business logic separation
- **Dependency Injection**: FastAPI's DI system
- **Clean Architecture**: Domain-centric design

## Running Locally

```bash
# Install dependencies
poetry install

# Run service
uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload
```

## API Endpoints

- `GET /products` - Get all products
- `GET /products/{id}` - Get product by ID
- `POST /products` - Create new product
- `PUT /products/{id}` - Update product
- `DELETE /products/{id}` - Delete product
- `PATCH /products/{id}/stock` - Update stock

## Testing

```bash
# Unit tests
pytest tests/unit

# Integration tests
pytest tests/integration

# All tests
pytest
```

## Environment Variables

See `.env.example` for required configuration.
