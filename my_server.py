# import json
# import os
# from typing import Any, Dict, List, Literal, Annotated, Optional
# from fastmcp import FastMCP, Context
# from fastmcp.server.dependencies import get_http_headers  # Import for headers access
# import logging
# from fastmcp.server.auth.providers.jwt import JWTVerifier
# from datetime import datetime
# from pydantic import Field, StringConstraints



# # ============================================================
# # MCP Server Setup
# # ============================================================
# mcp = FastMCP()

# # ------------------------------------------------------------
# # Mock Data Directory
# # ------------------------------------------------------------

# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# #MOCK_DATA_DIR = os.path.join(BASE_DIR,"..", "mock_data")
# MOCK_DATA_DIR = os.path.join(BASE_DIR, "mock_data")
# # ============================================================
# # UNIVERSAL NORMALIZED MOCK LOADER
# # Handles ANY JSON shape provided by the client.
# # ============================================================
# def load_mock(filename: str) -> Dict[str, Any]:
#     """
#     Loads a JSON file and normalizes its structure to avoid errors.
#     Supports shapes:
#       - dict
#       - list of dicts
#       - {"data": {...}}
#       - [{"data": {...}}]
#     Ensures tools can always access:
#       celebration, celebrations, comments, people, comment, metadata
#     """

#     full_path = os.path.join(MOCK_DATA_DIR, filename)

#     with open(full_path, "r") as f:
#         raw = json.load(f)

#     # If list → take first element
#     if isinstance(raw, list):
#         raw = raw[0] if raw else {}

#     # If {"data": {...}} → unwrap
#     if isinstance(raw, dict) and "data" in raw and isinstance(raw["data"], dict):
#         raw = raw["data"]

#     # Force dictionary
#     if not isinstance(raw, dict):
#         raw = {}

#     # Normalize structure
#     normalized = {
#         "celebration": raw.get("celebration", {}),
#         "celebrations": raw.get("celebrations", []),
#         "comments": raw.get("comments", []),
#         "people": raw.get("people", []),
#         "comment": raw.get("comment", {}),
#         "metadata": raw.get("metadata", {})
#     }

#     return normalized


# # ============================================================
# # TOOL 1: SEARCH CELEBRATIONS
# # ============================================================
# @mcp.tool(
#     name="search_celebrations",
#     description="Search for past or upcoming service anniversary celebrations."
# )
# def search_celebrations(
#     notBeforeDate: Annotated[datetime | None, Field(description="Do not include celebrations with a date before this value")],
#     notAfterDate: Annotated[datetime | None, Field(description="Do not include celebrations with a date after this value")],
#     searchQuery: Annotated[Optional[Annotated[str, StringConstraints(min_length=2, strict=True)]],Field(description="String to search for in the search property")] = None,
#     searchProperty: Annotated[Literal["name", "email"], Field(description="Property to search by")] = "name",
#     team: Annotated[Literal["my_team", "other_teams", "all"], Field(description="Only show results for individuals that fit this team segmentation")] = "my_team",
#     timePeriod: Annotated[Literal["future", "past"], Field(description="Only show results that occurred in either the future or the past")] = "future"
#     ) -> Dict[str, Any]:

#     """
#     Search for service anniversary celebrations based on date range, team segmentation,
#     text search, and time period (future or past).

#     JSON Schema for tool parameters:
#     {
#     "type": "object",
#     "properties": {
#         "notBeforeDate": {
#         "type": ["string", "null"],
#         "format": "date-time",
#         "description": "Do not include celebrations with a date earlier than this value. Must be ISO-8601. Use null for no lower bound."
#         },
#         "notAfterDate": {
#         "type": ["string", "null"],
#         "format": "date-time",
#         "description": "Do not include celebrations with a date later than this value. Must be ISO-8601. Use null for no upper bound."
#         },
#         "searchQuery": {
#         "type": ["string", "null"],
#         "minLength": 2,
#         "description": "Text to search for within the selected searchProperty. Must be at least 2 characters. Use null for no keyword filter."
#         },
#         "searchProperty": {
#         "type": "string",
#         "enum": ["name", "email"],
#         "description": "Specifies which property to search in. 'name' searches by person’s full name; 'email' searches by email address."
#         },
#         "team": {
#         "type": "string",
#         "enum": ["my_team", "other_teams", "all"],
#         "description": "Filter celebrations by team segmentation. 'my_team' = only user's team; 'other_teams' = not user's team; 'all' = everyone."
#         },
#         "timePeriod": {
#         "type": "string",
#         "enum": ["future", "past"],
#         "description": "Filter celebrations by time period: 'future' = upcoming celebrations, 'past' = already occurred celebrations."
#         }
#     },
#     "required": ["notBeforeDate", "notAfterDate"]
#     }
#     """


