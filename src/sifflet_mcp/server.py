import argparse
import logging
import os
from typing import List

import uvicorn
from dotenv import load_dotenv
from mcp.server import FastMCP
from mcp.server.sse import SseServerTransport
from sifflet_sdk.client import Configuration, ApiClient, PublicTagReferenceDto
from sifflet_sdk.client.api import (
    incident_api,
    rule_api,
    asset_api,
    text_to_monitor_api,
    assets_api,
    lineage_api,
)
from sifflet_sdk.client.models.asset_dto import AssetDto
from sifflet_sdk.client.models.incident_scope import IncidentScope
from sifflet_sdk.client.models.incident_search_criteria import IncidentSearchCriteria
from sifflet_sdk.client.models.issue_details_dto import IssueDetailsDto
from sifflet_sdk.client.models.lineage_entity_dto import LineageEntityDto
from sifflet_sdk.client.models.patch_incident_dto import PatchIncidentDto
from sifflet_sdk.client.models.public_asset_filter_dto import PublicAssetFilterDto
from sifflet_sdk.client.models.public_asset_pagination_dto import (
    PublicAssetPaginationDto,
)
from sifflet_sdk.client.models.public_asset_search_criteria_dto import (
    PublicAssetSearchCriteriaDto,
)
from sifflet_sdk.client.models.public_page_dto_public_get_asset_list_dto import (
    PublicPageDtoPublicGetAssetListDto,
)
from sifflet_sdk.client.models.public_reference_by_id_or_email_dto import (
    PublicReferenceByIdOrEmailDto,
)
from sifflet_sdk.client.models.text_to_monitor_request_dto import (
    TextToMonitorRequestDto,
)
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount, Route

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
SIFFLET_API_TOKEN = os.environ.get("SIFFLET_API_TOKEN")
SIFFLET_BACKEND_URL = os.environ.get("SIFFLET_BACKEND_URL")

# Create the MCP server
mcp = FastMCP("sifflet-mcp")


def get_backend_api_client() -> ApiClient:
    # API token & information
    token_prefix = "Bearer "
    header_authorization_name = "Authorization"

    if SIFFLET_API_TOKEN is None:
        logger.error(
            "SIFFLET_API_TOKEN environment variable not set in Sifflet MCP configuration"
        )
        raise ValueError("SIFFLET_API_TOKEN environment variable not set")
    if SIFFLET_BACKEND_URL is None:
        logger.error("SIFFLET_BACKEND_URL environment variable not set")
        raise ValueError(
            "SIFFLET_BACKEND_URL environment variable not set in Sifflet MCP configuration"
        )

    configuration = Configuration(host=SIFFLET_BACKEND_URL)
    api_client = ApiClient(
        configuration,
        header_name=header_authorization_name,
        header_value=token_prefix + SIFFLET_API_TOKEN,
    )
    return api_client


@mcp.tool(
    "asset_by_urn",
    description="""
        Get asset information by urn. The urn is the unique identifier a asset, for example dataset:0826ce5c-7027-4857-aa47-b639265d1867. It can be found when you search for an asset.
        """,
)
async def asset_by_urn(asset_urn: str) -> dict:
    asset_client = asset_api.AssetApi(get_backend_api_client())
    asset_details: AssetDto = asset_client.get_asset_by_urn(urn=asset_urn)
    return {"asset": asset_details.to_dict()}


@mcp.tool(
    "search_asset",
    description="""
        Search assets, tables, dashboards, pipelines.
        asset_type can be one of the following: TABLE_AND_VIEW, PIPELINE, DASHBOARD, ML_MODEL
        health_status can be one of the following: URGENT_INCIDENTS, HIGH_RISK_INCIDENTS, NO_INCIDENTS, NOT_MONITORED, UNSUPPORTED
        owners is a list of owners emails associated with the asset
        tags is a list of tags associated with the asset
        text_search is a string to search in the asset name or description
        items_per_page is the number of items to return per page
        page is the page number to return. Pages start at 0.
        """,
)
async def search_asset(
    items_per_page: int,
    page: int,
    text_search: str,
    asset_type: List[str],
    health_status: List[str],
    owners_email: List[str],
    tags: List[str],
) -> dict:
    # use public API
    asset_client = assets_api.AssetsApi(get_backend_api_client())
    owners_list = [PublicReferenceByIdOrEmailDto(email=owner) for owner in owners_email]
    tag_list = [PublicTagReferenceDto(name=tag) for tag in tags]

    asset_search_criteria = PublicAssetSearchCriteriaDto(
        pagination=PublicAssetPaginationDto(
            itemsPerPage=items_per_page,
            page=page,
        ),
        filter=PublicAssetFilterDto(
            textSearch=text_search,
            assetType=asset_type,
            healthStatus=health_status,
            owners=owners_list,
            tags=tag_list,
        ),
    )
    asset_details: PublicPageDtoPublicGetAssetListDto = asset_client.public_get_assets(
        asset_search_criteria
    )
    return {"assets": asset_details.to_dict()}


