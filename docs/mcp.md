# MCP server

The guide runs a public [Model Context Protocol](https://modelcontextprotocol.io/) (MCP) server at `https://guide.wagtail.org/mcp`, so AI agents can search and read the guide. It needs no authentication.

It complements the guide's other agent-facing features: [llms.txt](https://guide.wagtail.org/llms.txt), Markdown versions of every page, the agent skill, and the [WebMCP](https://webmachinelearning.github.io/webmcp/) tools pages register in the browser.

## Tools

All tools are read-only.

| Tool              | Description                                                                                               |
| ----------------- | --------------------------------------------------------------------------------------------------------- |
| `search_docs`     | Search pages in one language (`locale`, English by default). Returns title, description, URL and section. |
| `fetch_docs_page` | Fetch a page as Markdown from its URL or path, including its title, description and canonical URL.        |

## Connecting a client

Add `https://guide.wagtail.org/mcp` to your MCP client as a remote server, using the Streamable HTTP transport. It needs no authentication. For example, in Claude Code:

```sh
claude mcp add --transport http wagtail-guide https://guide.wagtail.org/mcp
```

## Development

The server lives in `apps/mcp_server`:

- `services.py`: the search and page lookups, as plain functions.
- `server.py`: the MCP tools, using the official [MCP Python SDK](https://py.sdk.modelcontextprotocol.io/).
- `views.py`: a Django view serving the SDK's server.

The SDK serves HTTP as an ASGI app, while the site runs under WSGI. The view bridges the two: it runs one stateless request through the SDK per Django request, with JSON responses rather than event streams. This supports both the stateless 2026-07-28 protocol and earlier versions that start with an `initialize` handshake. The view only accepts POST requests, and rejects requests with an `Origin` header for another site.

The server doesn't offer change notifications (`subscriptions/listen`), as its tools only change on deploy, and a worker thread can't hold a long-lived stream open. As a safety net, the view gives up on the SDK after 20 seconds and responds with a 504.

To try the server locally, run the development server and connect the [MCP Inspector](https://github.com/modelcontextprotocol/inspector) to `http://localhost:8000/mcp`, using its proxy connection rather than a direct one. Direct connections come from the Inspector's own origin, which the server rejects.

```sh
npx @modelcontextprotocol/inspector
```

## Operations

- Requests are logged at INFO level, with the MCP method, tool name, response status, protocol version, and client name and user agent. Tool arguments aren't logged.
- MCP requests are POST requests, so Cloudflare doesn't cache them, and they all reach the application. Apply a Cloudflare rate limiting rule to `/mcp`, for example around 100 requests per minute per IP address.
- Search queries made through MCP aren't recorded as search query hits, to keep agent traffic out of the search promotion statistics.
