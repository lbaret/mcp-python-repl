import contextlib
import io
import os
import traceback

from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Python-REPL", json_response=True, port=8000, host="0.0.0.0")

# Python REPL tool
@mcp.tool()
def python_interpreter(code: str) -> str:
    """
    # Python REPL Execution Tool

    This tool acts as a powerful execution engine for the LLM to run dynamic Python 3 snippets.
    It is designed to give you a reliable way to perform complex computations, explore datasets,
    interact with the local filesystem, or validate programmatic logic directly. Instead of
    guessing outcomes, you can execute code to verify your assumptions and get definitive results.

    ## Instructions

    1. **Output Observation**: You MUST use `print()` to extract values, explore variables, or confirm intermediate steps. The execution intercepts `sys.stdout`, so return values from expressions are not automatically captured.
    2. **Error Handling**: If your code raises an exception, the tool will catch it and return the full error traceback string. You can use this to debug and correct your code.
    3. **No Output**: If the execution succeeds but nothing is printed, it returns a standard success message indicating no console output.
    4. **State Persistence**: Code is executed via `exec()` within the function's scope. Local variables and imports from one call generally DO NOT persist to the next call. Treat each tool invocation as an independent execution.
    5. **Data Access**: You can access, read, and manipulate documents stored in the `/app/data` folder. Use standard Python libraries (like `os`, `pathlib`, etc.) to interact with these files.
    6. **Formatting**: Ensure the `code` string is well-formatted, standard Python 3 code with proper indentation.

    ## Arguments

    - `code` (str): The valid Python code block to execute.

    ## Returns

    `str`: The captured standard output from execution, or an error traceback.

    ## Examples

    **1. Analyzing data from the data directory:**
    ```python
    import json
    with open('/app/data/metrics.json', 'r') as f:
        data = json.load(f)

    average = sum(data['values']) / len(data['values'])
    print(f"Average metric value: {average}")
    ```

    **2. Multi-step logic and calculations:**
    ```python
    def calculate_fibonacci(n):
        a, b = 0, 1
        for _ in range(n):
            a, b = b, a + b
        return a

    result = calculate_fibonacci(10)
    print(f"The 10th Fibonacci number is: {result}")
    ```
    """
    output = io.StringIO()

    try:
        with contextlib.redirect_stdout(output):
            exec(code)

        result = output.getvalue()
        return result if result else "Execution successful (no console output)."

    except Exception:
        error_msg = f"Execution error :\n{traceback.format_exc()}"
        return error_msg

# List PDF files in /app/data
@mcp.tool()
def list_files() -> str:
    """
    # PDF Files Listing Tool

    This tool is designed to give you a quick and reliable way to discover all the PDF documents
    currently available in the primary data directory (`/app/data`). It scans the folder and returns
    a list of filenames, which you can then use for further processing, analysis, or passing to
    other tools.

    ## Instructions

    1. **Functionality**: The tool automatically checks the `/app/data` directory for any files with a `.pdf` extension (case-insensitive).
    2. **Output Format**: It returns a bulleted list of the discovered PDF filenames. If no PDF files are found, it clearly states that none are present.
    3. **Usage**: Use this tool when you need to know exactly what PDF files are available before attempting to read, analyze, or manipulate them.

    ## Returns

    `str`: A formatted string containing the list of PDF files found in `/app/data`, or a message indicating no PDF files were found.

    ## Examples

    **1. Discovering available PDFs before analysis:**
    ```python
    # You decide to call the tool to see what's available
    # Tool call: list_files()

    # Example Output:
    # Found the following PDF files in /app/data:
    # - report_Q1.pdf
    # - financial_summary.pdf
    ```

    **2. Handling empty directory case:**
    ```python
    # Tool call: list_files()

    # Example Output:
    # No PDF files found in /app/data.
    ```
    """
    data_dir = "/app/data"

    if not os.path.exists(data_dir):
        return f"Error: Directory '{data_dir}' does not exist."

    try:
        pdf_files = [
            f
            for f in os.listdir(data_dir)
            if os.path.isfile(os.path.join(data_dir, f)) and f.lower().endswith(".pdf")
        ]

        if not pdf_files:
            return f"No PDF files found in {data_dir}."

        result = [f"Found the following PDF files in {data_dir}:"]
        for pdf in sorted(pdf_files):
            result.append(f"- {pdf}")

        return "\n".join(result)

    except Exception as e:
        return f"Error listing files: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
