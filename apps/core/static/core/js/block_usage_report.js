(function blockUsageReport() {
    function closestRowCell(target) {
        return target.closest('.block-usage-report [data-block-index]');
    }

    function toggleHighlight(target, add) {
        const cell = closestRowCell(target);
        if (!cell) return;
        const key = cell.getAttribute('data-block-index');
        const table = cell.closest('.block-usage-report');
        if (!table) return;
        table
            .querySelectorAll(`[data-block-index="${CSS.escape(key)}"]`)
            .forEach((el) => {
                el.classList.toggle('block-usage__row--hover', add);
            });
    }

    document.addEventListener('mouseover', (event) => {
        toggleHighlight(event.target, true);
    });

    document.addEventListener('mouseout', (event) => {
        toggleHighlight(event.target, false);
    });
})();
