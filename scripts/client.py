"""
Client to test the MCP server running on streamable-http.
Before running this client, ensure the server is started:
    uv run src/mcp_repl/server.py
"""

import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


async def run():
    """Run the streamable http client example."""
    print("Connecting to streamable-http server at http://127.0.0.1:8000/mcp ...")
    async with streamable_http_client("http://127.0.0.1:8000/mcp") as (read, write, _):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            print("Connected successfully!")

            tools = await session.list_tools()
            for tool in tools.tools:
                print(f"Tool available: {tool.name}\nDescription:{tool.description}", end="\n\n\n")
            
            # Test execute_python_code tool 
            if any(tool.name == "execute_python_code" for tool in tools.tools):
                print("-" * 40)
                print("Testing execute_python_code tool:")
                test_code = "print('Hello from the Python REPL tool!')\nx = 2 + 3\nprint(f'2 + 3 = {x}')"
                print(f"Running code:\n{test_code}")
                result = await session.call_tool("execute_python_code", {"code": test_code})
                
                print("\nReceived result:")
                for content in result.content:
                    if content.type == "text":
                        print(content.text)


def main():
    """Entry point for the client."""
    try:
        asyncio.run(run())
    except Exception as e:
        print(f"Connection failed: {e}")
        print("Please ensure the server is running (uv run src/mcp_repl/server.py)")


if __name__ == "__main__":
    main()