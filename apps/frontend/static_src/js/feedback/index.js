import { Tooltip } from 'bootstrap';

/**
 * Function to fetch cookie according to django docs
 * https://docs.djangoproject.com/en/4.1/howto/csrf/#acquiring-the-token-if-csrf-use-sessions-and-csrf-cookie-httponly-are-false
 *
 * @param {string} name
 * @returns {string?}
 */
function getCookie(name) {
    const cookies = (document.cookie || '')
        .split(';')
        .map((cookie) => cookie.trim());

    const foundCookie = cookies.find(
        (cookie) => cookie.substring(0, name.length + 1) === name + '=',
    );

    return foundCookie
        ? decodeURIComponent(foundCookie.substring(name.length + 1))
        : null;
}

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
    const feedbackContainer = document.querySelector(
        '[data-feedback-container]',
    );
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
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-type': 'application/json; charset=UTF-8',
                },
            });
            const data = await res.json();
            tooltipList.forEach((tooltip) => {
                tooltip.dispose();
            });
            feedbackContainer.innerHTML = 'Thanks for your feedback!';
            if (feedback === 'unhappy') {
                feedbackPk = data.pk;
                additionalFeedbackContainer.classList.add('active');
            }
        } catch (err) {
            // eslint-disable-next-line no-console
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
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-type': 'application/json; charset=UTF-8',
                },
            });
            additionalFeedbackContainer.innerHTML = '';
        } catch (err) {
            // eslint-disable-next-line no-console
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
        submitButton.addEventListener('click', () =>
            updateFeedback(feedbackPk),
        );
    }
};
