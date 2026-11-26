
import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():

    server_params = StdioServerParameters(
        command=sys.executable,
        args=["server.py"],
    )

    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            await session.initialize()

            # Discover tools from MCP server
            tools = await session.list_tools()

            print("\nTools discovered from MCP Server:")

            for tool in tools.tools:
                print("-", tool.name)

            # Call tool directly without an LLM
            result = await session.call_tool(
                "create_new_task",
                arguments={"title": "Test MCP with second client"}
            )

            print("\nTool execution result:")

            for content in result.content:
                if hasattr(content, "text"):
                    print(content.text)

            # Retrieve tasks
            tasks = await session.call_tool(
                "get_all_tasks",
                arguments={}
            )

            print("\nAll tasks:")

            for content in tasks.content:
                if hasattr(content, "text"):
                    print(content.text)


if __name__ == "__main__":
    asyncio.run(main())
