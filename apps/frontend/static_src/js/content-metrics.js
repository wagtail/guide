/**
 * Count links in the page content that lead to other pages of the same site.
 *
 * Uses the live preview's own URL as the base, so relative, root-relative and
 * absolute links all resolve the same way the browser would.
 *
 * @param {string} innerHTML HTML of the main content, from `ExtractedContent`.
 * @returns {number}
 */
export const countInternalLinks = (innerHTML) => {
  const page = new URL(window.location.href);
  const container = document.createElement('div');
  container.innerHTML = innerHTML;

  // In-page anchors and links to the current page aren't "internal links".
  return Array.from(container.querySelectorAll('a[href]')).reduce(
    (targets, link) => {
      const target = new URL(link.href);
      if (target.origin === page.origin && target.pathname !== page.pathname) {
        targets.add(target.pathname);
      }
      return targets;
    },
    new Set(),
  ).size;
};

/**
 * Register the "Internal links" metric with the Wagtail userbar. The userbar
 * loads before our main script and defines `window.wagtail.userbar`.
 */
export const initContentMetrics = () => {
  window.wagtail.userbar.registerMetric({
    id: 'internal-links',
    getLabel: () => 'Internal links',
    compute: (data) => countInternalLinks(data.innerHTML).toString(),
  });
};
