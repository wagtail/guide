/* global gettext */
import { Tooltip } from 'bootstrap';
import { getCsrfToken } from '../csrf-token';

/**
 * Code to enable tooltip according to
 * https://getbootstrap.com/docs/5.2/components/tooltips/#enable-tooltips
 */
export const handleFeedback = () => {
  const tooltipTriggerList = document.querySelectorAll(
    '[data-bs-toggle="tooltip"]',
  );
  const tooltipList = [...tooltipTriggerList].map(
    (tooltipTriggerEl) => new Tooltip(tooltipTriggerEl),
  );

  const happyButton = document.querySelector('[data-happy-button]');
  const unhappyButton = document.querySelector('[data-unhappy-button]');
  const feedbackContainer = document.querySelector('[data-feedback-container]');
  const feedbackStatus = document.querySelector('[data-feedback-status]');
  const additionalFeedbackContainer = document.querySelector(
    '[data-additional-feedback-container]',
  );
  const submitButton = document.querySelector('[data-submit-button]');
  const feedbackText = document.querySelector('[data-feedback-text]');

  let feedbackPk = null;

  const postFeedback = async (feedback) => {
    try {
      const res = await fetch(window.location.pathname, {
        method: 'POST',
        body: JSON.stringify({
          feedback,
        }),
        headers: {
          'X-CSRFToken': getCsrfToken(),
          'Content-type': 'application/json; charset=UTF-8',
        },
      });
      const data = await res.json();
      tooltipList.forEach((tooltip) => {
        tooltip.dispose();
      });
      // Announce the confirmation in the live region, and move focus to it
      // before removing the buttons so focus isn't lost to the page body.
      feedbackStatus.textContent = gettext('Thanks for your feedback!');
      feedbackStatus.focus();
      feedbackContainer.remove();
      feedbackPk = data.pk;
      additionalFeedbackContainer.classList.add('active');
    } catch (err) {
      console.log(err);
    }
  };

  const updateFeedback = async (pk) => {
    try {
      await fetch(window.location.pathname, {
        method: 'POST',
        body: JSON.stringify({
          pk,
          feedback_text: feedbackText.value,
        }),
        headers: {
          'X-CSRFToken': getCsrfToken(),
          'Content-type': 'application/json; charset=UTF-8',
        },
      });
      feedbackStatus.focus();
      additionalFeedbackContainer.innerHTML = '';
    } catch (err) {
      console.log(err);
    }
  };
  if (happyButton) {
    happyButton.addEventListener('click', () => postFeedback('happy'));
  }
  if (unhappyButton) {
    unhappyButton.addEventListener('click', () => postFeedback('unhappy'));
  }
  if (submitButton) {
    submitButton.addEventListener('click', () => updateFeedback(feedbackPk));
  }
};
