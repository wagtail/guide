# Agent readiness results: guide.wagtail.org

Which agent readiness techniques do AI agents actually use on the guide, and do they help agents answer users' questions? Results from October 2026, for [#486](https://github.com/wagtail/guide/issues/486). See [README.md](README.md) for the method and how to rerun it.

## In short

- **The MCP server is the one technique that clearly pays off.** With it, agents answered 97–100% of questions correctly on every model, against 80–89% when browsing the site. They were also up to twice as fast, and up to four times cheaper. This assumes the user has connected the server: agents don't find or connect MCP servers on their own, so users need to know it exists.
- **Agents only use discovery files that pages link to.** On the guide as it is, llms.txt, the agent skill, `.well-known` files, openapi.json and robots.txt were used in **0 of 564 runs**, even when we sent agents to the site to look something up: agents search the web, get a deep link, and read that one page. Once our Markdown pages linked to llms.txt and llms-full.txt, Haiku started using them in a few runs. Files that no page links to stayed unused.
- **Markdown is used on every page fetch, but our Markdown pages hide the navigation**, including the link to llms.txt. Agents saw fewer links in Markdown than in HTML, so they sometimes couldn't find the right page. The same site with every agent feature switched off did as well or better (+7 points for Haiku and Opus, level for Sonnet).
- **Converting pages to Markdown from their HTML, with Wagtail 8.1's converter, fixes the problem for Sonnet but not yet for Haiku.** Section pages now list their pages and every page links to llms.txt. Sonnet improved in every repeat (89% → 93%), now level with or slightly above the plain site (90%), and llms-full.txt and llms.txt got their first visits. Haiku is still 7 points behind the plain site (80% against 87%): the homepage doesn't link to Releases, because the converter leaves out the menu.
- **Links in the page's `<head>` (AI catalog, API catalog, openapi.json) don't reach agents answering users.** Claude Code reads pages as text, without `<head>`. Given curl to read raw HTML, agents never used it (0 of 198 runs). These links serve crawlers and scanners like ora.ai.
- **Cheap fixes:** ship the MCP server, convert Markdown from HTML (with a link to every section, Releases included, on the homepage), and redirect `/en/latest/*` to `/en/*`.

## What we tested

We asked Claude Code 33 realistic questions about using Wagtail, from "How do I schedule a page?" to "Why aren't my changes showing on the site?", and checked whether each answer had the right facts and linked to the right guide page. Each question ran 3 times on each model, under 4 conditions:

| Condition       | What the agent has                                      | What it tells us                  |
| --------------- | ------------------------------------------------------- | --------------------------------- |
| No tools        | Nothing, memory only                                    | How much the model already knows  |
| Real site       | Web search and page fetching, on the guide as it is     | What happens today                |
| Plain site      | The same, on the guide with every agent feature removed | What our agent features are worth |
| Real site + MCP | The same as real site, plus the guide's MCP server      | What MCP adds                     |

