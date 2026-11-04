import { beforeEach, describe, expect, it, vi } from 'vite-plus/test';
import MobileMenu from '.';

describe('MobileMenu', () => {
  let instance;
  let toggle;
  let menu;

  beforeEach(() => {
    document.body.className = '';
    document.body.innerHTML = `
            <button data-mobile-menu-toggle aria-expanded="false"></button>
            <nav data-mobile-menu></nav>
        `;
    toggle = document.querySelector('[data-mobile-menu-toggle]');
    menu = document.querySelector('[data-mobile-menu]');
    instance = new MobileMenu(toggle);
  });

  it('opens the menu on click and notifies listeners', () => {
    const onMenuOpen = vi.fn();
    document.addEventListener('onMenuOpen', onMenuOpen);

    toggle.click();

    expect(toggle.getAttribute('aria-expanded')).toBe('true');
    expect(menu.classList.contains('is-visible')).toBe(true);
    expect(document.body.classList.contains('no-scroll')).toBe(true);
    expect(instance.state.open).toBe(true);
    expect(onMenuOpen).toHaveBeenCalledOnce();

    document.removeEventListener('onMenuOpen', onMenuOpen);
  });

  it('closes the menu on a second click', () => {
    toggle.click();
    toggle.click();

    expect(toggle.getAttribute('aria-expanded')).toBe('false');
    expect(menu.classList.contains('is-visible')).toBe(false);
    expect(document.body.classList.contains('no-scroll')).toBe(false);
    expect(instance.state.open).toBe(false);
  });
});
