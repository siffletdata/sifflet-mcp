import logging
import os
import argparse

import uvicorn
from dotenv import load_dotenv
from mcp.server import FastMCP
from mcp.server.sse import SseServerTransport
from sifflet_sdk.client import Configuration, ApiClient
from sifflet_sdk.client.api import incident_api, rule_api, asset_api
from sifflet_sdk.client.model.incident_scope import IncidentScope
from sifflet_sdk.client.model.incident_search_criteria import IncidentSearchCriteria
from sifflet_sdk.client.model.patch_incident_dto import PatchIncidentDto
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount, Route

# Create an MCP server
mcp = FastMCP("sifflet-mcp")

# Load environment variables
load_dotenv()

SIFFLET_API_TOKEN = os.environ.get("SIFFLET_API_TOKEN")
SIFFLET_BACKEND_URL = os.environ.get("SIFFLET_BACKEND_URL", "http://localhost:8090")
# API token & information
TOKEN_PREFIX = "Bearer "
HEADER_AUTHORISATION_NAME = "Authorization"
HEADER_APP_NAME = "X-Application-Name"

# Token types
PREDICTION_TOKEN_NAME = "prediction_jwt_token"
QUALITY_TOKEN_NAME = "quality_jwt_token"


def get_backend_api_client() -> ApiClient:
    configuration = Configuration(host=SIFFLET_BACKEND_URL)
    api_client = ApiClient(
        configuration,
        header_name=HEADER_AUTHORISATION_NAME,
        header_value=TOKEN_PREFIX + SIFFLET_API_TOKEN,
    )
    return api_client


@mcp.tool("asset_by_urn")
async def asset_by_urn(asset_urn: str) -> dict:
    asset_client = asset_api.AssetApi(get_backend_api_client())
    asset_details = asset_client.get_asset_by_urn(urn=asset_urn)
    return {"asset": asset_details}


# Add incident resource
@mcp.tool(
    "get_all_incidents",
    description="""
          Get all incidents. You can filter the incidents.
          Sort is done by createdAt by default. By default sort is descending. But you can change it using sort=asc.
          Status can be OPEN, IN_PROGRESS, CLOSED.
          User can be a list of users.
          Text search is a string.
          Pages start at 0.
          """,
)
def get_all_incidents(
    items_per_page: int,
    page: int,
    status: list[str],
    text_search: str,
    user: list[str],
    sort: str = "desc",
):
    if sort not in ["asc", "desc"]:
        raise ValueError("Sort must be either 'asc' or 'desc'")
    sort_list = ["createdDate,DESC"] if sort == "desc" else ["createdDate,ASC"]
    incident_search_criteria = IncidentSearchCriteria(
        items_per_page=items_per_page,
        page=page,
        sort=sort_list,
        status=status,
        text_search=text_search,
        user=user,
    )
    return {
        "incidents": incident_api.IncidentApi(
            get_backend_api_client()
        ).get_all_incident(incident_search_criteria)
    }


# Add incident resource
@mcp.tool("get_incident_by_issue_number")
def close_incident(issue_nbr: int) -> dict:
    return {
        "incident": incident_api.IncidentApi(
            get_backend_api_client()
        ).get_incident_by_issue_number(issue_nbr)
    }


@mcp.tool("get_incident_details_by_issue_number")
async def incident_tool(issue_number: int) -> dict:
    incident_scope: IncidentScope = incident_api.IncidentApi(
        get_backend_api_client()
    ).get_incident_scope_by_issue_number(issue_number)
    return {"incident_details": incident_scope}


@mcp.tool("get_rule_by_id")
async def get_rule_by_id(rule_id: int) -> dict:
    rule_api_client = rule_api.RuleApi(get_backend_api_client())
    rule_dto = rule_api_client.get_sifflet_rule_by_id(id=rule_id)
    return {"rule": rule_dto}


@mcp.tool("close_incident_by_id_and_should_qualify_monitor")
async def close_incident_by_id_and_should_qualify_monitor(
    incident_id: str, should_qualify_monitor: bool
) -> dict:
    incident_api_client = incident_api.IncidentApi(get_backend_api_client())
    if should_qualify_monitor:
        qualification = "QUALIFIED_MONITORS_REVIEWED"
    else:
        qualification = "REVIEWED"

    patch_incident_dto = PatchIncidentDto(
        status="CLOSED",
        qualification=qualification,
    )
    incident_api_client.patch_incident(
        id=incident_id, patch_incident_dto=patch_incident_dto
    )


@mcp.tool("open_incident_by_id")
async def open_incident_by_id(incident_id: str) -> dict:
    incident_api_client = incident_api.IncidentApi(get_backend_api_client())

    patch_incident_dto = PatchIncidentDto(status="OPEN", qualification=None)
    incident_api_client.patch_incident(
        id=incident_id, patch_incident_dto=patch_incident_dto
    )


def run_starlette_sse():
    # Set up the SSE transport for MCP communication.
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
        _server = mcp._mcp_server
        async with sse.connect_sse(
            request.scope,
            request.receive,
            request._send,
        ) as (reader, writer):
            await _server.run(reader, writer, _server.create_initialization_options())

    # Create the Starlette app with two endpoints
    app = Starlette(
        debug=True,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )

    # Start the server
    uvicorn.run(app, host="localhost", port=8007)


def run_server():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sse", action="store_true", help="Run the server in SSE mode")
    args = parser.parse_args()
    if args.sse:
        logging.info("Starting MCP server SSE mode with Starlette")
        run_starlette_sse()
    else:
        logging.info("Starting MCP server stdio mode")
        mcp.run()


if __name__ == "__main__":
    run_server()
