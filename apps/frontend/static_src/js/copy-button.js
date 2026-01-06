import { Dropdown } from 'bootstrap';

class CopyButton {
    static selector() {
        return '[data-copy-widget]';
    }

    constructor(node) {
        this.node = node;

        this.dropdown = new Dropdown(
            this.node.querySelector('[data-bs-toggle="dropdown"]'),
        );

        this.markdownURL = document.querySelector(
            '[rel="alternate"][type="text/markdown;charset=utf-8"]',
        ).href;

        this.copyPage = this.node.querySelector('[data-copy-page]');
        this.copyLink = this.node.querySelector('[data-copy-link]');
        this.copyPrompt = this.node.querySelector('[data-copy-prompt]');

        this.handleCopyPage = this.handleCopyPage.bind(this);
        this.handleCopyLink = this.handleCopyLink.bind(this);
        this.handleCopyPrompt = this.handleCopyPrompt.bind(this);

        this.copyPage.addEventListener('click', this.handleCopyPage);
        this.copyLink.addEventListener('click', this.handleCopyLink);
        this.copyPrompt.addEventListener('click', this.handleCopyPrompt);
    }

    async handleCopyPage() {
        try {
            const response = await fetch(this.markdownURL);
            if (!response.ok) throw new Error('Failed to fetch markdown');
            const text = await response.text();

            await navigator.clipboard.writeText(text);
            this.showFeedback(this.copyPage);
        } catch (error) {
            // eslint-disable-next-line no-console
            console.error('Copy failed', error);
        }
    }

    async handleCopyLink() {
        try {
            await navigator.clipboard.writeText(this.markdownURL);
            this.showFeedback(this.copyPage);
        } catch (error) {
            // eslint-disable-next-line no-console
            console.error('Copy failed', error);
        }
    }

    async handleCopyPrompt() {
        try {
            const response = await fetch(this.copyPrompt.dataset.copyPrompt);
            if (!response.ok) throw new Error('Failed to fetch markdown');
            const text = await response.text();

            await navigator.clipboard.writeText(text);
            this.showFeedback(this.copyPage);
        } catch (error) {
            // eslint-disable-next-line no-console
            console.error('Copy failed', error);
        }
    }

    showFeedback(btn) {
        /* eslint-disable no-param-reassign */
        const btnText = btn.textContent;

        btn.textContent = this.node.dataset.successText;

        setTimeout(() => {
            btn.textContent = btnText;
        }, 2000);
    }
}

export default CopyButton;
