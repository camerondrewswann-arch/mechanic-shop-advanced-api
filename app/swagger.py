def build_swagger_spec(host: str, schemes: list[str]) -> dict:
    """Return the Swagger 2.0 document displayed at /docs."""
    bearer_security = [{"BearerAuth": []}]

    return {
        "swagger": "2.0",
        "info": {
            "title": "Mechanic Shop Advanced API",
            "version": "1.0.0",
            "description": (
                "Manage customers, mechanics, service tickets, and inventory. "
                "Protected endpoints require an Authorization header formatted as "
                "Bearer <token>."
            ),
        },
        # Render requires the hostname only here—no https:// prefix.
        "host": host,
        "basePath": "/",
        "schemes": schemes,
        "consumes": ["application/json"],
        "produces": ["application/json"],
        "securityDefinitions": {
            "BearerAuth": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "Enter: Bearer YOUR_TOKEN",
            }
        },
        "definitions": {
            "Login": {
                "type": "object",
                "required": ["email", "password"],
                "properties": {
                    "email": {"type": "string", "format": "email"},
                    "password": {"type": "string", "format": "password"},
                },
            },
            "InventoryPayload": {
                "type": "object",
                "required": ["name", "price"],
                "properties": {
                    "name": {"type": "string", "example": "Brake Pad"},
                    "price": {"type": "number", "format": "float", "example": 49.99},
                },
            },
            "TicketEditPayload": {
                "type": "object",
                "required": ["add_ids", "remove_ids"],
                "properties": {
                    "add_ids": {"type": "array", "items": {"type": "integer"}},
                    "remove_ids": {"type": "array", "items": {"type": "integer"}},
                },
            },
        },
        "paths": {
            "/health": {
                "get": {
                    "tags": ["Health"],
                    "summary": "Verify the deployed API is running",
                    "responses": {"200": {"description": "Healthy service"}},
                }
            },
            "/customers/login": {
                "post": {
                    "tags": ["Customers"],
                    "summary": "Log in a customer and receive a JWT",
                    "parameters": [
                        {
                            "in": "body",
                            "name": "body",
                            "required": True,
                            "schema": {"$ref": "#/definitions/Login"},
                        }
                    ],
                    "responses": {
                        "200": {"description": "Token returned"},
                        "401": {"description": "Invalid credentials"},
                        "429": {"description": "Rate limit exceeded"},
                    },
                }
            },
            "/customers/": {
                "get": {
                    "tags": ["Customers"],
                    "summary": "Return paginated customers",
                    "parameters": [
                        {"name": "page", "in": "query", "type": "integer", "default": 1},
                        {"name": "per_page", "in": "query", "type": "integer", "default": 5},
                    ],
                    "responses": {"200": {"description": "Paginated customer results"}},
                }
            },
            "/customers/my-tickets": {
                "get": {
                    "tags": ["Customers"],
                    "summary": "Return tickets owned by the authenticated customer",
                    "security": bearer_security,
                    "responses": {
                        "200": {"description": "Customer tickets"},
                        "401": {"description": "Missing or invalid token"},
                    },
                }
            },
            "/mechanics/login": {
                "post": {
                    "tags": ["Mechanics"],
                    "summary": "Log in a mechanic and receive a mechanic JWT",
                    "parameters": [
                        {
                            "in": "body",
                            "name": "body",
                            "required": True,
                            "schema": {"$ref": "#/definitions/Login"},
                        }
                    ],
                    "responses": {"200": {"description": "Token returned"}},
                }
            },
            "/mechanics/ranked": {
                "get": {
                    "tags": ["Mechanics"],
                    "summary": "Rank mechanics by number of assigned tickets",
                    "responses": {"200": {"description": "Ranked mechanics"}},
                }
            },
            "/inventory/": {
                "get": {
                    "tags": ["Inventory"],
                    "summary": "List all inventory parts",
                    "responses": {"200": {"description": "Inventory list"}},
                },
                "post": {
                    "tags": ["Inventory"],
                    "summary": "Create an inventory part",
                    "security": bearer_security,
                    "parameters": [
                        {
                            "in": "body",
                            "name": "body",
                            "required": True,
                            "schema": {"$ref": "#/definitions/InventoryPayload"},
                        }
                    ],
                    "responses": {
                        "201": {"description": "Part created"},
                        "401": {"description": "Mechanic token required"},
                    },
                },
            },
            "/inventory/{item_id}": {
                "get": {
                    "tags": ["Inventory"],
                    "summary": "Get one inventory part",
                    "parameters": [
                        {"name": "item_id", "in": "path", "required": True, "type": "integer"}
                    ],
                    "responses": {"200": {"description": "Inventory part"}},
                },
                "put": {
                    "tags": ["Inventory"],
                    "summary": "Update an inventory part",
                    "security": bearer_security,
                    "parameters": [
                        {"name": "item_id", "in": "path", "required": True, "type": "integer"},
                        {
                            "in": "body",
                            "name": "body",
                            "schema": {"$ref": "#/definitions/InventoryPayload"},
                        },
                    ],
                    "responses": {"200": {"description": "Part updated"}},
                },
                "delete": {
                    "tags": ["Inventory"],
                    "summary": "Delete an inventory part",
                    "security": bearer_security,
                    "parameters": [
                        {"name": "item_id", "in": "path", "required": True, "type": "integer"}
                    ],
                    "responses": {"200": {"description": "Part deleted"}},
                },
            },
            "/service-tickets/{ticket_id}/edit": {
                "put": {
                    "tags": ["Service Tickets"],
                    "summary": "Add and remove mechanics from a ticket",
                    "security": bearer_security,
                    "parameters": [
                        {"name": "ticket_id", "in": "path", "required": True, "type": "integer"},
                        {
                            "in": "body",
                            "name": "body",
                            "required": True,
                            "schema": {"$ref": "#/definitions/TicketEditPayload"},
                        },
                    ],
                    "responses": {"200": {"description": "Ticket mechanics updated"}},
                }
            },
            "/service-tickets/{ticket_id}/add-part/{part_id}": {
                "put": {
                    "tags": ["Service Tickets"],
                    "summary": "Attach one inventory part to a service ticket",
                    "security": bearer_security,
                    "parameters": [
                        {"name": "ticket_id", "in": "path", "required": True, "type": "integer"},
                        {"name": "part_id", "in": "path", "required": True, "type": "integer"},
                    ],
                    "responses": {"200": {"description": "Part attached to ticket"}},
                }
            },
        },
    }
