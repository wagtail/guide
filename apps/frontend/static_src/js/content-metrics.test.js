import { beforeEach, describe, expect, it } from 'vite-plus/test';
import {
  countInternalLinks,
  estimatePageEmissions,
  formatPageEmissions,
  formatPageWeight,
  initContentMetrics,
  sumPageWeight,
} from './content-metrics';

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

describe('sumPageWeight', () => {
  it('sums the transfer size of all resources and the document', () => {
    const entries = [
      { transferSize: 1000, encodedBodySize: 900 },
      { transferSize: 2500, encodedBodySize: 2400 },
    ];
    expect(sumPageWeight(entries, { transferSize: 5000 })).toBe(8500);
  });

  it('falls back to encoded body size when transfer size is not reported', () => {
    const entries = [
      { transferSize: 0, encodedBodySize: 700 },
      { transferSize: NaN, encodedBodySize: 300 },
    ];
    expect(
      sumPageWeight(entries, { transferSize: 0, encodedBodySize: 900 }),
    ).toBe(1900);
  });

  it('counts resources with withheld timing details as 0', () => {
    const entries = [
      { transferSize: 0, encodedBodySize: 0 },
      { transferSize: 300, encodedBodySize: 300 },
    ];
    expect(sumPageWeight(entries, undefined)).toBe(300);
  });

  it('returns 0 when nothing was recorded', () => {
    expect(sumPageWeight([], undefined)).toBe(0);
  });
});

describe('formatPageWeight', () => {
  it('labels unknown sizes', () => {
    expect(formatPageWeight(0)).toBe('Unknown');
  });

  it('formats sizes in kB and MB', () => {
    expect(formatPageWeight(1_500)).toBe('1.5 kB');
    expect(formatPageWeight(42_000)).toBe('42 kB');
    expect(formatPageWeight(1_500_000)).toBe('1.5 MB');
    expect(formatPageWeight(250_000_000)).toBe('250 MB');
    expect(formatPageWeight(2_500_000_000)).toBe('2.5 GB');
  });
});

describe('estimatePageEmissions', () => {
  // Per GB: (0.055 × 458.29 + 0.012) for data centers, plus the same for
  // networks (0.059 / 0.013) and user devices (0.080 / 0.081):
  // 25.2179 + 27.0521 + 36.7442 = 89.0142 gCO2e/GB.
  const PER_GB = 89.0142;

  it('estimates emissions per GB of data transferred', () => {
    expect(estimatePageEmissions(1e9)).toBeCloseTo(PER_GB, 3);
  });

  it('scales linearly with page weight', () => {
    expect(estimatePageEmissions(49_000)).toBeCloseTo(
      (PER_GB * 49_000) / 1e9,
      5,
    );
    expect(estimatePageEmissions(0)).toBe(0);
  });
});

describe('formatPageEmissions', () => {
  it('shows grams of CO2e with the page weight in parentheses', () => {
    expect(formatPageEmissions(49_000)).toBe('0.00 (49kB)');
    expect(formatPageEmissions(276_500)).toBe('0.02 (277kB)');
    expect(formatPageEmissions(1_500_000)).toBe('0.13 (1.5MB)');
  });
});

describe('initContentMetrics', () => {
  it('registers the content metrics with the userbar', () => {
    const registered = [];
    window.wagtail = {
      userbar: { registerMetric: (metric) => registered.push(metric) },
    };
    document.body.innerHTML = '<a href="/en/cms/">CMS</a>';

    initContentMetrics();

    expect(registered).toHaveLength(2);
    expect(registered.map((metric) => metric.id)).toEqual([
      'internal-links',
      'page-weight',
    ]);
    expect(registered[0].getLabel()).toBe('Internal links');
    expect(registered[0].compute({ innerHTML: document.body.innerHTML })).toBe(
      '1',
    );
    expect(registered[1].getLabel()).toBe('gCO2e / pageview');
    expect(
      registered[1].compute({ innerHTML: document.body.innerHTML }),
    ).toMatch(/^\d+\.\d{2} (\(.+\)|Unknown)$/);
  });

  it('does nothing when the userbar is not rendered', () => {
    delete window.wagtail;

    expect(() => initContentMetrics()).not.toThrow();
  });
});
