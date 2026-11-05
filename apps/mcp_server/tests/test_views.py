import json
from unittest import mock

import anyio
import httpx2
from asgiref.sync import async_to_sync
from django.core.asgi import get_asgi_application
from django.core.signals import request_finished, request_started
from django.db import close_old_connections
from django.test import TestCase
from django.urls import reverse
from mcp import Client
from mcp.client.streamable_http import streamable_http_client

from apps.core.factories import ContentPageFactory, HomePageFactory

LEGACY_HEADERS = {
    "Accept": "application/json, text/event-stream",
    "MCP-Protocol-Version": "2025-11-25",
}

TOOL_NAMES = ["search_docs", "fetch_docs_page"]


class MCPTestMixin:
    def post(self, message, headers=LEGACY_HEADERS):
        return self.client.post(
            reverse("mcp"),
            json.dumps({"jsonrpc": "2.0", "id": 1, **message}),
            content_type="application/json",
            headers=headers,
        )

    def call_tool(self, name, arguments=None):
        response = self.post(
            {
                "method": "tools/call",
                "params": {"name": name, "arguments": arguments or {}},
            }
        )
        self.assertEqual(response.status_code, 200)
        return response.json()["result"]


class TestMCPView(MCPTestMixin, TestCase):
    def setUp(self):
        HomePageFactory()

    def test_get_not_allowed(self):
        response = self.client.get(reverse("mcp"))
        self.assertEqual(response.status_code, 405)

    def test_legacy_initialize(self):
        response = self.post(
            {
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-11-25",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "1"},
                },
            },
        )
        self.assertEqual(response.status_code, 200)
        result = response.json()["result"]
        self.assertEqual(result["protocolVersion"], "2025-11-25")
        self.assertEqual(result["serverInfo"]["name"], "wagtail-guide")
        self.assertIn("https://docs.wagtail.org/", result["instructions"])

    def test_logs_legacy_client(self):
        with self.assertLogs("apps.mcp_server.views", "INFO") as logs:
            self.post(
                {
                    "method": "initialize",
                    "params": {
                        "protocolVersion": "2025-11-25",
                        "capabilities": {},
                        "clientInfo": {"name": "test-client", "version": "1.0"},
                    },
                },
                headers={**LEGACY_HEADERS, "User-Agent": "test-agent"},
            )
        [log] = logs.output
        self.assertIn("method=initialize name=None status=200", log)
        self.assertIn("protocol=2025-11-25 client=test-client/1.0", log)
        self.assertIn("user_agent='test-agent'", log)

    def test_logs_tool_calls_without_arguments(self):
        with self.assertLogs("apps.mcp_server.views", "INFO") as logs:
            self.call_tool("search_docs", {"query": "secret-query"})
        [log] = logs.output
        self.assertIn("method=tools/call name=search_docs status=200", log)
        self.assertNotIn("secret-query", log)

    def test_subscriptions_not_supported(self):
        meta = {
            "io.modelcontextprotocol/protocolVersion": "2026-07-28",
            "io.modelcontextprotocol/clientCapabilities": {},
        }
        response = self.post(
            {
                "method": "subscriptions/listen",
                "params": {"_meta": meta, "notifications": {"toolsListChanged": True}},
            },
            headers={
                "Accept": "application/json, text/event-stream",
                "MCP-Protocol-Version": "2026-07-28",
                "Mcp-Method": "subscriptions/listen",
            },
        )
        # The protocol's own "method not found" 404, not a language redirect.
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual(response.json()["error"]["code"], -32601)

    def test_timeout(self):
        async def slow_service(*args):
            await anyio.sleep(1)

        with (
            mock.patch("apps.mcp_server.views.REQUEST_TIMEOUT", 0.01),
            mock.patch("apps.mcp_server.server.run_service", slow_service),
            self.assertLogs("apps.mcp_server.views", "INFO"),
        ):
            response = self.post(
                {
                    "method": "tools/call",
                    "params": {"name": "search_docs", "arguments": {"query": "x"}},
                }
            )
        self.assertEqual(response.status_code, 504)

    def test_rejects_other_origins(self):
        response = self.post(
            {"method": "tools/list"},
            headers={**LEGACY_HEADERS, "Origin": "https://example.com"},
        )
        self.assertEqual(response.status_code, 403)

    def test_allows_own_origin(self):
        response = self.post(
            {"method": "tools/list"},
            headers={**LEGACY_HEADERS, "Origin": "http://testserver"},
        )
        self.assertEqual(response.status_code, 200)

    def test_tools_are_read_only(self):
        tools = self.post({"method": "tools/list"}).json()["result"]["tools"]
        self.assertEqual([tool["name"] for tool in tools], TOOL_NAMES)
        for tool in tools:
            with self.subTest(tool=tool["name"]):
                self.assertTrue(tool["annotations"]["readOnlyHint"])
                self.assertNotIn("\n", tool["description"])


class TestMCPClient(TestCase):
    """
    End-to-end with the SDK's own client, sending HTTP requests to Django
    in-process. Django runs the sync view on the test's thread, so it sees the
    test's data.
    """

    def setUp(self):
        self.home_page = HomePageFactory()
        self.page = ContentPageFactory(parent=self.home_page, title="Streamfield")

        # Like Django's test client, keep the request handler from closing
        # the test's database connection, which it does for connections in a
        # transaction, such as the test's own.
        for signal in (request_started, request_finished):
            signal.disconnect(close_old_connections)
            self.addCleanup(signal.connect, close_old_connections)

    def run_client(self, mode="auto", **calls):
        async def run():
            http_client = httpx2.AsyncClient(
                transport=httpx2.ASGITransport(app=get_asgi_application())
            )
            # An explicit port, as httpx leaves default ones out of the ASGI
            # scope, and Wagtail needs one to find the site.
            transport = streamable_http_client(
                "http://testserver:8000/mcp", http_client=http_client
            )
            async with http_client, Client(transport, mode=mode) as client:
                results = {"version": client.protocol_version}
                results["tools"] = await client.list_tools()
                for name, arguments in calls.items():
                    results[name] = await client.call_tool(name, arguments)
                return results

        return async_to_sync(run)()

    def test_protocol_versions(self):
        for mode, expected_version in (
            ("legacy", "2025-11-25"),
            ("auto", "2026-07-28"),
            ("2026-07-28", "2026-07-28"),
        ):
            with self.subTest(mode=mode):
                results = self.run_client(
                    mode,
                    search_docs={"query": "streamfield"},
                    fetch_docs_page={"url": self.page.full_url},
                )
                self.assertEqual(results["version"], expected_version)
                tools = results["tools"].tools
                self.assertEqual([tool.name for tool in tools], TOOL_NAMES)

                search = results["search_docs"]
                self.assertFalse(search.is_error)
                titles = [page["title"] for page in search.structured_content["result"]]
                self.assertEqual(titles, ["Streamfield"])

                fetch = results["fetch_docs_page"]
                self.assertFalse(fetch.is_error)
                self.assertIn("# Streamfield", fetch.content[0].text)

    def test_invalid_arguments(self):
        result = self.run_client(search_docs={"query": "x" * 201})["search_docs"]
        self.assertTrue(result.is_error)
