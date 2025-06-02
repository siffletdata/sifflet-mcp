# Contributing

## Environment Setup
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

## New tools
To add new features or tools:

1. Add new tool functions in `server.py` using the `@mcp.tool` decorator
2. The server will automatically discover and use these tools
