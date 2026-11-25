
from mcp.server.fastmcp import FastMCP

from database import (
    create_table,
    add_task,
    list_tasks,
    complete_task,
    delete_task
)

# Create MCP server
mcp = FastMCP("Personal Task Manager")

# Initialize database
create_table()


@mcp.tool()
def create_new_task(title: str) -> str:
    """Create a new task."""
    return add_task(title)


@mcp.tool()
def get_all_tasks() -> str:
    """Get all saved tasks."""
    tasks = list_tasks()

    if not tasks:
        return "No tasks found."

    return str(tasks)


@mcp.tool()
def mark_task_completed(task_id: int) -> str:
    """Mark a task as completed using its ID."""
    return complete_task(task_id)


@mcp.tool()
def remove_task(task_id: int) -> str:
    """Delete a task using its ID."""
    return delete_task(task_id)


if __name__ == "__main__":
    mcp.run(transport="stdio")
