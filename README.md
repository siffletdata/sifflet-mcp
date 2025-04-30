# Sifflet MCP - AI-Powered Incident Management

A ChatGPT-like assistant for managing Sifflet incidents using Chainlit and Claude AI.

## Description

This project provides an AI assistant interface for managing Sifflet data quality incidents efficiently. The assistant can perform various actions
such as:

- Listing incidents
- Getting incident details
- Closing incidents
- Managing rules
- Checking asset data

Built with Chainlit, the interface provides a chat experience with AI-powered assistance backed by Claude 3.5 Sonnet.

## Prerequisites

- Python 3.12+
- `uv` (Python package installer/environment manager)
- Sifflet backend running locally or remotely

## Environment Setup

1. Clone the repository
   ```bash
   git clone https://github.com/siffletdata/sifflet-mcp.git
   cd sifflet-mcp
   ```

2. Create and activate a virtual environment with `uv`
   ```bash
   uv venv
   source .venv/bin/activate
   ```

3. Run the mcp server
   ```bash
   uv run sifflet-mcp [--sse]
   ```

## Using with MCP Clients

If you used the installation script, the mcp server has been installed in your user directory at ~/.sifflet/sifflet-mcp/.

You will need the following information:
- `<access_token>`: you can find more information on how to generate it [here](https://docs.siffletdata.com/docs/generate-an-api-token)
- `<your_sifflet_backend_url>`: Full URL to the Sifflet backend for instance: `https://<tenant_name>.siffletdata.com/api/`

### Cursor
```json
{
  "mcpServers": {
    "mcp_server_sifflet": {
      "command": "<path to repository>/.venv/bin/sifflet-mcp",
      "env": {
        "SIFFLET_API_TOKEN": "<access_token>",
        "SIFFLET_URL": "<your_sifflet_backend_url>"
      }
    }
  }
}
```

### Claude

Follow the instructions in the [Claude documentation](https://modelcontextprotocol.io/quickstart/user#2-add-the-filesystem-mcp-server) to set up `claude_desktop_config.json`.

Then, add the following configuration to your `claude_desktop_config.json` file:

```json
{
  "mcpServers": {
    "sifflet-mcp": {
      "command": "<path to repository>/.venv/bin/sifflet-mcp",
      "env": {
        "SIFFLET_API_TOKEN": "<access_token>",
        "SIFFLET_URL": "<your_sifflet_backend_url>"
      }
    }
  }
}


```

## Development

```
uv run pre-commit install
```

To add new features or tools:

1. Add new tool functions in `server.py` using the `@mcp.tool` decorator
2. The server will automatically discover and use these tools