Two follow-up conditions ran on Haiku and Sonnet: [Markdown converted from HTML](#real-site-with-markdown-from-html), and the same with [curl to read raw HTML](#do-agents-read-raw-html-when-they-can).

The plain site removes llms.txt, llms-full.txt, Markdown pages and content negotiation, the agent skill, the AI and API catalogs, openapi.json, the MCP server, JSON-LD, WebMCP, Markdown 404s and Content Signals.

The questions cover information gathering (15), troubleshooting (8), release notes (6), and developer questions (4): 3 that the developer docs answer, and 1 that the guide answers with a link to them. They're asked in three ways:

- **Naming the guide** (19): "Using the user guide on guide.wagtail.org, how do I…?"
- **Not naming it** (9): "How do I…? Link to official documentation." The agent has to find the guide.
- **Sending the agent to the site** (5): "Go to guide.wagtail.org and find out…", like the tasks in the [ora.ai traces](https://github.com/agentready-org/standard/blob/main/data/traces.csv). Haiku and Sonnet only.

## How AI agents read web pages

Different kinds of AI agents see different parts of a page, which explains most of our results. Our benchmark uses Claude Code, a coding agent with a page-fetching tool.

| Kind of agent                                                  | Examples                                                    | How it reads a page                                                                                                                                      | Sees `<head>` links (AI catalog, openapi.json)? |
| -------------------------------------------------------------- | ----------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------- |
| Assistants and coding agents with a fetch tool that summarizes | Claude Code (WebFetch), Gemini CLI                          | Asks for the page (Claude Code asks for Markdown first), converts it to text, and has a small model summarize it. The main model only reads the summary. | No                                              |
| Agents with a fetch tool that passes the page on               | OpenCode                                                    | Gives the page's Markdown, text or HTML straight to the model                                                                                            | Only when asking for HTML                       |
| Agents with a shell                                            | Claude Code, Codex CLI, with `curl` allowed                 | Reads the raw HTML, if the agent chooses to                                                                                                              | Yes, but agents rarely choose it (see below)    |
| Browser agents                                                 | Claude in Chrome, ChatGPT agent and Atlas, Perplexity Comet | Reads what's shown on screen (accessibility tree and screenshots), and runs JavaScript, so it can use WebMCP tools                                       | No                                              |
| Search and AI crawlers                                         | GPTBot, ClaudeBot, OAI-SearchBot, PerplexityBot             | Reads raw HTML to build search indexes, which agents then search                                                                                         | Yes, but they don't answer users directly       |
| Readiness scanners                                             | ora.ai, is-agentic                                          | Checks which files and links a site has, and scores them                                                                                                 | Yes                                             |

What this means for our results:

- **Agents answering users mostly see text and links in the page itself.** Files and tags only machines read (`<head>` links, JSON-LD, `.well-known` files) reach crawlers and scanners, which is why ora.ai scores the guide 20/20 on discovery while our agents never used those files.
- **Agents follow links, they don't guess.** A May 2026 [Ahrefs study](https://ahrefs.com/blog/llmstxt-study/) of 137,000 sites found 97% of llms.txt files got no requests, and that "AI tools fetch llms.txt when a link, an index, or a user instruction tells them it exists". Claude Code was the second biggest named reader of llms.txt, after GPTBot.
- **Results for other kinds of agents may differ.** Browser agents can use WebMCP, and agents that read raw HTML can see `<head>` links. We only tested Claude Code.

## Results at a glance

Share of answers with the right facts and the right guide link, mean ± variation across 3 repeats:

| Condition                                 | Haiku 5.5   | Sonnet 5.5   | Opus 5.5\*   |
| ----------------------------------------- | ----------- | ------------ | ------------ |
| No tools                                  | 10% ± 2     | 15% ± 3      | 36% ± 4      |
| Real site                                 | 80% ± 2     | 89% ± 2      | 89% ± 4      |
| Plain site                                | 87% ± 5     | 90% ± 2      | 96% ± 0      |
| Real site, Markdown from HTML†            | 80% ± 2     | 93% ± 2      | not run      |
| Real site, Markdown from HTML, with curl‡ | 76% ± 5     | 85% ± 3      | not run      |
| **Real site + MCP**                       | **97% ± 3** | **100% ± 0** | **100% ± 0** |

\* Opus ran the first 28 questions, without the "go to the site" ones.
† The guide with page Markdown converted from the rendered HTML. See [Real site with Markdown from HTML](#real-site-with-markdown-from-html).
‡ The same, with curl available to read raw HTML. See [Do agents read raw HTML when they can?](#do-agents-read-raw-html-when-they-can)

### MCP versus the real site

| Model      | Correct answers | Time per answer | Cost per answer |
| ---------- | --------------- | --------------- | --------------- |
| Haiku 5.5  | +17 pts         | 22s → 11s       | 1.6¢ → 0.4¢     |
| Sonnet 5.5 | +11 pts         | 17s → 10s       | 2.8¢ → 2.5¢     |
| Opus 5.5   | +11 pts         | 28s → 16s       | 4.6¢ → 4.0¢     |

### By type of question (real site → with MCP)

| Question type         | Haiku       | Sonnet      | Opus        |
| --------------------- | ----------- | ----------- | ----------- |
| Information gathering | 84% → 96%   | 91% → 100%  | 91% → 100%  |
| Troubleshooting       | 67% → 100%  | 79% → 100%  | 88% → 100%  |
| Release notes         | 72% → 94%   | 89% → 100%  | 80% → 100%  |
| Developer questions   | 100% → 100% | 100% → 100% | 100% → 100% |

### By how the question is asked (real site → with MCP)

| Framing                     | Haiku      | Sonnet     | Opus       |
| --------------------------- | ---------- | ---------- | ---------- |
| Names the guide             | 81% → 98%  | 95% → 100% | 95% → 100% |
| Doesn't name the guide      | 74% → 100% | 81% → 100% | 78% → 100% |
| Sends the agent to the site | 87% → 87%  | 80% → 100% | not run    |

Troubleshooting and questions that don't name the guide gain the most: with MCP, the agent goes straight to the guide instead of relying on web search.

### Without the site

With no tools, models know many of the facts (68–86%) but rarely the guide page to cite (13–39%). Opus knows the most. Questions about recent releases (Wagtail 7.3 to 8.0) were answered correctly 0–13% of the time from memory, so for recent changes, agents need the site.

## Which techniques agents actually use

Share of runs that used each technique, across all models and conditions with web access:

| Technique                                         | Used?                                                                        | Evidence                                                                                   | Verdict                                                      |
| ------------------------------------------------- | ---------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ | ------------------------------------------------------------ |
| MCP server                                        | **Yes, ~87% of runs that had it**                                            | Agents chose it over web search almost every time                                          | Keep, and promote it                                         |
| Markdown content negotiation                      | **Yes, every fetch**                                                         | Claude Code always asks for Markdown first, and gets it                                    | Keep, but fix the navigation (below)                         |
| Guide pages (docs)                                | Yes, 54–87% of runs                                                          | The main source of answers                                                                 | Keep accurate                                                |
| Web search                                        | Yes, 57–92% of runs without MCP                                              | The usual first step, to find a deep link, even when sent to the site                      | Make sure pages rank and stay current                        |
| Homepage                                          | Sometimes: Haiku ~43%, Sonnet ~8%, Opus ~1%                                  | Mostly when sent to the site; stronger models go straight to a page                        | Markdown version needs the full table of contents            |
| Markdown mirror URLs (`/markdown/`)               | Rarely, 0–12%                                                                | Mostly Opus, after seeing the link                                                         | Fine as is                                                   |
| llms-full.txt, sitemap.xml                        | Almost never: 1–2% of Opus runs. llms-full.txt: 5% of Haiku runs once linked | Reached through links, never by guessing                                                   | Link from pages agents read                                  |
| llms.txt                                          | **Never** on the guide as it is; 1% of Haiku runs once linked                | Today's Markdown homepage doesn't link to it                                               | Link it from Markdown pages (tested with Markdown from HTML) |
| Agent skill (`.well-known/agent-skills`)          | **Never**                                                                    | No page links to it                                                                        | Link it from the homepage, then retest                       |
| AI catalog, API catalog, openapi.json, robots.txt | **Never**                                                                    | Linked only from `<head>`, which Claude Code drops; given curl, agents never read raw HTML | Keep for crawlers and scanners                               |
| Agent-friendly 404s                               | **Never seen**                                                               | Claude Code doesn't pass the body of a 404 to the model                                    | No impact with Claude Code                                   |
| JSON-LD, WebMCP, Content Signals                  | Can't be used by Claude Code                                                 | It converts pages to text, without scripts, and doesn't run JavaScript                     | Not measurable with this agent                               |

### Why the ora.ai study saw agents use discovery files

The [ora.ai traces](https://github.com/agentready-org/standard/blob/main/data/traces.csv) show llms.txt used in 23–77% of runs, depending on the model. Their data points to three differences with our setup, not to the agent harness (both harnesses they tested used llms.txt):

- **Where the agent starts.** Their agents started on the site's homepage in 91–96% of runs, for tasks like "find the pricing". Ours mostly start from a web search, which lands on the right page directly.
- **Links.** 86% of their llms.txt fetches followed a link the agent had seen. Agents almost never guess the path. Our Markdown pages, which are what Claude Code reads, don't link to llms.txt.
- **The model.** Claude Fable 5 used llms.txt in 54–77% of their runs, and almost never searched the web. Other models used it in 23–37%. We haven't tested Fable yet.

To check the first point, we added 5 questions that send the agent to the site ("Go to guide.wagtail.org and find out…"). Agents then reached the homepage much more often (Haiku 86%, Sonnet 46%), but still searched first in most runs, and **still never opened llms.txt**. This fits the links explanation: from today's Markdown homepage, there's no link to follow. With [Markdown from HTML](#real-site-with-markdown-from-html), which links llms.txt from every page, Haiku started opening it.

### Why the ora.ai study doesn't report on MCP

The ora.ai study measured which files agents reached and where their answers came from, not whether the answers were right, so it couldn't show what MCP adds. Its traces have no MCP column, and only 20 of 1,033 runs got their answer from an MCP server. Agents don't connect MCP servers mid-task: the user connects them before the session starts. An agent browsing a site barely meets MCP.

Our "real site + MCP" condition connects the guide's MCP server before every run, like a user who has installed it. So it measures what MCP is worth once installed, not whether agents find it. That makes promoting the server part of shipping it.

## What a typical agent does

The most common paths through the site, per model:

| Model  | Real site                                                                     | With MCP                     |
| ------ | ----------------------------------------------------------------------------- | ---------------------------- |
| Haiku  | search → guide page (×1–2), often via the homepage                            | MCP search (×1–2) → MCP read |
| Sonnet | search → guide page (38%), or **search only, without reading any page (30%)** | MCP search → MCP read        |
| Opus   | search → guide page (32%), or straight to a guide page from memory (12%)      | MCP search → MCP read        |

When sent to the site, the most common path is **search → guide homepage → guide page** (Haiku) or **search → guide page** (Sonnet).

- **Agents take 2–3 steps.** They don't explore: one search, one or two pages, then the answer.
- **Sonnet often answers from search snippets alone.** Only just over half its real-site answers cite a page it actually read, against 88% with MCP.
- **Search sends agents to old guide URLs** (`/en-6.3.x/…`, `/en-latest/…`) in 23–64% of runs. These redirect to the current page, so the answers stay right.
- **Developer questions go to docs.wagtail.org**, as they should, in every condition with web access.

## Where agents fail

Outside the no-tools condition, failures fall into four kinds:

| Kind of failure                    | Example                                                               | Cause                                                                            |
| ---------------------------------- | --------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| Couldn't find the right guide page | Cites the developer docs or a section page instead of "Manage images" | Markdown section pages don't list their pages (fixed by Markdown from HTML)      |
| Missed part of a multi-page answer | "What changed from 7.2 to 8.0?" covers 8.0 only                       | Same: the Markdown Releases page lists no releases (fixed by Markdown from HTML) |
| Used an outdated source            | Cites the old editor manual on docs.wagtail.org                       | Old pages still rank in search                                                   |
| Wrong or incomplete answer         | Mixes up multi-site and multi-tenancy                                 | The page answers it, but the agent read it too quickly                           |

Questions that failed most often on the real site:

- **"What changed between 7.2 and 8.0?"**: Opus failed 3 out of 3 on the real site and passed 3 out of 3 on the plain site. On the real site, it never found the 7.4 release notes.
- **"Go to guide.wagtail.org and find the latest release"**: Haiku and Sonnet failed 2 out of 3 on the real site. The guide gave them no list of releases to follow (the homepage doesn't link to Releases, and the Markdown Releases page listed none), so they answered from the developer docs instead.
- **"How do I see which pages are locked?"**: agents go to the old editor manual on docs.wagtail.org.
- **"What's the difference between multi-site and multi-tenancy?"**: answers mix up multi-tenancy and multi-instance.
- **"How do I get a deleted document back?"**: some answers miss that deleted documents can't be recovered.

### Why the real site sometimes does worse than the plain site

Claude Code asks for Markdown, and our Markdown pages leave out the navigation:

| Page     | Links in HTML                     | Links in Markdown |
| -------- | --------------------------------- | ----------------- |
| Homepage | 47 (every page, through the menu) | 5 (four sections) |
| Releases | 16 (every release)                | 0                 |

With the plain site, agents get HTML with the full menu, see "Manage images" or "New in Wagtail 7.4", and go there. With the real site, they see only the section names, and either guess or give up on the guide.

## Real site with Markdown from HTML

Our Markdown pages are rendered from page content only, so they leave out what visitors see around it: the "In this section" lists of section pages, and links to llms.txt. We tested the alternative: converting each page's rendered HTML to Markdown, with the `HTMLToMarkdownConverter` coming in Wagtail 8.1.

### How we tested it

- **Prototype on the guide:** the guide still runs Wagtail 8.0, so we tested a copy of the converter from Wagtail's `main` branch, adapted to 8.0 (with `draftjs_exporter` 7.3.1, and entity map keys as strings, as in 8.1). The change itself, using Wagtail 8.1's converter, is on the `feature/markdown-responses` branch.
- **What agents get:** page Markdown responses (content negotiation and `/markdown/` URLs) are converted from the page's full HTML (`content_selector="body"`), after the same frontmatter and `Page URL` line as before. The converter leaves out the menu (`<nav>`), and we marked the feedback form and language switcher with `data-markdown-ignore`. llms-full.txt and the MCP server are unchanged.
- **What changed for agents:** section pages list their pages (Releases: 0 → 16 links, How-to guides: 0 → 12), content pages start with an "On this page" list, and every page links to llms.txt and llms-full.txt. The homepage still links only to its four sections, not to Releases.
- **Eval run:** the "real site" condition only, on all 33 questions, 3 repeats, on Haiku and Sonnet, against the same local copy and proxy as the other conditions. Everything else was the same.

### Results (today's Markdown → Markdown from HTML)

|                               | Haiku 5.5     | Sonnet 5.5    |
| ----------------------------- | ------------- | ------------- |
| **All questions**             | 80% → 80%     | 89% → **93%** |
| Information gathering         | 84% → 82%     | 91% → 93%     |
| Troubleshooting               | 67% → **79%** | 79% → **88%** |
| Release notes                 | 72% → 61%     | 89% → 94%     |
| Names the guide               | 81% → **88%** | 95% → 96%     |
| Doesn't name the guide        | 74% → 74%     | 81% → 85%     |
| Sends the agent to the site   | 87% → **60%** | 80% → **93%** |
| llms-full.txt / llms.txt used | 0% → 5% / 1%  | 0% → 0%       |

- **Sonnet did better on Markdown from HTML than on today's Markdown in every repeat** (94%, 94%, 91% against 88%, 91%, 88%), and is now level with or slightly above the plain site (91%, 88%, 91%).
- **Haiku gains on troubleshooting and on questions naming the guide, but loses on "go to the site" and release questions.** In those runs, it opens the homepage, finds no link to Releases (the link is only in the menu, which the converter leaves out), and answers from docs.wagtail.org instead. Some losses are search noise, like citing the Icelandic copy of a page.
- **Discovery files got their first use** once pages linked to them: Haiku opened llms-full.txt in 5% of runs and llms.txt in 1%.

The converter fixes section pages, but not the homepage. Listing every section, Releases included, in the homepage's content (not only in the menu) should fix the rest.

### Machine-first formats and agent paths with Markdown from HTML

| Format                                                        | Today's Markdown               | Markdown from HTML                          | How agents got there                    |
| ------------------------------------------------------------- | ------------------------------ | ------------------------------------------- | --------------------------------------- |
| Markdown through content negotiation                          | Every fetch                    | Every fetch (all 199 successful page loads) | Claude Code always asks for Markdown    |
| llms-full.txt                                                 | Never                          | Haiku, 5 runs                               | A link on the page, mostly the homepage |
| llms.txt                                                      | Never                          | Haiku, 1 run                                | A link on the homepage                  |
| `/markdown/` URLs                                             | Haiku 4% of runs, Sonnet never | Haiku 5 runs, Sonnet 1 run                  | Links in search results or on pages     |
| Agent skill, `.well-known`, sitemap, openapi.json, robots.txt | Never                          | Never                                       | No page links to them                   |

- **Every machine-first visit followed a link** the agent had just seen (10 out of 10 for Haiku). None came from guessing a path. This matches the [ora.ai finding](#why-the-oraai-study-saw-agents-use-discovery-files) that agents reach discovery files through links.
- **All 10 runs that used them passed.** For Haiku, the homepage became a useful stop: "search → guide homepage → guide page" went from 11% to 18% of runs, and from the homepage it sometimes took llms.txt or llms-full.txt as a shortcut (for example "search → guide homepage → llms-full.txt → guide page").
- **Sonnet's paths didn't change.** It still goes "search → guide page" (37%) or answers from search results alone (35%). Its gain comes from better section pages when it lands on them.
- **10% of requests to the guide were 404s**, all guessed developer-docs-style paths like `/en/latest/…`, and 31% were redirects, mostly old versioned URLs from search.

Linking from pages agents already read is what makes machine-first formats used. To get the agent skill or other discovery files used, link them from the homepage too.

## Do agents read raw HTML when they can?

The AI catalog, API catalog and openapi.json are linked only from the page's `<head>`, which Claude Code's fetch tool drops. The one way Claude Code can see them is to fetch raw HTML with `curl`.

### How we tested it

We gave agents the same tools as the real site condition, plus `curl` through Claude Code's Bash tool (other shell commands weren't approved), on the guide with Markdown from HTML. curl gets raw HTML, `<head>` included, through the same proxy as other requests. We ran all 33 questions, 3 repeats, on Haiku and Sonnet. To check the setup, we asked an agent to fetch the homepage with curl and read its AI catalog link: it did.

### Results

|                                                                 | Haiku 5.5 | Sonnet 5.5 |
| --------------------------------------------------------------- | --------- | ---------- |
| Correct answers, Markdown from HTML                             | 80% ± 2   | 93% ± 2    |
| Correct answers, Markdown from HTML with curl                   | 76% ± 5   | 85% ± 3    |
| Runs that used curl                                             | 0 of 99   | 0 of 99    |
| `<head>` links followed (AI catalog, API catalog, openapi.json) | 0         | 0          |

- **Agents never chose curl.** Every page was read with Claude Code's own fetch tool, so no `<head>` link was ever seen.
- **Sonnet did worse with curl available, in every repeat** (88%, 82%, 85% against 94%, 94%, 91%), without using it. It read fewer pages (43% of answers came from a page it read, against 52%). Adding the Bash tool changes Claude Code's instructions and tools, which may explain this, but we can't tell from these runs. Haiku's difference is within noise.

So for agents like Claude Code, `<head>` links don't help users' questions. Keep them for crawlers and scanners, and put anything agents should find in the page's visible content.

## Cost

Costs are Claude Code's own figures at API list prices. They include web search fees and the page summaries WebFetch makes, but not grading.

| Model      | Cost per answer (real site) | Cost per answer (with MCP) | Whole benchmark      |
| ---------- | --------------------------- | -------------------------- | -------------------- |
| Haiku 5.5  | 1.6¢                        | 0.4¢                       | $3.56 (396 answers)  |
| Sonnet 5.5 | 2.8¢                        | 2.5¢                       | $9.06 (396 answers)  |
| Opus 5.5   | 4.6¢                        | 4.0¢                       | $12.68 (336 answers) |

The whole benchmark, about 1,130 answers, cost **about $25**. The Markdown from HTML rerun added $1.48 (Haiku) and $2.66 (Sonnet), and the curl condition $1.45 (Haiku) and $2.81 (Sonnet), 198 answers each. Rerunning one condition on one model costs $1–4 and takes about 15 minutes.

### Markdown versus HTML: size, cost and speed

Our Markdown pages are 4 to 27 times smaller than the same pages in HTML:

| Page          | HTML  | Markdown                | Smaller by |
| ------------- | ----- | ----------------------- | ---------- |
| Homepage      | 61 KB | 2.3 KB (~570 tokens)    | 27×        |
| Releases      | 48 KB | 2.4 KB (~600 tokens)    | 20×        |
| Page status   | 48 KB | 4.0 KB (~1,000 tokens)  | 12×        |
| Manage images | 52 KB | 6.0 KB (~1,500 tokens)  | 9×         |
| Manage pages  | 68 KB | 18.5 KB (~4,600 tokens) | 4×         |

For Claude Code, this saves almost nothing. Comparing the real site (Markdown) with the plain site (HTML), the page summaries Claude Code makes for each fetch cost about the same: 0.18¢ against 0.20¢ for Sonnet runs (11% fewer tokens), and 0.18¢ for both in Opus runs (2% fewer tokens). Cost and time per answer are within 0.3¢ and 2 seconds.

This is because Claude Code doesn't give the page to the model. WebFetch converts HTML to Markdown itself, then a small model (Haiku) summarizes the page, and most of the ~11,000–15,000 tokens per fetch are that summarizing step's own instructions. The main model only reads the summary.

Agents that put the whole page in their context, for example by fetching it with `curl` or with tools that return the full page, would save far more: there, the page size is the cost. We'll measure that when we add other agents. For Claude Code, what Markdown changes is which content and links agents see, not how much they pay.

## Recommendations

| Priority | Change                                                                                                                                                                                                         | Expected effect                                                                                                                                      |
| -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1        | **Ship the MCP server**, and make it easy to install: in the docs, llms.txt, the agent skill and the MCP Registry                                                                                              | +11–17 points on every model, faster and cheaper answers                                                                                             |
| 2        | **Convert page Markdown from the rendered HTML** with Wagtail 8.1's `HTMLToMarkdownConverter`, and link every section (Releases included) from the homepage's content, since the converter leaves out the menu | Measured: +4 points for Sonnet, level for Haiku. Linking Releases from the homepage should recover the "go to the site" questions Haiku still misses |
| 3        | **Redirect `/en/latest/*` to `/en/*`**                                                                                                                                                                         | Every 404 agents hit was a guessed path like this                                                                                                    |
| 4        | Keep llms.txt and the other discovery files, and link them from pages agents read, like the homepage                                                                                                           | Agents reached them only through links: once linked, Haiku used llms.txt and llms-full.txt. Unlinked files were never used                           |
| 5        | Ask the developer docs to point the old editor manual to the guide                                                                                                                                             | Removes an outdated source agents still land on                                                                                                      |

After changes 2 and 3, rerun the "real site" condition to measure them. Testing Claude Fable 5.1 would show whether a model that navigates sites directly uses llms.txt once it's linked.

## Caveats

- **One agent.** These are Claude Code results. Other agents fetch pages differently. Some read HTML and see JSON-LD, some fetch from their own servers, and some may read llms.txt. We'll add them next.
- **33 questions.** At 3 repeats, differences under about 5 points are within noise. The Sonnet real versus plain site gap (1 point) is noise; the Haiku and Opus gaps (7 points) are consistent across repeats and match the navigation problem we found in the traces. Sonnet's +4 points with Markdown from HTML held in all 3 repeats. The "send the agent to the site" results come from 5 questions only, so read them as indicative.
- **MCP was connected in advance.** The MCP results show what the server is worth once a user has connected it. Claude Code agents can't connect one mid-task, so how many people benefit depends on how many install it.
- **Local copy of the site.** The eval ran against a local copy with the same content as production (and the unreleased MCP server), through a proxy that makes it look like guide.wagtail.org. Production adds Cloudflare caching.
- **The curl condition ran on the guide with Markdown from HTML,** so compare it with that condition, not with the guide as it is.
- **Markdown from HTML is a prototype.** It ran on Haiku and Sonnet only, on a copy of the Wagtail 8.1 converter adapted to 8.0. Its Haiku differences on "go to the site" questions come from 5 questions, so read them as indicative.
- **Search results are live.** Web search used the real search index, so its results may change over time.
