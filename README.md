# Sifflet MCP Server

An MCP (Model Context Protocol) server that enables data observability operations with the [Sifflet](https://www.siffletdata.com/) platform.

## Features

This project provides an MCP server enabling interactions with Sifflet API :

- Explore assets: Search for tables, views, dashboards, and other data assets. View their schema, owners, tags, and their metadata.
- Explore monitors: Discover existing monitors and generate their Monitor-as-Code YAML configurations.
- Explore incidents: List all data observability incidents detected by the Sifflet platform.
- Perform impact analysis: Start from an incident and trace the downstream assets affected.

## Sample Use Cases

Here are a few scenarios where the Sifflet MCP Server can be particularly helpful:

- **Understanding Downstream Impact**: You're modifying a dbt model and need to identify the owners of dependent downstream models and dashboards. The MCP server can provide these details, allowing you to proactively notify them about your upcoming changes.
- **Accessing Up-to-Date Table Metadata**: You're about to update a table in your data warehouse. Before you proceed, you can query the MCP server to get its latest metadata. This includes information on how the table is currently monitored in Sifflet, whether it's involved in any ongoing incidents, the list of its frequent users, and other relevant operational details.
- **Bootstrapping New Asset Monitoring**: You're creating a new table (or dbt model) and want to ensure it's well-monitored from the start. You can ask the MCP server to list the Sifflet monitors already created for similar existing assets. The server can then provide the Monitor-as-Code YAML configurations, which you can adapt and deploy.

## Usage
### Prerequisites

- [`uv`](https://docs.astral.sh/uv/) (Python package installer/environment manager)
  ```bash
    # uv installation script for Linux/MacOS
    curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- A Sifflet backend running locally or remotely. You will need the following information:
  - `SIFFLET_API_TOKEN`: you can find more information on how to generate it [here](https://docs.siffletdata.com/docs/generate-an-api-token). You can create a API token with the role `Viewer`.
  - `SIFFLET_BACKEND_URL`: Full URL to the Sifflet backend for instance: `https://<tenant_name>.siffletdata.com/api/`



### Using with MCP Clients

#### Cursor

Add the following configuration in the `mcp.json`. Follow [Cursor instructions](https://docs.cursor.com/context/model-context-protocol#configuring-mcp-servers) to set it up.

```json
{
  "mcpServers": {
    "mcp_server_sifflet": {
      "command": "uvx",
      "args": ["sifflet-mcp@latest"],
      "env": {
        "SIFFLET_API_TOKEN": "<access_token>",
        "SIFFLET_BACKEND_URL": "https://<tenant_name>.siffletdata.com/api/"
      }
    }
  }
}
```

**Note:** You may need to use the full path to the `uvx` executable in the `command` field. You can find the full path by running `which uvx` in your terminal.

#### Claude Desktop

Follow the instructions in the [Claude documentation](https://modelcontextprotocol.io/quickstart/user#2-add-the-filesystem-mcp-server) to set up `claude_desktop_config.json`.

Then, add the following configuration to your `claude_desktop_config.json` file:

```json
{
  "mcpServers": {
    "sifflet-mcp": {
      "command": "uvx",
      "args": ["sifflet-mcp@latest"],
      "env": {
        "SIFFLET_API_TOKEN": "<access_token>",
        "SIFFLET_BACKEND_URL": "https://<tenant_name>.siffletdata.com/api/"
      }
    }
  }
}


```

**Note:** You may need to use the full path to the `uvx` executable in the `command` field. You can find the full path by running `which uvx` in your terminal.

## Contributing

For development setup and contribution guidelines, please see [CONTRIBUTING.md](CONTRIBUTING.md).

## Reporting Problems

If you encounter any problems or have a bug to report, please feel free to open an issue on this GitHub repository.
Alternatively, you can reach out to your Sifflet Customer Success team.
