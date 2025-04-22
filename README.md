# Sifflet MCP - AI-Powered Incident Management

A ChatGPT-like assistant for managing Sifflet incidents using Chainlit and Claude AI.

## Description

This project provides an AI assistant interface for managing Sifflet data quality incidents efficiently. The assistant can perform various actions such as:
- Listing incidents
- Getting incident details
- Closing incidents
- Managing rules
- Checking asset data

Built with Chainlit, the interface provides a chat experience with AI-powered assistance backed by Claude 3.5 Sonnet.

## Prerequisites

- Python 3.8+
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

3. Install dependencies
   ```bash
   uv install
   ```

4. Set up environment variables by creating a `.env` file with:
   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key
   API_TOKEN=your_sifflet_api_token
   ```

## Running the Application

1. Start the MCP server:
   ```bash
   uv run src/server.py
   ```

2. In a separate terminal, start the Chainlit application:
   ```bash
   uv run chainlit run src/app.py -w
   ```

3. Open your browser at the URL shown in the terminal (typically http://localhost:8000)

## Project Structure

- `src/app.py` - Main Chainlit application with Claude AI integration
- `src/server.py` - MCP server for handling Sifflet API interactions
- `.env` - Environment variables for API keys and credentials

## Development

To add new features or tools:
1. Add new tool functions in `server.py` using the `@mcp.tool` decorator
2. The assistant will automatically discover and use these tools
