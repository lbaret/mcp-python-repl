FROM python:3.14

RUN apt-get update && apt-get install -y curl

WORKDIR /app

COPY pyproject.toml /app/pyproject.toml
COPY README.md /app/README.md

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

COPY src/ /app/src/

RUN uv venv --python 3.14
ENV PATH="/app/.venv/bin:${PATH}"
RUN uv sync

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "src.mcp_repl.api:app", "--host", "0.0.0.0", "--port", "8000"]