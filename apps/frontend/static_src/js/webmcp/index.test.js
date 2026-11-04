import {
  beforeEach,
  afterEach,
  describe,
  expect,
  it,
  vi,
} from 'vite-plus/test';
import { initWebMcp } from '.';

const registeredTools = new Map();

const createModelContext = () => ({
  registerTool: vi.fn(async (tool) => {
    registeredTools.set(tool.name, tool);
  }),
});

const csrfToken = 'test-csrf-token';

beforeEach(() => {
  registeredTools.clear();
  document.body.innerHTML = `<input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">`;
  window.languageCode = '';
});

afterEach(() => {
  document.body.innerHTML = '';
  vi.unstubAllGlobals();
  delete document.modelContext;
  delete navigator.modelContext;
  delete window.languageCode;
});

describe('initWebMcp', () => {
  it('does nothing when the modelContext API is absent', async () => {
    const debug = vi.spyOn(console, 'debug').mockImplementation(() => {});
    await initWebMcp();
    expect(debug).toHaveBeenCalledOnce();
    expect(Object.keys(registeredTools)).toHaveLength(0);
  });

  it('registers both tools with name, schema, execute and signal', async () => {
    const modelContext = createModelContext();
    document.modelContext = modelContext;

    await initWebMcp();

    expect(modelContext.registerTool).toHaveBeenCalledTimes(4);

    const search = registeredTools.get('search_docs');
    const feedback = registeredTools.get('submit_page_feedback');

    for (const tool of [search, feedback]) {
      expect(tool).toEqual(
        expect.objectContaining({
          name: expect.any(String),
          description: expect.any(String),
          inputSchema: expect.objectContaining({ type: 'object' }),
          execute: expect.any(Function),
          signal: expect.any(AbortSignal),
        }),
      );
      expect(tool.signal.aborted).toBe(false);
    }

    expect(search.inputSchema).toEqual(
      expect.objectContaining({
        required: ['query'],
        properties: expect.objectContaining({
          query: expect.objectContaining({ type: 'string' }),
          limit: expect.objectContaining({ type: 'integer' }),
        }),
      }),
    );

    expect(feedback.inputSchema).toEqual(
      expect.objectContaining({
        required: ['feedback'],
        properties: expect.objectContaining({
          feedback: expect.objectContaining({
            type: 'string',
            enum: ['happy', 'unhappy'],
          }),
          comment: expect.objectContaining({ type: 'string' }),
        }),
      }),
    );
  });

  it('aborts the tools on pagehide', async () => {
    document.modelContext = createModelContext();
    await initWebMcp();

    document.dispatchEvent(new Event('pagehide'));

    const search = registeredTools.get('search_docs');
    const feedback = registeredTools.get('submit_page_feedback');
    expect(search.signal.aborted).toBe(true);
    expect(feedback.signal.aborted).toBe(true);
  });

  it('search_docs fetches search_json with languageCode prefix and returns results', async () => {
    window.languageCode = 'fr';
    const results = [
      { id: 1, title: 'Page one', full_url: '/en/page-one/' },
      { id: 2, title: 'Page two', full_url: '/en/page-two/' },
    ];
    const fetchMock = vi.fn(async () => ({
      json: async () => results,
    }));
    vi.stubGlobal('fetch', fetchMock);
    document.modelContext = createModelContext();

    await initWebMcp();
    const search = registeredTools.get('search_docs');

    const returned = await search.execute({ query: 'streamfield' });

    expect(fetchMock).toHaveBeenCalledWith(
      'http://localhost:3000/fr/search_json/?query=streamfield',
    );
    expect(returned).toEqual(results);
  });

  it('search_docs slices results to limit and returns a message on error', async () => {
    const results = Array.from({ length: 12 }, (_, i) => ({ id: i }));
    const fetchMock = vi.fn(async () => ({ json: async () => results }));
    vi.stubGlobal('fetch', fetchMock);
    document.modelContext = createModelContext();

    await initWebMcp();
    const search = registeredTools.get('search_docs');

    expect(await search.execute({ query: 'x', limit: 2 })).toHaveLength(2);

    fetchMock.mockRejectedValue(new Error('network down'));
    expect(await search.execute({ query: 'x' })).toBe(
      'Search failed: network down',
    );
  });

  it('submit_page_feedback posts the feedback with the CSRF header', async () => {
    const fetchMock = vi.fn(async () => ({ json: async () => ({ pk: 7 }) }));
    vi.stubGlobal('fetch', fetchMock);
    document.modelContext = createModelContext();

    await initWebMcp();
    const feedback = registeredTools.get('submit_page_feedback');

    const result = await feedback.execute({ feedback: 'happy' });

    expect(fetchMock).toHaveBeenCalledWith(
      window.location.pathname,
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ feedback: 'happy' }),
        headers: expect.objectContaining({ 'X-CSRFToken': csrfToken }),
      }),
    );
    expect(result).toContain('happy');
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it('submit_page_feedback sends the comment follow-up when pk is returned', async () => {
    const fetchMock = vi.fn(async () => ({ json: async () => ({ pk: 42 }) }));
    vi.stubGlobal('fetch', fetchMock);
    document.modelContext = createModelContext();

    await initWebMcp();
    const feedback = registeredTools.get('submit_page_feedback');

    await feedback.execute({ feedback: 'unhappy', comment: 'Confusing part' });

    expect(fetchMock).toHaveBeenCalledTimes(2);
    expect(fetchMock).toHaveBeenLastCalledWith(
      window.location.pathname,
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ pk: 42, feedback_text: 'Confusing part' }),
        headers: expect.objectContaining({ 'X-CSRFToken': csrfToken }),
      }),
    );
  });

  it('returns a message instead of throwing when feedback POST fails', async () => {
    const fetchMock = vi.fn(async () => {
      throw new Error('server error');
    });
    vi.stubGlobal('fetch', fetchMock);
    document.modelContext = createModelContext();

    await initWebMcp();
    const feedback = registeredTools.get('submit_page_feedback');

    expect(await feedback.execute({ feedback: 'happy' })).toContain(
      'Feedback submission failed',
    );
  });

  it('fetch_page_markdown returns a message when the page has no markdown link', async () => {
    document.body.innerHTML = '';
    document.head.innerHTML = '';
    const fetchMock = vi.fn();
    vi.stubGlobal('fetch', fetchMock);
    document.modelContext = createModelContext();

    await initWebMcp();
    const markdown = registeredTools.get('fetch_page_markdown');

    expect(await markdown.execute({})).toBe(
      'This page has no Markdown version.',
    );
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('fetch_page_markdown fetches the markdown link and returns tokens', async () => {
    const markdownUrl = 'http://localhost:3000/en/topics/writing/markdown/';
    document.head.innerHTML =
      '<link rel="alternate" type="text/markdown;charset=utf-8" media="all" href="' +
      markdownUrl +
      '">';
    const fetchMock = vi.fn(async () => ({
      text: async () => '# Writing\n\nContent here.',
      headers: new Headers({ 'x-markdown-tokens': '128' }),
    }));
    vi.stubGlobal('fetch', fetchMock);
    document.modelContext = createModelContext();

    await initWebMcp();
    const markdown = registeredTools.get('fetch_page_markdown');

    expect(await markdown.execute({})).toEqual({
      url: markdownUrl,
      markdown: '# Writing\n\nContent here.',
      tokens: 128,
    });
    expect(fetchMock).toHaveBeenCalledWith(markdownUrl);
  });

  it('fetch_page_markdown omits tokens when the header is absent', async () => {
    const markdownUrl = 'http://localhost:3000/en/topics/writing/markdown/';
    document.head.innerHTML =
      '<link rel="alternate" type="text/markdown;charset=utf-8" media="all" href="' +
      markdownUrl +
      '">';
    const fetchMock = vi.fn(async () => ({
      text: async () => '# Writing',
      headers: new Headers(),
    }));
    vi.stubGlobal('fetch', fetchMock);
    document.modelContext = createModelContext();

    await initWebMcp();
    const markdown = registeredTools.get('fetch_page_markdown');

    expect(await markdown.execute({})).toEqual({
      url: markdownUrl,
      markdown: '# Writing',
    });
  });

  it('fetch_page_markdown returns a message on fetch error', async () => {
    const markdownUrl = 'http://localhost:3000/en/topics/writing/markdown/';
    document.head.innerHTML =
      '<link rel="alternate" type="text/markdown;charset=utf-8" media="all" href="' +
      markdownUrl +
      '">';
    const fetchMock = vi.fn(async () => {
      throw new Error('network down');
    });
    vi.stubGlobal('fetch', fetchMock);
    document.modelContext = createModelContext();

    await initWebMcp();
    const markdown = registeredTools.get('fetch_page_markdown');

    expect(await markdown.execute({})).toBe(
      'Markdown fetch failed: network down',
    );
  });

  it('fetch_llms_index fetches llms.txt at the site root', async () => {
    const text = '# Wagtail documentation\n\n- [Page](/en/page/): A page.';
    const fetchMock = vi.fn(async () => ({
      text: async () => text,
    }));
    vi.stubGlobal('fetch', fetchMock);
    document.modelContext = createModelContext();

    await initWebMcp();
    const llms = registeredTools.get('fetch_llms_index');

    expect(await llms.execute({})).toEqual({
      url: 'http://localhost:3000/llms.txt',
      markdown: text,
    });
    expect(fetchMock).toHaveBeenCalledWith('http://localhost:3000/llms.txt');
  });

  it('fetch_llms_index returns a message on fetch error', async () => {
    const fetchMock = vi.fn(async () => {
      throw new Error('network down');
    });
    vi.stubGlobal('fetch', fetchMock);
    document.modelContext = createModelContext();

    await initWebMcp();
    const llms = registeredTools.get('fetch_llms_index');

    expect(await llms.execute({})).toBe('llms.txt fetch failed: network down');
  });
});
