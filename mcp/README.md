# mcp/ — source-system MCP servers

One MCP server per source system (APM, traces, logs, RUM, work-order, wiki, …) so private
corpora and source data stay in the operator's environment. The core talks to these servers
and never holds long-lived source credentials directly (`docs/architecture.md §5`). Built in
**Phase 5**.
