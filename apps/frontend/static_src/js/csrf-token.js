/**
 * Get the CSRF token from the hidden input rendered by Django's
 * {% csrf_token %} template tag.
 *
 * @returns {string?}
 */
export const getCsrfToken = () =>
  document.querySelector('[name="csrfmiddlewaretoken"]')?.value;
