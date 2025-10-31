import uuid
from datetime import datetime, timezone, timedelta
from fastmcp import FastMCP
from pydantic import BaseModel, Field

# ===================================================
# FastMCP Server Setup
# ===================================================
mcp = FastMCP("Service_Anniversary_MCP_Server")

# ===================================================
# MOCK HELPERS
# ===================================================
def _mock_person(i: int) -> dict:
    """Generate mock person details for demonstration."""
    return {
        "rosterPersonId": str(uuid.uuid4()),
        "firstName": f"User{i}",
        "lastName": "Example",
        "emailAddress": f"user{i}@example.com",
        "avatarUrl": "https://example.com/avatar.png",
        "jobTitle": "Software Engineer",
        "isInMyTeam": (i % 2 == 0)
    }

def _mock_celebration(i: int) -> dict:
    """Generate mock celebration details for demonstration."""
    now = datetime.now(timezone.utc)
    return {
        "celebrationId": str(uuid.uuid4()),
        "milestoneName": f"Service Anniversary {i}",
        "date": (now + timedelta(days=(i * 7))).isoformat(),
        "imageUrl": "https://example.com/milestone.png",
        "totalInvites": 5 + i,
        "canContribute": True,
        "hasContributed": (i % 2 == 0),
        "hasCelebratorThanked": (i % 3 == 0),
        "allowPrivateComments": True,
        "thankYouMessage": {
            "comment": "Thanks team!",
            "totalLikes": i
        },
        "celebrator": _mock_person(i)
    }

def _mock_person_search(query: str, limit: int = 5):
    """Generate mock person search results."""
    results = []
    for i in range(1, limit + 1):
        results.append({
            "rosterPersonId": str(uuid.uuid4()),
            "firstName": f"{query.capitalize()}_{i}",
            "lastName": "Example",
            "emailAddress": f"{query.lower()}{i}@example.com",
            "avatarUrl": "https://example.com/avatar.png",
            "jobTitle": "Software Engineer",
            "isCurrentUser": False
        })
    return results

# ===================================================
# TOOL IMPLEMENTATIONS
# ===================================================


mcp=FastMCP('mcp_biw_toolkit')

class Pagination(BaseModel):
    limit: int = Field("limit")
    cursor: int = Field("cursor")

class Filters(BaseModel):
    team: str = Field()
    timePeriod: str = Field()
    notBeforeDate: str = Field()
    notAfterDate: str = Field()

class Search(BaseModel):
    by: str = Field()
    identifier: str = Field()

class QueryFields(BaseModel):
    search: Search = Field(default_factory=Search)
    pagination: Pagination = Field(default_factory=Pagination)
    filters: Filters = Field(default_factory=Filters)

class Query(BaseModel):
    query: QueryFields = Field(default_factory=QueryFields,description="query felds")

@mcp.tool(name="search")
def search(query: Query) -> dict:
    """
    Search for service anniversary celebrations based on criteria.
    args:
        query (Query): The search query parameters.
    returns:
        dict: A dictionary containing the search results and metadata.
    """
    limit = query.query.pagination.limit
    cursor = query.query.pagination.cursor

    celebrations = [_mock_celebration(i + cursor + 1) for i in range(limit)]
    metadata = {"total": 100, "nextCursor": cursor + limit}

    return {"celebrations": celebrations, "metadata": metadata}

# search_input_schema = {
#     "type": "object",
#     "properties": {
#         "query": {
#         "type": "object",
#         "properties": {
#             "search": {
#             "type": "object",
#             "properties": {
#                 "by": { "type": "string", "enum": ["email", "name"] },
#                 "identifier": { "type": "string" }
#             },
#             "required": ["by", "identifier"]
#             },
#             "filters": {
#             "type": "object",
#             "properties": {
#                 "team": { "type": "string", "enum": ["my_team", "other_teams", "all"] },
#                 "timePeriod": { "type": "string", "enum": ["future", "past"] },
#                 "notBeforeDate": { "type": "string", "format": "date" },
#                 "notAfterDate": { "type": "string", "format": "date" }
#             }
#             },
#             "pagination": {
#             "type": "object",
#             "properties": {
#                 "limit": { "type": "integer" },
#                 "cursor": { "type": "integer" }
#             }
#             }
#         }
#         }
#     }
# }

# @mcp.tool(
#     # name="search",
#     # description="Search for service anniversary celebrations based on criteria.",
#     #input_schema=search_input_schema
# )

