# Environment Variables Setup

This document explains how to configure environment variables for the E-commerce Microservices project.

## Quick Start

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Update the `.env` file with your credentials:**
   - For development, you can use the provided defaults
   - For production, **you must change all passwords and secret keys**

3. **Start the services:**
   ```bash
   docker-compose up -d
   ```

## Environment Files

### `.env`
- Contains actual credentials and configuration
- **Never commit this file to version control** (already in .gitignore)
- Each developer should have their own `.env` file

### `.env.example`
- Template showing all required environment variables
- Contains placeholder values, not real credentials
- **Safe to commit to version control**
- Use this as a reference when setting up new environments

## Environment Variables Reference

### RabbitMQ Configuration
| Variable | Description | Default (Dev) |
|----------|-------------|---------------|
| `RABBITMQ_DEFAULT_USER` | RabbitMQ username | ecommerce |
| `RABBITMQ_DEFAULT_PASS` | RabbitMQ password | ecommerce123 |

### PostgreSQL Databases
Each service has its own database with separate credentials:

#### Order Service Database
| Variable | Description | Default (Dev) |
|----------|-------------|---------------|
| `ORDER_DB_USER` | Database username | order_user |
| `ORDER_DB_PASSWORD` | Database password | order123 |
| `ORDER_DB_NAME` | Database name | order_db |
| `ORDER_DB_PORT` | External port | 5433 |

#### Payment Service Database
| Variable | Description | Default (Dev) |
|----------|-------------|---------------|
| `PAYMENT_DB_USER` | Database username | payment_user |
| `PAYMENT_DB_PASSWORD` | Database password | payment123 |
| `PAYMENT_DB_NAME` | Database name | payment_db |
| `PAYMENT_DB_PORT` | External port | 5434 |

#### Product Service Database
| Variable | Description | Default (Dev) |
|----------|-------------|---------------|
| `PRODUCT_DB_USER` | Database username | product_user |
| `PRODUCT_DB_PASSWORD` | Database password | product123 |
| `PRODUCT_DB_NAME` | Database name | product_db |
| `PRODUCT_DB_PORT` | External port | 5435 |

#### User Service Database
| Variable | Description | Default (Dev) |
|----------|-------------|---------------|
| `USER_DB_USER` | Database username | user_user |
| `USER_DB_PASSWORD` | Database password | user123 |
| `USER_DB_NAME` | Database name | user_db |
| `USER_DB_PORT` | External port | 5436 |

#### Cart Service Database
| Variable | Description | Default (Dev) |
|----------|-------------|---------------|
| `CART_DB_USER` | Database username | cart_user |
| `CART_DB_PASSWORD` | Database password | cart123 |
| `CART_DB_NAME` | Database name | cart_db |
| `CART_DB_PORT` | External port | 5437 |

### JWT Configuration
| Variable | Description | Default (Dev) |
|----------|-------------|---------------|
| `JWT_SECRET_KEY` | Secret key for JWT signing | microservices-demo-secret-key-change-in-production |
| `JWT_ALGORITHM` | JWT algorithm | HS256 |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time | 30 |

### SMTP Configuration (MailHog)
| Variable | Description | Default (Dev) |
|----------|-------------|---------------|
| `SMTP_HOST` | SMTP server host | mailhog |
| `SMTP_PORT` | SMTP server port | 1025 |

### Service Ports
| Variable | Description | Default (Dev) |
|----------|-------------|---------------|
| `API_GATEWAY_PORT` | API Gateway port | 9000 |
| `ORDER_SERVICE_PORT` | Order Service port | 8001 |
| `PAYMENT_SERVICE_PORT` | Payment Service port | 8002 |
| `EMAIL_SERVICE_PORT` | Email Service port | 8003 |
| `PRODUCT_SERVICE_PORT` | Product Service port | 8004 |
| `USER_SERVICE_PORT` | User Service port | 8005 |
| `CART_SERVICE_PORT` | Cart Service port | 8006 |
| `FRONTEND_PORT` | Frontend port | 3000 |

### RabbitMQ Ports
| Variable | Description | Default (Dev) |
|----------|-------------|---------------|
| `RABBITMQ_AMQP_PORT` | AMQP protocol port | 5672 |
| `RABBITMQ_MANAGEMENT_PORT` | Management UI port | 15672 |

### MailHog Ports
| Variable | Description | Default (Dev) |
|----------|-------------|---------------|
| `MAILHOG_SMTP_PORT` | SMTP server port | 1026 |
| `MAILHOG_WEB_PORT` | Web UI port | 8026 |

### Service URLs (Internal Docker Network)
| Variable | Description | Default (Dev) |
|----------|-------------|---------------|
| `USER_SERVICE_URL` | User service internal URL | http://user-service:8005 |
| `PRODUCT_SERVICE_URL` | Product service internal URL | http://product-service:8004 |
| `CART_SERVICE_URL` | Cart service internal URL | http://cart-service:8006 |
| `ORDER_SERVICE_URL` | Order service internal URL | http://order-service:8001 |
| `PAYMENT_SERVICE_URL` | Payment service internal URL | http://payment-service:8002 |
| `EMAIL_SERVICE_URL` | Email service internal URL | http://email-service:8003 |

### Frontend Configuration
| Variable | Description | Default (Dev) |
|----------|-------------|---------------|
| `VITE_API_URL` | API Gateway URL (from browser) | http://localhost:9000/api |

## Security Best Practices

### Development Environment
- The provided defaults are suitable for local development
- Never use development credentials in production

### Production Environment
1. **Generate strong passwords:**
   ```bash
   # Example: Generate a random password
   openssl rand -base64 32
   ```

2. **Generate a secure JWT secret:**
   ```bash
   # Example: Generate a random JWT secret
   openssl rand -hex 64
   ```

3. **Update all database passwords**
4. **Update RabbitMQ credentials**
5. **Use environment-specific `.env` files**
6. **Consider using a secrets management solution** (e.g., AWS Secrets Manager, HashiCorp Vault)

### CI/CD Considerations
- Store secrets in your CI/CD platform's secret management
- Never commit `.env` files to version control
- Use different credentials for each environment (dev, staging, production)

## Troubleshooting

### Services can't connect to databases
- Check that environment variables are correctly set in `.env`
- Verify database credentials match in both the database service and application service
- Ensure the database containers are healthy: `docker-compose ps`

### "Environment variable not found" errors
- Ensure you've created `.env` from `.env.example`
- Check that all required variables are defined
- Restart docker-compose after changing `.env`: `docker-compose down && docker-compose up -d`

### Changes to `.env` not taking effect
- Docker Compose reads `.env` at startup
- Restart services after modifying `.env`:
  ```bash
  docker-compose down
  docker-compose up -d
  ```

## Additional Resources

- [Docker Compose Environment Variables](https://docs.docker.com/compose/environment-variables/)
- [Pydantic Settings Management](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [12-Factor App Configuration](https://12factor.net/config)
