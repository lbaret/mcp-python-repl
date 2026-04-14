import contextlib
import io
import traceback

from mcp.server.fastmcp import FastMCP

# Create an MCP server
mcp = FastMCP("Python-REPL", json_response=True, port=8000, host="0.0.0.0")

# Python REPL tool
@mcp.tool()
def execute_python_code(code: str) -> str:
    """
    Executes raw Python 3 code dynamically and captures its standard output.
    
    This tool is designed for LLMs to run Python code snippets to accomplish tasks, 
    explore data, or perform computations. The execution intercepts `sys.stdout`, so 
    the ONLY way to see the results of your code is to explicitly use the `print()` function.

    Key behaviors and instructions for LLMs:
    - **Output Observation:** You MUST use `print()` to extract values, explore variables, 
      or confirm intermediate steps. Return values from expressions are not automatically captured.
    - **Error Handling:** If your code raises an exception, the tool will catch it and 
      return the full error traceback string. You can use this to debug and correct your code.
    - **No Output:** If the execution succeeds but nothing is printed, it returns a 
      standard success message indicating no console output.
    - **State Persistence:** Code is executed via `exec()` within the function's scope. Local 
      variables and imports from one call generally DO NOT persist to the next call. Treat 
      each tool invocation as an independent execution unless you read/write from the disk.
    - **Formatting:** Ensure the `code` string is well-formatted, standard Python 3 code 
      with proper indentation.

    Args:
        code (str): The valid Python code block to execute.
        
    Returns:
        str: The captured standard output from execution, or an error traceback.
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

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
