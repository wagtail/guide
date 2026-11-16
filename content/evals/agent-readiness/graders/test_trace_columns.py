import json
import unittest

from trace_columns import codex_tool_calls, get_assert


def codex_turn(*items):
    return json.dumps({"items": list(items), "finalResponse": "answer", "usage": None})


class TestCodexTraceColumns(unittest.TestCase):
    def test_not_a_codex_turn(self):
        self.assertIsNone(codex_tool_calls(None))
        self.assertIsNone(codex_tool_calls("not json"))
        self.assertIsNone(codex_tool_calls(json.dumps({"messages": []})))

    def test_searches_curl_and_mcp(self):
        raw = codex_turn(
            {"id": "1", "type": "web_search", "query": "wagtail schedule page"},
            {
                "id": "1b",
                "type": "web_search",
                "query": "https://guide.wagtail.org/en/concepts/scheduled-publishing/",
            },
            {
                "id": "2",
                "type": "command_execution",
                "command": '/bin/zsh -lc \'curl -s -H "Accept: text/markdown" '
                "https://guide.wagtail.org/llms.txt'",
                "aggregated_output": "# Wagtail user guide",
                "exit_code": 0,
                "status": "completed",
            },
            {
                "id": "3",
                "type": "mcp_tool_call",
                "server": "guide",
                "tool": "fetch_docs_page",
                "arguments": {"url": "/en/concepts/scheduled-publishing/"},
                "result": {"content": [{"type": "text", "text": "Go-live at"}]},
                "status": "completed",
            },
            {"id": "4", "type": "agent_message", "text": "answer"},
        )
        result = get_assert(
            "See https://guide.wagtail.org/en/concepts/scheduled-publishing/",
            {"providerResponse": {"raw": raw, "metadata": {}}},
        )
        scores = result["named_scores"]
        self.assertTrue(result["reason"].startswith("codex: 4 tool calls"))
        self.assertEqual(scores["web_search_used"], 1)
        self.assertEqual(scores["llms_txt_reached"], 1)
        self.assertEqual(scores["mcp_used"], 1)
        self.assertEqual(scores["curl_calls"], 1)
        self.assertEqual(scores["answer_grounded"], 1)
        self.assertEqual(scores["web_fetch_calls"], 2)

    def test_claude_tool_calls_take_precedence(self):
        result = get_assert(
            "answer",
            {
                "providerResponse": {
                    "raw": codex_turn(),
                    "metadata": {
                        "toolCalls": [{"name": "WebSearch", "input": {}, "output": ""}]
                    },
                }
            },
        )
        self.assertTrue(result["reason"].startswith("claude: 1 tool calls"))


if __name__ == "__main__":
    unittest.main()
