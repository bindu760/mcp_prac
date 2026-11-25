
import asyncio
import json
import os
import sys

from dotenv import load_dotenv
from groq import Groq

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# Load environment variables
load_dotenv()

# Initialize Groq
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Model name
MODEL = "openai/gpt-oss-20b"


async def main():

    # Start MCP server using current Python interpreter
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["server.py"],
    )

    # Connect to MCP server
    async with stdio_client(server_params) as (read, write):

        async with ClientSession(read, write) as session:

            # Initialize MCP connection
            await session.initialize()

            # Discover MCP tools
            mcp_tools = await session.list_tools()

            print("\nAvailable MCP Tools:")
            for tool in mcp_tools.tools:
                print("-", tool.name)

            # Convert MCP tools into Groq tool format
            tools = []

            for tool in mcp_tools.tools:
                tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description or "",
                        "parameters": tool.inputSchema,
                    }
                })

            # Conversation history
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a personal task assistant. "
                        "Use MCP tools to manage tasks. "
                        "Use tools whenever the user asks to add, "
                        "list, complete, or delete tasks. "
                        "Do not invent tool results. "
                        "Respond in a friendly and concise manner."
                    )
                }
            ]

            # Chat loop
            while True:

                user_input = input("\nYou: ").strip()

                if user_input.lower() in ["exit", "quit", "bye"]:
                    print("Assistant: Goodbye!")
                    break

                if not user_input:
                    continue

                messages.append({
                    "role": "user",
                    "content": user_input
                })

                # Send user message to Groq
                response = client.chat.completions.create(
                    model=MODEL,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                )

                response_message = response.choices[0].message

                # Save response
                messages.append(
                    response_message.model_dump(exclude_none=True)
                )

                # Handle tool calls
                while response_message.tool_calls:

                    for tool_call in response_message.tool_calls:

                        tool_name = tool_call.function.name

                        tool_args = json.loads(
                            tool_call.function.arguments
                        )

                        print(f"\n[Calling MCP Tool: {tool_name}]")

                        # Execute tool using MCP
                        result = await session.call_tool(
                            tool_name,
                            arguments=tool_args
                        )

                        # Extract tool result
                        tool_result = "\n".join(
                            content.text
                            for content in result.content
                            if hasattr(content, "text")
                        )

                        # Send result back to LLM
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": tool_result
                        })

                    # Ask LLM again with tool results
                    response = client.chat.completions.create(
                        model=MODEL,
                        messages=messages,
                        tools=tools,
                        tool_choice="auto",
                    )

                    response_message = response.choices[0].message

                    messages.append(
                        response_message.model_dump(
                            exclude_none=True
                        )
                    )

                # Display final response
                print("\nAssistant:", response_message.content)


if __name__ == "__main__":
    asyncio.run(main())
