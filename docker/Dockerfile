# EntityLearn Docker Image
# Multi-stage build for minimal final image size

FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN pip install --no-cache-dir uv

# Copy project files
COPY pyproject.toml README.md ./
COPY core/ core/

# Install dependencies to a virtual env using uv
RUN uv sync --frozen --no-dev

FROM python:3.11-slim AS runtime

WORKDIR /app

# Create non-root user
RUN useradd --create-home --shell /bin/bash entitylearn

# Copy virtual env from builder
COPY --from=builder /app/.venv /app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy application code
COPY --chown=entitylearn:entitylearn . .

# Copy packs
COPY packs/ packs/

# Create data directory
RUN mkdir -p /app/data && chown -R entitylearn:entitylearn /app/data

USER entitylearn

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import httpx; httpx.get('http://localhost:8000/health')" || exit 1

ENTRYPOINT ["entitylearn"]
CMD ["serve", "--host", "0.0.0.0", "--port", "8000"]