# def search(query: dict) -> dict:
#     """
#     Search for service anniversary celebrations based on criteria.
#     args:
#         {
#             "type": "object",
#             "properties": {
#                 "query": {
#                 "type": "object",
#                 "properties": {
#                     "search": {
#                     "type": "object",
#                     "properties": {
#                         "by": { "type": "string", "enum": ["email", "name"] },
#                         "identifier": { "type": "string" }
#                     },
#                     "required": ["by", "identifier"]
#                     },
#                     "filters": {
#                     "type": "object",
#                     "properties": {
#                         "team": { "type": "string", "enum": ["my_team", "other_teams", "all"] },
#                         "timePeriod": { "type": "string", "enum": ["future", "past"] },
#                         "notBeforeDate": { "type": "string", "format": "date" },
#                         "notAfterDate": { "type": "string", "format": "date" }
#                     }
#                     },
#                     "pagination": {
#                     "type": "object",
#                     "properties": {
#                         "limit": { "type": "integer" },
#                         "cursor": { "type": "integer" }
#                     }
#                     }
#                 }
#                 }
#             }
#         }
    
#     """
#     pagination = query.get("pagination", {})
#     limit = int(pagination.get("limit", 5))
#     cursor = int(pagination.get("cursor", 0))

#     celebrations = [_mock_celebration(i + cursor + 1) for i in range(limit)]
#     metadata = {"total": 100, "nextCursor": cursor + limit}

#     return {"celebrations": celebrations, "metadata": metadata}

@mcp.tool(
    name="get_full_name", description="""
    Get the full name of a person given their first and last names.
    args:
        first_name (str): The first name of the person.
        last_name (str): The last name of the person.
        returns:
        str: The full name of the person in the format "First Last".
    example:
        Input:
        first_name: "John"
        last_name: "Doe"
        Output:
        "John Doe"
    """)
def get_full_name(first_name: str, last_name: str) -> str:
    return f"{first_name} {last_name}"

@mcp.tool()    
def get_personal_details(first_name: str, last_name: str, email_address: str, company_name: str ) -> dict:
    """
    Get the personal details of a person given their first and last names, email address and company name.
          args: 
          first_name (str): The first name of the person.
          last_name (str): The last name of the person.
          email_address (str): The email address of the person.
          returns:
          dict: A dictionary containing the personal details of the person.
              {
                  "firstName": "string",
                  "lastName": "string",
                  "emailAddress": "string",
                  "fullName": "string",
                    "company_name": "string"
              }
          example:
              Input:
              first_name: "John"
              last_name: "Doe"
              email_address: "john.doe@example.com"
            company_name: "example.Inc"
                Output:
                {
                    "firstName": "John",
                    "lastName": "Doe",
                    "emailAddress": "john.doe@exampl.com",
                    "fullName": "John Doe",
                    "company_name": "example.Inc"
                }
    """
    full_name = get_full_name(first_name, last_name)
    return {
        "firstName": first_name,
        "lastName": last_name,
        "emailAddress": email_address,
        "fullName": full_name,
        "company_name": company_name
    }   

@mcp.tool(
    name="celebration_contributions",
    description="""
    Retrieve comments and replies contributed to a specific celebration.

    args:
        query (dict): {
            "celebrationId": "uuid",
            "cursor": "uuid"
        }

    returns:
        dict: {
            "celebration": {...},
            "comments": [...],
            "metadata": {"totalComments": int, "nextCursor": "uuid"}
        }

    example:
        Input:
        {
            "celebrationId": "123e4567-e89b-12d3-a456-426614174000",
            "cursor": "00000000-0000-0000-0000-000000000000"
        }

        Output:
        {
            "celebration": {...},
            "comments": [...],
            "metadata": {"totalComments": 1, "nextCursor": "uuid"}
        }
    """
)
def celebration_contributions(query: dict) -> dict:
    celebration = _mock_celebration(1)
    contributor = {
        "rosterPersonId": str(uuid.uuid4()),
        "firstName": "John",
        "lastName": "Doe",
        "emailAddress": "john.doe@example.com",
        "avatarUrl": "https://example.com/john.png",
        "jobTitle": "Engineer",
        "isCurrentUser": False
    }
    replies = [{
        "commentId": str(uuid.uuid4()),
        "isPrivate": False,
        "totalLikes": 1,
        "comment": "Nice work!",
        "contributor": contributor,
        "replies": []
    }]
    comments = [{
        "commentId": str(uuid.uuid4()),
        "isPrivate": False,
        "totalLikes": 5,
        "comment": "Congratulations on your milestone!",
        "contributor": contributor,
        "replies": replies
    }]
    metadata = {"totalComments": len(comments), "nextCursor": str(uuid.uuid4())}

    return {"celebration": celebration, "comments": comments, "metadata": metadata}


