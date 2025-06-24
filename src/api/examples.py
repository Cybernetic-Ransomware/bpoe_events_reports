"""
These examples are included in the OpenAPI schema, but are not rendered in Swagger UI for path parameters.

You can view them directly in the generated OpenAPI JSON:
    http://localhost:8080/openapi.json

This limitation affects all `examples` for `Path(...)`, `Query(...)`, etc. in Swagger UI,
although they are valid in the OpenAPI 3.1 spec and may be used by external tools.

The provided example UUIDs are prepared for use with a Postman Mock Server,
to enable quick testing of different response scenarios based on the event_id value.
"""


summary_event_id_examples = {
    "successUUID": {
        "summary": "Valid UUID",
        "value": "123e4567-e89b-12d3-a456-426614174000",
    },
    "failureUUID": {
        "summary": "Invalid UUID",
        "value": "abcdef12-3456-7890-abcd-ef1234512345",
    },
    "404": {
        "summary": "ExternalServiceUnexpectedError",
        "value": "abcdef12-3456-7890-abcd-ef1234567890",
    },
}
