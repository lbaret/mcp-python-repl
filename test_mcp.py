import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client
async def run():
    a = sse_client('http://localhost:8000/mcp/sse')
    read, write = await a.__aenter__()
    s = ClientSession(read, write)
    await s.__aenter__()
    await s.initialize()
    res = await s.list_tools()
    print(res)
    await s.__aexit__(None,None,None)
    await a.__aexit__(None,None,None)
asyncio.run(run())
