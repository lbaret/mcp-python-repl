# mcp-python-repl

An MCP server running on streamable-http with a Python REPL tool.

## Installation

This project uses `uv` as its package manager. To get started locally:

1. Ensure you have Python 3.14 or later installed.
2. Install `uv` if you haven't already. Refers to [official website](https://docs.astral.sh/uv/getting-started/installation/).
3. Install project dependencies, by running the following command:

```bash
uv sync
```

## Docker

If you prefer to run the application in an isolated container, Docker is supported out of the box.

### Customizing the REPL Environment

If you need specific Python packages available within the REPL environment, you can add them before building the docker image using `uv add`:

```bash
uv add <library-name>
```

### Build the Image

Build the Docker container with the following command:

```bash
docker build -t mcp-repl .
```

### Run the Container

Start both the MCP server and ingestion API using:

```bash
docker run -d -v mcp-repl:/app/data -p 8000:8000 mcp-repl
```

Both the MCP server and ingestion API will be exposed on port `8000`.

## FastMCP and FastAPI Integration

This application leverages **FastMCP** integrated with **FastAPI** to provide both the MCP server and custom REST endpoints on the same port (8000). The MCP server uses a `sse` (Server-Sent Events) transport when used with **FastAPI**.
- **`src/mcp_repl/server.py`**: Defines the `FastMCP` server, registers the `python_interpreter` tool (which dynamically executes Python 3 code and captures standard output) and the `list_files` tool (which discovers PDF documents), and configures the `streamable-http` transport.
- **`src/mcp_repl/api.py`**: A FastAPI application that provides additional endpoints (`/upload` for PDF ingestion and validation, `GET /files` for listing and `DELETE /files/{filename}` for deleting ingested PDF documents, `/status` for health checks) and mounts the FastMCP server's SSE application at the `/mcp` route.

> [!WARNING]
> **No Security Layer Added**: This project currently does not implement any authentication, authorization, or secure sandboxing boundaries. The `python_interpreter` tool allows arbitrary Python code execution on the host machine or container, and all endpoints are publicly unauthenticated. You **must** manage and implement your own security and proxy layers before deploying this in a production or publicly exposed environment.

## Usage Examples

We provide several example scripts in the `examples/` directory to demonstrate various interactions with the application.

### 1. API Alive Check (`examples/api_alive.py`)

A simple script to check if the server is up and verify the endpoints.

```bash
uv run python examples/api_alive.py
```
**Explanation:** This script performs an HTTP GET request to the `/status` endpoint to securely confirm the server is "Online" and to fetch the base mounting path for MCP operations.

### 2. File Ingestion (`examples/ingestion.py`)

A script to test the `/upload` endpoint, demonstrating file ingestion into the server.

```bash
uv run python examples/ingestion.py
```
**Explanation:** This script makes HTTP POST requests to upload sample files. It demonstrates the validation process ensuring only valid `.pdf` files are successfully saved to an isolated `/app/data` directory, while non-PDF files return errors.

### 3. MCP Client (`examples/client.py`)

A full working MCP client that communicates with the MCP Server to discover tools and request tool execution.

**1. Start the Server** (if not using Docker):

```bash
uv run src/mcp_repl/server.py
```

**2. Run the Client Script**

```bash
uv run python examples/client.py
```

**Explanation:** This client connects to the streamable HTTP endpoint (`http://localhost:8000/mcp/sse`), initializing a continuous `sse_client` session. It queries the server for the list of available tools, and specifically invokes tools such as `python_interpreter` to run python strings dynamically on the server or `list_files` to interact with files, collecting and streaming back the output.
