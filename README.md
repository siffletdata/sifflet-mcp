# Sifflet MCP

A Model Context Protocol (MCP) server for interacting with [Sifflet](https://www.siffletdata.com/) data observability platform.

## Description

This project provides an MCP server interface for interacting with the Sifflet data quality platform. The server enables various data quality management operations such as:

- Exploring assets and their metadata
- Exploring monitors or generation yaml for monitor-as-code
- Searching incidents
- Exploring impacted assets downstream and impact analysis


## Usage
### Prerequisites

- [`uv`](https://docs.astral.sh/uv/) (Python package installer/environment manager)
  ```bash
    # uv installation script for Linux/MacOS
    curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- A Sifflet backend running locally or remotely. You will need the following information:
  - `<access_token>`: you can find more information on how to generate it [here](https://docs.siffletdata.com/docs/generate-an-api-token)
  - `<your_sifflet_backend_url>`: Full URL to the Sifflet backend for instance: `https://<tenant_name>.siffletdata.com/api/`



### Using with MCP Clients

#### Cursor

Add the following configuration in the `mcp.json`. Follow [Cursor instructions](https://docs.cursor.com/context/model-context-protocol#configuring-mcp-servers) to set it up.

```json
{
  "mcpServers": {
    "mcp_server_sifflet": {
      "command": "uv run --with sifflet-mcp --no-project sifflet-mcp",
      "env": {
        "SIFFLET_API_TOKEN": "<access_token>",
        "SIFFLET_URL": "<your_sifflet_backend_url>"
      }
    }
  }
}
```

#### Claude

Follow the instructions in the [Claude documentation](https://modelcontextprotocol.io/quickstart/user#2-add-the-filesystem-mcp-server) to set up `claude_desktop_config.json`.

Then, add the following configuration to your `claude_desktop_config.json` file:

```json
{
  "mcpServers": {
    "sifflet-mcp": {
      "command": "uvx",
      "args": ["sifflet-mcp"],
      "env": {
        "SIFFLET_API_TOKEN": "<access_token>",
        "SIFFLET_URL": "<your_sifflet_backend_url>"
      }
    }
  }
}


```

## Development

Environment Setup
```bash
# clone the repository
git clone https://github.com/siffletdata/sifflet-mcp.git
cd sifflet-mcp
# create a virtual environment
uv venv
# install pre-commit
uv run pre-commit install
# run the server
uv run sifflet-mcp [--sse]

# Cursor setup: mcp.json or equivalent 
# You may need to put the full path to the uv executable in the command field. You can get this by running `which uv` on MacOS/Linux or `where uv` on Windows.
uv --directory <PATH_TO_PARENT_FOLDER>/sifflet-mcp run src/sifflet_mcp/server.py
```

To add new features or tools:

1. Add new tool functions in `server.py` using the `@mcp.tool` decorator
2. The server will automatically discover and use these tools
