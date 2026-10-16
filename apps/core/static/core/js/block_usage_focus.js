(function blockUsageFocus() {
    // Scroll to and briefly highlight a StreamField block when the page
    // editor is opened with a `#block-index-N` URL fragment (used by the
    // "Annotated blocks usage" report to link directly to a specific block).
    //
    // Blocks are identified by their position in the stream rather than
    // their UUID, because a block's UUID can differ between the live page
    // and the latest draft revision, whereas its position is stable.
    function focusBlock(index) {
        const children = document.querySelectorAll('[data-streamfield-child]');
        if (children.length <= index) return false;
        const el = children[index];

        // StreamField blocks render asynchronously (Telepath), so expanding
        // a collapsed block and scrolling to it needs to happen after the
        // element actually exists in the DOM.
        const toggle = el.querySelector('[data-panel-toggle]');
        if (toggle && toggle.getAttribute('aria-expanded') === 'false') {
            toggle.click();
        }

        setTimeout(() => {
            el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            el.classList.add('block-usage--highlight');
            setTimeout(() => {
                el.classList.remove('block-usage--highlight');
            }, 3000);
        }, 200);
        return true;
    }

    function init() {
        const hash = window.location.hash;
        const prefix = '#block-index-';
        if (!hash || hash.indexOf(prefix) !== 0) return;
        const index = parseInt(hash.slice(prefix.length), 10);
        if (Number.isNaN(index)) return;

        // Poll for up to 10s: the target block may not have rendered yet.
        let attempts = 0;
        const interval = setInterval(() => {
            if (focusBlock(index) || attempts > 100) {
                clearInterval(interval);
            }
            attempts += 1;
        }, 100);
    }

    if (document.readyState === 'complete') init();
    else window.addEventListener('load', init);
})();
