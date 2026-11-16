"""CLI controls and a Vibe 3 export shim around Harbor's installed agents."""

import json

from harbor.agents.installed.claude_code import ClaudeCode
from harbor.agents.installed.vibe import Vibe


class NoToolsClaude(ClaudeCode):
    def build_cli_flags(self):
        return super().build_cli_flags() + " --tools ''"


class WebClaude(ClaudeCode):
    def build_cli_flags(self):
        return super().build_cli_flags() + " --tools WebSearch,WebFetch"


class CurrentVibe(Vibe):
    """Expose Vibe 3's JSON export to Harbor's existing trajectory converter."""

    def build_cli_flags(self):
        return (
            super().build_cli_flags()
            + " --output json --output-dir /logs/agent/vibe-export"
        )

    def _get_session_chain(self):
        return [self.logs_dir / "vibe-export"]

    def _read_messages(self, session_dir):
        messages = []
        for entry in json.loads((self.logs_dir / "vibe.txt").read_text()):
            if entry["type"] == "message":
                messages.append(entry)
            elif entry["type"] == "reasoning":
                messages.append(
                    {"role": "assistant", "reasoning_content": entry["text"]}
                )
            elif entry["type"] == "effect":
                detail, state = entry["detail"], entry["state"]
                if not detail.get("toolName"):
                    raise ValueError("Unknown Vibe effect; cannot audit tool access")
                messages.extend(
                    [
                        {
                            "role": "assistant",
                            "tool_calls": [
                                {
                                    "id": entry["id"],
                                    "function": {
                                        "name": detail["toolName"],
                                        "arguments": detail.get("input", {}),
                                    },
                                }
                            ],
                        },
                        {
                            "role": "tool",
                            "tool_call_id": entry["id"],
                            "content": json.dumps(state),
                        },
                    ]
                )
            else:
                raise ValueError(f"Unknown Vibe entry type: {entry['type']}")
        return messages

    def _read_meta(self, session_dir):
        export = json.loads((session_dir / "export.json").read_text())
        if export.get("outcome") != "finished":
            raise ValueError(f"Vibe did not finish: {export.get('outcome')}")
        usage = export.get("usage") or {}
        return {
            **export,
            "stats": {
                "session_prompt_tokens": usage.get("input_tokens"),
                "session_completion_tokens": usage.get("output_tokens"),
                "session_cost": export.get("cost_usd"),
            },
        }


class NoToolsVibe(CurrentVibe):
    def _build_config_toml(self):
        return (
            "enable_connectors = false\nenable_mcp = false\nenable_subagents = false\n"
            + super()._build_config_toml()
        )

    def build_cli_flags(self):
        return super().build_cli_flags() + " --disabled-tools '*'"
