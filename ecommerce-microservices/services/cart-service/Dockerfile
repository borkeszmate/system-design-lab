FROM python:3.11-slim

WORKDIR /app

# Install poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

# Copy application code
COPY . .

# Expose port
EXPOSE 8006

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8006", "--reload"]
