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
 * Size reported by the Performance API, treating withheld values as 0.
 *
 * Browsers report 0 (or NaN for withheld values) when timing details are not
 * available, e.g. for cross-origin resources served without a
 * `Timing-Allow-Origin` header. Those count as an unknown size of 0.
 *
 * @param {number | undefined} size
 * @returns {number}
 */
const reportedBytes = (size) => (Number.isFinite(size) && size > 0 ? size : 0);

/**
 * Sum the transfer size of every resource the browser loaded for this page,
 * using the "resource timing" entries of the Performance API.
 *
 * The document itself is not a resource timing entry, so its own size is
 * included separately (encoded body size, or transfer size when available).
 *
 * Browsers only report timing details (and therefore sizes) for cross-origin
 * resources when the server sends a `Timing-Allow-Origin` header, so some
 * third-party resources may be counted as 0. Resources served from the cache
 * report a transfer size of 0 too, and fall back to their encoded body size so
 * the total stays comparable between visits.
 *
 * @param {PerformanceResourceTiming[]} entries Resource timing entries.
 * @param {PerformanceNavigationTiming | undefined} navigation Timing entry for the document.
 * @returns {number} Total bytes transferred.
 */
export const sumPageWeight = (entries, navigation) => {
  const resources = entries.reduce(
    (total, entry) =>
      total +
      (reportedBytes(entry.transferSize) ||
        reportedBytes(entry.encodedBodySize)),
    0,
  );
  const documentSize = navigation
    ? reportedBytes(navigation.transferSize) ||
      reportedBytes(navigation.encodedBodySize)
    : 0;
  return resources + documentSize;
};

/**
 * Read the page weight from the Performance API. Resources are collected at
 * call time rather than at load, so lazily loaded resources are included.
 */
export const getPageWeight = () =>
  sumPageWeight(
    performance.getEntriesByType('resource'),
    performance.getEntriesByType('navigation')[0],
  );

/**
 * Format a byte count for the userbar, e.g. "1.5 MB" or "42 kB".
 *
 * @param {number} bytes
 * @returns {string}
 */
export const formatPageWeight = (bytes) => {
  if (!bytes) {
    return 'Unknown';
  }
  const units = ['kB', 'MB', 'GB'];
  let value = bytes / 1000;
  let unit = 0;
  while (value >= 1000 && unit < units.length - 1) {
    value /= 1000;
    unit += 1;
  }
  return `${value < 10 ? value.toFixed(1) : Math.round(value)} ${units[unit]}`;
};

/**
 * Sustainable Web Design model v4, as a single figure in grams of CO2e per GB
 * of data transferred: https://sustainablewebdesign.org/estimating-digital-emissions/
 *
 * Energy intensities are split per system segment, and each segment splits its
 * energy into operational and embodied use. Operational emissions are
 * multiplied by the grid carbon intensity, while embodied emissions are left
 * unscaled (as the methodology does).
 *
 * With the most pessimistic assumptions (no green hosting, all visitors new,
 * no browser cache), every page view transfers all its data through every
 * segment, so the per-view formula reduces to page weight × this constant.
 */
const CARBON_INTENSITY = 458.29; // gCO2e/kWh, Ember "World" 2025.

const emissionSegments = [
  // Operational and embodied energy intensity, in kWh/GB.
  { operational: 0.055, embodied: 0.012 }, // Data centers.
  { operational: 0.059, embodied: 0.013 }, // Networks.
  { operational: 0.08, embodied: 0.081 }, // User devices.
];

/**
 * Emissions in grams of CO2e for one page view of a given weight, using the
 * Sustainable Web Design model v4: (OPDC + EMDC) + (OPN + EMN) + (OPUD + EMUD).
 *
 * Operational emissions are the operational energy intensity scaled by the
 * grid carbon intensity, while embodied emissions are the embodied energy
 * intensity as-is.
 *
 * @param {number} bytes Page weight, in bytes.
 * @returns {number}
 */
export const estimatePageEmissions = (bytes) =>
  emissionSegments.reduce(
    (total, { operational, embodied }) =>
      total + (bytes / 1e9) * (operational * CARBON_INTENSITY + embodied),
    0,
  );

/**
 * Describe the emissions of loading this page, e.g. "0.02 (49kB)".
 *
 * @param {number} bytes Page weight, in bytes.
 * @returns {string}
 */
export const formatPageEmissions = (bytes) =>
  `${estimatePageEmissions(bytes).toFixed(2)} (${formatPageWeight(
    bytes,
  ).replace(' ', '')})`;

/**
 * Register the content metrics with the Wagtail userbar. The userbar
 * loads before our main script and defines `window.wagtail.userbar`.
 */
export const initContentMetrics = () => {
  window.wagtail.userbar.registerMetric({
    id: 'internal-links',
    getLabel: () => 'Internal links',
    compute: (data) => countInternalLinks(data.innerHTML).toString(),
  });
  window.wagtail.userbar.registerMetric({
    id: 'page-weight',
    getLabel: () => 'gCO2e / pageview',
    compute: () => formatPageEmissions(getPageWeight()),
  });
};