@mcp.tool(
    name="comment",
    description="""
    Add or reply to a comment on a celebration.

    args:
        query (dict): {
            "celebrationId": "uuid",
            "commentId": "uuid",
            "comment": "string",
            "isPrivate": bool
        }

    returns:
        dict: {
            "celebration": {...},
            "comment": {...}
        }

    example:
        Input:
        {
            "celebrationId": "123e4567-e89b-12d3-a456-426614174000",
            "commentId": "11111111-2222-3333-4444-555555555555",
            "comment": "Congratulations!",
            "isPrivate": false
        }

        Output:
        {
            "celebration": {...},
            "comment": {
                "commentId": "uuid",
                "isPrivate": false,
                "totalLikes": 0,
                "comment": "Congratulations!",
                "contributor": {...}
            }
        }
    """
)
def comment(query: dict) -> dict:
    celebration = _mock_celebration(1)
    contributor = {
        "rosterPersonId": str(uuid.uuid4()),
        "firstName": "Madan",
        "lastName": "Shetty",
        "emailAddress": "madan.shetty@example.com",
        "avatarUrl": "https://example.com/avatar_madan.png",
        "jobTitle": "Software Engineer",
        "isCurrentUser": True
    }
    new_comment = {
        "commentId": str(uuid.uuid4()),
        "isPrivate": query.get("isPrivate", False),
        "totalLikes": 0,
        "comment": query.get("comment", ""),
        "contributor": contributor
    }

    return {"celebration": celebration, "comment": new_comment}


@mcp.tool(
    name="invite",
    description="""
    Invite contributors (internal or external) to a celebration.

    args:
        query (dict): {
            "celebrationId": "uuid",
            "byRosterPersonId": [{"rosterPersonId": "uuid"}],
            "byEmailAddress": [{"emailAddress": "string", "firstName": "string", "lastName": "string"}]
        }

    returns:
        dict: {
            "celebration": {...},
            "invitationSummary": {"invitesSent": int, "alreadyInvited": int},
            "invitedContributors": [...],
            "suggestedInvitees": [...]
        }

    example:
        Input:
        {
            "celebrationId": "123e4567-e89b-12d3-a456-426614174000",
            "byRosterPersonId": [{"rosterPersonId": "uuid"}],
            "byEmailAddress": [{"emailAddress": "abc@example.com", "firstName": "Amit", "lastName": "Kumar"}]
        }

        Output:
        {
            "celebration": {...},
            "invitationSummary": {"invitesSent": 2, "alreadyInvited": 1},
            "invitedContributors": [...],
            "suggestedInvitees": [...]
        }
    """
)
def invite(query: dict) -> dict:
    celebration = _mock_celebration(1)
    summary = {"invitesSent": 2, "alreadyInvited": 1}
    invited_contributors = [
        {"emailAddress": "jane.doe@example.com", "firstName": "Jane", "lastName": "Doe"},
        {"emailAddress": "john.smith@example.com", "firstName": "John", "lastName": "Smith"}
    ]
    suggested_invitees = [
        {"rosterPersonId": str(uuid.uuid4()), "firstName": "Amit", "lastName": "Kumar"},
        {"rosterPersonId": str(uuid.uuid4()), "firstName": "Priya", "lastName": "Sharma"}
    ]
    return {
        "celebration": celebration,
        "invitationSummary": summary,
        "invitedContributors": invited_contributors,
        "suggestedInvitees": suggested_invitees
    }


@mcp.tool(
    name="find_invitees",
    description="""
    Search for internal people to invite to a celebration.

    args:
        query (dict): {
            "search": {"by": "name"|"email", "query": "string"},
            "celebrationId": "uuid"
        }

    returns:
        dict: {
            "people": [...],
            "metadata": {"totalResults": int}
        }

    example:
        Input:
        {
            "search": {"by": "name", "query": "John"},
            "celebrationId": "123e4567-e89b-12d3-a456-426614174000"
        }

        Output:
        {
            "people": [...],
            "metadata": {"totalResults": 5}
        }
    """
)
def find_invitees(query: dict) -> dict:
    search_data = query.get("search", {})
    query_str = search_data.get("query", "")
    people = _mock_person_search(query_str, 5)
    metadata = {"totalResults": len(people)}
    return {"people": people, "metadata": metadata}


# ===================================================
# RUN SERVER
# ===================================================
if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="127.0.0.1", port=8080)
    #mcp.run()  # for local testing
    #mcp.run(transport="http", host="127.0.0.1", port=8000)
