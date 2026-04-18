import marimo

__generated_with = "0.23.1"
app = marimo.App(width="medium")


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # MCP Server example with Ollama

    ## Settings up Ollama

    In the same way we launched our **MCP server**, you can use Docker service to run Ollama in a container, by running:

    ```bash
    docker run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
    ```

    ## Overview
    This notebook demonstrates a practical implementation of the **Model Context Protocol (MCP)** to bridge the gap between local Large Language Models and external data sources. While LLMs are powerful, their utility is often constrained by their knowledge cutoff and lack of access to real-time, private, or specialized data.

    By utilizing **Ollama** for local inference and a **custom-built MCP server**, we create an agentic workflow where the model can dynamically call tools to fetch contextually relevant information before generating a response.

    ---

    ## Core Components
    * **Ollama:** A lightweight framework for running high-performance models (like Llama 3 or Mistral) locally.
    * **MCP Server (Custom):** A specialized server that exposes unique capabilities—such as querying a specific database, interacting with a local filesystem, or fetching real-time API data—via a standardized protocol.
    * **Orchestration Layer:** Python logic that manages the communication between the LLM and the MCP host, handling tool calls and state management.

    ---

    ## Key Objectives
    1.  **Environment Setup:** Configuring the Python environment and ensuring the Ollama service is reachable.
    2.  **MCP Integration:** Connecting to a custom MCP server and inspecting its available tools and resources.
    3.  **Tool-Calling Workflow:** Implementing a "Reasoning-Action" loop where the LLM identifies the need for external data, invokes the MCP tool, and synthesizes the final output based on the retrieved context.
    4.  **Practical Example:** A concrete walkthrough to show the protocol in action (e.g., querying local technical documentation or system metrics).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Imports
    """)
    return


@app.cell
def _():
    import os
    import re
    from functools import partial

    import marimo as mo
    import ollama
    from mcp import ClientSession
    from mcp.client.sse import sse_client

    import warnings
    warnings.filterwarnings('ignore')
    return ClientSession, mo, ollama, partial, sse_client


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Functions & Classes
    """)
    return


@app.cell
def _(ClientSession, mo, ollama, sse_client):
    def pull_with_marimo_progress(model_name: str, client: ollama.Client) -> None:
        try:
            need_download = True
            client_models = client.list().models
            for cmodel in client_models:
                if model_name.lower() in cmodel.model.lower():
                    need_download = False
                    break
        except:
            need_download = True

        if need_download:
            with mo.status.progress_bar(title=f"Downloading : {model_name}", total=0) as bar:
                for progress in client.pull(model_name, stream=True):
                    status = progress.get('status', 'In progress...')
                    completed = progress.get('completed')
                    total = progress.get('total')
                    if total and completed:
                        percent = (completed / total) * 100

                        comp_mb = completed // (1024 * 1024)
                        tot_mb = total // (1024 * 1024)

                        bar.update(
                            increment=0,
                            subtitle=f"{status} - {percent:.1f}% ({comp_mb} MB / {tot_mb} MB)"
                        )
                    else:
                        bar.update(increment=0, subtitle=status)
        else:
            print("Model has already been downloaded.")

    async def call_llm(
        messages,
        config,
        client,
        model_name="gemma4:26b",
    ) -> str:
        sse_ctx = sse_client("http://localhost:8000/mcp/sse")
        read, write = await sse_ctx.__aenter__()
        session_ctx = ClientSession(read, write)
        session = await session_ctx.__aenter__()
        await session.initialize()

        tools_response = await session.list_tools()
        tools = tools_response.dict().get("tools")

        tool_init_prompt = """If the tool output contains one or more file names, 
        then give the user only the filename found. Do not add additional details. 
        If the tool output is empty ask the user to try again. Here is the tool output: """

        messages = [
            {
                "role": "system",
                "content": "You MUST provide an answer to the user query. You have the option to call tools, and if you have a response from a tool you MUST build a new response inserting tool query."
            },
        ]

        messages += [
            {"role": msg.role, "content": msg.content} for msg in messages
        ]

        response = client.chat(
            model=model_name,
            messages=messages,
            tools=tools,
            options={
                "temperature": 0.,
            }
        )

        if response.message.tool_calls:
            for tool_call_id, tool_call in enumerate(response.message.tool_calls): 
                if "python_interpreter" in tool_call.function.name:
                    result = await session.call_tool("python_interpreter", tool_call.function.arguments)
                else:
                    raise ValueError(f"Tool `{tool_call.function.name}` is not recognized")

                tool_call_message = tool_call.copy().dict()
                messages.append(
                    {
                        "role": "assistant",
                        "content": None,
                        "tool_call": tool_call_message
                    }
                )
                messages.append(
                    {
                        "role": "tool",
                        "tool_name": tool_call.function.name,
                        "content": tool_init_prompt + result.content[0].text
                    }
                )

            # Retrieve final chat completion with the gathered history  
            response = client.chat(
                model=model_name,
                messages=messages,
                tools=tools,
                options={
                    "temperature": 0.,
                }
            )

        await session_ctx.__aexit__(None, None, None)
        await sse_ctx.__aexit__(None, None, None)
        return response.message.content if response.message.content else "<Empty Response>"

    return call_llm, pull_with_marimo_progress


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Initialize Ollama Client

    You can download any Ollama model you want by changing `model_name` variable name which will be used as parameters when calling the function `pull_with_marimo_progress`.
    """)
    return


@app.cell
def _(ollama, pull_with_marimo_progress):
    client = ollama.Client(
        host="localhost:11434"
    )

    model_name = "gemma4:26b"

    # Download model if needed
    pull_with_marimo_progress(model_name=model_name, client=client)
    return client, model_name


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Chat

    Here you can test to chat with the model.
    If you need to debug model flow, you can use `chat_records.messages`.
    """)
    return


@app.cell
def _(call_llm, client, mo, model_name, partial):
    initial_user_query = "Please write and execute a python code to multiply 2 random numbers. Once the tool has executed, write a short response providing the answer in a markdown format."

    chatbot = mo.ui.chat(
        partial(
            call_llm,
            client=client,
            model_name=model_name
        ),
        prompts=[initial_user_query],
        show_configuration_controls=False,
        allow_attachments=False,
    )
    chatbot
    return (chatbot,)


@app.cell
def _(chatbot):
    chatbot.value
    return


if __name__ == "__main__":
    app.run()
