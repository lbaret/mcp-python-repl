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

## Usage Example

To test the MCP server, you can use the provided client script which connects to the streamable HTTP endpoint and executes Python code using the REPL tool.

**1. Start the Server** (if not using Docker):

```bash
uv run src/mcp_repl/server.py
```

**2. Run the Client Script**

Open a separate terminal and run:

```bash
uv run examples/client.py
```

**Expected Output:**

The client connection handles initialization and testing. You should see output indicating successful connection, a list of available tools including `execute_python_code`, and the result of the test script (for example, showing `2 + 3 = 5`).