#     data = load_mock("20251107-mock-data-search_celebrations.json")
#     celebrations = data["celebrations"]

#     summary = f"{len(celebrations)} celebrations found."

#     return {
#         "summary": summary,
#         "celebrations": celebrations,
#         "metadata": {"totalCelebrations": len(celebrations)}
#     }


# # ============================================================
# # TOOL 2: CELEBRATION CONTRIBUTIONS
# # ============================================================
# @mcp.tool(
#     name="celebration_contributions",
#     description="Retrieve all comments and replies for a given celebration."
# )
# def celebration_contributions(
#     celebrationId: str
# ) -> Dict[str, Any]:

#     data = load_mock("20251107-mock-data-celebration_contributions.json")

#     # Ensure correct ID
#     data["celebration"]["celebrationId"] = celebrationId

#     return {
#         "celebration": data["celebration"],
#         "comments": data["comments"],
#         "metadata": {"totalComments": len(data["comments"])}
#     }


# # ============================================================
# # TOOL 3: COMMENT
# # ============================================================
# @mcp.tool(
#     name="comment",
#     description="Add a comment to a celebration."
# )
# def comment_tool(
#     celebrationId: str,
#     comment: str,
#     isPrivate: bool = False
# ) -> Dict[str, Any]:

#     data = load_mock("20251107-mock-data-comment.json")

#     data["celebration"]["celebrationId"] = celebrationId
#     data["comment"]["comment"] = comment
#     data["comment"]["isPrivate"] = isPrivate

#     return {
#         "celebration": data["celebration"],
#         "comment": data["comment"]
#     }


# # ============================================================
# # TOOL 4: FIND INVITEES
# # ============================================================
# @mcp.tool(
#     name="find_invitees",
#     description="Search for internal people to invite to a celebration."
# )

# def find_invitees(
#     searchProperty: Literal["name", "email"] = "name",
#     searchQuery: str = ""
# ) -> Dict[str, Any]:
#     data = load_mock("20251107-mock-data-find_invitees.json")
#     people = data["people"]

#     if searchProperty == "name":
#         name = searchQuery.lower()
#         person = [p for p in people if name in p["firstName"].lower() or name in p["lastName"].lower()]
#         return {
#             "people": person,
#             "metadata": {"totalResults": len(person)}
#         }

#     elif searchProperty == "email":
#         email = searchQuery.lower()
#         person = [p for p in people if email in p["emailAddress"].lower()]
#         return {
#             "people": person,
#             "metadata": {"totalResults": len(person)}
#         }


#     # return {
#     #     "people": data["people"],
#     #     "metadata": {"totalResults": len(data["people"])}
#     # }


# # ============================================================
# # TOOL 5: INVITE FOR CELEBRATION
# # ============================================================

# @mcp.tool(
#     name="invite",
#     description="Invite a person to a celebration."
# )
# def invite(
#     celebrationId: str,
#     emailAddress: str
# ) -> Dict[str, Any]:

#     data = load_mock("20251107-mock-data-invite.json")

#     data["celebration"]["celebrationId"] = celebrationId
#     data["celebration"]["emailAddress"] = emailAddress

#     return{
#         "celebration": data["celebration"],
#         "metadata":  {"totalResults": len(data["celebration"])}
#     }



from fastmcp import FastMCP
import json

mcp = FastMCP("Demo 🚀")

@mcp.tool
def get_healthnav_links():
    """
    Returns HealthNav navigation and related links
    """

    RESPONSE_PAYLOAD = {
        "content": [
                    {
                    "type": "text",
                    "text": json.dumps({
                        "pageNavigationLink": {
                            "linkId": "MdclBnftsNoHpcc",
                            "linkAbsoluteURL": "<A>View page</A>"
                        },
                        "relatedLinks": [
                            {
                                "linkId": "HEALTHNAV_LANDING_PAGE",
                                "linkAbsoluteURL": "<A href=\"/web/testhealthnav05/healthcareNavigation\">HealthNav Landing Page</A>"
                            },
                            {
                                "linkId": "COMPASS_RECOMMENDATION_FIND_DOC_LNK",
                                "linkAbsoluteURL": "<A href=\"/web/testhealthnav05/healthcareNavigation/smartSelectMD\">Compass Recommendation Find Doc</A>"
                            }
                        ]
                    })
                }
            ],
            "isError": False
            }


    return RESPONSE_PAYLOAD

# if __name__ == "__main__":
    # mcp.run()
    # mcp.run(transport="streamable-http", host="127.0.0.1", port=8080)



# ===================================================
# RUN SERVER
# ===================================================
if __name__ == "__main__":
    #mcp.run()
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8080)
