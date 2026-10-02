// Wire up light/dark mode buttons (there may be more than one, e.g. one in
// the header tools on desktop and one in the burger menu on mobile).
document.querySelectorAll('.js-theme-toggle').forEach((button) => {
    button.addEventListener('click', (event) => {
        document.dispatchEvent(
            new CustomEvent('theme:toggle-theme-mode', event),
        );
    });
});
