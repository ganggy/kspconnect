"""Entry point to run the FastMCP Server."""

import sys
from src.server.mcp_app import mcp

if __name__ == "__main__":
    transport = "stdio"
    if "--sse" in sys.argv:
        transport = "sse"
    
    # Run the MCP server
    mcp.run(transport=transport)
