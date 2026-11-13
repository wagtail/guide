# External methods and what to check next

Research hypotheses informed the [trace findings](README.md) and [retrieval measurements](retrieval.md).

## Different evaluations measure different outcomes

| Reference                     | What is actually measured                                                             | Implication for this benchmark                                                                       |
| ----------------------------- | ------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| AgentReady / Ora              | Website capabilities, observed reach, and controlled fetchability probes              | A readable endpoint is a prerequisite, not proof of a correct answer.                                |
| Cloudflare                    | Static capability checks and a separate documentation-navigation benchmark            | Separate organic discovery from runs explicitly started at an index.                                 |
| Joost's Website Specification | Recommended/optional representation and discovery conventions                         | Record conformance separately; specify which version and applicable requirements.                    |
| Tom Cranstoun's MX            | Explicit semantics, state, provenance and lifecycle guidance                          | Useful hypotheses and metadata requirements; not an experimentally established answer-quality score. |
| Mintlify                      | Hosted telemetry, survey results, and controlled URL discovery                        | Navigation efficiency can improve while a coarse success metric stays near its ceiling.              |
| Ahrefs GEO research           | Citation candidates, citations, visibility and stability over prompt populations/time | Search exposure, page opening, citing and factual support are separate stages.                       |

Our benchmark evaluates documentation answers under given prompts and tool arms. It does not measure whether real users complete a Wagtail task, website-wide accessibility, unsolicited answer-engine visibility, indexing, or support for purchases/authenticated actions.

## AgentReady, Ora and Joost

