"""Library connector v0: a local, read-only MCP server over one newsletters Library.

Run:  python mcp/library/server.py --library /path/to/<library>
  or: NEWSLETTERS_LIBRARY=/path/to/<library> python mcp/library/server.py

Three tools, all read-only: list_editions, read_edition, search_library.
Transport: stdio only (local). No writes, no auth, no network. See spec.md in
docs/runs/2026-11-07/lanes/D-connector/.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from library_reader import Library, LibraryError  # noqa: E402

try:  # MCP Python SDK 2.x
    from mcp.server.mcpserver import MCPServer as _Server
    from mcp.server.mcpserver.exceptions import ToolError
except ImportError:  # MCP Python SDK 1.x
    from mcp.server.fastmcp import FastMCP as _Server  # type: ignore[no-redef]
    from mcp.server.fastmcp.exceptions import ToolError  # type: ignore[no-redef]

from mcp.types import ToolAnnotations  # noqa: E402

READ_ONLY = ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)

INSTRUCTIONS = (
    "This server reads one newsletters Library: the published editions (reports, newsletters, "
    "articles, shows, learning) of one organization. It is read-only and serves Published "
    "editions only. Use list_editions to see what exists, search_library to find where a topic "
    "is discussed, and read_edition to read one in full. Quote editions faithfully and name the "
    "edition (title and ref) you are quoting."
)


def build_server(library_path: str | Path):
    library = Library(library_path)
    server = _Server(name="newsletters-library", instructions=INSTRUCTIONS)

    @server.tool(annotations=READ_ONLY)
    def list_editions() -> dict:
        """List the published editions in this Library: slug, ref, type, title, issue, date.
        Also reports how many editions exist but are withheld because they are not published."""
        return library.list_editions()

    @server.tool(annotations=READ_ONLY)
    def read_edition(slug: str) -> dict:
        """Read one published edition in full, as plain text. `slug` comes from list_editions
        or search_library (for example "report-kickoff")."""
        try:
            return library.read_edition(slug)
        except LibraryError as exc:
            raise ToolError(str(exc)) from exc  # message reaches the model

    @server.tool(annotations=READ_ONLY)
    def search_library(query: str, limit: int = 10) -> dict:
        """Find published editions that contain every word of `query` (case-insensitive).
        Returns matches ranked by number of hits, each with a short snippet."""
        try:
            return library.search(query, limit)
        except LibraryError as exc:
            raise ToolError(str(exc)) from exc  # message reaches the model

    return server


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Read-only MCP server over one newsletters Library")
    parser.add_argument("--library", default=os.environ.get("NEWSLETTERS_LIBRARY"),
                        help="Library folder (contains ids.json and site/)")
    args = parser.parse_args(argv)
    if not args.library:
        parser.error("pass --library PATH or set NEWSLETTERS_LIBRARY")
    try:
        server = build_server(args.library)
    except LibraryError as exc:
        parser.error(str(exc))
    server.run()  # stdio


if __name__ == "__main__":
    main()
