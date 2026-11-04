# Agent readiness evals

Which of the guide's agent readiness features do agents actually use, and do they help agents answer users' questions correctly? This eval runs Claude Code against the guide with realistic user questions, records which surfaces each run reached (llms.txt, Markdown pages, content negotiation, MCP, agent skill, and more), and grades the answers. It follows up on [#486](https://github.com/wagtail/guide/issues/486). The latest results are in [RESULTS.md](RESULTS.md).

The method borrows from the [draftjs_exporter skill evals](https://github.com/wagtail/draftjs_exporter/blob/main/docs/contributing/evals.md) and Anthropic's [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents). The trace columns follow the [ora.ai / Vercel agent readiness dataset](https://github.com/agentready-org/standard/blob/main/data/traces.csv), so the results can be compared.

## Arms

Each arm is a variant of the same experiment: the same questions, the same model with the default Claude Code system prompt, run in an empty directory outside the repository with no user or project settings. Arms differ in one thing only:

| Arm         | What's different                                                             | Measures                                                        |
| ----------- | ---------------------------------------------------------------------------- | --------------------------------------------------------------- |
| `baseline`  | No tools                                                                     | What the model knows from memory                                |
| `web`       | `WebSearch` and `WebFetch`, on the guide as it is                            | What agents do today, and which features they find on their own |
| `web-plain` | Same tools, on a plain site without any agent readiness features (see below) | What the features are worth: `web` minus `web-plain`            |
| `web+mcp`   | Same tools, plus the guide's MCP server                                      | Whether agents prefer MCP when they have it, and do better      |
| `web+curl`  | Same tools, plus `curl` through Claude Code's Bash tool                      | Whether agents read raw HTML, and the links in its `<head>`     |

The plain site is served by the proxy (`proxy.py`), with no changes to the guide. It returns 404 for llms.txt, llms-full.txt, Markdown pages, everything under `/.well-known/` (agent skills, AI catalog, API catalog), `openapi.json` and the MCP server. It ignores requests for Markdown, so pages come back as HTML. From pages, it removes JSON-LD, Markdown and catalog links, and the script bundle that registers WebMCP tools. From robots.txt, it removes the Content Signals.

## Cases

`tests.yaml` covers the guide's tasks: information gathering, troubleshooting, and keeping up with releases, plus developer questions.

- Release cases cover recent releases (Wagtail 7.3 to 8.0), which models know little about from memory.
- Some prompts name the guide, others don't, so the agent has to find it, and some send the agent to the site ("Go to guide.wagtail.org and find…"), like the ora.ai tasks.
- Negative cases are developer questions, which the developer docs answer rather than the guide.
- Bridge cases are developer questions the guide answers itself, with a link to the developer docs.

## Grading

- **Answer checks** (pass or fail): key facts, and the URL of the guide page that answers the question.
- **Judge** (pass or fail): an `llm-rubric` for nuance, graded by Claude Sonnet 5.5 with no tools. When it can't tell, it passes the answer with a reason starting `UNKNOWN:`, and `summarize.py` lists those for review by hand.
- **Trace columns** (recorded, never fail a test): `graders/trace_columns.py` classifies each tool call into a surface and reports them as named scores. `answer_grounded` means the answer cites a guide page the run fetched. `versioned_url_reached` flags versioned guide URLs like `/en-6.3.x/` (which redirect to the current page), and `legacy_editor_manual_reached` the old editor manual on docs.wagtail.org. `curl_calls` and `permission_denials` count shell use in the `web+curl` arm. `*_linked` counts fetches of URLs that appeared in an earlier tool output, but `WebFetch` returns a summary of the page rather than the page, so links are undercounted.
- **Proxy log**: the agent's trace doesn't show request headers, so the proxy logs every guide request with its `Accept` header, status, and the content type served. This is how we see Markdown content negotiation.

`just eval-agents-check` runs before every eval, without calling a model. It checks that every case's reference answer passes its answer checks, that empty, refusing, URL-only and URL-less answers fail them, and that no prompt contains the facts its checks look for.

## Running the evals

Requires Node 26 (see `.nvmrc`), `uv`, and a local Claude Code login or `ANTHROPIC_API_KEY`. With a Claude subscription login, runs count towards your plan's usage limits instead of being billed per token. The costs promptfoo reports are what the same tokens would cost through the API.

```sh
just eval-agents-init                 # promptfoo + Claude Agent SDK, once

# In one terminal: the proxy, forwarding to `just run` (local) or the live site (prod).
just eval-agents-proxy local

# In another terminal:
just eval-agents                      # Claude Sonnet 5.5
just eval-agents claude-haiku-5-5 --repeat 3 --output run.json
just eval-agents-view                 # promptfoo viewer

uv run python content/evals/agent-readiness/summarize.py run.json \
    --proxy-log ~/.cache/guide-agent-eval/requests.jsonl
```

Local mode needs the development server running with the guide's real content, for example from a restored production database dump: the fixtures from `just buildfixtures` don't have the pages the cases ask about.

The first run creates a mitmproxy certificate authority in `~/.mitmproxy`. Only the agent trusts it, through `NODE_EXTRA_CA_CERTS`, and the proxy only intercepts `guide.wagtail.org`. In local mode, those requests go to the development server, so unreleased features like the MCP server can be tested with the real domain in every URL. `WebSearch` results still come from the live search index.

`just eval-agents` also builds a CA bundle for the `web+curl` arm, as curl doesn't read `NODE_EXTRA_CA_CERTS`.

promptfoo exits with code 100 when any test fails, which is expected for the `baseline` arm.

### Running one arm, or testing a site change

To rerun one arm, filter providers by label, like `--filter-providers '^web$'`, and `--filter-pattern '^start-'` to run some cases only. To measure a change to the site, rerun the `web` arm against the changed local site, relabel its results (`jq '.results.results[].provider.label = "web-md"' run.json > web-md.json`), and pass them to `summarize.py` next to the earlier runs, which reports each label as its own arm. `--override` replaces an arm's results with a rerun of it:

```sh
uv run python content/evals/agent-readiness/summarize.py run-1.json run-2.json \
    --override baseline-rerun.json
```

## Reading results with care

- **One repeat is not enough to act on.** Run with `--repeat 3` before comparing arms, and compare arms at the same repeat count.
- **Grade what the agent produced, not the path.** Trace columns show which features were used, and a run that skips llms.txt but answers correctly isn't a failure.
- **Read the transcripts.** Before trusting a score, check failing runs in `just eval-agents-view`: if a correct answer failed, fix the case, not the agent.
- **The proxy log is per eval run, not per test.** Clear `requests.jsonl` before a run to attribute its requests.
- **Cost is what Claude Code reports per run, at API list prices.** It includes the model, the Haiku calls `WebFetch` uses to summarize pages, and web search fees, but not the judge. With a subscription login, it's what the run would cost through the API, not what you pay.
- **Local mode is not production.** Production adds Cloudflare caching and the live content.
