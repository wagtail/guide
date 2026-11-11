# Neuralwatt energy analysis feasibility

On 11 November 2026, a read-only probe confirmed this account can access both
`GET /v1/usage/requests` and `GET /v1/usage/sessions`. A two-minute window from
6 November returned historical DeepSeek requests with timestamps, token counts,
energy in joules/kWh, attribution methods and costs. No inference was launched.
This confirms availability, not a completed energy benchmark.

Harbor's saved trial results contain agent execution start/end timestamps, and
the trace extractor now preserves that interval in local `trials.jsonl`.
The [request API](https://docs.neuralwatt.com/api/usage-requests) supports
model and ISO timestamp filtering plus pagination. Its request identifier is
the original `X-Request-ID` header, not the chat-completion body identifier.
Availability of matching request IDs in our native logs still needs auditing.

The preferred calculation is to sum all matched inference requests within each
task attempt, then report median and mean Wh per attempt for each matched
cohort × harness × model × arm. Retain failures and timeouts, track retries
separately, and also show total Wh divided by successful tasks so efficiency
cannot improve merely by failing early. Report matched coverage and measured,
estimated and missing energy separately. This measures Neuralwatt-attributed
inference energy, excluding local execution, search/MCP services and network
energy.

Batch energy divided by task count gives a **mean**, not a median. Time windows
alone are insufficient when tasks or unrelated account traffic overlap.
Request IDs are preferable; otherwise timestamp, model and token-count joins
need explicit ambiguity checks. Aggregate means can still be useful for an
isolated batch whose traffic can be attributed reliably. Never divide the same
overlapping request into multiple arms without declaring an allocation model.

[Sessions](https://docs.neuralwatt.com/api/sessions) offer convenient energy
rollups, but their default prefix-derived grouping can merge repeated prompts
or split rewritten conversations. They are not automatically one session per
benchmark task. Future native request tagging could make attribution exact;
the documented session identity also affects cache routing, so changing it
would be an experimental intervention, not a neutral retrospective fix.

A reporting change overlaps this experiment:
[Neuralwatt's 6 November changelog](https://neuralwatt.com/changelog?area=energy)
says consumed energy previously sometimes reflected billing adjustments.
New requests report measured energy (or marked estimates), while historical
rows retain the old figures. The precise deployment boundary and whether a
given earlier row was affected are not established here. Do not pool all
November 5–11 energy as if measurement semantics were identical, or reconstruct
physical energy from billed dollars. Use the recorded attribution fields and
preserve this limitation in any comparison.

Next step: export request metadata once, audit exact-ID coverage and overlapping
time windows, and validate task matching on a small sample before calculating
arm-level statistics. No median energy figures have yet been calculated.
