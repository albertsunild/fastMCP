import json
import os
from typing import Any, Dict, List, Literal
from fastmcp import FastMCP, Context
from fastmcp.server.dependencies import get_http_headers  # Import for headers access
import logging
from fastmcp.server.auth.providers.jwt import JWTVerifier


# Enable detailed logging
logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("fastmcp.server.context.to_client")
log.setLevel(logging.DEBUG)


OKTA_ISSUER = os.getenv("OIDC_ISSUER", "https://trial-9445494.okta.com/oauth2/default")
OKTA_AUDIENCE = os.getenv("OIDC_AUDIENCE", "api://default")

auth = JWTVerifier(
    jwks_uri=f"{OKTA_ISSUER}/v1/keys",     # Okta JWKS endpoint
    issuer=OKTA_ISSUER,                    # Must match the 'iss' in your token
    audience=OKTA_AUDIENCE,                # Must match 'aud' claim in your token
    algorithm="RS256",                      # Okta uses RS256 by default
    required_scopes= ["mcp.read", "mcp.write"]
)

# ============================================================
# MCP Server Setup
# ============================================================
mcp = FastMCP("Service_Awards_MCP_Server", 
              version="0.1.0",
              host="localhost",
              port=8080,
              stateless_http=True,
              #auth=auth
              )

# ------------------------------------------------------------
# Mock Data Directory
# ------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#MOCK_DATA_DIR = os.path.join(BASE_DIR,"..", "mock_data")
MOCK_DATA_DIR = os.path.join(BASE_DIR, "mock_data")
# ============================================================
# UNIVERSAL NORMALIZED MOCK LOADER
# Handles ANY JSON shape provided by the client.
# ============================================================
def load_mock(filename: str) -> Dict[str, Any]:
    """
    Loads a JSON file and normalizes its structure to avoid errors.
    Supports shapes:
      - dict
      - list of dicts
      - {"data": {...}}
      - [{"data": {...}}]
    Ensures tools can always access:
      celebration, celebrations, comments, people, comment, metadata
    """

    full_path = os.path.join(MOCK_DATA_DIR, filename)

    with open(full_path, "r") as f:
        raw = json.load(f)

    # If list → take first element
    if isinstance(raw, list):
        raw = raw[0] if raw else {}

    # If {"data": {...}} → unwrap
    if isinstance(raw, dict) and "data" in raw and isinstance(raw["data"], dict):
        raw = raw["data"]

    # Force dictionary
    if not isinstance(raw, dict):
        raw = {}

    # Normalize structure
    normalized = {
        "celebration": raw.get("celebration", {}),
        "celebrations": raw.get("celebrations", []),
        "comments": raw.get("comments", []),
        "people": raw.get("people", []),
        "comment": raw.get("comment", {}),
        "metadata": raw.get("metadata", {})
    }

    return normalized


# ============================================================
# TOOL 1: SEARCH CELEBRATIONS
# ============================================================
@mcp.tool(
    name="search_celebrations",
    description="Search for past or upcoming service anniversary celebrations."
)
def search_celebrations(
    #searchProperty: Literal["name", "email"] = "name",
    #searchQuery: str = "",
    team: Literal["my_team", "other_teams", "all"] = "my_team",
    timePeriod: Literal["future", "past"] = "future",
    notBeforeDate: str = "",
    notAfterDate: str = ""
) -> Dict[str, Any]:

    data = load_mock("20251107-mock-data-search_celebrations.json")
    celebrations = data["celebrations"]

    summary = f"{len(celebrations)} celebrations found."

    return {
        "summary": summary,
        "celebrations": celebrations,
        "metadata": {"totalCelebrations": len(celebrations)}
    }


# ============================================================
# TOOL 2: CELEBRATION CONTRIBUTIONS
# ============================================================
@mcp.tool(
    name="celebration_contributions",
    description="Retrieve all comments and replies for a given celebration."
)
def celebration_contributions(
    celebrationId: str
) -> Dict[str, Any]:

    data = load_mock("20251107-mock-data-celebration_contributions.json")

    # Ensure correct ID
    data["celebration"]["celebrationId"] = celebrationId

    return {
        "celebration": data["celebration"],
        "comments": data["comments"],
        "metadata": {"totalComments": len(data["comments"])}
    }


# ============================================================
# TOOL 3: COMMENT
# ============================================================
@mcp.tool(
    name="comment",
    description="Add a comment to a celebration."
)
def comment_tool(
    celebrationId: str,
    comment: str,
    isPrivate: bool = False
) -> Dict[str, Any]:

    data = load_mock("20251107-mock-data-comment.json")

    data["celebration"]["celebrationId"] = celebrationId
    data["comment"]["comment"] = comment
    data["comment"]["isPrivate"] = isPrivate

    return {
        "celebration": data["celebration"],
        "comment": data["comment"]
    }


# ============================================================
# TOOL 4: FIND INVITEES
# ============================================================
@mcp.tool(
    name="find_invitees",
    description="Search for internal people to invite to a celebration."
)

def find_invitees(
    searchProperty: Literal["name", "email"] = "name",
    searchQuery: str = ""
) -> Dict[str, Any]:
    data = load_mock("20251107-mock-data-find_invitees.json")
    people = data["people"]

    if searchProperty == "name":
        name = searchQuery.lower()
        person = [p for p in people if name in p["firstName"].lower() or name in p["lastName"].lower()]
        return {
            "people": person,
            "metadata": {"totalResults": len(person)}
        }

    elif searchProperty == "email":
        email = searchQuery.lower()
        person = [p for p in people if email in p["emailAddress"].lower()]
        return {
            "people": person,
            "metadata": {"totalResults": len(person)}
        }


    # return {
    #     "people": data["people"],
    #     "metadata": {"totalResults": len(data["people"])}
    # }


# ============================================================
# TOOL 5: INVITE FOR CELEBRATION
# ============================================================

@mcp.tool(
    name="invite",
    description="Invite a person to a celebration."
)
def invite(
    celebrationId: str,
    emailAddress: str
) -> Dict[str, Any]:

    data = load_mock("20251107-mock-data-invite.json")

    data["celebration"]["celebrationId"] = celebrationId
    data["celebration"]["emailAddress"] = emailAddress

    return{
        "celebration": data["celebration"],
        "metadata":  {"totalResults": len(data["celebration"])}
    }


@mcp.tool(
    name="add_numbers",
    description="To add two numbers"
)
async def add_numbers(a: float, b: float, ctx: Context) -> float:
    """Add two numbers."""
    # Access headers via dependency function
    headers = get_http_headers()
    await ctx.debug("Incoming headers for 'add':", extra={"headers": dict(headers)})  # Log as dict for cleaner output

    # Extract access token
    token = headers.get("authorization", "")
    if token:
        await ctx.info("Access token received", extra={"auth_preview": token[:20] + "..." if len(token) > 20 else token})
    else:
        await ctx.warning("No access token provided in headers")

    result = a + b
    await ctx.info(f"Computed: {a} + {b} = {result}")
    return result

# ===================================================
# RUN SERVER
# ===================================================
if __name__ == "__main__":
    #mcp.run()
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8080)
