import { Tooltip } from "bootstrap"

export const handleFeedback = () => {
    //  Code to enable tooltip according to
    //  https://getbootstrap.com/docs/5.2/components/tooltips/#enable-tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]')
    const tooltipList = [...tooltipTriggerList].map(tooltipTriggerEl => new Tooltip(tooltipTriggerEl))

    const happyButton = document.querySelector('[data-happy-button]')
    const finishButton = document.querySelector('[data-finish-button]')
    const feedbackText = document.querySelector('[data-feedback-text]')
    const feedbackContainer = document.querySelector('[data-feedback-container]')

    const post_feedback = async (event, feedback) => {
        const pathname = window.location.pathname.split('/')
        const slug = pathname[pathname.length - 2]

        try {
            await fetch(`${window.location.origin}/submit-feedback/`, {
                method: "POST",
                body: JSON.stringify({
                    ...feedback,
                    slug, 
                }),
                headers: {
                    "Content-type": "application/json; charset=UTF-8"
                }
            })
            tooltipList.forEach((tooltip) => {
                tooltip.dispose()
            })
            feedbackContainer.innerHTML = 'Thanks for your feedback!'
        } catch(err) {
            console.log(err)
        }

    }
    happyButton.addEventListener("click", event => post_feedback(event, {feedback: "happy", feedback_text: ''}))
    finishButton.addEventListener("click", event => post_feedback(event, {feedback: "unhappy", feedback_text: feedbackText.value}))
}