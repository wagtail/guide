import { beforeEach, describe, expect, it } from 'vite-plus/test';
import { countInternalLinks, initContentMetrics } from './content-metrics';

describe('countInternalLinks', () => {
  beforeEach(() => {
    // The test page is the site under test: localhost:3000 is "internal".
    window.history.replaceState(null, '', '/en/editor-guide/writing/');
  });

  it('counts root-relative, relative and same-site absolute links', () => {
    document.body.innerHTML = `
      <a href="/en/editor-guide/">Guide</a>
      <a href="/zh_hans/editor-guide/writing/">Chinese version</a>
      <a href="http://localhost:3000/en/getting-started/">Absolute</a>
    `;
    expect(countInternalLinks(document.body.innerHTML)).toBe(3);
  });

  it('ignores external and non-HTTP links', () => {
    document.body.innerHTML = `
      <a href="https://wagtail.org/">Wagtail</a>
      <a href="//docs.wagtail.org/en/stable/">Docs</a>
      <a href="mailto:hello@example.com">Email</a>
      <a href="tel:+123456789">Phone</a>
      <a>No href</a>
    `;
    expect(countInternalLinks(document.body.innerHTML)).toBe(0);
  });

  it('ignores in-page anchors and links to the current page', () => {
    document.body.innerHTML = `
      <a href="#installation">Anchor</a>
      <a href="/en/editor-guide/writing/">Self</a>
      <a href="/en/editor-guide/pages/">Other page</a>
    `;
    expect(countInternalLinks(document.body.innerHTML)).toBe(1);
  });

  it('counts each target page once', () => {
    document.body.innerHTML = `
      <a href="/en/editor-guide/pages/">Pages</a>
      <a href="/en/editor-guide/pages/#creating">Create a page</a>
      <a href="/en/editor-guide/images/">Images</a>
    `;
    expect(countInternalLinks(document.body.innerHTML)).toBe(2);
  });

  it('finds links nested inside other content', () => {
    document.body.innerHTML = `
      <div><h2><a href="/en/tutorial/">Tutorial</a></h2></div>
      <figure><figcaption><a href="/en/cms/">CMS</a></figcaption></figure>
    `;
    expect(countInternalLinks(document.body.innerHTML)).toBe(2);
  });

  it('returns 0 for content without links', () => {
    document.body.innerHTML = '<p>No links here.</p>';
    expect(countInternalLinks(document.body.innerHTML)).toBe(0);
  });
});

describe('initContentMetrics', () => {
  it('registers the internal links metric with the userbar', () => {
    const registered = [];
    window.wagtail = {
      userbar: { registerMetric: (metric) => registered.push(metric) },
    };
    document.body.innerHTML = '<a href="/en/cms/">CMS</a>';

    initContentMetrics();

    expect(registered).toHaveLength(1);
    expect(registered[0].id).toBe('internal-links');
    expect(registered[0].getLabel()).toBe('Internal links');
    expect(registered[0].compute({ innerHTML: document.body.innerHTML })).toBe(
      '1',
    );
  });
});
