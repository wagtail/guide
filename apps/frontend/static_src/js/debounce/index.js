/**
 * Delay calling `callback` until `wait` milliseconds have passed without it
 * being called again. Trailing-edge only, which is all we need for search.
 */
export function debounce(callback, wait) {
  let timeout;

  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => callback(...args), wait);
  };
}
