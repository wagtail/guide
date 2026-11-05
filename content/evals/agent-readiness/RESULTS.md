# Agent readiness results: guide.wagtail.org

Which agent readiness techniques do AI agents actually use on the guide, and do they help agents answer users' questions? Results from October 2026, for [#486](https://github.com/wagtail/guide/issues/486). See [README.md](README.md) for the method and how to rerun it.

## In short

- **The MCP server is the one technique that clearly pays off.** With it, every agent we tested answered 97–100% of questions correctly, against 80–93% when browsing the site, and up to twice as fast. This needs the user to connect the server first: agents don't find or connect MCP servers on their own, so people need to know it exists.
- **Agents find pages through web search, not through the site.** Claude Code searched the web in 65–92% of real-site runs. It searches like a person would on Google, opens the guide page the results point to, and answers. So the site's own maps and files (llms.txt, llms-full.txt, robots.txt, the agent skill, `.well-known` files, openapi.json) were used in only 9 of 579 real-site runs. OpenCode's web search mostly failed during our runs (see [Caveats](#caveats)), so OpenCode shows what agents do without search: they browse from the homepage and guess `/sitemap.xml` (104 real-site runs, 92 of them OpenCode).
- **Our Markdown pages hide the navigation**, so when agents do browse, they get lost or guess. The same site with every agent feature switched off did as well or better on every model (up to +7 points). Converting Markdown from the page's HTML, with Wagtail 8.1's converter, closes most of that gap.
- **llms.txt gets used when an agent can see a link to it.** Once our Markdown pages linked to llms.txt, OpenCode, which shows the model the whole page, opened it in 44–60% of runs. Claude Code, which shows the model a summary of the page, almost never did. Using llms.txt didn't clearly make answers more accurate. Reading llms-full.txt made GPT-5.5's answers 1.7 times as expensive as llms.txt alone.
- **Cheap fixes:** ship the MCP server and make it easy to install, convert Markdown from HTML (with every section, Releases included, linked from the homepage), link llms.txt but not llms-full.txt from pages, and keep old guide URLs redirecting.

## What we tested

We asked AI agents 33 realistic questions about using Wagtail, from "How do I schedule a page?" to "Why aren't my changes showing on the site?", and checked whether each answer had the right facts and linked to the right guide page. Each question ran 3 times per model, under these conditions:

| Condition                     | What the agent has                                                    | What it tells us                     |
| ----------------------------- | --------------------------------------------------------------------- | ------------------------------------ |
| No tools                      | Nothing, memory only                                                  | How much the model already knows     |
| Real site                     | Web search and page fetching, on the guide as it is                   | What happens today                   |
| Plain site                    | The same, on the guide with every agent feature removed               | What our agent features are worth    |
| Real site, Markdown from HTML | The same as real site, with page Markdown converted from the HTML     | What Wagtail 8.1's converter changes |
| Real site + MCP               | The same as real site, plus the guide's MCP server, already connected | What MCP adds                        |

We tested two agents, with six models in all:

- **Claude Code** with Claude Haiku 5.5, Sonnet 5.5, Opus 5.5 and Fable 5.1. Opus ran 28 of the 33 questions, and no Markdown from HTML.
- **OpenCode**, an open source coding agent, with OpenAI's GPT-5.4 mini and GPT-5.5.

The plain site removes llms.txt, llms-full.txt, Markdown pages and content negotiation, the agent skill, the AI and API catalogs, openapi.json, the MCP server, JSON-LD, WebMCP, Markdown 404s and Content Signals.

The questions cover information gathering (15), troubleshooting (8), release notes (6), and developer questions (4): 3 that the developer docs answer, and 1 that the guide answers with a link to them. They're asked in three ways:

- **Naming the guide** (19): "Using the user guide on guide.wagtail.org, how do I…?"
- **Not naming it** (9): "How do I…? Link to official documentation." The agent has to find the guide.
- **Sending the agent to the site** (5): "Go to guide.wagtail.org and find out…", like the tasks in the [ora.ai study](https://github.com/agentready-org/standard/blob/main/data/traces.csv).

## How AI agents find and read pages

Agents answering a question work much like a person with a search engine:

1. They **search the web**: Claude Code with Anthropic's search tool, OpenCode with a search engine called Exa. Exa rejected most of OpenCode's searches in our runs, so OpenCode mostly skipped this step (see [Caveats](#caveats)).
2. They get back titles, links and short snippets, and open the most promising link. That's usually a **deep link**: a specific page inside the guide, like "Scheduled publishing", rather than the homepage.
3. They read that page and answer, citing it.

Because search hands them the right page straight away, agents rarely need to browse the guide, use its menu, or read a site map like llms.txt. The search engine has already done the mapping.

How much of a page the model sees depends on the agent:

| Kind of agent                                  | Examples                                                    | What the model sees                                                           | Sees links to llms.txt on the page?         |
| ---------------------------------------------- | ----------------------------------------------------------- | ----------------------------------------------------------------------------- | ------------------------------------------- |
| Agents whose fetch tool summarizes             | Claude Code, Gemini CLI                                     | A short summary of the page, written for the question by a small model        | Rarely: links seldom make it into summaries |
| Agents whose fetch tool passes the page on     | OpenCode                                                    | The whole page, converted to Markdown                                         | Yes                                         |
| Agents with a shell                            | Claude Code, Codex CLI, with `curl` allowed                 | The raw HTML, if the agent chooses to use it                                  | Yes, but agents rarely choose it            |
| Browser agents                                 | Claude in Chrome, ChatGPT agent and Atlas, Perplexity Comet | What's shown on screen, and it can run JavaScript, so it can use WebMCP tools | Yes, as visible links                       |
| Search and AI crawlers, and readiness scanners | GPTBot, ClaudeBot, PerplexityBot; ora.ai                    | The raw HTML, to build search indexes or scores                               | Yes, but they don't answer users directly   |

Links that are only in the page's `<head>`, like our AI catalog, API catalog and openapi.json links, reach crawlers and scanners, not agents answering users. That's a large part of why the guide's ora.ai score rose from 55 to 71 out of 100 (29 September to 6 October), mostly through the API catalog and openapi.json, while our agents never used those files.

## Results at a glance

Share of answers with the right facts and the right guide link, mean across 3 repeats:

| Condition                     | Haiku 5.5 | Sonnet 5.5 | Opus 5.5\* | Fable 5.1 | GPT-5.4 mini | GPT-5.5  |
| ----------------------------- | --------- | ---------- | ---------- | --------- | ------------ | -------- |
| Agent                         | Claude    | Claude     | Claude     | Claude    | OpenCode     | OpenCode |
| No tools                      | 10%       | 15%        | 36%        | 41%       | 13%          | 30%      |
| Real site                     | 80%       | 89%        | 89%        | 90%       | 88%          | 93%      |
| Plain site                    | 87%       | 90%        | 96%        | 95%       | 88%          | 95%      |
| Real site, Markdown from HTML | 80%       | 93%        | not run    | 93%       | 89%          | 92%      |
| **Real site + MCP**           | **97%**   | **100%**   | **100%**   | **100%**  | **98%**      | **99%**  |

\* Opus ran the first 28 questions, without the "go to the site" ones.

Each cell is 33 questions × 3 repeats (Opus 28 × 3), so 1 point is about one answer. MCP's gain is statistically clear: across questions, 33 did better with MCP and 3 worse (sign test, p < 0.0001). The other gains below are measured and consistent in direction, but small enough that a rerun could move them by a few points.

### MCP versus the real site

| Model        | Correct answers | Time per answer | Cost per answer |
| ------------ | --------------- | --------------- | --------------- |
| Haiku 5.5    | +17 pts         | 22s → 11s       | 1.6¢ → 0.4¢     |
| Sonnet 5.5   | +11 pts         | 17s → 10s       | 2.8¢ → 2.5¢     |
| Opus 5.5     | +11 pts         | 28s → 16s       | 4.6¢ → 4.0¢     |
| Fable 5.1    | +10 pts         | 36s → 18s       | 13.3¢ → 11.2¢   |
| GPT-5.4 mini | +10 pts         | 22s → 16s       | 1.5¢ → 1.0¢     |
| GPT-5.5      | +6 pts          | 23s → 15s       | 8.3¢ → 4.7¢     |

With MCP, agents chose it over web search in 85–91% of runs. Troubleshooting questions and questions that don't name the guide gain the most: the agent goes straight to the guide instead of relying on search results.

### Without the site

With no tools, models know many of the facts but rarely the guide page to cite. Questions about recent releases (Wagtail 7.3 to 8.0) were answered correctly 0–13% of the time from memory, so for recent changes, agents need the site.

## Which techniques agents actually use

On the guide as it is (1,158 runs with the real site, with and without MCP):

| Technique                                                           | Used?                                                                                                          | Verdict                                                       |
| ------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------- |
| MCP server                                                          | **Yes, 85–91% of runs that had it**                                                                            | Keep, and promote it                                          |
| Web search                                                          | **Yes, Claude Code in 65–92% of real-site runs** (OpenCode tried in 84–97%, but most calls failed)             | Make sure pages rank and stay current                         |
| Markdown content negotiation                                        | **Yes, on almost every fetch**: both agents ask for Markdown first                                             | Keep, but convert it from the HTML (below)                    |
| Guide pages                                                         | Yes, 54–89% of runs                                                                                            | The main source of answers                                    |
| Homepage                                                            | Varies: GPT-5.5 68%, Haiku 43%, GPT-5.4 mini 34%, Sonnet 8%, Opus and Fable under 10%                          | Its Markdown needs links to every section                     |
| sitemap.xml                                                         | 104 runs, guessed: GPT-5.5 66%, GPT-5.4 mini 27%, Fable 10%, when the Markdown pages had no links to follow    | Keep it. With Markdown from HTML, the guessing mostly stopped |
| llms.txt, llms-full.txt                                             | **5 runs**                                                                                                     | Link llms.txt from pages (below)                              |
| robots.txt                                                          | 4 runs, all GPT-5.4 mini                                                                                       | Fine as is                                                    |
| Agent skill, `.well-known` files, AI and API catalogs, openapi.json | **Never**                                                                                                      | Keep for crawlers and scanners                                |
| Agent-friendly 404s                                                 | Never seen: neither agent passes a 404's body to the model (and the eval server's debug mode served HTML 404s) | No impact with these agents                                   |
| JSON-LD, WebMCP, Content Signals                                    | Not usable by these agents: they read text, without running scripts                                            | Not measurable here                                           |

### Agents guess paths when the page gives them nothing to follow

Claude Haiku, Sonnet and Opus rarely guessed URLs. GPT-5.5 and Fable did:

- **GPT-5.5 fetched `/sitemap.xml` in 66% of real-site runs**, usually right after reading the Markdown homepage, which has almost no links. On the plain site, where the homepage has its full menu, it did so in 8%.
- **Fable types URLs from memory.** It went straight to old addresses like `/en-latest/how-to-guides/…`, and visited versioned guide URLs in about 65% of runs. These redirect to the current page, so the answers stay right, which makes keeping those redirects important.
- **The 404s we checked were all guessed paths**, mostly developer-docs-style URLs like `/en/latest/…`.

## llms.txt: used only when agents see a link to it

Our Markdown pages are rendered from the page content alone, so they don't link to llms.txt. Once we converted Markdown from the HTML, every page linked to it:

| Real site, with Markdown from HTML | Claude Haiku | Claude Sonnet | Claude Fable  | GPT-5.4 mini (OpenCode) | GPT-5.5 (OpenCode) |
| ---------------------------------- | ------------ | ------------- | ------------- | ----------------------- | ------------------ |
| Opened llms.txt                    | 1%           | 0%            | 0%            | **44%**                 | **60%**            |
| Opened llms-full.txt               | 5%           | 0%            | 1%            | **27%**                 | **24%**            |
| Guessed sitemap.xml                | 0%           | 0%            | 0% (from 10%) | 10% (from 27%)          | 5% (from 66%)      |

Before the change, llms.txt and llms-full.txt were at 0–1% for all five.

**Why OpenCode followed the link and Claude Code didn't:** OpenCode gives the model the whole page, so the llms.txt link is always in view. Claude Code gives the model a short summary written for the question, and a footer link to llms.txt rarely makes it into a summary about scheduling pages. Haiku, the one Claude model that used it, was also the one that opened the homepage most often.

**It didn't clearly make answers better.** Overall accuracy stayed about the same: llms.txt was a different route to the same pages. There's a hint of a gain for GPT-5.5, whose runs that opened llms.txt scored 100% against 86% on the same 14 questions, but that's too few to be sure. It also explains most of OpenCode's visits to `/markdown/` pages, which llms.txt links to (99 of 102 runs). Note that OpenCode's web search was mostly failing in these runs, so it was browsing, which is exactly when a site map gets used.

**llms-full.txt made GPT-5.5's answers 1.7 times as expensive.** It's the whole guide in one 177 KB file. In the Markdown-from-HTML runs, GPT-5.5's cost per answer was:

| GPT-5.5 runs (Markdown from HTML) | Runs | Cost per answer | Input tokens per answer | Correct |
| --------------------------------- | ---- | --------------- | ----------------------- | ------- |
| Opened llms-full.txt              | 24   | 16.2¢           | 78k                     | 88%     |
| Opened llms.txt only              | 49   | 9.7¢            | 40k                     | 96%     |
| Opened neither                    | 26   | 3.6¢            | 13k                     | 88%     |

The cost comes from the file, the agent and the model together:

- **The file:** OpenCode passes fetched pages to the model whole, up to 50 KB. So reading llms-full.txt adds about 50 KB of text, roughly 13k tokens.
- **The agent:** that text stays in the conversation, and the agent sends the whole conversation back to the model on every later step. GPT-5.5 usually read llms-full.txt at step 3 or 4, straight from a link on the page it had just read, then took one or more steps after it.
- **The model:** GPT-5.5 is expensive per token. GPT-5.4 mini paid about 1¢ more per answer for the same behavior, and Claude Code barely more (Haiku 2.0¢ against 1.5¢, 5 runs), because it summarizes pages before the model sees them.

So it isn't an odd path. Opening this one large file costs more, and with an expensive model and an agent that keeps whole pages in context, that adds up. On the same questions, GPT-5.5 runs that opened it cost more every time (14 of 14). llms.txt itself, a short index, is cheap and worth linking. llms-full.txt is better left for tools that ask for it directly.

### Why other studies saw more llms.txt use

**The ora.ai and Vercel study** ([data](https://github.com/agentready-org/standard/tree/main/data): 1,033 runs on 25 product sites, June–August 2026) saw llms.txt used in 32% of runs overall. Their tasks were things like finding pricing or rate limits on SaaS and developer-tool sites:

- llms.txt use was concentrated: all 329 runs that used it were on 6 sites, and on the other 19 sites it was 0%, including 9 sites that publish one. That looks like our 0–1% before we linked it.
- 63% of their runs started on the homepage (91.5% of runs that reached it). Ours mostly start with a web search, which lands on the answer page directly. On our five "go to the site" questions, homepage-first rose to 40–100%.
- 86% of their llms.txt visits followed a link the agent had just seen. Agents almost never type `/llms.txt` on a hunch.
- Claude Fable 5 used llms.txt in 54–77% of their runs. In Claude Code on our questions, Fable 5.1 searched the web in about 80% of runs and opened llms.txt or llms-full.txt in about 1%. Even on our five "go to the site" questions, it searched or typed the page address from memory.

**The Mintlify study** ([State of Knowledge 2026](https://www.mintlify.com/state-of-knowledge/2026)) found Markdown with a link to llms.txt cut 404s about 20× and tokens by 26–60%. Their agents could only use `curl`, with no web search, on a copy of the site at a local address, so they had to browse from the front page and read raw pages. That's when a site map matters most and when raw HTML is most expensive. Their `md-link` condition is close to our Markdown from HTML, and their finding that Markdown alone leaves agents guessing matches ours.

The common thread: **llms.txt gets used when an agent lands on a page that links to it and has to find its own way.** With web search, that's rare.

## Markdown pages: why the real site does worse than the plain site

Both agents ask for Markdown, and today's Markdown pages leave out the navigation:

| Page     | Links in HTML                        | Links in Markdown today | Links in Markdown from HTML, footer included |
| -------- | ------------------------------------ | ----------------------- | -------------------------------------------- |
| Homepage | 59 (every section, through the menu) | 5 (four sections)       | 16                                           |
| Releases | 57 (including all 16 releases)       | 0                       | 26 (including all 16 releases)               |

Unique link targets in the page body, counted on the eval site.

On the plain site, agents get HTML with the full menu, see "Manage images" or "New in Wagtail 7.4", and go there. On the real site, they see only section names, and either guess or give up on the guide. The release questions show it most: GPT-5.5 scored 78% on them on the real site against 94% on the plain site, stopping at 7.0 instead of finding 7.4.

### Real site with Markdown from HTML

We converted each page's rendered HTML to Markdown, with the `HTMLToMarkdownConverter` coming in Wagtail 8.1.

- **How we tested it:** the eval site ran Wagtail 8.0 with Wagtail 8.1's converter copied in, unchanged apart from import paths and one compatibility fix. The change itself, on Wagtail 8.1rc1, is on the `feature/markdown-responses` branch.
- **What agents get:** the whole page body converted to Markdown, minus the menu (`<nav>`), the feedback form and the language switcher. Section pages list their pages, content pages start with an "On this page" list, and every page links to llms.txt and llms-full.txt. llms-full.txt and the MCP server are unchanged.
- **Results:** Sonnet +4 points and Fable +3, both now level with or close to the plain site. Haiku and the GPT models are level with today's Markdown. The homepage still doesn't link to Releases, because that link is only in the menu, so Haiku still misses "go to the site" release questions.

### Markdown versus HTML: size and cost

Markdown converted from HTML is 3.7 to 31 times smaller than the same pages in HTML (median 9.5×, homepage 61 KB → 2.3 KB). That barely changes what agents pay:

- **Claude Code** summarizes every page with a small model, so the main model sees about 1k characters of summary whatever the format. The summary costs 0.05–0.09¢ per fetch, with no consistent difference between HTML and Markdown.
- **OpenCode** converts HTML to Markdown itself before the model sees it, so pages it read were only 1.9 times smaller as Markdown (median 4.1k characters against 7.6k).

Agents that read raw pages, like Mintlify's curl-only agents, would save far more. For the agents we tested, what Markdown changes is which links agents see, not how much they pay.

## Do agents read raw HTML when they can?

Given `curl` alongside their usual tools (Claude Haiku and Sonnet, 198 runs), agents never used it. Every page was read with Claude Code's own fetch tool. This differs from Mintlify's setup, where curl was the only tool. Sonnet scored lower with curl available (85% against 93%) without using it. Adding the shell tool changes Claude Code's instructions, which may explain it.

## What a typical agent does

| Agent and model    | Real site                                                                       | With MCP              |
| ------------------ | ------------------------------------------------------------------------------- | --------------------- |
| Claude Haiku       | search → guide page, often via the homepage                                     | MCP search → MCP read |
| Claude Sonnet      | search → guide page, or **search results only, without reading a page** (30%)   | MCP search → MCP read |
| Claude Opus, Fable | search → guide page, or straight to a page address from memory                  | MCP search → MCP read |
| OpenCode (GPT)     | search → guide page, often via the homepage, then sitemap.xml or a section page | MCP search → MCP read |

- **Agents take a few steps and stop.** One search, one to three pages, then the answer.
- **Search sends agents to old guide URLs** (`/en-6.3.x/…`, `/en-latest/…`). These redirect to the current page.
- **Developer questions go to docs.wagtail.org**, as they should, in every condition with web access.
- **OpenCode doesn't say it's an agent:** it sends a browser `User-Agent`, so the guide's logs can't tell it apart from a person.

## Where agents fail

| Kind of failure                    | Example                                                               | Cause                                                                       |
| ---------------------------------- | --------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| Couldn't find the right guide page | Cites the developer docs or a section page instead of "Manage images" | Markdown section pages don't list their pages (fixed by Markdown from HTML) |
| Missed part of a multi-page answer | A question about saving incomplete blocks answered 7.0, not 7.4       | The Markdown Releases page lists no releases (fixed by Markdown from HTML)  |
| Used an outdated source            | Cites the old editor manual on docs.wagtail.org                       | Old pages still rank in search, and models remember them                    |
| Wrong or incomplete answer         | "How do I find stale pages?" answered without the Aging pages report  | The page answers it, but the agent didn't find or read it                   |

The questions that failed most often outside MCP: finding stale pages, locked pages (the old editor manual), recovering deleted documents, and the difference between snippets and pages.

## Recommendations

| Priority | Change                                                                                                                                                                | Expected effect                                                                                                              |
| -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| 1        | **Ship the MCP server**, and make it easy to install: in the docs, llms.txt, the agent skill and the MCP Registry                                                     | +6–17 points on every model, up to twice as fast                                                                             |
| 2        | **Convert page Markdown from the rendered HTML** with Wagtail 8.1's `HTMLToMarkdownConverter`, and link every section, Releases included, from the homepage's content | Measured: up to +4 points, and agents stop guessing the sitemap. The homepage links should recover Haiku's release questions |
| 3        | **Link llms.txt from pages, but not llms-full.txt**                                                                                                                   | llms.txt gets used once linked. llms-full.txt doubled GPT-5.5's cost per answer, for no gain                                 |
| 4        | **Keep old guide URLs redirecting**, and redirect `/en/latest/*` to `/en/*`                                                                                           | Agents use remembered and searched old URLs in up to 65% of runs, and guessed paths cause the 404s                           |
| 5        | Ask the developer docs to redirect all of the old editor manual to the guide                                                                                          | 32% of failures cite it. Some pages redirect already, but agents still get it from search and memory, and many old pages 404 |

After changes 2 and 3 are live, rerun the real-site condition to measure them.

## Cost

Costs are each agent's own figures at API list prices. They include web search and page summaries, but not grading.

| Model        | Cost per answer (real site) | Cost per answer (with MCP) | All our runs         |
| ------------ | --------------------------- | -------------------------- | -------------------- |
| Haiku 5.5    | 1.6¢                        | 0.4¢                       | $6.49 (594 answers)  |
| Sonnet 5.5   | 2.8¢                        | 2.5¢                       | $14.53 (594 answers) |
| Opus 5.5     | 4.6¢                        | 4.0¢                       | $12.68 (336 answers) |
| Fable 5.1    | 13.3¢                       | 11.2¢                      | $54.76 (495 answers) |
| GPT-5.4 mini | 1.5¢                        | 1.0¢                       | $6.77 (495 answers)  |
| GPT-5.5      | 8.3¢                        | 4.7¢                       | $33.28 (495 answers) |

In all, about 3,000 answers for **about $130**. Rerunning one condition on one model costs $1–15 and takes 10–50 minutes.

## Caveats

- **Two agents.** These are Claude Code and OpenCode results. Browser agents and agents that read raw HTML would see more of the page, including WebMCP and `<head>` links.
- **OpenCode's web search mostly failed.** Exa answered 674 of OpenCode's 864 searches with a rate-limit error (HTTP 429): all of GPT-5.5's, and about half of GPT-5.4 mini's on the real and plain sites. The agent reported these as normal results, so the traces didn't flag them. OpenCode's results show agents browsing without search, which is why they open the homepage, sitemap.xml and llms.txt more. A rerun with working search would show OpenCode's usual behavior.
- **33 questions.** At 3 repeats, gaps of a few points can come from a handful of answers; only the MCP gain is statistically clear. The "go to the site" results come from 5 questions only, so read them as indicative.
- **MCP was connected in advance.** The MCP results show what the server is worth once a user has connected it. Agents can't connect one mid-task, so how many people benefit depends on how many install it.
- **Local copy of the site.** The eval ran against a local copy with the same content as production (and the unreleased MCP server), through a proxy that makes it look like guide.wagtail.org. Production adds Cloudflare caching.
- **Search results are live.** Web search used the real search index, and OpenCode's search returns text Exa crawled from the live site, so some answers come from search results without a page fetch.
- **Markdown from HTML is a prototype.** It ran Wagtail 8.1's converter copied into the 8.0 site, on every model except Opus.
- **The MCP server isn't live yet.** The eval used the unmerged `feature/public-mcp` branch.
- **Markdown 404s weren't live.** The eval server ran in debug mode, so 404s came back as Django's HTML debug page. Neither agent passes a 404's body to the model, so this doesn't change the results.
- **The curl condition ran on Markdown from HTML**, on Haiku and Sonnet only.
- **Fable's runs were split** between a usage-credit login and an API key, after a spend limit stopped the first run. Both use the same model and settings.
