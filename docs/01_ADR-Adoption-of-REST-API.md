# ADR: Adoption of REST API for Communication Between _db_handler_ and _events_reports_ Services

## Context
In this microservices architecture, db_handler is responsible for database access and business logic related to event data,
while events_reports is responsible for generating user-facing summaries of events.
These services must exchange data such as event metadata, time ranges, participants, and locations.
Several communication patterns were considered, including gRPC, direct database access, and message queues.
Ultimately, REST API over HTTP was chosen as the communication method between the services.

## Decision
_events_reports_ will communicate with _db_handler_ via REST API over HTTP,
using clearly defined endpoints to retrieve necessary data for report generation.

## Rationale
### Loose Coupling and Clear Interfaces
- REST APIs provide explicit boundaries and interface contracts between services.
- Encourages separation of concerns and avoids tight coupling between codebases.

### Simplicity and Familiarity
- REST over HTTP is a widely adopted standard, well understood by most developers.
- Simple to implement and debug using standard tools such as curl, Postman, or browser extensions.

### Environment Compatibility
- Works across environments without additional setup or protocol-specific tooling.
- Plays well with container orchestration systems and load balancers.

### Avoiding Shared Database Access
- Direct access from events_reports to the database managed by _db_handler_ would create tight coupling and break encapsulation.
- REST API ensures that _db_handler_ remains the single source of truth and gatekeeper for its data.

### Observability and Logging
- HTTP requests and responses can be easily logged, traced, and monitored.
- Enables clearer auditing of inter-service interactions and easier debugging in production.

### Scalability and Extensibility
- REST API can evolve independently from consumers, with versioning strategies if needed.
- Facilitates future use cases such as external clients, webhooks, or admin panels consuming the same data.

## Consequences
### Positive Outcomes
- Clean service boundaries and improved maintainability.
- Consistent, well-documented contract for inter-service communication.
- Easier to simulate and test via tools like Postman or FastAPI’s Swagger UI.
- Enables mocking in integration and end-to-end tests (e.g., using Postman Mock Server).

### Challenges & Mitigation
- Increased latency and overhead vs. internal in-process calls or shared memory – mitigated by internal network optimizations and caching.
- Schema mismatch risk between producer and consumer – mitigated by using shared schema definitions (e.g., Pydantic models) and contract testing.
- Lack of streaming – mitigated by using pagination or chunked responses if needed.

## Status


Accepted – REST API will be used for synchronous communication between _db_handler_ and _events_reports_, \
with future evaluation for potential optimization (e.g., introducing caching or gRPC for specific high-performance needs).