The relevant Ora is **ora.ai**, which AgentReady credits alongside Vercel. AgentReady's v2 specification, dated October 2026, separates requirements from scanner scoring and makes action requirements conditional on whether a product actually supports actions. For the guide's read-only documentation questions, payment and state-changing action protocols are **not applicable**, rather than missing capabilities to penalize. [AgentReady specification](https://github.com/agentready-org/standard/blob/main/spec/spec.md)

AgentReady's public methodology describes 1,033 agent runs across 25 sites and 190 deterministic probes. The probes succeed on a planted answer string appearing in fetched content. That supports a fetchability claim, not a conclusion that representation/discovery changes cannot influence answer accuracy, speed or cost. [AgentReady dataset methodology](https://raw.githubusercontent.com/agentready-org/standard/main/data/README.md)

Ora's navigation report and later matched-business AX study use different populations and designs. Their homepage-reach or business-performance figures should not become replication targets for our selected documentation tasks. Ranker 3.0, released 10 November, adds checks of MCP descriptions/schemas, document rendering and real versus soft 404s. Those would be useful technical probes, but its weights and caps are scanner policy, not a conversion formula for our pass rate. [Navigation report](https://ora.ai/blog/what-agents-actually-reach), [AX study](https://ora.ai/blog/ax-is-the-new-aeo), [Ranker 3.0](https://ora.ai/blog/introducing-ranker-3)

Joost de Valk's specification recommends Markdown endpoints and `llms.txt`, while treating MCP as optional. The Markdown guidance includes representation parity and `Content-Type`, `Content-Location` and `Vary: Accept` behavior. These are testable independently of model performance, but our current tool traces cannot establish HTTP negotiation. Record the reference/version rather than inventing a consensus readiness score. [Markdown endpoints](https://specification.website/spec/agent-readiness/markdown-source-endpoints/), [llms.txt](https://specification.website/spec/agent-readiness/llms-txt/), [MCP discovery](https://specification.website/spec/agent-readiness/mcp-and-tool-discovery/)

## Cloudflare and Tom's MX work

Cloudflare's 17 April launch article separates its capability scanner from an OpenCode/Kimi documentation benchmark. The benchmark starts agents at `llms.txt`, so it cannot show spontaneous index discovery. Its discussion of repeated index searching suggests useful checks for repeated fetches, queries and local grep loops. The default scanner did not require `llms.txt`; it was an optional check. [Cloudflare Agent Readiness](https://blog.cloudflare.com/agent-readiness/)

AFDocs provides an existing static-audit implementation with seven categories and 28 checks, including availability, discoverability and truncation risk. Its spec is currently v0.6.0; its 0.x check IDs/output may change. If we add a static audit, pin an existing tool and retain individual findings rather than writing another scanner or treating its aggregate score as answer quality. [AFDocs repository](https://github.com/agent-ecosystem/afdocs)

“The AEM Guy” is **Tom Cranstoun**, confirmed by his own profile. His MX principles emphasize explicit meaning, provenance, lifecycle, locale and canonical identity. Those are relevant to our legacy-manual and versioned-URL questions: a URL pattern alone does not establish which content version the agent actually received. His UI-state guidance could inform future interactive tasks, but documentation answers cannot validate it. Accessibility and agent compatibility should not be treated as empirically interchangeable outcomes. [Tom's profile](https://mx.allabout.network/blog/profiles/about.tom.cranstoun.html), [MX principles](https://mx.allabout.network/learn/key-principles.html), [Explicit over implicit](https://mx.allabout.network/learn/explicit-over-implicit.html)

## Mintlify and Ahrefs

Mintlify's State of Knowledge report combines different evidence types. Its traffic comparison uses server-side agent requests and client-side human page loads—different units—so it should not be read as a proportion of users or completed tasks. [State of Knowledge 2026](https://www.mintlify.com/state-of-knowledge/2026)

The underlying experiment comprises 20 sites × 5 questions × 4 formats × 2 agents × 3 repeats: 2,400 runs. It reports fewer failed requests with Markdown and index pointers, while reported accuracy stays high. Crucially, that accuracy is **expected normalized URL-path matching**, not factual-answer grading. Claude uses curl with web-search/MCP tools disabled, and the benchmark uses a proxy, a frozen page inventory and replay snapshots. Its effect sizes should not be projected onto our native/MCP arms. The reusable lesson is to measure retrieval friction separately and control content/representation explicitly. [Engineering write-up](https://www.mintlify.com/blog/llms-txt-agent-benchmark), [Benchmark source](https://github.com/mintlify/docs-url-discovery-bench)

There was no unique match for “the Ahrefs GEO review,” so the review considered these relevant primary studies separately:

- **Retrieval versus opening versus citation:** the 1.4-million-prompt page-selection study distinguishes candidate results from opened pages. Do not count every search-result URL as a visit, or assume search-provider metadata reflects a model preference. Its date/model labels warrant caution; no precise collection-date claim is needed here. [Why ChatGPT cites pages](https://ahrefs.com/blog/why-chatgpt-cites-pages/)
- **Citation stability:** the study follows approximately 37,500 initially cited sites over 20 days and distinguishes answers without citations from replacement within citation-bearing answers. Our three repeats can measure within-batch consistency, not longitudinal stability. [Citation-stability study](https://ahrefs.com/blog/how-stable-are-ai-citations/)
- **Features versus effects:** the JSON-LD study follows 1,885 pages adding schema against approximately 4,000 controls, finding no meaningful positive citation change in the examined products. Its matched observational design still has limitations, but cautions against awarding causal credit for feature presence. [Schema study](https://ahrefs.com/blog/schema-ai-citations/)
- **Visibility limitations:** the fan-out study explicitly corrected a claim about searches to one about visible query traces. Absence of observable queries does not establish absence of search; this is directly relevant to Codex wrappers. [Query fan-out study](https://ahrefs.com/blog/query-fan-out-chatgpt/)

## What we can do with the saved data

These recommendations are our synthesis of the sources above. “Feasible” is not a claim that every check below has already been implemented.

| Check                    | Definition and denominator                                                                         | Status                                                                                                                     |
| ------------------------ | -------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| Technique prevalence     | Present / eligible trajectories; unknown and opaque counts retained                                | Implemented for 47 patterns, separately by cohort/model/arm.                                                               |
| Retrieval friction       | Calls, errors, repeated queries/URLs, timing and cost for all attempts                             | Counts/distributions and presence flags implemented. Error-type/call-level rates can be derived from saved native outputs. |
| Source-selection funnel  | Configured/exposed → discovery observed → invocation → returned content → citation → claim support | Several stages are recorded; end-to-end adjudication is not yet implemented. Preconfigured MCP is assisted exposure.       |
| Version/audience routing | Legacy URLs at request and final-answer stages; editor-guide versus developer-doc routing          | URL-pattern counts implemented. Actual served-version/factual-support checks need returned passages or snapshots.          |
| Query construction       | Observable query count, official-domain filters, version terms, editor/developer terminology       | Feasible from saved inputs; keep an explicit observable-query denominator.                                                 |
| Repeat consistency       | No-citation frequency and citation-set overlap within the same case/model/arm                      | Feasible from final answers; existing three repeats do not support longitudinal claims.                                    |
| First useful evidence    | Calls/time until a passage supporting required facts appears                                       | Needs a reviewed case-to-evidence map or validated semantic adjudication. A matching URL is only a proxy.                  |
| Grading validity         | Contrast failed assertions with actual answer content and retrieved source version                 | Two concrete issues documented in the trace findings; scores retained unchanged.                                           |

## Data access and retention

The [data-coverage inventory](data/data-coverage.csv) checks local artifact presence by cohort/harness: ATIF, native log, trial config, manifest, replayed answer, system text, timing and cost. File presence does not prove completeness. Thirty unavailable trajectories and opaque nested calls remain limitations; extraction does not invent missing evidence.

Keep the original exports under `~/.cache/guide-agent-eval/harbor/`, including manifests, original/retry mappings, native text logs, ATIF, final answers and per-assertion grades. The published CSVs deliberately omit tool bodies, query/answer excerpts, credentials and absolute paths. They are not substitutes for the local raw artifacts. Current existence is verified; an independent archival backup has **not** been made. Session databases and authentication stores are not required for the published analysis and must not be copied blindly into a public archive.

Preserve exact tool inputs, result order/ranking/snippets, call/result IDs, timestamps, versions and instruction snapshots where present. Full tool output can sometimes support source adjudication; a harness-produced summary is not the same as the original HTTP response. Keep exact and normalized URLs separately, and record content hashes/canonical/version/locale metadata when already available. Do not backfill a historical snapshot by fetching today's site.

Future proxy/server instrumentation should capture trial-correlated requested/final URLs, redirect chains, HTTP method/status, sanitized `Accept`/`User-Agent`, response `Content-Type`/`Vary`/canonical links, sizes, timing, truncation, cache state and `Retry-After`. Exclude authorization and cookies. Native remote tools may bypass a local proxy, so report capture coverage. An MCP invocation may generate several server HTTP requests; keep those units distinct.

For MCP, preserve a per-batch server/tool-schema snapshot, descriptions/instructions, discovery evidence and result identifiers/sizes/timing. We have the guide initialization/schema snapshot for the pilot; do not assume it proves the exact server state of every subsequent run.

## Small next experiments, not another broad rerun

1. Fix or version the latest-release expectation and make the multi-tenancy fact check semantic enough to accept correct paraphrases; rerun both sides against the same grading snapshot when making a new comparison.
2. Freeze the guide content and independently vary representation (HTML/Markdown) and discovery (index link absent/present), with identical questions/models and interleaved order.
3. Compare organic discovery against an explicitly supplied index or configured MCP server. Keep supplied server instructions/descriptions as a documented part of the intervention.
4. Add a small freshness challenge with old/current pages and explicit supersession metadata; score selected source version and supported facts separately from URL form.
5. Only if real editor task completion becomes a goal, add an independently scored interactive Wagtail task set. It should complement, not replace, these documentation-answer tasks.

These are proposals. They require no custom agent adapters, and none has been launched as part of this analysis.
