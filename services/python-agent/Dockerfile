FROM debian:bookworm-slim

# Install dependencies for uv and Python build
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

# Copy dependency files and Python version
COPY pyproject.toml .python-version ./

# Install dependencies (uv will download Python 3.14 automatically)
RUN uv sync --no-install-project

# Copy source code
COPY python_agent ./python_agent

# Install the project
RUN uv sync

ENV PORT=3001

EXPOSE 3001

CMD ["uv", "run", "uvicorn", "python_agent.server:app", "--host", "0.0.0.0", "--port", "3001"]