# Add incident resource
@mcp.tool(
    "search_incidents",
    description="""
          Search incidents
          Sort is done by createdAt by default. By default sort is descending. But you can change it using sort=asc.
          You can filter by status, user and text search.
          Status can be OPEN, IN_PROGRESS, CLOSED.
          Text search is a string.
          Pages start at 0.
          """,
)
async def search_incidents(
    items_per_page: int,
    page: int,
    status: list[str],
    text_search: str,
    sort: str = "desc",
) -> dict:
    if sort not in ["asc", "desc"]:
        raise ValueError("Sort must be either 'asc' or 'desc'")
    sort_list = ["createdDate,DESC"] if sort == "desc" else ["createdDate,ASC"]
    incident_search_criteria = IncidentSearchCriteria(
        itemsPerPage=items_per_page,
        page=page,
        sort=sort_list,
        status=status,
        textSearch=text_search,
    )
    return {
        "incidents": incident_api.IncidentApi(get_backend_api_client())
        .get_all_incident(incident_search_criteria)
        .to_dict()
    }


# Add incident resource
@mcp.tool(
    "get_incident_by_issue_number",
    description="""
        Get incident details by issue number. The issue number is the unique identifier of the incident, for example 1234.
        """,
)
async def get_incident_details_by_issue_number(issue_nbr: int) -> dict:
    incident_details: IssueDetailsDto = incident_api.IncidentApi(
        get_backend_api_client()
    ).get_incident_by_issue_number(issue_nbr)
    return {"incident": incident_details.to_dict()}


@mcp.tool(
    "get_incident_scope_by_issue_number",
    description="""
        Get incident scope by issue number. The issue number is the unique identifier of the incident, for example 1234.
        The scope is the list of assets and monitors associated with the incident.
        """,
)
async def get_incident_scope_by_issue_number(issue_number: int) -> dict:
    incident_scope: IncidentScope = incident_api.IncidentApi(
        get_backend_api_client()
    ).get_incident_scope_by_issue_number(issue_number)
    return {"incident_details": incident_scope.to_dict()}


@mcp.tool(
    "get_monitor_details_by_id",
    description="""
        Get monitor details by id. 
        The monitor_id is the monitor UUID. The id can be found when you search for a monitor.
        monitor_id is the unique identifier of the monitor, for example 3b8a1333-aef0-468a-893b-e87dfc095c82
        """,
)
async def get_monitor_details_by_id(monitor_id: str) -> dict:
    rule_api_client = rule_api.RuleApi(get_backend_api_client())
    rule_dto = rule_api_client.get_sifflet_rule_details(id=monitor_id)
    return {"monitor": rule_dto.to_dict()}


@mcp.tool(
    "close_incident_by_id",
    description="""
        Close an incident by id. The id is the unique identifier of the incident, for example 1234.
        The should_qualify_monitor is a boolean that indicates if the monitor should be qualified or not.
        """,
)
async def close_incident_by_id(incident_id: str, should_qualify_monitor: bool) -> dict:
    incident_api_client = incident_api.IncidentApi(get_backend_api_client())
    if should_qualify_monitor:
        qualification = "QUALIFIED_MONITORS_REVIEWED"
    else:
        qualification = "REVIEWED"

    patch_incident_dto = PatchIncidentDto(
        status="CLOSED",
        qualification=qualification,
    )
    result = incident_api_client.patch_incident(
        id=incident_id, patch_incident_dto=patch_incident_dto
    ).to_dict()
    return {"incident": result}


@mcp.tool(
    "open_incident_by_id",
    description="""
        Open an incident by id. The id is the unique identifier of the incident, for example 1234.
        """,
)
async def open_incident_by_id(incident_id: str) -> dict:
    incident_api_client = incident_api.IncidentApi(get_backend_api_client())

    patch_incident_dto = PatchIncidentDto(status="OPEN", qualification=None)
    result = incident_api_client.patch_incident(
        id=incident_id, patch_incident_dto=patch_incident_dto
    ).to_dict()
    return {"incident": result}


# Monitor as code
@mcp.tool(
    "get_monitor_code_by_description",
    description="""
        Returns a monitor configuration based on the input query
        The input is a description of the monitor you want to create.
        The description should be a natural language description of the monitor you want to create.
        The dataset_ids is a list of dataset ids that the monitor should be applied to. You must provide at least one dataset id. You can find the id of the dataset using search_asset. 
        The description is a string that describes the monitor you want to create. For example: "Create a monitor that checks if the number of rows in the table is greater than 1000".
        The result is a YAML string that contains the monitor configuration.
        """,
)
async def get_monitor_code_by_description(
    description: str, dataset_ids: list[str]
) -> dict:
    text_to_monitor_client = text_to_monitor_api.TextToMonitorApi(
        get_backend_api_client()
    )
    text_to_monitor_dto = TextToMonitorRequestDto(
        datasetIds=dataset_ids, inputText=description
    )
    generated_monitor = text_to_monitor_client.text_to_monitor(text_to_monitor_dto)
    return generated_monitor.yaml_code


@mcp.tool(
    "get_downstream_assets_of_asset",
    description="""
          Get all downstream assets of an asset. An Urn is the unique identifier of an asset, for example dataset:0826ce5c-7027-4857-aa47-b639265d1867. It can be found when you search for an asset.
          """,
)
async def get_downstream_assets_of_asset(urn: str) -> dict:
    lineage_api_client = lineage_api.LineageApi(get_backend_api_client())
    downstreams: List[LineageEntityDto] = (
        lineage_api_client.get_lineage_downstreams_by_urn(urn=urn)
    )
    dict_downstream = list(map(lambda x: x.to_dict(), downstreams))
    return {"downstreams": dict_downstream}


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
        logger.info("Starting MCP server SSE mode with Starlette")
        run_starlette_sse()
    else:
        logger.info("Starting MCP server stdio mode")
        mcp.run()


if __name__ == "__main__":
    run_server()
