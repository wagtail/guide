import { beforeEach, describe, expect, it } from 'vite-plus/test';
import { initActiveNavItem } from '.';

describe('initActiveNavItem', () => {
  beforeEach(() => {
    window.history.pushState({}, '', '/en/how-to-guides/');
    document.body.innerHTML = `
            <a class="navigation__link" href="/en/concepts/">Concepts</a>
            <a class="navigation__link" href="/en/how-to-guides/">Guides</a>
        `;
  });

  it('marks only the link matching the current path as active', () => {
    initActiveNavItem();

    const [concepts, guides] = document.querySelectorAll('.navigation__link');
    expect(concepts.classList.contains('active')).toBe(false);
    expect(guides.classList.contains('active')).toBe(true);
  });
});
