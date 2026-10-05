import { getCsrfToken } from '../csrf-token';

/**
 * Register WebMCP tools so AI agents can search the docs and submit
 * feedback. See https://webmachinelearning.github.io/webmcp/
 *
 * @returns {Promise<void>}
 */
export const initWebMcp = async () => {
  // Older Chrome builds expose the API on navigator instead of document.
  const modelContext = document.modelContext ?? navigator.modelContext;

  if (!modelContext) {
    console.debug('WebMCP modelContext API not available');
    return;
  }

  const controller = new AbortController();
  // Traditional multi-page site: unregister tools when the page goes away.
  document.addEventListener('pagehide', () => controller.abort(), {
    once: true,
  });

  const requestOptions = { signal: controller.signal };

  try {
    await Promise.all([
      modelContext.registerTool({
        name: 'search_docs',
        description:
          'Search the Wagtail documentation. Returns a list of matching pages with title, description, URL and parent section.',
        inputSchema: {
          type: 'object',
          properties: {
            query: {
              type: 'string',
              description: 'Search query',
            },
            limit: {
              type: 'integer',
              description:
                'Maximum number of results to return (defaults to 10)',
            },
          },
          required: ['query'],
        },
        execute: async ({ query, limit }) => {
          const searchUrl = `${window.location.origin}${
            window.languageCode ? `/${window.languageCode}` : ''
          }/search_json/?${new URLSearchParams({ query })}`;

          try {
            const response = await fetch(searchUrl);
            const results = await response.json();
            return results.slice(0, limit || 10);
          } catch (err) {
            return `Search failed: ${err.message}`;
          }
        },
        ...requestOptions,
      }),
      modelContext.registerTool({
        name: 'submit_page_feedback',
        description:
          'Submit feedback about the current documentation page. Use after reading a page, or when the user says a page was helpful/unhelpful.',
        inputSchema: {
          type: 'object',
          properties: {
            feedback: {
              type: 'string',
              enum: ['happy', 'unhappy'],
              description:
                'Whether the page was helpful (happy) or unhelpful (unhappy)',
            },
            comment: {
              type: 'string',
              description: 'Optional additional feedback text',
            },
          },
          required: ['feedback'],
        },
        execute: async ({ feedback, comment }) => {
          try {
            const response = await fetch(window.location.pathname, {
              method: 'POST',
              body: JSON.stringify({ feedback }),
              headers: {
                'X-CSRFToken': getCsrfToken(),
                'Content-type': 'application/json; charset=UTF-8',
              },
            });
            const data = await response.json();

            if (data.pk && comment) {
              await fetch(window.location.pathname, {
                method: 'POST',
                body: JSON.stringify({ pk: data.pk, feedback_text: comment }),
                headers: {
                  'X-CSRFToken': getCsrfToken(),
                  'Content-type': 'application/json; charset=UTF-8',
                },
              });
            }

            return `Feedback (${feedback}) submitted for this page.`;
          } catch (err) {
            return `Feedback submission failed: ${err.message}`;
          }
        },
        ...requestOptions,
      }),
      modelContext.registerTool({
        name: 'fetch_page_markdown',
        description:
          "Fetch the current page's content as Markdown, a cleaner representation for LLM consumption than the HTML. Only works when the current page has a Markdown representation.",
        inputSchema: {
          type: 'object',
          properties: {},
        },
        execute: async () => {
          const url = document.querySelector(
            'link[rel="alternate"][type^="text/markdown"]',
          )?.href;

          if (!url) {
            return 'This page has no Markdown version.';
          }

          try {
            const response = await fetch(url);
            const markdown = await response.text();
            const tokens = response.headers.get('x-markdown-tokens');
            return {
              url,
              markdown,
              ...(tokens !== null && { tokens: parseInt(tokens, 10) }),
            };
          } catch (err) {
            return `Markdown fetch failed: ${err.message}`;
          }
        },
        ...requestOptions,
      }),
      modelContext.registerTool({
        name: 'fetch_llms_index',
        description:
          "Fetch the site's llms.txt index, listing all documentation pages with their URLs and descriptions.",
        inputSchema: {
          type: 'object',
          properties: {},
        },
        execute: async () => {
          const url = `${window.location.origin}/llms.txt`;

          try {
            const response = await fetch(url);
            return { url, markdown: await response.text() };
          } catch (err) {
            return `llms.txt fetch failed: ${err.message}`;
          }
        },
        ...requestOptions,
      }),
    ]);
  } catch (err) {
    console.debug('WebMCP tool registration failed', err);
  }
};
