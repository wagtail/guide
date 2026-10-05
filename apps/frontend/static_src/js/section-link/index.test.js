import { beforeEach, describe, expect, it } from 'vite-plus/test';
import { initSectionLink } from '.';

describe('initSectionLink', () => {
    beforeEach(() => {
        document.body.innerHTML = `
            <h1 id="title">Title</h1>
            <h2>No id</h2>
            <h3 id="subsection">Subsection</h3>
        `;
    });

    it('appends a section link to headings with an id', () => {
        initSectionLink();

        const links = document.querySelectorAll('a.section-link');
        expect([...links].map((link) => link.getAttribute('href'))).toEqual([
            '#title',
            '#subsection',
        ]);
        expect(links[0].textContent).toBe('¶');
        expect(links[0].parentElement.id).toBe('title');
    });

    it('skips headings without an id', () => {
        initSectionLink();

        expect(document.querySelector('h2 a')).toBeNull();
    });
});
