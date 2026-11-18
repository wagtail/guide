import {
  afterEach,
  beforeEach,
  describe,
  expect,
  it,
  vi,
} from 'vite-plus/test';
import { handleFeedback } from '.';

describe('handleFeedback', () => {
  let fetchMock;

  beforeEach(() => {
    vi.stubGlobal('gettext', (text) => text);
    fetchMock = vi.fn(async () => ({ json: async () => ({ pk: 1 }) }));
    vi.stubGlobal('fetch', fetchMock);

    document.body.innerHTML = `
      <div class="feedback">
        <input type="hidden" name="csrfmiddlewaretoken" value="test-csrf-token">
        <div data-feedback-container>
          <h2>Was this page helpful?</h2>
          <button data-bs-toggle="tooltip" data-bs-title="This page was helpful" data-happy-button aria-label="Happy"></button>
          <button data-bs-toggle="tooltip" data-bs-title="This page could be improved" data-unhappy-button aria-label="Unhappy"></button>
        </div>
        <div role="status" tabindex="-1" data-feedback-status></div>
        <div data-additional-feedback-container>
          <label for="feedback">Your feedback</label>
          <textarea data-feedback-text id="feedback"></textarea>
          <button data-submit-button>Submit</button>
        </div>
      </div>
    `;
    handleFeedback();
  });

  afterEach(() => {
    document.body.innerHTML = '';
    vi.unstubAllGlobals();
  });

  it.each(['happy', 'unhappy'])(
    'announces %s feedback in the existing status region and moves focus to it',
    async (feedback) => {
      const status = document.querySelector('[role="status"]');
      const button = document.querySelector(`[data-${feedback}-button]`);
      button.focus();
      button.click();

      await vi.waitFor(() => {
        expect(status.textContent).toBe('Thanks for your feedback!');
      });
      // The same element that was on the page before the update, so screen
      // readers already track it as a live region.
      expect(status.isConnected).toBe(true);
      expect(document.activeElement).toBe(status);
      expect(JSON.parse(fetchMock.mock.calls[0][1].body)).toEqual({
        feedback,
      });
    },
  );

  it('keeps focus on the confirmation after submitting a comment', async () => {
    const status = document.querySelector('[role="status"]');
    document.querySelector('[data-unhappy-button]').click();
    await vi.waitFor(() => {
      expect(document.activeElement).toBe(status);
    });

    document.querySelector('[data-feedback-text]').value = 'Add a screenshot';
    const submit = document.querySelector('[data-submit-button]');
    submit.focus();
    submit.click();

    await vi.waitFor(() => {
      expect(submit.isConnected).toBe(false);
    });
    expect(document.activeElement).toBe(status);
    expect(status.isConnected).toBe(true);
    expect(JSON.parse(fetchMock.mock.calls[1][1].body)).toEqual({
      pk: 1,
      feedback_text: 'Add a screenshot',
    });
  });
});
