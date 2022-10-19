import { Tooltip } from 'bootstrap';
// Function to fetch cookie according to django docs
// https://docs.djangoproject.com/en/4.1/howto/csrf/#acquiring-the-token-if-csrf-use-sessions-and-csrf-cookie-httponly-are-false
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === name + '=') {
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1),
                );
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');

export const handleFeedback = () => {
    //  Code to enable tooltip according to
    //  https://getbootstrap.com/docs/5.2/components/tooltips/#enable-tooltips
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

    const post_feedback = async (feedback) => {
        try {
            const res = await fetch(window.location.pathname, {
                method: 'POST',
                body: JSON.stringify({
                    feedback,
                }),
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-type': 'application/json; charset=UTF-8',
                },
            });
            const data = await res.json();
            tooltipList.forEach((tooltip) => {
                tooltip.dispose();
            });
            feedbackContainer.innerHTML = 'Thanks for your feedback!';
            if (feedback == 'unhappy') {
                feedbackPk = data['pk'];
                additionalFeedbackContainer.classList.add('active');
            }
        } catch (err) {
            console.log(err);
        }
    };

    const update_feedback = async (pk) => {
        try {
            await fetch(window.location.pathname, {
                method: 'POST',
                body: JSON.stringify({
                    pk,
                    feedback_text: feedbackText.value,
                }),
                headers: {
                    'X-CSRFToken': csrftoken,
                    'Content-type': 'application/json; charset=UTF-8',
                },
            });
            additionalFeedbackContainer.innerHTML = '';
        } catch (err) {
            console.log(err);
        }
    };
    if (happyButton) {
        happyButton.addEventListener('click', () => post_feedback('happy'));
    }
    if (unhappyButton) {
        unhappyButton.addEventListener('click', () => post_feedback('unhappy'));
    }
    if (submitButton) {
        submitButton.addEventListener('click', () =>
            update_feedback(feedbackPk),
        );
    }
};
